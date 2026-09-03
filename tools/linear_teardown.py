#!/usr/bin/env python3
"""Empty the old workspace and turn the surviving team into the new one.

The Free plan allows two teams, so the old team is not deleted -- it is emptied
and renamed (FC -> WV), which keeps the plan slot and side-steps the fact that
`teamDelete` frees its slot asynchronously. The steps, in order:

    1. log organization.createdIssueCount
    2. permanently delete every legacy issue
    3. log organization.createdIssueCount again (does deleting free Free-plan room?)
    4. delete every project, initiative and label the spec does not name
    5. delete the archived probe team, so the second slot is really free
    6. teamUpdate the legacy team to the spec's key and name

Every step is guarded so that re-running after a crash is a no-op for the parts
that already happened, and every deletion is scoped to ids captured before the
first mutation -- never to a filter evaluated at call time.
"""

import sys
import time

from linear_api import LinearError, gql
from linear_common import norm

# The one team this tool may rewrite, by id: renaming does not change it, so a
# resumed run still recognises the team after step 6 turned FC into WV.
LEGACY_TEAM_ID = "ae7176f0-da44-48c8-b1cf-ecaf30240783"
LEGACY_TEAM_KEY = "FC"
SURVIVOR_TEAM_KEY = "WV"
ARCHIVED_PROBE_TEAM_KEY = "ZZA"

ISSUE_DELETE_BATCH = 20
TEAM_DELETE_POLL_SECONDS = 120
POLL_INTERVAL = 5

COUNTER_QUERY = "query { organization { id urlKey createdIssueCount } }"


