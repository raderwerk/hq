#!/usr/bin/env python3
"""Refuse-to-run checks that sit in front of every destructive Linear operation.

Two independent gates:

1. `check_workspace` -- the API key must resolve to THE workspace this repo is
   allowed to rewrite. The teardown is scoped by exclusion ("everything not in
   the spec"), so a key that points somewhere else would empty a stranger's
   workspace. `LINEAR_API_KEY` in the environment silently beats the key file,
   which is exactly how that happens by accident.
2. `check_backup` -- the export that is the only rollback path after a permanent
   delete must be complete, fresh and a superset of what is live right now.
"""

import datetime
import glob
import json
import os
import time

EXPECTED_ORG = {
    "id": "496f9ed7-9270-4def-9591-617d73915cb1",
    "urlKey": "fightclub-techhub",
}

BACKUP_MAX_AGE_HOURS = 2

# Sections whose live ids must all appear in the backup before we delete anything.
COVERED = (
    ("issues", "issues"),
    ("projects", "projects"),
    ("initiatives", "initiatives"),
    ("documents", "documents"),
)


class Refusal(SystemExit):
    def __init__(self, message):
        SystemExit.__init__(self, "REFUSING TO RUN: %s" % message)


def check_workspace(organization, org_arg, key_source):
    """Abort unless the key resolves to EXPECTED_ORG and to `--org`."""
    if not organization:
        raise Refusal("could not read `organization` -- cannot prove which workspace this key "
                      "belongs to")
    live = {"id": organization.get("id"), "urlKey": organization.get("urlKey")}
    if live != EXPECTED_ORG:
        raise Refusal(
            "this API key belongs to workspace %r (id %s), not %r (id %s). Key source: %s. "
            "Nothing was read further and nothing was written."
            % (live["urlKey"], live["id"], EXPECTED_ORG["urlKey"], EXPECTED_ORG["id"],
               key_source))
    if org_arg and org_arg != live["urlKey"]:
        raise Refusal("--org %r does not match the live workspace %r" % (org_arg, live["urlKey"]))
    return live


def newest_backup(directory):
    """Newest linear/backup-*.json. `.partial` exports do not match the glob."""
    candidates = sorted(glob.glob(os.path.join(directory, "backup-*.json")), key=os.path.getmtime)
    return candidates[-1] if candidates else None


def _parse_iso(value):
    """Epoch seconds for an ISO stamp, with or without a UTC offset."""
    text = (value or "").replace("Z", "+0000")
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            moment = datetime.datetime.strptime(text, fmt)
        except (TypeError, ValueError):
            continue
        if moment.tzinfo is None:
            moment = moment.astimezone()
        return moment.timestamp()
    return None


def backup_age_hours(backup):
    exported = ((backup.get("_meta") or {}).get("exportedAt"))
    stamp = _parse_iso(exported) if exported else None
    if stamp is None:
        return None
    return max(0.0, (time.time() - stamp) / 3600.0)


def check_backup(path, snapshot, destructive, on_warning=None):
    """Gate the run on a usable backup. Returns a short status line.

    `destructive` is True only when the run will really delete things; a dry run
    still checks completeness and coverage but downgrades staleness to a warning,
    because rehearsing the plan destroys nothing.
    """
    if not path:
        raise Refusal("no backup file found -- run backup_linear.py first")
    if not os.path.exists(path):
        raise Refusal("backup file %s does not exist" % path)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            backup = json.load(fh)
    except ValueError as exc:
        raise Refusal("backup %s is not valid JSON (%s)" % (path, exc))

    errors = backup.get("_errors") or {}
    if errors:
        raise Refusal("backup %s reports failed sections (%s) -- it is incomplete"
                      % (path, ", ".join(sorted(errors))))

    missing_report = []
    for live_key, backup_key in COVERED:
        live_ids = {n["id"] for n in snapshot.get(live_key) or []}
        backed_ids = {n["id"] for n in backup.get(backup_key) or [] if n.get("id")}
        missing = sorted(live_ids - backed_ids)
        if missing:
            missing_report.append("%s: %d not in the backup (%s%s)"
                                  % (backup_key, len(missing), ", ".join(missing[:3]),
                                     " ..." if len(missing) > 3 else ""))
    if missing_report:
        raise Refusal("backup %s does not cover the live workspace -- %s. Re-run "
                      "backup_linear.py." % (path, "; ".join(missing_report)))

    age = backup_age_hours(backup)
    age_text = "unknown age" if age is None else "%.1fh old" % age
    stale = age is None or age > BACKUP_MAX_AGE_HOURS
    if stale:
        message = ("backup %s is %s (limit %dh); take a fresh export before the destructive run"
                   % (os.path.basename(path), age_text, BACKUP_MAX_AGE_HOURS))
        if destructive:
            raise Refusal(message)
        if on_warning:
            on_warning(message)

    counts = {k: len(backup.get(k) or []) for _, k in COVERED}
    return "backup %s OK (%s, %s)" % (
        os.path.basename(path), age_text,
        ", ".join("%s=%d" % (k, v) for k, v in sorted(counts.items())))
