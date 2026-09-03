#!/usr/bin/env python3
"""Apply design/linear-spec.json to the live Linear workspace, idempotently.

    python3 build_linear.py --dry-run --teardown --backup-required --validate
    python3 build_linear.py --apply --teardown --probe --backup-required
    python3 build_linear.py --verify                  # compare live workspace to the spec

Order: workspace guard -> backup gate -> issue-budget check -> probes -> teardown
-> teams+states+settings -> labels -> probe -> initiatives -> projects (+milestones,
+initiative link) -> templates -> documents -> issues.

Nothing mutates unless --apply is given, and a dry run is a true rehearsal: the
teardown replays itself on the in-memory snapshot, so `--dry-run --teardown`
prints the operations `--apply --teardown` will send.

Users are never touched.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from linear_api import (LinearError, gql, key_source, last_headers,  # noqa: E402
                        page, stats)
import linear_check  # noqa: E402
import linear_guard  # noqa: E402
from linear_common import (RESERVED_STATE_TYPES, TEAM_SETTINGS,  # noqa: E402
                           TEMPLATE_BODY_KEYS, TEMPLATE_SERVER_BLOBS, Plan,
                           label_key, norm, norm_markdown, parse_template_data)
from linear_probe import Probe  # noqa: E402
from linear_teardown import LEGACY_TEAM_ID, Teardown  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_PATH = os.path.join(ROOT, "design", "linear-spec.json")
BACKUP_DIR = os.path.join(ROOT, "linear")
IDMAP_PATH = os.path.join(ROOT, "linear", "idmap.json")

PLAN_LIMIT_RETRIES = 8
PLAN_LIMIT_WAIT = 15

# Free plan. Creating an issue raises organization.createdIssueCount; whether
# deleting one lowers it again is what the probe and the teardown measure.
FREE_PLAN_ISSUE_CAP = 250
PROBE_ISSUE_ALLOWANCE = 5

# Linear owns these two state types: they cannot be created, and it refuses to
# archive them, so the reconciliation leaves them alone.
PROTECTED_STATE_TYPES = ("triage", "duplicate")

# What teamCreate seeds a new team with (verified against this workspace).
DEFAULT_TEAM_STATES = [
    {"name": "Triage", "type": "triage", "position": 0},
    {"name": "Backlog", "type": "backlog", "position": 0},
    {"name": "Todo", "type": "unstarted", "position": 1},
    {"name": "In Progress", "type": "started", "position": 2},
    {"name": "Done", "type": "completed", "position": 3},
    {"name": "Canceled", "type": "canceled", "position": 4},
    {"name": "Duplicate", "type": "duplicate", "position": 5},
]


class Builder(object):
    def __init__(self, spec, apply_changes, teardown, verbose=True, probe=False,
                 idmap_path=IDMAP_PATH, allow_tight_budget=False):
        self.spec = spec
        self.apply = apply_changes
        self.teardown = teardown
        self.verbose = verbose
        self.probe = probe
        self.idmap_path = idmap_path
        self.allow_tight_budget = allow_tight_budget
        self.plan = Plan()
        self.ids = {}          # "kind:key" -> linear id (or a <dry:...> placeholder)
        self.snapshot = {}
        self.probe_results = {}
        self.spec_team_keys = [t["key"] for t in spec.get("teams", [])]

    # ---------- id bookkeeping ----------

    def put_id(self, kind, key, value):
        self.ids["%s:%s" % (kind, key)] = value

    def get_id(self, kind, key):
        return self.ids.get("%s:%s" % (kind, key))

    def placeholder(self, kind, key):
        return "<dry:%s:%s>" % (kind, key)

    def is_placeholder(self, value):
        return isinstance(value, str) and value.startswith("<dry:")

    def assert_no_placeholders(self, variables):
        """A dry-run placeholder in a real payload means an id we never got back."""
        def walk(node, path):
            if isinstance(node, dict):
                for key, value in node.items():
                    walk(value, "%s.%s" % (path, key))
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    walk(value, "%s[%d]" % (path, index))
            elif self.is_placeholder(node):
                raise LinearError("refusing to send %s=%s: that is a dry-run placeholder, so an "
                                  "earlier mutation never returned an id" % (path, node))
        walk(variables, "vars")

    # ---------- mutation plumbing ----------

    def mutate(self, kind, op, name, query, variables, result_path, detail="",
               tolerate=False, record=True):
        """Record the action; execute it only when --apply is on. Returns the payload."""
        if "success" not in query:
            raise ValueError("the mutation for %s %s must select `success`" % (op, kind))
        if record:
            self.plan.add(op, kind, name, detail, query=query, variables=variables)
        if not self.apply:
            return None
        try:
            node = self.execute(query, variables, result_path)
        except LinearError as exc:
            if not tolerate:
                raise
            self.plan.problem("%s %s %r was refused (%s); continuing" % (op, kind, name, exc))
            return None
        if self.verbose:
            sys.stderr.write("  %s %s %s\n" % (op, kind, name))
            sys.stderr.flush()
        return node

    def execute(self, query, variables, result_path):
        """Send one mutation and insist that it actually did something."""
        self.assert_no_placeholders(variables)
        data = gql(query, variables, retry_transport=False)
        root = result_path.split(".")[0]
        payload = (data or {}).get(root)
        if not isinstance(payload, dict):
            raise LinearError("mutation %s returned no payload" % root,
                              query=query, variables=variables)
        if not payload.get("success"):
            raise LinearError("mutation %s reported success=%r" % (root, payload.get("success")),
                              query=query, variables=variables)
        node = data
        for part in result_path.split("."):
            node = (node or {}).get(part)
        if node is None:
            raise LinearError("mutation %s succeeded but returned a null %s -- refusing to carry "
                              "on with an unknown id" % (root, result_path),
                              query=query, variables=variables)
        return node

    # Bodies Linear re-serialises; see norm_markdown for what it rewrites.
    MARKDOWN_FIELDS = ("description", "content")

    @classmethod
    def diff_fields(cls, live, wanted):
        """Fields in `wanted` whose live value differs (None in wanted = leave alone)."""
        out = {}
        for key, value in wanted.items():
            if value is None:
                continue
            current = live.get(key)
            if isinstance(value, str) and isinstance(current, str):
                if key in cls.MARKDOWN_FIELDS:
                    if norm_markdown(value) != norm_markdown(current):
                        out[key] = value
                elif value.strip() != current.strip():
                    out[key] = value
            elif current != value:
                out[key] = value
        return out

    def checkpoint(self):
        """Persist the id map mid-run, so a crash still leaves a trail."""
        if self.apply:
            self.write_idmap(self.idmap_path)

    # ---------- reading the live workspace ----------

    def load_snapshot(self):
        sys.stderr.write("Reading live workspace ...\n")
        snap = {}
        head = gql("query { viewer { id name email } "
                   "organization { id name urlKey createdIssueCount } }")
        snap["viewer"] = head["viewer"]
        snap["organization"] = head["organization"]
        snap["users"] = page("users", "id name displayName email app active", False, 50)
        snap["teams"] = page(
            "teams",
            "id key name description icon color cyclesEnabled cycleStartDay cycleDuration "
            "cycleCooldownTime upcomingCycleCount cycleLockToActive "
            "cycleIssueAutoAssignStarted triageEnabled issueEstimationType archivedAt "
            "autoCloseStateId defaultIssueState { id name } "
            "states { nodes { id name type color position description archivedAt "
            "issues(first: 1) { nodes { id } } } }",
            False, 10, on_problem=self.plan.problem)
        snap["archivedTeams"] = page("teams", "id key name archivedAt", True, 25,
                                     on_problem=self.plan.problem)
        snap["issueLabels"] = page(
            "issueLabels", "id name color description isGroup parent { id name } team { id key }",
            False, 100)
        snap["projectLabels"] = page(
            "projectLabels", "id name color description isGroup parent { id name }", False, 100)
        snap["templates"] = gql(
            "query { templates { id name type description templateData team { id key } } }"
        )["templates"]
        snap["initiatives"] = page(
            "initiatives", "id name description content status", False, 10)
        snap["projects"] = page(
            "projects",
            "id name description content sortOrder lead { id name } "
            "teams { nodes { id key } } labels { nodes { id name } } "
            "initiatives { nodes { id name } } "
            "projectMilestones { nodes { id name description targetDate sortOrder } }",
            False, 10)
        snap["documents"] = page(
            "documents", "id title project { id name } initiative { id name }", False, 25)
        issues = page(
            "issues",
            "id identifier title description priority estimate sortOrder trashed "
            "team { id key } state { id name } project { id name } "
            "projectMilestone { id name } delegate { id name } parent { id title } "
            "labels { nodes { id name } }",
            False, 25)
        trashed = [i for i in issues if i.get("trashed")]
        if trashed:
            self.plan.note("%d issue(s) sit in the trash: ignored for matching, but they may "
                           "still count against the Free-plan issue budget" % len(trashed))
        snap["issues"] = [i for i in issues if not i.get("trashed")]
        self.snapshot = snap
        self.reindex()
        sys.stderr.write(
            "  teams=%d issues=%d projects=%d initiatives=%d labels=%d docs=%d templates=%d\n"
            % (len(snap["teams"]), len(snap["issues"]), len(snap["projects"]),
               len(snap["initiatives"]), len(snap["issueLabels"]), len(snap["documents"]),
               len(snap["templates"])))

    def reindex(self):
        """(Re)build every lookup over the snapshot. The teardown edits the snapshot
        in place -- in dry runs too -- and calls this again afterwards."""
        snap = self.snapshot
        self.by_team_key = {t["key"]: t for t in snap["teams"]}
        self.label_by_key = {self.live_label_key(l): l for l in snap["issueLabels"]}
        self.project_label_by_name = {norm(l["name"]): l for l in snap["projectLabels"]}
        self.initiative_by_name = {norm(i["name"]): i for i in snap["initiatives"]}
        self.project_by_name = {norm(p["name"]): p for p in snap["projects"]}
        self.document_by_title = {norm(d["title"]): d for d in snap["documents"]}
        self.template_by_key = {}
        for t in snap["templates"]:
            tk = (t.get("team") or {}).get("key")
            self.template_by_key[(t["type"], norm(t["name"]), tk)] = t
        self.issue_by_key = {}
        for i in snap["issues"]:
            tk = (i.get("team") or {}).get("key")
            self.issue_by_key[(tk, norm(i["title"]))] = i
        self.app_user_by_name = {norm(u["name"]): u for u in snap["users"] if u.get("app")}

    # ---------- label identity ----------

    @staticmethod
    def live_label_key(live):
        parent = (live.get("parent") or {}).get("name")
        return norm(label_key(live["name"], parent))

    @staticmethod
    def spec_label_key(spec_label):
        return label_key(spec_label["name"], spec_label.get("group"))

    def spec_label_keys(self):
        return {norm(self.spec_label_key(l)) for l in self.spec.get("labels", [])}

    def spec_group_pair(self, group):
        """Two label references from one group -- what the probe pokes Linear with."""
        members = [self.spec_label_key(l) for l in self.spec.get("labels", [])
                   if norm(l.get("group") or "") == norm(group)]
        return members[:2]

    def resolve_label_id(self, reference, where):
        """'group/child' first, then a bare child name if it is unambiguous."""
        found = self.get_id("label", reference)
        if found:
            return found
        if "/" not in reference:
            tails = [key for key in self.ids
                     if key.startswith("label:") and key.endswith("/" + reference)]
            if len(tails) == 1:
                return self.ids[tails[0]]
            if len(tails) > 1:
                self.plan.problem("%s references %r, which exists in %d groups (%s); write it as "
                                  "group/child" % (where, reference, len(tails),
                                                   ", ".join(sorted(t[6:] for t in tails))))
                return None
        self.plan.problem("%s references unknown label %r" % (where, reference))
        return None

    # ---------- gates ----------

    def guard_workspace(self, org_arg):
        live = linear_guard.check_workspace(self.snapshot.get("organization"), org_arg,
                                            key_source())
        sys.stderr.write("Workspace: %s (%s), key from %s\n"
                         % (live["urlKey"], live["id"], key_source()))

    def check_backup(self, backup_path):
        status = linear_guard.check_backup(
            backup_path, self.snapshot, destructive=self.apply and self.teardown,
            on_warning=self.plan.problem)
        sys.stderr.write("%s\n" % status)

    def check_issue_budget(self):
        """The Free plan counts issues ever created, so rebuilds are finite."""
        created = (self.snapshot.get("organization") or {}).get("createdIssueCount")
        if created is None:
            return
        need = len(self.spec.get("issues", [])) + PROBE_ISSUE_ALLOWANCE
        head = FREE_PLAN_ISSUE_CAP - created
        message = ("Free-plan issue budget: %d created, %d of %d left, this build needs %d"
                   % (created, head, FREE_PLAN_ISSUE_CAP, need))
        self.plan.note(message)
        sys.stderr.write("%s\n" % message)
        if head >= need:
            return
        if self.apply and self.teardown and not self.allow_tight_budget:
            raise SystemExit(
                "REFUSING TO RUN: %s. If deleting issues does not give the counter back, this "
                "build strands partway through issueCreate. Prove it with --probe first, or "
                "pass --allow-tight-budget." % message)
        self.plan.problem("%s -- the build does not fit unless deleting issues frees the counter"
                          % message)

    def preflight(self):
        """Resolve every live-side reference before the first mutation."""
        for name in sorted({i["delegate"] for i in self.spec.get("issues", [])
                            if i.get("delegate")}):
            if norm(name) not in self.app_user_by_name:
                self.plan.problem(
                    "no installed app user named %r -- %d issue(s) would land without a delegate "
                    "(installed app users: %s)"
                    % (name, sum(1 for i in self.spec["issues"] if i.get("delegate") == name),
                       ", ".join(sorted(u["name"] for u in self.app_user_by_name.values()))
                       or "none"))

    # ---------- step c: teams, states, settings ----------

    def build_teams(self):
        for spec_team in self.spec.get("teams", []):
            key = spec_team["key"]
            live = self.by_team_key.get(key)
            wanted = {"name": spec_team.get("name")}
            wanted.update({f: spec_team.get(f) for f in TEAM_SETTINGS})
            if live:
                self.put_id("team", key, live["id"])
                changes = self.diff_fields(live, wanted)
                if changes:
                    self.update_team(key, live["id"], changes)
                else:
                    self.plan.add("ok", "team", key, "already matches spec")
            else:
                team = self.create_team(spec_team, wanted)
                team_id = team["id"] if team else self.placeholder("team", key)
                self.put_id("team", key, team_id)
                self.by_team_key[key] = self.fresh_team_states(spec_team, team_id)
            self.build_states(spec_team)
            self.checkpoint()

    TEAM_UPDATE = ("mutation($id: String!, $input: TeamUpdateInput!) "
                   "{ teamUpdate(id: $id, input: $input) { success team { id } } }")

    def update_team(self, key, team_id, changes):
        """teamUpdate, except that an icon Linear dislikes must not kill the run.

        `teamCreate` silently drops an icon outside Linear's vocabulary, but
        `teamUpdate` rejects the entire payload with 'Argument Validation Error'.
        The same spec value therefore passes when the team is created and fails on
        every run after that, taking the other settings in the payload with it.
        Probed 2026-09-03: the vocabulary is closed -- 'Wrench' is in it, 'Gear'
        is not -- so the icon is dropped and reported, and the rest still lands.
        """
        try:
            return self.mutate("team", "update", key, self.TEAM_UPDATE,
                               {"id": team_id, "input": changes}, "teamUpdate.team",
                               detail=", ".join(sorted(changes)))
        except LinearError as exc:
            if "icon" not in changes or not exc.matches("Argument Validation Error", "icon"):
                raise
            rejected = changes.pop("icon")
            self.plan.problem(
                "team %s: Linear refused icon %r, so the team keeps the one it has. Choose an "
                "icon from Linear's own set or drop it from the spec." % (key, rejected))
            if not changes:
                return None
            return self.mutate("team", "update", key, self.TEAM_UPDATE,
                               {"id": team_id, "input": changes}, "teamUpdate.team",
                               detail="retry without icon: " + ", ".join(sorted(changes)))

    def fresh_team_states(self, spec_team, team_id):
        """States a just-created team has: read them back, or predict them in a dry run."""
        if self.apply:
            data = gql("query($id: String!) { team(id: $id) { id key autoCloseStateId "
                       "defaultIssueState { id name } states { nodes "
                       "{ id name type color position description archivedAt "
                       "issues(first: 1) { nodes { id } } } } } }", {"id": team_id})
            return data["team"]
        predicted = [dict(node) for node in DEFAULT_TEAM_STATES]
        if not spec_team.get("triageEnabled"):
            predicted = [s for s in predicted if s["type"] != "triage"]
        for state in predicted:
            state["id"] = self.placeholder("defaultState",
                                           "%s/%s" % (spec_team["key"], state["name"]))
        return {"id": team_id, "key": spec_team["key"], "states": {"nodes": predicted}}

    def create_team(self, spec_team, wanted):
        payload = dict(wanted)
        payload["key"] = spec_team["key"]
        payload = {k: v for k, v in payload.items() if v is not None}
        query = ("mutation($input: TeamCreateInput!) "
                 "{ teamCreate(input: $input) { success team { id key } } }")
        # Recorded once, outside the retry loop: a plan-limit retry is the same
        # intended operation, not another one.
        self.plan.add("create", "team", spec_team["key"], spec_team.get("name", ""),
                      query=query, variables={"input": payload})
        if not self.apply:
            return None
        for attempt in range(1, PLAN_LIMIT_RETRIES + 1):
            try:
                return self.execute(query, {"input": payload}, "teamCreate.team")
            except LinearError as exc:
                if exc.matches("icon") and "icon" in payload:
                    self.plan.problem("team %s: icon %r rejected, creating without an icon"
                                      % (spec_team["key"], payload.pop("icon")))
                    continue
                # Deliberately narrow: a plain 'rate limit' must not burn 8 x 15s here.
                limit_hit = exc.matches("free plan", "upgrade", "maximum number of teams",
                                        "team limit")
                if limit_hit and attempt < PLAN_LIMIT_RETRIES:
                    sys.stderr.write("  team limit hit (attempt %d/%d): %s -- waiting %ds\n"
                                     % (attempt, PLAN_LIMIT_RETRIES, exc, PLAN_LIMIT_WAIT))
                    time.sleep(PLAN_LIMIT_WAIT)
                    continue
                raise
        raise LinearError("teamCreate for %s kept failing on the plan limit" % spec_team["key"])

    def build_states(self, spec_team):
        key = spec_team["key"]
        team_id = self.get_id("team", key)
        live_team = self.by_team_key.get(key) or {}
        live_states = [s for s in (live_team.get("states") or {}).get("nodes", [])
                       if not s.get("archivedAt")]
        by_name = {norm(s["name"]): s for s in live_states}
        by_type = {}
        for state in live_states:
            by_type.setdefault(state["type"], []).append(state)

        matched = set()
        for spec_state in spec_team.get("states", []):
            name = spec_state["name"]
            # `position` is deliberately absent: see STATE_SERVER_OWNED. It is
            # still sent on create below, where Linear sometimes honours it.
            wanted = {"name": name, "color": spec_state.get("color"),
                      "description": spec_state.get("description")}
            live = by_name.get(norm(name))
            if live is None and spec_state["type"] == "triage":
                # `triage` is not creatable; Linear makes one when triageEnabled is on.
                candidates = [s for s in by_type.get("triage") or [] if s["id"] not in matched]
                live = candidates[0] if candidates else None
                if live is None:
                    self.plan.problem(
                        "team %s: the spec wants a triage state %r but the team has none; it "
                        "appears only after triageEnabled is on (teamCreate/teamUpdate above sets "
                        "it, but a re-run is needed to rename it)" % (key, name))
                    continue
            if live is not None:
                matched.add(live["id"])
                self.put_id("state", "%s/%s" % (key, name), live["id"])
                if live["type"] != spec_state["type"]:
                    self.plan.problem(
                        "team %s state %r is type %r but the spec wants %r; "
                        "WorkflowStateUpdateInput cannot change type, so this state has to be "
                        "recreated by hand" % (key, name, live["type"], spec_state["type"]))
                if spec_state["type"] in RESERVED_STATE_TYPES:
                    # See RESERVED_STATE_TYPES: every field of this state is
                    # refused, so there is nothing to reconcile. It is already
                    # registered under the spec's name above, which is what the
                    # issues need -- they route by id, not by label.
                    if norm(live["name"]) != norm(name):
                        self.plan.problem(
                            "team %s: the %s state is reserved by Linear and refuses every "
                            "update, so the board keeps calling it %r where the spec says %r. "
                            "Issues still land in it correctly; only the label differs."
                            % (key, spec_state["type"], live["name"], name))
                    self.plan.add("keep", "state", "%s/%s" % (key, name),
                                  "reserved %s state, not updatable" % spec_state["type"])
                    continue
                changes = self.diff_fields(live, wanted)
                if changes:
                    self.mutate("state", "update", "%s/%s" % (key, name),
                                "mutation($id: String!, $input: WorkflowStateUpdateInput!) "
                                "{ workflowStateUpdate(id: $id, input: $input) "
                                "{ success workflowState { id } } }",
                                {"id": live["id"], "input": changes},
                                "workflowStateUpdate.workflowState",
                                detail=", ".join(sorted(changes)))
                else:
                    self.plan.add("ok", "state", "%s/%s" % (key, name), "already matches spec")
                continue

            payload = {"teamId": team_id, "name": name, "type": spec_state["type"],
                       "color": spec_state.get("color")}
            if spec_state.get("position") is not None:
                payload["position"] = spec_state["position"]
            if spec_state.get("description"):
                payload["description"] = spec_state["description"]
            node = self.mutate("state", "create", "%s/%s" % (key, name),
                               "mutation($input: WorkflowStateCreateInput!) "
                               "{ workflowStateCreate(input: $input) "
                               "{ success workflowState { id } } }",
                               {"input": payload}, "workflowStateCreate.workflowState",
                               detail=spec_state["type"])
            self.put_id("state", "%s/%s" % (key, name),
                        node["id"] if node else self.placeholder("state", "%s/%s" % (key, name)))

        self.archive_unused_states(spec_team, live_team, live_states, matched)

    def archive_unused_states(self, spec_team, live_team, live_states, matched):
        key = spec_team["key"]
        doomed = []
        for state in live_states:
            if state["id"] in matched:
                continue
            if state["type"] in PROTECTED_STATE_TYPES:
                self.plan.add("keep", "state", "%s/%s" % (key, state["name"]),
                              "type %s is managed by Linear and cannot be archived"
                              % state["type"])
                continue
            if (state.get("issues") or {}).get("nodes"):
                self.plan.add("keep", "state", "%s/%s" % (key, state["name"]),
                              "not in spec but still holds issues -- left alone")
                continue
            doomed.append(state)
        if not doomed:
            return
        self.repoint_team_states(spec_team, live_team, {s["id"] for s in doomed})
        for state in doomed:
            self.mutate("state", "archive", "%s/%s" % (key, state["name"]),
                        "mutation($id: String!) { workflowStateArchive(id: $id) { success } }",
                        {"id": state["id"]}, "workflowStateArchive",
                        detail="default state not in the spec, holds no issues", tolerate=True)

    def repoint_team_states(self, spec_team, live_team, doomed_ids):
        """A state the team points at (default or auto-close) refuses to archive,
        so both pointers move to their spec states first."""
        key = spec_team["key"]
        fixes = {}
        pointers = (("defaultIssueStateId", (live_team.get("defaultIssueState") or {}).get("id"),
                     spec_team.get("defaultState")),
                    ("autoCloseStateId", live_team.get("autoCloseStateId"),
                     spec_team.get("autoCloseState")))
        for field, current, wanted_name in pointers:
            if not wanted_name:
                continue
            target = self.get_id("state", "%s/%s" % (key, wanted_name))
            if not target:
                self.plan.problem("team %s wants %s = %r but that state has no id"
                                  % (key, field, wanted_name))
                continue
            if current != target:
                fixes[field] = target
        if not fixes:
            return
        self.mutate("team", "update", key,
                    "mutation($id: String!, $input: TeamUpdateInput!) "
                    "{ teamUpdate(id: $id, input: $input) { success team { id } } }",
                    {"id": self.get_id("team", key), "input": fixes}, "teamUpdate.team",
                    detail="%s -- must happen before the old states are archived"
                           % ", ".join(sorted(fixes)))

    # ---------- step d1: labels ----------

    def build_labels(self):
        specs = self.spec.get("labels", [])
        for spec_label in [l for l in specs if l.get("isGroup")]:
            self.sync_issue_label(spec_label)
        for spec_label in [l for l in specs if not l.get("isGroup")]:
            self.sync_issue_label(spec_label)

        wanted_project_labels = []
        for project in self.spec.get("projects", []):
            for name in project.get("labels") or []:
                if name not in wanted_project_labels:
                    wanted_project_labels.append(name)
        for name in wanted_project_labels:
            self.sync_project_label(name)
        self.checkpoint()

    def sync_issue_label(self, spec_label):
        name = spec_label["name"]
        key = self.spec_label_key(spec_label)
        is_group = bool(spec_label.get("isGroup"))
        parent_id = None
        if spec_label.get("group"):
            parent_id = self.get_id("label", spec_label["group"])
            if parent_id is None:
                self.plan.problem("label %r references unknown group %r"
                                  % (key, spec_label["group"]))
        live = self.label_by_key.get(norm(key))
        if live:
            self.put_id("label", key, live["id"])
            wanted = {"name": name, "color": spec_label.get("color"),
                      "description": spec_label.get("description"), "isGroup": is_group}
            changes = self.diff_fields(live, wanted)
            live_parent = (live.get("parent") or {}).get("id")
            if parent_id and not self.is_placeholder(parent_id) and live_parent != parent_id:
                changes["parentId"] = parent_id
            if changes:
                self.mutate("label", "update", key,
                            "mutation($id: String!, $input: IssueLabelUpdateInput!) "
                            "{ issueLabelUpdate(id: $id, input: $input) "
                            "{ success issueLabel { id } } }",
                            {"id": live["id"], "input": changes}, "issueLabelUpdate.issueLabel",
                            detail=", ".join(sorted(changes)))
            else:
                self.plan.add("ok", "label", key, "already matches spec")
            return

        payload = {"name": name, "color": spec_label.get("color"),
                   "description": spec_label.get("description")}
        if is_group:
            payload["isGroup"] = True
        if parent_id:
            payload["parentId"] = parent_id
        if spec_label.get("teamKey"):
            payload["teamId"] = self.get_id("team", spec_label["teamKey"])
        payload = {k: v for k, v in payload.items() if v is not None}
        try:
            node = self.mutate("label", "create", key,
                               "mutation($input: IssueLabelCreateInput!) "
                               "{ issueLabelCreate(input: $input) { success issueLabel { id } } }",
                               {"input": payload}, "issueLabelCreate.issueLabel",
                               detail=("group" if is_group
                                       else (spec_label.get("group") or "flat")))
        except LinearError as exc:
            if not exc.matches("duplicate label name"):
                raise
            # Linear label names are unique across the whole workspace, groups
            # included, so two groups cannot both hold a child called `intern`.
            # Which of the two keeps the name is a design decision, not one this
            # tool may make: register no id, so every reference to this label is
            # reported by resolve_label_id instead of silently landing on the
            # namesake in the other group.
            self.plan.problem(
                "label %r refused as a duplicate: Linear label names are unique workspace-wide "
                "and %r already exists under another group. Every issue and template that "
                "references %r loses that label until one of the two is renamed in the spec."
                % (key, name, key))
            return
        self.put_id("label", key, node["id"] if node else self.placeholder("label", key))

    def sync_project_label(self, name):
        live = self.project_label_by_name.get(norm(name))
        if live:
            self.put_id("projectLabel", name, live["id"])
            self.plan.add("ok", "projectLabel", name, "already exists")
            return
        node = self.mutate("projectLabel", "create", name,
                           "mutation($input: ProjectLabelCreateInput!) "
                           "{ projectLabelCreate(input: $input) { success projectLabel { id } } }",
                           {"input": {"name": name}}, "projectLabelCreate.projectLabel")
        self.put_id("projectLabel", name,
                    node["id"] if node else self.placeholder("projectLabel", name))

    # ---------- step d2: initiatives ----------

    def build_initiatives(self):
        for spec_initiative in self.spec.get("initiatives", []):
            name = spec_initiative["name"]
            wanted = {"name": name,
                      "description": spec_initiative.get("description"),
                      "content": spec_initiative.get("content"),
                      "status": spec_initiative.get("status")}
            live = self.initiative_by_name.get(norm(name))
            if live:
                self.put_id("initiative", name, live["id"])
                changes = self.diff_fields(live, wanted)
                if changes:
                    self.mutate("initiative", "update", name,
                                "mutation($id: String!, $input: InitiativeUpdateInput!) "
                                "{ initiativeUpdate(id: $id, input: $input) "
                                "{ success initiative { id } } }",
                                {"id": live["id"], "input": changes},
                                "initiativeUpdate.initiative", detail=", ".join(sorted(changes)))
                else:
                    self.plan.add("ok", "initiative", name, "already matches spec")
                continue
            payload = {k: v for k, v in wanted.items() if v is not None}
            node = self.mutate("initiative", "create", name,
                               "mutation($input: InitiativeCreateInput!) "
                               "{ initiativeCreate(input: $input) { success initiative { id } } }",
                               {"input": payload}, "initiativeCreate.initiative")
            self.put_id("initiative", name,
                        node["id"] if node else self.placeholder("initiative", name))
        self.checkpoint()

    # ---------- step d3: projects, milestones, initiative links ----------

    def build_projects(self):
        viewer_id = self.snapshot["viewer"]["id"]
        for index, spec_project in enumerate(self.spec.get("projects", [])):
            name = spec_project["name"]
            team_ids = [self.get_id("team", k) for k in spec_project.get("teamKeys", [])]
            team_ids = [t for t in team_ids if t]
            label_ids = [self.get_id("projectLabel", n)
                         for n in spec_project.get("labels") or []]
            label_ids = [l for l in label_ids if l]
            lead_id = viewer_id if spec_project.get("leadRole") == "mens" else None

            live = self.project_by_name.get(norm(name))
            if live:
                project_id = live["id"]
                self.put_id("project", name, project_id)
                wanted = {"name": name,
                          "description": spec_project.get("description"),
                          "content": spec_project.get("content")}
                changes = self.diff_fields(live, wanted)
                live_labels = {n["id"] for n in (live.get("labels") or {}).get("nodes", [])}
                real_labels = [l for l in label_ids if not self.is_placeholder(l)]
                if real_labels and set(real_labels) - live_labels:
                    changes["labelIds"] = sorted(live_labels | set(real_labels))
                if lead_id and (live.get("lead") or {}).get("id") != lead_id:
                    changes["leadId"] = lead_id
                if changes:
                    self.mutate("project", "update", name,
                                "mutation($id: String!, $input: ProjectUpdateInput!) "
                                "{ projectUpdate(id: $id, input: $input) "
                                "{ success project { id } } }",
                                {"id": project_id, "input": changes}, "projectUpdate.project",
                                detail=", ".join(sorted(changes)))
                else:
                    self.plan.add("ok", "project", name, "already matches spec")
            else:
                payload = {"name": name, "teamIds": team_ids, "sortOrder": float(index)}
                for field in ("description", "content"):
                    if spec_project.get(field):
                        payload[field] = spec_project[field]
                if label_ids:
                    payload["labelIds"] = label_ids
                if lead_id:
                    payload["leadId"] = lead_id
                node = self.mutate("project", "create", name,
                                   "mutation($input: ProjectCreateInput!) "
                                   "{ projectCreate(input: $input) { success project { id } } }",
                                   {"input": payload}, "projectCreate.project",
                                   detail="teams " + "+".join(spec_project.get("teamKeys", [])))
                project_id = node["id"] if node else self.placeholder("project", name)
                self.put_id("project", name, project_id)
                live = None

            self.build_milestones(spec_project, project_id, live)
            self.link_initiative(spec_project, project_id, live)
            self.checkpoint()

    def build_milestones(self, spec_project, project_id, live):
        live_by_name = {}
        if live:
            for milestone in (live.get("projectMilestones") or {}).get("nodes", []):
                live_by_name[norm(milestone["name"])] = milestone
        for index, spec_milestone in enumerate(spec_project.get("milestones") or []):
            name = spec_milestone["name"]
            label = "%s / %s" % (spec_project["name"], name)
            wanted = {"name": name, "description": spec_milestone.get("description"),
                      "targetDate": spec_milestone.get("targetDate"),
                      "sortOrder": float(index)}
            existing = live_by_name.get(norm(name))
            if existing:
                self.put_id("milestone", label, existing["id"])
                changes = self.diff_fields(
                    existing, {k: v for k, v in wanted.items() if k != "sortOrder"})
                if changes:
                    self.mutate("milestone", "update", label,
                                "mutation($id: String!, $input: ProjectMilestoneUpdateInput!) "
                                "{ projectMilestoneUpdate(id: $id, input: $input) "
                                "{ success projectMilestone { id } } }",
                                {"id": existing["id"], "input": changes},
                                "projectMilestoneUpdate.projectMilestone",
                                detail=", ".join(sorted(changes)))
                continue
            payload = {k: v for k, v in wanted.items() if v is not None}
            payload["projectId"] = project_id
            node = self.mutate("milestone", "create", label,
                               "mutation($input: ProjectMilestoneCreateInput!) "
                               "{ projectMilestoneCreate(input: $input) "
                               "{ success projectMilestone { id } } }",
                               {"input": payload}, "projectMilestoneCreate.projectMilestone")
            self.put_id("milestone", label,
                        node["id"] if node else self.placeholder("milestone", label))

    def link_initiative(self, spec_project, project_id, live):
        initiative_name = spec_project.get("initiative")
        if not initiative_name:
            return
        initiative_id = self.get_id("initiative", initiative_name)
        if not initiative_id:
            self.plan.problem("project %r references unknown initiative %r"
                              % (spec_project["name"], initiative_name))
            return
        if live:
            linked = {norm(n["name"]) for n in (live.get("initiatives") or {}).get("nodes", [])}
            if norm(initiative_name) in linked:
                return
        self.mutate("initiativeLink", "create",
                    "%s -> %s" % (initiative_name, spec_project["name"]),
                    "mutation($input: InitiativeToProjectCreateInput!) "
                    "{ initiativeToProjectCreate(input: $input) "
                    "{ success initiativeToProject { id } } }",
                    {"input": {"initiativeId": initiative_id, "projectId": project_id}},
                    "initiativeToProjectCreate.initiativeToProject")

    # ---------- step d4: templates ----------

    def template_data(self, spec_template, with_labels=True):
        """`with_labels=False` is for the probe, which runs before the labels exist."""
        defaults = spec_template.get("defaults") or {}
        body = spec_template.get("body") or ""
        kind = spec_template["type"]
        if kind == "issue":
            data = {"description": body}
            # No title unless the spec asks for one: otherwise every issue made
            # from the Bug template starts out titled "Bug".
            if defaults.get("title"):
                data["title"] = defaults["title"]
            label_ids = [self.resolve_label_id(n, "template %r" % spec_template["name"])
                         for n in defaults.get("labels") or []] if with_labels else []
            label_ids = [l for l in label_ids if l]
            if label_ids:
                data["labelIds"] = label_ids
            if defaults.get("priority") is not None:
                data["priority"] = defaults["priority"]
            if defaults.get("estimate") is not None:
                data["estimate"] = defaults["estimate"]
            return data
        if kind == "project":
            return {"name": spec_template["name"],
                    "description": spec_template.get("description") or "",
                    "content": body}
        return {"title": spec_template["name"], "content": body}

    def build_templates(self):
        for spec_template in self.spec.get("templates", []):
            name = spec_template["name"]
            kind = spec_template["type"]
            team_key = spec_template.get("teamKey")
            if team_key in (None, "", "None", "null"):
                team_key = None
            label = "%s [%s%s]" % (name, kind, "/" + team_key if team_key else "/workspace")
            data = self.template_data(spec_template)
            team_id = self.get_id("team", team_key) if team_key else None
            if team_key and not team_id:
                self.plan.problem("template %r references unknown team %r" % (name, team_key))
                continue

            live = self.template_by_key.get((kind, norm(name), team_key))
            if live:
                self.put_id("template", label, live["id"])
                changes = {}
                if (live.get("description") or "") != (spec_template.get("description") or ""):
                    changes["description"] = spec_template.get("description") or ""
                # See TEMPLATE_BODY_KEYS: templateData arrives as a JSON string,
                # and the markdown body is rendered into a server blob under a
                # different key, so only the keys Linear echoes back verbatim can
                # be compared. The body rides along on any real change.
                live_data = parse_template_data(live.get("templateData"))
                drift = sorted(k for k, v in data.items()
                               if k not in TEMPLATE_BODY_KEYS and live_data.get(k) != v)
                if drift:
                    merged = {k: v for k, v in live_data.items()
                              if k not in TEMPLATE_SERVER_BLOBS}
                    merged.update(data)
                    changes["templateData"] = merged
                    self.plan.note("template %r: templateData drift on %s"
                                   % (name, ", ".join(drift)))
                elif any(k in data for k in TEMPLATE_BODY_KEYS):
                    self.plan.note("template bodies are not reconciled on re-runs: Linear stores "
                                   "them as rendered blobs, so an edited body in the spec only "
                                   "lands if another templateData key changes with it")
                if changes:
                    self.mutate("template", "update", label,
                                "mutation($id: String!, $input: TemplateUpdateInput!) "
                                "{ templateUpdate(id: $id, input: $input) "
                                "{ success template { id } } }",
                                {"id": live["id"], "input": changes}, "templateUpdate.template",
                                detail=", ".join(sorted(changes)), tolerate=True)
                else:
                    self.plan.add("ok", "template", label, "already matches spec")
                continue

            payload = {"name": name, "type": kind, "templateData": data,
                       "description": spec_template.get("description")}
            payload = {k: v for k, v in payload.items() if v is not None}
            if team_id:
                payload["teamId"] = team_id
            node = self.mutate("template", "create", label,
                               "mutation($input: TemplateCreateInput!) "
                               "{ templateCreate(input: $input) { success template { id } } }",
                               {"input": payload}, "templateCreate.template",
                               detail="templateData keys: " + ",".join(sorted(data)),
                               tolerate=True)
            self.put_id("template", label,
                        node["id"] if node else self.placeholder("template", label))
        self.checkpoint()

    # ---------- step d5: documents ----------

    def build_documents(self):
        for spec_document in self.spec.get("documents", []):
            title = spec_document["title"]
            scope = spec_document.get("scope") or ""
            kind, _, target = scope.partition(":")
            parent_field, parent_id = None, None
            if kind == "project":
                parent_field, parent_id = "projectId", self.get_id("project", target)
            elif kind == "initiative":
                parent_field, parent_id = "initiativeId", self.get_id("initiative", target)
            if not parent_id:
                self.plan.problem("document %r has an unresolvable scope %r" % (title, scope))
                continue

            live = self.document_by_title.get(norm(title))
            if live:
                self.put_id("document", title, live["id"])
                self.plan.add("ok", "document", title, "already exists (content left alone)")
                continue
            payload = {"title": title, "content": spec_document.get("content") or "",
                       parent_field: parent_id}
            node = self.mutate("document", "create", title,
                               "mutation($input: DocumentCreateInput!) "
                               "{ documentCreate(input: $input) { success document { id } } }",
                               {"input": payload}, "documentCreate.document", detail=scope,
                               tolerate=True)
            self.put_id("document", title,
                        node["id"] if node else self.placeholder("document", title))
        self.checkpoint()

    # ---------- step d6: issues ----------

    def resolve_delegate(self, name):
        if not name:
            return None
        user = self.app_user_by_name.get(norm(name))
        return user["id"] if user else None

    def state_type(self, team_key, state_name):
        for spec_team in self.spec.get("teams", []):
            if spec_team["key"] != team_key:
                continue
            for state in spec_team.get("states", []):
                if norm(state["name"]) == norm(state_name):
                    return state["type"]
        return None

    def issue_payload(self, spec_issue):
        team_key = spec_issue["teamKey"]
        title = spec_issue["title"]
        payload = {"teamId": self.get_id("team", team_key), "title": title}
        if spec_issue.get("description"):
            payload["description"] = spec_issue["description"]
        state_id = self.get_id("state", "%s/%s" % (team_key, spec_issue["state"]))
        triage = self.state_type(team_key, spec_issue["state"]) == "triage"
        if state_id and triage and self.probe_results.get("triageStateAccepted") is False:
            self.plan.problem("issue %r drops its stateId: the probe showed issueCreate does not "
                              "keep an issue in the triage state %s/%s"
                              % (title, team_key, spec_issue["state"]))
        elif state_id:
            payload["stateId"] = state_id
            if triage and "triageStateAccepted" not in self.probe_results and not self.probe:
                self.plan.problem(
                    "issues are seeded straight into the triage state %s/%s; run --probe as well, "
                    "so that issueCreate is known to accept that stateId"
                    % (team_key, spec_issue["state"]))
        else:
            self.plan.problem("issue %r wants state %r on team %s, which the spec does not define"
                              % (title, spec_issue["state"], team_key))
        if spec_issue.get("project"):
            project_id = self.get_id("project", spec_issue["project"])
            if project_id:
                payload["projectId"] = project_id
            else:
                self.plan.problem("issue %r references unknown project %r"
                                  % (title, spec_issue["project"]))
        if spec_issue.get("milestone") and spec_issue.get("project"):
            key = "%s / %s" % (spec_issue["project"], spec_issue["milestone"])
            milestone_id = self.get_id("milestone", key)
            if milestone_id:
                payload["projectMilestoneId"] = milestone_id
            else:
                self.plan.problem("issue %r references unknown milestone %r"
                                  % (title, spec_issue["milestone"]))
        label_ids = [self.resolve_label_id(n, "issue %r" % title)
                     for n in spec_issue.get("labels") or []]
        label_ids = [l for l in label_ids if l]
        if label_ids:
            payload["labelIds"] = label_ids
        if spec_issue.get("priority") is not None:
            payload["priority"] = spec_issue["priority"]
        if spec_issue.get("estimate") is not None:
            payload["estimate"] = spec_issue["estimate"]
        delegate_id = self.resolve_delegate(spec_issue.get("delegate"))
        if delegate_id:
            payload["delegateId"] = delegate_id
        if spec_issue.get("sortHint") is not None:
            payload["sortOrder"] = float(spec_issue["sortHint"])
        return payload

    def build_issues(self):
        spec_issues = sorted(self.spec.get("issues", []),
                             key=lambda i: (i.get("sortHint") is None, i.get("sortHint") or 0))
        for spec_issue in spec_issues:
            team_key = spec_issue["teamKey"]
            title = spec_issue["title"]
            key = "%s/%s" % (team_key, title)
            payload = self.issue_payload(spec_issue)
            live = self.issue_by_key.get((team_key, norm(title)))
            if live:
                self.put_id("issue", key, live["id"])
                wanted = dict(payload)
                wanted.pop("teamId", None)
                wanted.pop("sortOrder", None)
                live_flat = {
                    "title": live.get("title"), "description": live.get("description"),
                    "priority": live.get("priority"), "estimate": live.get("estimate"),
                    "stateId": (live.get("state") or {}).get("id"),
                    "projectId": (live.get("project") or {}).get("id"),
                    "projectMilestoneId": (live.get("projectMilestone") or {}).get("id"),
                    "delegateId": (live.get("delegate") or {}).get("id"),
                    "labelIds": sorted(n["id"] for n in
                                       (live.get("labels") or {}).get("nodes", [])),
                }
                if "labelIds" in wanted:
                    wanted["labelIds"] = sorted(wanted["labelIds"])
                changes = self.diff_fields(live_flat, wanted)
                if changes:
                    self.mutate("issue", "update", key,
                                "mutation($id: String!, $input: IssueUpdateInput!) "
                                "{ issueUpdate(id: $id, input: $input) { success issue { id } } }",
                                {"id": live["id"], "input": changes}, "issueUpdate.issue",
                                detail=", ".join(sorted(changes)))
                else:
                    self.plan.add("ok", "issue", key, "already matches spec")
                continue
            node = self.mutate("issue", "create", key,
                               "mutation($input: IssueCreateInput!) "
                               "{ issueCreate(input: $input) { success issue { id identifier } } }",
                               {"input": payload}, "issueCreate.issue",
                               detail="%s | %s" % (spec_issue.get("state"),
                                                   spec_issue.get("project") or "no project"))
            self.put_id("issue", key, node["id"] if node else self.placeholder("issue", key))
        self.checkpoint()
        self.link_sub_issues(spec_issues)

    def link_sub_issues(self, spec_issues):
        for spec_issue in spec_issues:
            parent_title = spec_issue.get("parent")
            if not parent_title:
                continue
            team_key = spec_issue["teamKey"]
            child_id = self.get_id("issue", "%s/%s" % (team_key, spec_issue["title"]))
            parent_id = self.get_id("issue", "%s/%s" % (team_key, parent_title))
            if not child_id or not parent_id:
                self.plan.problem("cannot link %r to parent %r: %s has no id"
                                  % (spec_issue["title"], parent_title,
                                     "the child" if not child_id else "the parent"))
                continue
            live = self.issue_by_key.get((team_key, norm(spec_issue["title"])))
            if live and (live.get("parent") or {}).get("id") == parent_id:
                continue
            self.mutate("issue", "update", "%s/%s" % (team_key, spec_issue["title"]),
                        "mutation($id: String!, $input: IssueUpdateInput!) "
                        "{ issueUpdate(id: $id, input: $input) { success issue { id } } }",
                        {"id": child_id, "input": {"parentId": parent_id}}, "issueUpdate.issue",
                        detail="parent -> %s" % parent_title)

    # ---------- orchestration ----------

    def run(self, backup_path, backup_required, org_arg=None, probe_only=False):
        self.load_snapshot()
        self.guard_workspace(org_arg)
        self.preflight()
        if self.apply or backup_required:
            self.check_backup(backup_path)
        self.check_issue_budget()

        prober = Probe(self) if self.probe else None
        if prober:
            prober.before_teardown(LEGACY_TEAM_ID)
        if probe_only:
            # Stop here on purpose. The two questions that gate the teardown --
            # does permanentlyDelete really remove an issue, and what does Linear
            # store in templateData -- are now settled against the legacy team,
            # while everything is still intact. The triage-state question cannot
            # be asked at this point: that state does not exist until teamCreate
            # makes KR, so plain --probe answers it mid-build instead.
            return
        if self.teardown:
            Teardown(self).run()
            if self.apply:
                self.load_snapshot()
        self.build_teams()
        self.build_labels()
        if prober:
            prober.after_labels(self.spec_team_keys[0])
        self.build_initiatives()
        self.build_projects()
        self.build_templates()
        self.build_documents()
        self.build_issues()

    def write_idmap(self, path):
        grouped = {}
        for key, value in sorted(self.ids.items()):
            kind, _, name = key.partition(":")
            grouped.setdefault(kind, {})[name] = value
        payload = {"_meta": {"writtenAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                             "spec": SPEC_PATH,
                             "counts": {k: len(v) for k, v in sorted(grouped.items())}},
                   **grouped}
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
        return payload["_meta"]["counts"]


INPUT_TYPE_RE = "$input: "


def main():
    parser = argparse.ArgumentParser(description="Apply linear-spec.json to Linear")
    parser.add_argument("--spec", default=SPEC_PATH)
    parser.add_argument("--backup", default=None,
                        help="default: the newest linear/backup-*.json")
    parser.add_argument("--idmap", default=IDMAP_PATH)
    parser.add_argument("--org", default=linear_guard.EXPECTED_ORG["urlKey"],
                        help="urlKey the API key has to resolve to")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the plan without mutating (the default)")
    parser.add_argument("--apply", action="store_true", help="actually mutate the workspace")
    parser.add_argument("--teardown", action="store_true",
                        help="empty the old workspace and rename its team into the spec's")
    parser.add_argument("--probe", action="store_true",
                        help="prove the unknown API shapes with throwaway records first")
    parser.add_argument("--probe-only", action="store_true",
                        help="run the pre-teardown probes and stop, changing nothing else")
    parser.add_argument("--backup-required", action="store_true",
                        help="hard-fail unless a complete, covering backup exists")
    parser.add_argument("--allow-tight-budget", action="store_true",
                        help="run even when the Free-plan issue budget looks too small")
    parser.add_argument("--verify", action="store_true",
                        help="re-read the workspace and diff it against the spec")
    parser.add_argument("--quiet", action="store_true", help="summary counts only")
    parser.add_argument("--validate", action="store_true",
                        help="introspect every planned input type and check the payload keys")
    args = parser.parse_args()

    with open(args.spec, "r", encoding="utf-8") as fh:
        spec = json.load(fh)
    spec_warnings = linear_check.validate_spec(spec)

    if args.verify:
        return linear_check.verify(
            spec, Builder(spec, apply_changes=False, teardown=False,
                          verbose=False), args.org)

    if args.apply and args.dry_run:
        parser.error("--apply and --dry-run are mutually exclusive")

    backup_path = args.backup or linear_guard.newest_backup(BACKUP_DIR)
    # --probe-only never tears anything down, so it must not be able to inherit
    # --teardown from the command line and delete on the way to the probes.
    teardown = args.teardown and not args.probe_only
    builder = Builder(spec, apply_changes=args.apply, teardown=teardown,
                      verbose=not args.quiet, probe=args.probe or args.probe_only,
                      idmap_path=args.idmap, allow_tight_budget=args.allow_tight_budget)
    for warning in spec_warnings:
        builder.plan.problem("spec: %s" % warning)
    try:
        builder.run(backup_path, args.backup_required, args.org, probe_only=args.probe_only)
    except LinearError as exc:
        sys.stderr.write("\nABORTED on a Linear error: %s\n" % exc)
        if exc.variables:
            sys.stderr.write(json.dumps(exc.variables, ensure_ascii=False)[:1500] + "\n")
        print("\nPLAN UP TO THE FAILURE")
        print(builder.plan.render(verbose=not args.quiet))
        if args.apply:
            print("id map written to %s: %s" % (args.idmap, builder.write_idmap(args.idmap)))
        return 1

    header = "APPLIED" if args.apply else "DRY RUN -- no mutations were sent"
    print("\n%s" % header)
    print(builder.plan.render(verbose=not args.quiet))
    print("\nAPI: %d requests, %d retries, %s requests left this hour"
          % (stats()["requests"], stats()["retries"],
             last_headers().get("x-ratelimit-requests-remaining", "?")))

    if args.validate:
        checked, issues, types = linear_check.validate_inputs(builder.plan)
        print("\nINPUT VALIDATION: %d payloads checked against %d live input types (%s)"
              % (checked, len(types), ", ".join(types)))
        for issue in issues:
            builder.plan.problem(issue)
        if not issues:
            print("  every payload key exists on its input type")

    if builder.probe_results:
        print("\nPROBE RESULTS")
        for key, value in sorted(builder.probe_results.items()):
            print("  %-26s %s" % (key, value))

    if builder.plan.notes:
        print("\nNOTES (%d)" % len(builder.plan.notes))
        for note in builder.plan.notes:
            print("  - %s" % note)

    if builder.plan.problems:
        print("\nPROBLEMS (%d)" % len(builder.plan.problems))
        for problem in builder.plan.problems:
            print("  - %s" % problem)

    if args.apply:
        counts = builder.write_idmap(args.idmap)
        print("\nid map written to %s: %s" % (args.idmap, counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