class Teardown(object):
    """Runs against a Builder: uses its plan, its snapshot and its mutate()."""

    def __init__(self, builder):
        self.builder = builder
        self.plan = builder.plan
        self.spec = builder.spec
        self.targets = {}

    # ---------- target capture ----------

    def capture(self):
        """Freeze what may be deleted, before anything mutates."""
        snap = self.builder.snapshot
        spec_projects = {norm(p["name"]) for p in self.spec.get("projects", [])}
        spec_initiatives = {norm(i["name"]) for i in self.spec.get("initiatives", [])}
        spec_issue_titles = {norm(i["title"]) for i in self.spec.get("issues", [])}
        spec_labels = self.builder.spec_label_keys()
        spec_project_labels = {norm(n) for p in self.spec.get("projects", [])
                               for n in p.get("labels") or []}

        legacy_team = next((t for t in snap["teams"] if t["id"] == LEGACY_TEAM_ID), None)
        archived_probe = next(
            (t for t in snap["archivedTeams"]
             if t.get("archivedAt") and t["key"] == ARCHIVED_PROBE_TEAM_KEY), None)

        issues = [i for i in snap["issues"]
                  if (i.get("team") or {}).get("id") == LEGACY_TEAM_ID
                  and norm(i["title"]) not in spec_issue_titles]
        projects = [p for p in snap["projects"] if norm(p["name"]) not in spec_projects]
        initiatives = [i for i in snap["initiatives"]
                       if norm(i["name"]) not in spec_initiatives]
        labels = [l for l in snap["issueLabels"]
                  if self.builder.live_label_key(l) not in spec_labels]
        # Project labels are flat in the spec, so a live one that sits inside a
        # group goes too: keeping it would leave it orphaned (or silently deleted
        # with its group) while the build still holds its id.
        project_labels = [l for l in snap["projectLabels"]
                          if norm(l["name"]) not in spec_project_labels or l.get("parent")]

        self.targets = {
            "legacyTeam": legacy_team,
            "archivedProbeTeam": archived_probe,
            "issues": issues,
            "projects": projects,
            "initiatives": initiatives,
            "labels": labels,
            "projectLabels": project_labels,
        }
        self.allowed_ids = {n["id"] for group in
                            ("issues", "projects", "initiatives", "labels", "projectLabels")
                            for n in self.targets[group]}
        for team in (legacy_team, archived_probe):
            if team:
                self.allowed_ids.add(team["id"])
        return self.targets

    def guard(self, record):
        if record["id"] not in self.allowed_ids:
            raise LinearError("teardown refused to touch %r: its id was not captured before "
                              "the first mutation" % record.get("name", record["id"]))
        return record["id"]

    # ---------- steps ----------

    def run(self):
        if self.builder.probe_results.get("permanentDeleteWorks") is False:
            raise SystemExit(
                "REFUSING TO RUN THE TEARDOWN: the probe issue was still readable after "
                "issueDelete(permanentlyDelete: true). Deleting the legacy issues would only "
                "trash them, which neither frees the Free-plan budget nor really removes the "
                "old workspace's data.")
        targets = self.capture()
        before = self.issue_counter("before deleting the legacy issues")
        self.delete_issues(targets["issues"])
        after = self.issue_counter("after deleting the legacy issues") \
            if self.builder.apply else None
        self.report_counter(before, after, len(targets["issues"]))
        self.builder.checkpoint()

        for project in targets["projects"]:
            self.builder.mutate("project", "delete", project["name"],
                                "mutation($id: String!) { projectDelete(id: $id) { success } }",
                                {"id": self.guard(project)}, "projectDelete",
                                detail="not in the spec")
        for initiative in targets["initiatives"]:
            self.delete_initiative(initiative)
        self.delete_labels(targets["labels"], targets["projectLabels"])
        self.builder.checkpoint()

        self.delete_archived_probe_team(targets["archivedProbeTeam"])
        self.rename_legacy_team(targets["legacyTeam"])
        self.apply_to_snapshot()
        self.builder.checkpoint()

    # ---------- step 1/3: the Free-plan issue counter ----------

    def issue_counter(self, moment):
        if not self.builder.apply:
            org = self.builder.snapshot.get("organization") or {}
            return org.get("createdIssueCount")
        count = gql(COUNTER_QUERY)["organization"]["createdIssueCount"]
        sys.stderr.write("  organization.createdIssueCount %s: %s\n" % (moment, count))
        sys.stderr.flush()
        return count

    def report_counter(self, before, after, deleted):
        if before is None:
            return
        if after is None:
            self.plan.note(
                "createdIssueCount is %s now; the real run logs it again after deleting the %d "
                "legacy issues, which is how we learn whether deletion gives Free-plan headroom "
                "back." % (before, deleted))
        elif before == after:
            self.plan.note(
                "createdIssueCount stayed at %s after deleting %d issues: permanent deletion "
                "does NOT give Free-plan headroom back, so budget the number of full rebuilds."
                % (before, deleted))
        else:
            self.plan.note(
                "createdIssueCount dropped %s -> %s after deleting %d issues: permanent deletion "
                "DOES free Free-plan headroom." % (before, after, deleted))

    # ---------- step 2: issues ----------

    def delete_issues(self, issues):
        if not issues:
            self.plan.add("skip", "issue", "no legacy issues left to delete")
            return
        self.plan.add("delete", "issue", "%d legacy issues" % len(issues),
                      "permanentlyDelete, batched %d per request" % ISSUE_DELETE_BATCH,
                      weight=len(issues))
        if not self.builder.apply:
            return
        done = 0
        for start in range(0, len(issues), ISSUE_DELETE_BATCH):
            chunk = issues[start:start + ISSUE_DELETE_BATCH]
            decls = ", ".join("$id%d: String!" % n for n in range(len(chunk)))
            body = " ".join("d%d: issueDelete(id: $id%d, permanentlyDelete: true) { success }"
                            % (n, n) for n in range(len(chunk)))
            variables = {"id%d" % n: self.guard(issue) for n, issue in enumerate(chunk)}
            data = gql("mutation(%s) { %s }" % (decls, body), variables, retry_transport=False)
            self.retry_failed_deletes(chunk, data)
            done += len(chunk)
            sys.stderr.write("  deleted %d/%d issues\n" % (done, len(issues)))
            sys.stderr.flush()

    def retry_failed_deletes(self, chunk, data):
        """One bad id in a batch must not silently take its 19 siblings with it."""
        for index, issue in enumerate(chunk):
            result = (data or {}).get("d%d" % index) or {}
            if result.get("success"):
                continue
            try:
                gql("mutation($id: String!) "
                    "{ issueDelete(id: $id, permanentlyDelete: true) { success } }",
                    {"id": issue["id"]}, retry_transport=False)
            except LinearError as exc:
                self.plan.problem("issueDelete failed for %s (%s): %s"
                                  % (issue.get("identifier") or issue["id"],
                                     issue.get("title"), exc))

    # ---------- step 4: initiatives and labels ----------

    def delete_initiative(self, initiative):
        deleted = self.builder.mutate(
            "initiative", "delete", initiative["name"],
            "mutation($id: String!) { initiativeDelete(id: $id) { success } }",
            {"id": self.guard(initiative)}, "initiativeDelete",
            detail="not in the spec", tolerate=True)
        if deleted is None and self.builder.apply:
            self.builder.mutate(
                "initiative", "archive", initiative["name"],
                "mutation($id: String!) { initiativeArchive(id: $id) { success } }",
                {"id": initiative["id"]}, "initiativeArchive",
                detail="initiativeDelete was refused", tolerate=True)

    def delete_labels(self, labels, project_labels):
        """Children before groups: deleting a group first orphans its members."""
        for label in sorted(labels, key=lambda l: bool(l.get("isGroup"))):
            self.builder.mutate(
                "label", "delete", label["name"],
                "mutation($id: String!) { issueLabelDelete(id: $id) { success } }",
                {"id": self.guard(label)}, "issueLabelDelete",
                detail="group" if label.get("isGroup") else "not in the spec", tolerate=True)
        for label in sorted(project_labels, key=lambda l: bool(l.get("isGroup"))):
            if label.get("isGroup"):
                why = "group"
            elif label.get("parent"):
                why = "sits in group %r; the spec keeps project labels flat" \
                      % (label["parent"] or {}).get("name")
            else:
                why = "not in the spec"
            self.builder.mutate(
                "projectLabel", "delete", label["name"],
                "mutation($id: String!) { projectLabelDelete(id: $id) { success } }",
                {"id": self.guard(label)}, "projectLabelDelete", detail=why, tolerate=True)

    # ---------- step 5: the archived probe team ----------

    def delete_archived_probe_team(self, team):
        if not team:
            self.plan.add("skip", "team", "no archived %s team to delete"
                          % ARCHIVED_PROBE_TEAM_KEY)
            return
        self.builder.mutate(
            "team", "delete", "%s (%s)" % (team["key"], team["name"]),
            "mutation($id: String!) { teamDelete(id: $id) { success entityId } }",
            {"id": self.guard(team)}, "teamDelete",
            detail="archived team, frees the second Free-plan slot", tolerate=True)
        if self.builder.apply:
            self.poll_team_gone(team["key"])

    def poll_team_gone(self, key):
        """An archived team disappears from the active listing immediately, so the
        only meaningful confirmation is that it left the archived listing too."""
        deadline = time.time() + TEAM_DELETE_POLL_SECONDS
        query = ("query { teams(first: 100, includeArchived: true) "
                 "{ nodes { key archivedAt } } }")
        while True:
            nodes = gql(query)["teams"]["nodes"]
            if key not in {t["key"] for t in nodes}:
                sys.stderr.write("  teamDelete confirmed: %s is gone from the archived "
                                 "listing too\n" % key)
                return True
            if time.time() >= deadline:
                self.plan.problem(
                    "team %s still appears in teams(includeArchived: true) after %ds; Linear "
                    "deletes team data asynchronously, so the second Free-plan slot may not be "
                    "free yet and teamCreate will retry" % (key, TEAM_DELETE_POLL_SECONDS))
                return False
            time.sleep(POLL_INTERVAL)

    # ---------- step 6: the rename that keeps the plan slot ----------

    def rename_legacy_team(self, team):
        spec_team = next((t for t in self.spec.get("teams", [])
                          if t["key"] == SURVIVOR_TEAM_KEY), None)
        if not spec_team:
            self.plan.problem("the spec has no team %r, so the legacy team cannot be renamed"
                              % SURVIVOR_TEAM_KEY)
            return
        if not team:
            self.plan.problem("legacy team %s (id %s) is not in the workspace; skipping the "
                              "rename" % (LEGACY_TEAM_KEY, LEGACY_TEAM_ID))
            return
        if team["key"] == SURVIVOR_TEAM_KEY:
            self.plan.add("ok", "team", SURVIVOR_TEAM_KEY, "legacy team was already renamed")
            self.builder.put_id("team", SURVIVOR_TEAM_KEY, team["id"])
            return
        if any(t["key"] == SURVIVOR_TEAM_KEY for t in self.builder.snapshot["teams"]):
            self.plan.problem("a team keyed %s already exists next to the legacy team; not "
                              "renaming" % SURVIVOR_TEAM_KEY)
            return
        self.builder.mutate(
            "team", "update", "%s -> %s" % (team["key"], SURVIVOR_TEAM_KEY),
            "mutation($id: String!, $input: TeamUpdateInput!) "
            "{ teamUpdate(id: $id, input: $input) { success team { id key } } }",
            {"id": self.guard(team),
             "input": {"key": SURVIVOR_TEAM_KEY, "name": spec_team["name"]}},
            "teamUpdate.team",
            detail="keeps the team slot and the issue counter; settings follow in build_teams")
        self.builder.put_id("team", SURVIVOR_TEAM_KEY, team["id"])

    # ---------- keep the in-memory snapshot honest ----------

    def apply_to_snapshot(self):
        """Replay the teardown on the snapshot, in dry runs too.

        Without this the dry run keeps seeing team FC and 129 issues, and would
        rehearse creating a third team on a two-team plan -- the opposite of what
        the real run does. Under --apply the snapshot is reloaded from the API
        afterwards anyway; this only has to make the rehearsal truthful.
        """
        snap = self.builder.snapshot
        gone = {n["id"] for group in ("issues", "projects", "initiatives",
                                      "labels", "projectLabels")
                for n in self.targets[group]}
        snap["issues"] = [i for i in snap["issues"] if i["id"] not in gone]
        snap["projects"] = [p for p in snap["projects"] if p["id"] not in gone]
        snap["initiatives"] = [i for i in snap["initiatives"] if i["id"] not in gone]
        snap["issueLabels"] = [l for l in snap["issueLabels"] if l["id"] not in gone]
        snap["projectLabels"] = [l for l in snap["projectLabels"] if l["id"] not in gone]

        probe = self.targets["archivedProbeTeam"]
        if probe:
            snap["archivedTeams"] = [t for t in snap["archivedTeams"] if t["id"] != probe["id"]]

        legacy = self.targets["legacyTeam"]
        spec_team = next((t for t in self.spec.get("teams", [])
                          if t["key"] == SURVIVOR_TEAM_KEY), None)
        if legacy and spec_team:
            legacy["key"] = SURVIVOR_TEAM_KEY
            legacy["name"] = spec_team["name"]
            # Its states now hold zero issues, which is what makes them archivable.
            for state in (legacy.get("states") or {}).get("nodes", []):
                state["issues"] = {"nodes": []}
        self.builder.reindex()
