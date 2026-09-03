#!/usr/bin/env python3
"""Vocabulary shared by the builder, the teardown, the probes and the checks."""

import json
import re


def norm(value):
    return " ".join((value or "").split()).strip().lower()


def label_key(name, group):
    """Labels are identified by group -- 'intern' exists under two of them."""
    return "%s/%s" % (group, name) if group else name


# What `template.templateData` actually does, probed against this workspace on
# 2026-09-03 (throwaway template, created and deleted):
#
#   * it is written as a JSON object but READ BACK AS A JSON STRING;
#   * `title`, `priority`, `estimate` and `labelIds` survive verbatim;
#   * the markdown body is rendered into a ProseMirror blob under a new key
#     (`description` -> `descriptionData`) and THE KEY WE SENT IS DROPPED;
#   * sending `description` again on templateUpdate regenerates that blob and
#     discards the old content, so re-sending a body is safe.
#
# So the body can never be compared against what we sent -- an equality check
# over every key would call all 16 templates drifted on every run. The build
# compares only the keys Linear echoes back, and re-sends the body whenever one
# of those really differs.
TEMPLATE_BODY_KEYS = ("description", "content")
TEMPLATE_SERVER_BLOBS = ("descriptionData", "contentData")

# Linear creates the triage state itself when triageEnabled goes on, and then
# refuses to change ANY of it. Probed against this workspace on 2026-09-03:
# name, color, description and position each came back "unable to update
# reserved state". A spec is free to call it something else -- issues still
# route to it by id, so nothing breaks -- but the board keeps showing "Triage".
RESERVED_STATE_TYPES = ("triage",)

# Linear also owns workflow-state ORDER. `workflowStateUpdate` echoes a new
# `position` back in its response and then does not store it: reading the state
# again returns the old value (probed 2026-09-03). Reconciling it would re-issue
# the same updates on every run forever, so the build sets position only at
# create time and leaves it alone afterwards.
STATE_SERVER_OWNED = ("position",)

# Linear does not store markdown verbatim, it re-serialises it. Probed against
# the 69 issues and 8 projects of this spec on 2026-09-03, it:
#   * adds and removes blank lines around block elements,
#   * rewrites `-` and `+` bullets to `*`,
#   * autolinks anything host- or address-shaped, so `user.app` comes back as
#     `[user.app](<http://user.app>)`.
# None of that is a content change, but a byte comparison calls all 69 issues
# drifted on every single run. The two patterns below invert exactly those three
# rewrites and nothing else, so a re-run is a true no-op while a real edit to a
# body still shows up as drift.
MARKDOWN_BULLET = re.compile(r"^(\s*)[-*+] ")
MARKDOWN_AUTOLINK = re.compile(r"\[([^\]]+)\]\(<(?:https?://|mailto:)([^>]+)>\)")


def norm_markdown(text):
    """A markdown body reduced to the part Linear cannot rewrite."""
    def unlink(match):
        label, target = match.group(1), match.group(2)
        same = target.lower().rstrip("/") == label.lower().rstrip("/")
        return label if same else match.group(0)

    text = MARKDOWN_AUTOLINK.sub(unlink, text or "")
    lines = (MARKDOWN_BULLET.sub(r"\1- ", line.rstrip()) for line in text.strip().splitlines())
    return "\n".join(line for line in lines if line)


def parse_template_data(raw):
    """templateData as an object, whether Linear hands back a string or a dict."""
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except ValueError:
            return {}
    return raw or {}


# Team fields the spec owns end to end. Anything not listed here is Linear's.
TEAM_SETTINGS = ("description", "icon", "color", "cyclesEnabled", "cycleStartDay",
                 "cycleDuration", "cycleCooldownTime", "upcomingCycleCount",
                 "cycleLockToActive", "cycleIssueAutoAssignStarted", "triageEnabled",
                 "issueEstimationType")

# Values each estimation scale can actually store. Anything else is rounded
# server-side, after which the build would "fix" it again on every run.
ESTIMATION_SCALES = {
    "notUsed": set(),
    "linear": {0, 1, 2, 3, 4, 5},
    "exponential": {0, 1, 2, 4, 8, 16},
    "fibonacci": {0, 1, 2, 3, 5, 8},
    "tShirt": {0, 1, 2, 3, 5, 8},
}


class Plan(object):
    """Every intended change, recorded once.

    A dry run prints it and stops there; --apply prints the same list after the
    fact. `problems` are things a human has to look at, `notes` are measurements
    worth reading (the Free-plan issue counter, what the probes learned).
    """

    def __init__(self):
        self.entries = []
        self.problems = []
        self.notes = []

    def add(self, op, kind, name, detail="", query=None, variables=None, weight=1):
        self.entries.append({"op": op, "kind": kind, "name": name, "detail": detail,
                             "query": query, "variables": variables, "weight": weight})

    def problem(self, text):
        if text not in self.problems:
            self.problems.append(text)

    def note(self, text):
        if text not in self.notes:
            self.notes.append(text)

    def counts(self):
        out = {}
        for e in self.entries:
            out.setdefault((e["kind"], e["op"]), 0)
            out[(e["kind"], e["op"])] += e.get("weight", 1)
        return out

    def render(self, verbose=True):
        lines = []
        if verbose:
            for e in self.entries:
                detail = (" -- " + e["detail"]) if e["detail"] else ""
                lines.append("  %-9s %-14s %s%s" % (e["op"], e["kind"], e["name"], detail))
        lines.append("")
        lines.append("  %-14s %-9s %s" % ("KIND", "OP", "COUNT"))
        for (kind, op), n in sorted(self.counts().items()):
            lines.append("  %-14s %-9s %d" % (kind, op, n))
        lines.append("  %-14s %-9s %d"
                     % ("TOTAL", "", sum(e.get("weight", 1) for e in self.entries)))
        return "\n".join(lines)
