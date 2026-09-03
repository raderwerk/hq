#!/usr/bin/env python3
"""Apply design/linear-spec.json to the live Linear workspace, idempotently.

    python3 build_linear.py --dry-run                 # plan only, no mutation (default)
    python3 build_linear.py --apply --backup-required # really build
    python3 build_linear.py --apply --teardown --backup-required
    python3 build_linear.py --verify                  # compare live workspace to the spec

Order: backup check -> teardown -> teams+states+settings -> labels -> initiatives ->
projects (+milestones, +initiative link) -> templates -> documents -> issues.

Nothing mutates unless --apply is given. Users are never touched.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from linear_api import LinearError, gql, page, stats  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_PATH = os.path.join(ROOT, "design", "linear-spec.json")
BACKUP_PATH = os.path.join(ROOT, "linear", "backup-2026-09-02.json")
IDMAP_PATH = os.path.join(ROOT, "linear", "idmap.json")

TEARDOWN_INITIATIVE = "Fightclub AI"
PLAN_LIMIT_RETRIES = 8
PLAN_LIMIT_WAIT = 15
TEAM_DELETE_POLL_SECONDS = 120
ISSUE_DELETE_BATCH = 20

TEAM_SETTINGS = ("description", "icon", "color", "cyclesEnabled", "triageEnabled",
                 "issueEstimationType")

# What teamCreate seeds a new team with (verified against this workspace's existing teams).
# `Triage` only appears when triageEnabled is on; `triage` and `duplicate` types cannot be
# created through workflowStateCreate, so the spec's triage state has to reuse this one.
DEFAULT_TEAM_STATES = [
    {"name": "Triage", "type": "triage", "position": 0},
    {"name": "Backlog", "type": "backlog", "position": 0},
    {"name": "Todo", "type": "unstarted", "position": 1},
    {"name": "In Progress", "type": "started", "position": 2},
    {"name": "Done", "type": "completed", "position": 3},
    {"name": "Canceled", "type": "canceled", "position": 4},
    {"name": "Duplicate", "type": "duplicate", "position": 5},
]


def norm(value):
    return " ".join((value or "").split()).strip().lower()


class Plan(object):
    """Records every intended change so --dry-run can print it and --apply can log it."""

    def __init__(self):
        self.entries = []
        self.problems = []

    def add(self, op, kind, name, detail="", query=None, variables=None, weight=1):
        self.entries.append({"op": op, "kind": kind, "name": name, "detail": detail,
                             "query": query, "variables": variables, "weight": weight})

    def problem(self, text):
        if text not in self.problems:
            self.problems.append(text)

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
                lines.append("  %-7s %-14s %s%s" % (e["op"], e["kind"], e["name"], detail))
        lines.append("")
        lines.append("  %-14s %-7s %s" % ("KIND", "OP", "COUNT"))
        for (kind, op), n in sorted(self.counts().items()):
            lines.append("  %-14s %-7s %d" % (kind, op, n))
        lines.append("  %-14s %-7s %d"
                     % ("TOTAL", "", sum(e.get("weight", 1) for e in self.entries)))
        return "\n".join(lines)


class Builder(object):
    def __init__(self, spec, apply_changes, teardown, verbose=True):
        self.spec = spec
        self.apply = apply_changes
        self.teardown = teardown
        self.verbose = verbose
        self.plan = Plan()
        self.ids = {}          # "kind:key" -> linear id (or a <dry:...> placeholder)
        self.snapshot = {}
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

    # ---------- mutation plumbing ----------

    def mutate(self, kind, op, name, query, variables, result_path, detail=""):
        """Record the action; execute it only when --apply is on. Returns the payload."""
        self.plan.add(op, kind, name, detail, query=query, variables=variables)
        if not self.apply:
            return None
        data = gql(query, variables)
        node = data
        for part in result_path.split("."):
            node = (node or {}).get(part)
        if self.verbose:
            sys.stderr.write("  %s %s %s\n" % (op, kind, name))
            sys.stderr.flush()
        return node

    @staticmethod
    def diff_fields(live, wanted):
        """Fields in `wanted` whose live value differs (None in wanted = leave alone)."""
        out = {}
        for key, value in wanted.items():
            if value is None:
                continue
            current = live.get(key)
            if isinstance(value, str) and isinstance(current, str):
                if value.strip() != current.strip():
                    out[key] = value
            elif current != value:
                out[key] = value
        return out

    # ---------- reading the live workspace ----------

    def load_snapshot(self):
        sys.stderr.write("Reading live workspace ...\n")
        snap = {}
        snap["viewer"] = gql("query { viewer { id name email } }")["viewer"]
        snap["users"] = page("users", "id name displayName email app active", False, 50)
        snap["teams"] = page(
            "teams",
            "id key name description icon color cyclesEnabled triageEnabled "
            "issueEstimationType archivedAt "
            "states { nodes { id name type color position description archivedAt "
            "issues(first: 1) { nodes { id } } } }",
            False, 10)
        snap["archivedTeams"] = page("teams", "id key name archivedAt", True, 25)
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
        snap["issues"] = page(
            "issues",
            "id identifier title description priority estimate sortOrder "
            "team { id key } state { id name } project { id name } "
            "projectMilestone { id name } delegate { id name } parent { id title } "
            "labels { nodes { id name } }",
            False, 25)
        self.snapshot = snap

        self.by_team_key = {t["key"]: t for t in snap["teams"]}
        self.label_by_name = {norm(l["name"]): l for l in snap["issueLabels"]}
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
        self.app_user_by_name = {
            norm(u["name"]): u for u in snap["users"] if u.get("app")
        }
        sys.stderr.write(
            "  teams=%d issues=%d projects=%d initiatives=%d labels=%d docs=%d templates=%d\n"
            % (len(snap["teams"]), len(snap["issues"]), len(snap["projects"]),
               len(snap["initiatives"]), len(snap["issueLabels"]), len(snap["documents"]),
               len(snap["templates"])))

    # ---------- step a: backup gate ----------

    def check_backup(self, backup_path):
        live_issues = len(self.snapshot["issues"])
        if not os.path.exists(backup_path):
            raise SystemExit("REFUSING TO RUN: backup file %s does not exist" % backup_path)
        try:
            with open(backup_path, "r", encoding="utf-8") as fh:
                backup = json.load(fh)
        except ValueError as exc:
            raise SystemExit("REFUSING TO RUN: backup %s is not valid JSON (%s)"
                             % (backup_path, exc))
        backed_up = len(backup.get("issues") or [])
        if backed_up < live_issues:
            raise SystemExit(
                "REFUSING TO RUN: backup holds %d issues but the workspace has %d -- "
                "re-run backup_linear.py" % (backed_up, live_issues))
        sys.stderr.write("Backup OK: %d issues archived vs %d live.\n" % (backed_up, live_issues))

    # ---------- step b: teardown ----------

    def run_teardown(self):
        stale = [t for t in self.snapshot["archivedTeams"] if t.get("archivedAt")]
        if stale:
            self.plan.problem(
                "archived team(s) %s still exist; teardown leaves archived teams alone, but they "
                "may still count against the free-plan 2-team limit"
                % ", ".join("%s (%s)" % (t["key"], t["name"]) for t in stale))
        victims = [t for t in self.snapshot["teams"] if t["key"] not in self.spec_team_keys]
        if not victims:
            self.plan.add("skip", "teardown", "no obsolete teams found")
            return
        victim_ids = {t["id"] for t in victims}
        victim_keys = sorted(t["key"] for t in victims)

        issues = [i for i in self.snapshot["issues"]
                  if (i.get("team") or {}).get("id") in victim_ids]
        self.delete_issues(issues)

        projects = [p for p in self.snapshot["projects"]
                    if any(t["id"] in victim_ids for t in (p.get("teams") or {}).get("nodes", []))]
        for project in projects:
            self.mutate("project", "delete", project["name"],
                        "mutation($id: String!) { projectDelete(id: $id) { success } }",
                        {"id": project["id"]}, "projectDelete")

        spec_initiative_names = {norm(i["name"]) for i in self.spec.get("initiatives", [])}
        for initiative in self.snapshot["initiatives"]:
            if norm(initiative["name"]) in spec_initiative_names:
                continue
            named = norm(initiative["name"]) == norm(TEARDOWN_INITIATIVE)
            self.delete_initiative(
                initiative,
                detail=("the initiative named in the teardown brief" if named
                        else "not in the spec"))

        for team in victims:
            self.mutate("team", "delete", "%s (%s)" % (team["key"], team["name"]),
                        "mutation($id: String!) { teamDelete(id: $id) { success entityId } }",
                        {"id": team["id"]}, "teamDelete",
                        detail="archives the team and schedules cascading deletion")
        if self.apply:
            self.poll_team_gone(victim_keys)

    def delete_issues(self, issues):
        if not issues:
            return
        self.plan.add("delete", "issue", "%d issues of obsolete teams" % len(issues),
                      "batched %d per request via aliased issueDelete" % ISSUE_DELETE_BATCH,
                      weight=len(issues))
        if not self.apply:
            return
        done = 0
        for start in range(0, len(issues), ISSUE_DELETE_BATCH):
            chunk = issues[start:start + ISSUE_DELETE_BATCH]
            decls = ", ".join("$id%d: String!" % n for n in range(len(chunk)))
            body = " ".join(
                "d%d: issueDelete(id: $id%d) { success }" % (n, n) for n in range(len(chunk)))
            variables = {"id%d" % n: issue["id"] for n, issue in enumerate(chunk)}
            gql("mutation(%s) { %s }" % (decls, body), variables)
            done += len(chunk)
            sys.stderr.write("  deleted %d/%d issues\n" % (done, len(issues)))
            sys.stderr.flush()

    def delete_initiative(self, initiative, detail=""):
        try:
            self.mutate("initiative", "delete", initiative["name"],
                        "mutation($id: String!) { initiativeDelete(id: $id) { success } }",
                        {"id": initiative["id"]}, "initiativeDelete", detail=detail)
        except LinearError as exc:
            self.plan.problem("initiativeDelete failed for %r (%s); archiving instead"
                              % (initiative["name"], exc))
            self.mutate("initiative", "archive", initiative["name"],
                        "mutation($id: String!) { initiativeArchive(id: $id) { success } }",
                        {"id": initiative["id"]}, "initiativeArchive")

    def poll_team_gone(self, keys):
        deadline = time.time() + TEAM_DELETE_POLL_SECONDS
        query = ("query { active: teams(first: 100) { nodes { key } } "
                 "all: teams(first: 100, includeArchived: true) { nodes { key archivedAt } } }")
        while True:
            data = gql(query)
            active = {t["key"] for t in data["active"]["nodes"]}
            archived = {t["key"] for t in data["all"]["nodes"] if t.get("archivedAt")}
            still = sorted(k for k in keys if k in active)
            if not still:
                sys.stderr.write(
                    "  teamDelete confirmed: %s gone from active teams (archived listing still "
                    "shows: %s)\n" % (", ".join(keys), ", ".join(sorted(archived & set(keys))) or "none"))
                return True
            if time.time() >= deadline:
                self.plan.problem(
                    "teamDelete: %s still listed as active after %ds; Linear deletes team data "
                    "asynchronously, so the free-plan team slot may not be free yet"
                    % (", ".join(still), TEAM_DELETE_POLL_SECONDS))
                sys.stderr.write("  teamDelete NOT confirmed for %s after %ds\n"
                                 % (", ".join(still), TEAM_DELETE_POLL_SECONDS))
                return False
            time.sleep(5)

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
                    self.mutate("team", "update", key,
                                "mutation($id: String!, $input: TeamUpdateInput!) "
                                "{ teamUpdate(id: $id, input: $input) { success team { id } } }",
                                {"id": live["id"], "input": changes}, "teamUpdate.team",
                                detail=", ".join(sorted(changes)))
                else:
                    self.plan.add("ok", "team", key, "already matches spec")
            else:
                team = self.create_team(spec_team, wanted)
                team_id = team["id"] if team else self.placeholder("team", key)
                self.put_id("team", key, team_id)
                self.by_team_key[key] = self.fresh_team_states(spec_team, team_id)
            self.build_states(spec_team)

    def fresh_team_states(self, spec_team, team_id):
        """States a just-created team has: read them back, or predict them in a dry run."""
        if self.apply:
            data = gql("query($id: String!) { team(id: $id) { id key states { nodes "
                       "{ id name type color position description archivedAt "
                       "issues(first: 1) { nodes { id } } } } } }", {"id": team_id})
            return data["team"]
        predicted = [dict(node) for node in DEFAULT_TEAM_STATES]
        if not spec_team.get("triageEnabled"):
            predicted = [s for s in predicted if s["type"] != "triage"]
        for state in predicted:
            state["id"] = self.placeholder("defaultState", "%s/%s" % (spec_team["key"], state["name"]))
        return {"id": team_id, "key": spec_team["key"], "states": {"nodes": predicted}}

    def create_team(self, spec_team, wanted):
        payload = dict(wanted)
        payload["key"] = spec_team["key"]
        payload = {k: v for k, v in payload.items() if v is not None}
        query = ("mutation($input: TeamCreateInput!) "
                 "{ teamCreate(input: $input) { success team { id key } } }")
        for attempt in range(1, PLAN_LIMIT_RETRIES + 1):
            try:
                return self.mutate(
                    "team", "create", spec_team["key"], query, {"input": payload},
                    "teamCreate.team", detail=spec_team.get("name", ""))
            except LinearError as exc:
                if exc.matches("icon") and "icon" in payload:
                    self.plan.problem("team %s: icon %r rejected, creating without an icon"
                                      % (spec_team["key"], payload.pop("icon")))
                    continue
                limit_hit = exc.matches("limit", "free plan", "upgrade", "maximum number of teams")
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
        live_team = self.by_team_key.get(key)
        live_states = [s for s in ((live_team or {}).get("states") or {}).get("nodes", [])
                       if not s.get("archivedAt")]
        by_name = {norm(s["name"]): s for s in live_states}
        by_type = {}
        for state in live_states:
            by_type.setdefault(state["type"], []).append(state)

        matched = set()
        for spec_state in spec_team.get("states", []):
            name = spec_state["name"]
            wanted = {"name": name, "color": spec_state.get("color"),
                      "position": spec_state.get("position"),
                      "description": spec_state.get("description")}
            live = by_name.get(norm(name))
            if live is None and spec_state["type"] == "triage":
                # `triage` is not creatable; Linear makes one when triageEnabled is on.
                candidates = by_type.get("triage") or []
                live = candidates[0] if candidates else None
                if live is None:
                    self.plan.problem(
                        "team %s: spec wants a triage state %r but the team has none; it appears "
                        "only after triageEnabled is on (teamCreate/teamUpdate above sets it, but "
                        "a re-run is needed to rename it)" % (key, name))
                    continue
            if live is not None:
                matched.add(live["id"])
                self.put_id("state", "%s/%s" % (key, name), live["id"])
                if live["type"] != spec_state["type"]:
                    self.plan.problem(
                        "team %s state %r is type %r but the spec wants %r; WorkflowStateUpdateInput "
                        "cannot change type, so this state must be recreated by hand"
                        % (key, name, live["type"], spec_state["type"]))
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

        for state in live_states:
            if state["id"] in matched:
                continue
            has_issues = bool((state.get("issues") or {}).get("nodes"))
            if has_issues:
                self.plan.add("keep", "state", "%s/%s" % (key, state["name"]),
                              "not in spec but still holds issues -- left alone")
                continue
            self.mutate("state", "archive", "%s/%s" % (key, state["name"]),
                        "mutation($id: String!) { workflowStateArchive(id: $id) { success } }",
                        {"id": state["id"]}, "workflowStateArchive",
                        detail="default state not in spec, no issues")

    # ---------- step d1: labels ----------

    def build_labels(self):
        specs = self.spec.get("labels", [])
        group_names = {norm(l["group"]) for l in specs if l.get("group")}
        parents = [l for l in specs if norm(l["name"]) in group_names]
        children = [l for l in specs if norm(l["name"]) not in group_names]

        for spec_label in parents:
            self.sync_issue_label(spec_label, is_group=True)
        for spec_label in children:
            self.sync_issue_label(spec_label, is_group=False)

        wanted_project_labels = []
        for project in self.spec.get("projects", []):
            for name in project.get("labels") or []:
                if name not in wanted_project_labels:
                    wanted_project_labels.append(name)
        for name in wanted_project_labels:
            self.sync_project_label(name)

    def sync_issue_label(self, spec_label, is_group):
        name = spec_label["name"]
        parent_id = None
        if spec_label.get("group"):
            parent_id = self.get_id("label", spec_label["group"])
            if parent_id is None:
                self.plan.problem("label %r references unknown group %r"
                                  % (name, spec_label["group"]))
        live = self.label_by_name.get(norm(name))
        if live:
            self.put_id("label", name, live["id"])
            wanted = {"name": name, "color": spec_label.get("color"),
                      "description": spec_label.get("description"), "isGroup": is_group}
            changes = self.diff_fields(live, wanted)
            live_parent = (live.get("parent") or {}).get("id")
            if parent_id and not self.is_placeholder(parent_id) and live_parent != parent_id:
                changes["parentId"] = parent_id
            if changes:
                self.mutate("label", "update", name,
                            "mutation($id: String!, $input: IssueLabelUpdateInput!) "
                            "{ issueLabelUpdate(id: $id, input: $input) "
                            "{ success issueLabel { id } } }",
                            {"id": live["id"], "input": changes}, "issueLabelUpdate.issueLabel",
                            detail=", ".join(sorted(changes)))
            else:
                self.plan.add("ok", "label", name, "already matches spec")
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
        node = self.mutate("label", "create", name,
                           "mutation($input: IssueLabelCreateInput!) "
                           "{ issueLabelCreate(input: $input) { success issueLabel { id } } }",
                           {"input": payload}, "issueLabelCreate.issueLabel",
                           detail=("group" if is_group else (spec_label.get("group") or "flat")))
        self.put_id("label", name, node["id"] if node else self.placeholder("label", name))

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

    def template_data(self, spec_template):
        defaults = spec_template.get("defaults") or {}
        body = spec_template.get("body") or ""
        kind = spec_template["type"]
        if kind == "issue":
            data = {"title": spec_template["name"], "description": body}
            label_ids = [self.get_id("label", n) for n in defaults.get("labels") or []]
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
                if live.get("templateData") != data:
                    changes["templateData"] = data
                if changes:
                    self.mutate("template", "update", label,
                                "mutation($id: String!, $input: TemplateUpdateInput!) "
                                "{ templateUpdate(id: $id, input: $input) "
                                "{ success template { id } } }",
                                {"id": live["id"], "input": changes}, "templateUpdate.template",
                                detail=", ".join(sorted(changes)))
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
                               detail="templateData keys: " + ",".join(sorted(data)))
            self.put_id("template", label,
                        node["id"] if node else self.placeholder("template", label))

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
                self.plan.problem("document %r has unresolvable scope %r" % (title, scope))
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
                               {"input": payload}, "documentCreate.document", detail=scope)
            self.put_id("document", title,
                        node["id"] if node else self.placeholder("document", title))

    # ---------- step d6: issues ----------

    def resolve_delegate(self, name):
        if not name:
            return None
        user = self.app_user_by_name.get(norm(name))
        if not user:
            self.plan.problem("no installed app user named %r -- delegate left empty "
                              "(installed app users: %s)"
                              % (name, ", ".join(sorted(u["name"] for u
                                                        in self.app_user_by_name.values())) or "none"))
            return None
        return user["id"]

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
        payload = {"teamId": self.get_id("team", team_key), "title": spec_issue["title"]}
        if spec_issue.get("description"):
            payload["description"] = spec_issue["description"]
        state_id = self.get_id("state", "%s/%s" % (team_key, spec_issue["state"]))
        if state_id:
            payload["stateId"] = state_id
            if self.state_type(team_key, spec_issue["state"]) == "triage":
                self.plan.problem(
                    "issues are seeded straight into the triage state %s/%s; Linear normally "
                    "puts issues there only through triage intake, so confirm issueCreate "
                    "accepts that stateId before the real run"
                    % (team_key, spec_issue["state"]))
        else:
            self.plan.problem("issue %r wants state %r on team %s, which the spec does not define"
                              % (spec_issue["title"], spec_issue["state"], team_key))
        if spec_issue.get("project"):
            project_id = self.get_id("project", spec_issue["project"])
            if project_id:
                payload["projectId"] = project_id
            else:
                self.plan.problem("issue %r references unknown project %r"
                                  % (spec_issue["title"], spec_issue["project"]))
        if spec_issue.get("milestone") and spec_issue.get("project"):
            key = "%s / %s" % (spec_issue["project"], spec_issue["milestone"])
            milestone_id = self.get_id("milestone", key)
            if milestone_id:
                payload["projectMilestoneId"] = milestone_id
            else:
                self.plan.problem("issue %r references unknown milestone %r"
                                  % (spec_issue["title"], spec_issue["milestone"]))
        label_ids = [self.get_id("label", n) for n in spec_issue.get("labels") or []]
        missing = [n for n, i in zip(spec_issue.get("labels") or [], label_ids) if not i]
        for name in missing:
            self.plan.problem("issue %r references unknown label %r"
                              % (spec_issue["title"], name))
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

        # second pass: sub-issues, matched by parent title inside the same team
        for spec_issue in spec_issues:
            parent_title = spec_issue.get("parent")
            if not parent_title:
                continue
            team_key = spec_issue["teamKey"]
            child_id = self.get_id("issue", "%s/%s" % (team_key, spec_issue["title"]))
            parent_id = self.get_id("issue", "%s/%s" % (team_key, parent_title))
            if not parent_id:
                self.plan.problem("issue %r references unknown parent %r"
                                  % (spec_issue["title"], parent_title))
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

    def run(self, backup_path, backup_required):
        self.load_snapshot()
        if self.apply or backup_required:
            self.check_backup(backup_path)
        if self.teardown:
            self.run_teardown()
            if self.apply:
                self.load_snapshot()
        self.build_teams()
        self.build_labels()
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


def validate_inputs(plan):
    """Check every planned `input:` payload against the live GraphQL input type.

    Read-only: it only runs introspection, never the mutation itself.
    """
    cache = {}
    problems = []
    checked = 0
    for entry in plan.entries:
        query, variables = entry.get("query"), entry.get("variables")
        if not query or not variables or "input" not in variables:
            continue
        marker = query.find(INPUT_TYPE_RE)
        if marker < 0:
            continue
        rest = query[marker + len(INPUT_TYPE_RE):]
        type_name = ""
        for char in rest:
            if not (char.isalnum() or char == "_"):
                break
            type_name += char
        if not type_name:
            continue
        if type_name not in cache:
            data = gql("query($n: String!) { __type(name: $n) { inputFields { name "
                       "type { kind name ofType { kind name enumValues { name } } "
                       "enumValues { name } } } } }", {"n": type_name})
            info = data.get("__type")
            if not info:
                problems.append("input type %s does not exist" % type_name)
                cache[type_name] = None
                continue
            cache[type_name] = {f["name"]: f["type"] for f in info["inputFields"]}
        fields = cache[type_name]
        if fields is None:
            continue
        checked += 1
        payload = variables["input"]
        if not isinstance(payload, dict):
            continue
        for name, field_type in fields.items():
            if field_type.get("kind") == "NON_NULL" and name not in payload:
                problems.append("%s %s %r: %s requires %r but the payload omits it"
                                % (entry["op"], entry["kind"], entry["name"], type_name, name))
        for key, value in payload.items():
            if key not in fields:
                problems.append("%s %s %r: %s has no field %r"
                                % (entry["op"], entry["kind"], entry["name"], type_name, key))
                continue
            inner = fields[key]
            if inner.get("kind") == "NON_NULL":
                inner = inner.get("ofType") or {}
            allowed = inner.get("enumValues")
            if allowed and isinstance(value, str):
                names = {v["name"] for v in allowed}
                if value not in names:
                    problems.append("%s %s %r: %s.%s = %r is not one of %s"
                                    % (entry["op"], entry["kind"], entry["name"], type_name,
                                       key, value, ", ".join(sorted(names))))
    return checked, sorted(set(problems)), sorted(k for k, v in cache.items() if v)


def verify(spec):
    """Re-read the workspace and report what the spec wants but does not have."""
    builder = Builder(spec, apply_changes=False, teardown=False, verbose=False)
    builder.load_snapshot()
    rows = []

    def compare(kind, wanted_names, live_names):
        wanted = {norm(n) for n in wanted_names}
        live = {norm(n) for n in live_names}
        missing = sorted(n for n in wanted_names if norm(n) not in live)
        extra = sorted(n for n in live_names if norm(n) not in wanted)
        rows.append((kind, len(wanted), len(live), missing, extra))

    compare("teams", [t["key"] for t in spec["teams"]],
            [t["key"] for t in builder.snapshot["teams"]])
    for spec_team in spec["teams"]:
        live_team = builder.by_team_key.get(spec_team["key"])
        live_states = [] if not live_team else [
            s["name"] for s in (live_team.get("states") or {}).get("nodes", [])
            if not s.get("archivedAt")]
        compare("states/%s" % spec_team["key"], [s["name"] for s in spec_team["states"]],
                live_states)
    compare("labels", [l["name"] for l in spec["labels"]],
            [l["name"] for l in builder.snapshot["issueLabels"]])
    wanted_project_labels = sorted({n for p in spec["projects"] for n in p.get("labels") or []})
    compare("projectLabels", wanted_project_labels,
            [l["name"] for l in builder.snapshot["projectLabels"]])
    compare("initiatives", [i["name"] for i in spec["initiatives"]],
            [i["name"] for i in builder.snapshot["initiatives"]])
    compare("projects", [p["name"] for p in spec["projects"]],
            [p["name"] for p in builder.snapshot["projects"]])
    compare("milestones", ["%s / %s" % (p["name"], m["name"])
                           for p in spec["projects"] for m in p.get("milestones") or []],
            ["%s / %s" % (p["name"], m["name"]) for p in builder.snapshot["projects"]
             for m in (p.get("projectMilestones") or {}).get("nodes", [])])
    compare("templates", ["%s [%s]" % (t["name"], t["type"]) for t in spec["templates"]],
            ["%s [%s]" % (t["name"], t["type"]) for t in builder.snapshot["templates"]])
    compare("documents", [d["title"] for d in spec["documents"]],
            [d["title"] for d in builder.snapshot["documents"]])
    compare("issues", ["%s/%s" % (i["teamKey"], i["title"]) for i in spec["issues"]],
            ["%s/%s" % ((i.get("team") or {}).get("key"), i["title"])
             for i in builder.snapshot["issues"]])

    print("VERIFY -- spec vs live workspace")
    print("  %-18s %6s %6s %8s %6s" % ("KIND", "SPEC", "LIVE", "MISSING", "EXTRA"))
    ok = True
    for kind, wanted, live, missing, extra in rows:
        print("  %-18s %6d %6d %8d %6d" % (kind, wanted, live, len(missing), len(extra)))
        if missing:
            ok = False
            for name in missing[:10]:
                print("      missing: %s" % name)
            if len(missing) > 10:
                print("      ... and %d more" % (len(missing) - 10))
        for name in extra[:5]:
            print("      extra:   %s" % name)
        if len(extra) > 5:
            print("      ... and %d more extra" % (len(extra) - 5))
    print("VERDICT: %s" % ("spec fully applied" if ok else "spec NOT fully applied"))
    return 0 if ok else 1


def main():
    parser = argparse.ArgumentParser(description="Apply linear-spec.json to Linear")
    parser.add_argument("--spec", default=SPEC_PATH)
    parser.add_argument("--backup", default=BACKUP_PATH)
    parser.add_argument("--idmap", default=IDMAP_PATH)
    parser.add_argument("--dry-run", action="store_true",
                        help="print the plan without mutating (the default)")
    parser.add_argument("--apply", action="store_true", help="actually mutate the workspace")
    parser.add_argument("--teardown", action="store_true",
                        help="delete issues, projects, initiatives and teams not in the spec")
    parser.add_argument("--backup-required", action="store_true",
                        help="hard-fail unless the backup exists and covers every live issue")
    parser.add_argument("--verify", action="store_true",
                        help="re-read the workspace and diff it against the spec")
    parser.add_argument("--quiet", action="store_true", help="summary counts only")
    parser.add_argument("--validate", action="store_true",
                        help="introspect every planned input type and check the payload keys")
    args = parser.parse_args()

    with open(args.spec, "r", encoding="utf-8") as fh:
        spec = json.load(fh)

    if args.verify:
        return verify(spec)

    if args.apply and args.dry_run:
        parser.error("--apply and --dry-run are mutually exclusive")

    builder = Builder(spec, apply_changes=args.apply, teardown=args.teardown,
                      verbose=not args.quiet)
    try:
        builder.run(args.backup, args.backup_required)
    except LinearError as exc:
        sys.stderr.write("\nABORTED on a Linear error: %s\n" % exc)
        if exc.variables:
            sys.stderr.write(json.dumps(exc.variables, ensure_ascii=False)[:1500] + "\n")
        print("\nPLAN UP TO THE FAILURE")
        print(builder.plan.render(verbose=not args.quiet))
        return 1

    header = "APPLIED" if args.apply else "DRY RUN -- no mutations were sent"
    print("\n%s" % header)
    print(builder.plan.render(verbose=not args.quiet))
    print("\nAPI: %d requests, %d retries" % (stats()["requests"], stats()["retries"]))

    if args.validate:
        checked, issues, types = validate_inputs(builder.plan)
        print("\nINPUT VALIDATION: %d payloads checked against %d live input types (%s)"
              % (checked, len(types), ", ".join(types)))
        for issue in issues:
            builder.plan.problem(issue)
        if not issues:
            print("  every payload key exists on its input type")

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
