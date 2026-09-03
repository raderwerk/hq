#!/usr/bin/env python3
"""Throwaway writes that settle the shapes the build depends on.

Four things the schema cannot tell us, all of them able to wreck a 300-mutation
run halfway through:

    a. what Linear stores in `templateData` (it normalises the blob, so a naive
       equality check would rewrite all 16 templates on every run)
    b. whether `issueDelete(permanentlyDelete: true)` really removes an issue,
       and whether the Free-plan `createdIssueCount` drops when it does
    c. whether `issueCreate` accepts a triage `stateId`, a `delegateId`, an
       estimate of 4 on the team's scale, and two labels from one group
    d. whether a description survives the markdown round trip unchanged

Every probe creates its own record, reads it back, and deletes it in a `finally`.
Nothing is ever deleted whose id did not come out of this module's own create.
Probes only write under --apply; `--probe --dry-run` just records the plan.
"""

import sys
import time

from linear_api import LinearError, gql

PREFIX = "zz-probe"

TEMPLATE_READBACK = "query($id: String!) { template(id: $id) { id name type templateData } }"
ISSUE_READBACK = """query($id: String!) { issue(id: $id) {
  id identifier title description estimate priority
  state { id name type } delegate { id name } labels { nodes { id name } } } }"""
COUNTER = "query { organization { createdIssueCount } }"


class Probe(object):
    def __init__(self, builder):
        self.builder = builder
        self.plan = builder.plan
        self.tag = "%s-%d" % (PREFIX, int(time.time()))
        self.results = builder.probe_results

    # ---------- helpers ----------

    def note(self, text):
        self.plan.note("probe: %s" % text)

    def is_gone(self, issue_id):
        try:
            return not (gql("query($id: String!) { issue(id: $id) { id } }",
                            {"id": issue_id}) or {}).get("issue")
        except LinearError:
            return True

    def create(self, kind, query, variables, path, detail=""):
        return self.builder.mutate(kind, "probe", self.tag, query, variables, path, detail=detail)

    def destroy(self, kind, query, variables, path, entity_id):
        if not entity_id or not self.builder.apply:
            return
        try:
            self.builder.mutate(kind, "probe-del", self.tag, query, variables, path,
                                detail="throwaway cleanup")
        except LinearError as exc:
            self.plan.problem("probe left %s %s behind (%s) -- delete it by hand"
                              % (kind, entity_id, exc))

    # ---------- phase a: before the teardown ----------

    def before_teardown(self, legacy_team_id):
        """Runs while the old team still exists, so the 129 real deletes that
        follow are not the first time we try `permanentlyDelete`."""
        self.probe_template()
        self.probe_permanent_delete(legacy_team_id)

    def probe_template(self):
        spec_template = next((t for t in self.builder.spec.get("templates", [])
                              if t["type"] == "issue"), None)
        if not spec_template:
            return
        data = self.builder.template_data(spec_template, with_labels=False)
        template_id = None
        try:
            node = self.create(
                "template", "mutation($input: TemplateCreateInput!) "
                "{ templateCreate(input: $input) { success template { id } } }",
                {"input": {"name": self.tag, "type": "issue", "templateData": data}},
                "templateCreate.template", detail="templateData round trip")
            if not self.builder.apply:
                return
            template_id = node["id"]
            live = gql(TEMPLATE_READBACK, {"id": template_id})["template"]["templateData"] or {}
            drifted = {k: (v, live.get(k)) for k, v in data.items() if live.get(k) != v}
            added = sorted(k for k in live if k not in data)
            self.results["templateDataKeys"] = sorted(data)
            self.results["templateDataServerKeys"] = added
            self.results["templateDataDrift"] = sorted(drifted)
            self.note("templateData came back with %d server-added key(s): %s"
                      % (len(added), ", ".join(added) or "none"))
            if drifted:
                self.note("templateData values Linear rewrote: %s -- the build compares only the "
                          "keys the spec owns, so this is survivable but worth knowing"
                          % ", ".join(sorted(drifted)))
        finally:
            self.destroy("template",
                         "mutation($id: String!) { templateDelete(id: $id) { success } }",
                         {"id": template_id}, "templateDelete", template_id)

    def probe_permanent_delete(self, team_id):
        if not team_id:
            return
        issue_id = None
        before = after_create = after_delete = None
        try:
            if self.builder.apply:
                before = gql(COUNTER)["organization"]["createdIssueCount"]
            node = self.create(
                "issue", "mutation($input: IssueCreateInput!) "
                "{ issueCreate(input: $input) { success issue { id } } }",
                {"input": {"teamId": team_id, "title": self.tag,
                           "description": "throwaway; proves issueDelete(permanentlyDelete)"}},
                "issueCreate.issue", detail="permanentlyDelete round trip")
            if not self.builder.apply:
                return
            issue_id = node["id"]
            after_create = gql(COUNTER)["organization"]["createdIssueCount"]
            gql("mutation($id: String!) "
                "{ issueDelete(id: $id, permanentlyDelete: true) { success } }",
                {"id": issue_id}, retry_transport=False)
            deleted_id, issue_id = issue_id, None
            after_delete = gql(COUNTER)["organization"]["createdIssueCount"]
            self.results["permanentDeleteWorks"] = self.is_gone(deleted_id)
            self.results["counterFreedByDelete"] = after_delete < after_create
            if not self.results["permanentDeleteWorks"]:
                self.plan.problem("probe: the throwaway issue is still readable after "
                                  "issueDelete(permanentlyDelete: true) -- deletion only "
                                  "trashes, so the Free-plan budget will not come back")
            self.note("createdIssueCount %s -> %s on create -> %s after permanentlyDelete: "
                      "deleting %s Free-plan headroom"
                      % (before, after_create, after_delete,
                         "gives back" if after_delete < after_create else "does NOT give back"))
        except LinearError as exc:
            self.plan.problem("probe: permanent delete could not be proven (%s); do not start "
                              "the teardown until it is" % exc)
        finally:
            if issue_id:
                self.destroy("issue", "mutation($id: String!) "
                             "{ issueDelete(id: $id, permanentlyDelete: true) { success } }",
                             {"id": issue_id}, "issueDelete", issue_id)

    # ---------- phase b: after teams and labels, before the real issues ----------

    def after_labels(self, team_key):
        """One throwaway issue that answers every open question about issueCreate."""
        spec_team = next((t for t in self.builder.spec.get("teams", [])
                          if t["key"] == team_key), None)
        if not spec_team:
            return
        triage = next((s for s in spec_team.get("states", []) if s["type"] == "triage"), None)
        state_id = self.builder.get_id("state", "%s/%s" % (team_key, triage["name"])) \
            if triage else None
        if triage and not state_id:
            raise SystemExit(
                "REFUSING TO CONTINUE: team %s has no triage state %r after teamCreate. The %d "
                "issues that target it would be created stateless."
                % (team_key, triage["name"], sum(1 for i in self.builder.spec["issues"]
                                                 if i.get("state") == triage["name"])))

        labels = self.builder.spec_group_pair("risico")
        label_ids = [self.builder.get_id("label", n) for n in labels]
        label_ids = [l for l in label_ids if l and not self.builder.is_placeholder(l)]
        description = ("Wegwerpissue van de probe.\n\n```yaml\nbronnen:\n"
                       "  - <link naar het klantdossier>\n```\n")
        payload = {"teamId": self.builder.get_id("team", team_key), "title": self.tag,
                   "description": description, "estimate": 4}
        if state_id and not self.builder.is_placeholder(state_id):
            payload["stateId"] = state_id
        if label_ids:
            payload["labelIds"] = label_ids
        delegate_id = self.builder.resolve_delegate(self.first_delegate())
        if delegate_id:
            payload["delegateId"] = delegate_id

        issue_id = None
        try:
            node = self.create("issue", "mutation($input: IssueCreateInput!) "
                               "{ issueCreate(input: $input) { success issue { id } } }",
                               {"input": payload}, "issueCreate.issue",
                               detail="triage state, delegate, estimate 4, two labels of one group")
            if not self.builder.apply:
                return
            issue_id = node["id"]
            live = gql(ISSUE_READBACK, {"id": issue_id})["issue"]
            self.check_readback(live, payload, description, labels, team_key, triage)
        finally:
            self.destroy("issue", "mutation($id: String!) "
                         "{ issueDelete(id: $id, permanentlyDelete: true) { success } }",
                         {"id": issue_id}, "issueDelete", issue_id)

    def check_readback(self, live, payload, description, labels, team_key, triage):
        state = (live.get("state") or {}).get("name")
        self.results["triageStateAccepted"] = bool(
            triage and state and state == triage["name"])
        if triage and state != triage["name"]:
            self.results["triageStateAccepted"] = False
            self.plan.problem(
                "probe: issueCreate with the triage stateId landed in %r instead of %r; the %s "
                "issues that want the triage state will be created without a stateId"
                % (state, triage["name"], team_key))

        estimate = live.get("estimate")
        self.results["estimateRoundTrip"] = estimate
        if estimate != payload["estimate"]:
            raise SystemExit(
                "REFUSING TO CONTINUE: estimate %s came back as %s, so the team's estimation "
                "scale rounds the spec's values and every run would re-issue an issueUpdate. "
                "Fix issueEstimationType or the spec estimates first."
                % (payload["estimate"], estimate))

        live_labels = [n["name"] for n in (live.get("labels") or {}).get("nodes", [])]
        self.results["sameGroupLabelsKept"] = len(live_labels)
        if labels and len(live_labels) < len(payload.get("labelIds") or []):
            self.note("two labels from one group came back as %d (%s): groups really are "
                      "single-select, so the spec self-check that forbids this stays"
                      % (len(live_labels), ", ".join(live_labels)))

        stored = live.get("description") or ""
        self.results["descriptionRoundTrip"] = stored.strip() == description.strip()
        if not self.results["descriptionRoundTrip"]:
            self.plan.problem(
                "probe: the description did not round-trip; Linear stored %d chars against %d "
                "sent. Placeholders in angle brackets are the usual cause -- check the spec "
                "before trusting the 'second run is a no-op' claim."
                % (len(stored), len(description)))

        if payload.get("delegateId"):
            self.results["delegateAccepted"] = bool(live.get("delegate"))
            if not live.get("delegate"):
                self.plan.problem("probe: delegateId was accepted but read back empty; the %d "
                                  "delegated issues will land unassigned"
                                  % sum(1 for i in self.builder.spec["issues"]
                                        if i.get("delegate")))
        sys.stderr.write("  probe results: %s\n" % self.results)
        sys.stderr.flush()

    def first_delegate(self):
        for issue in self.builder.spec.get("issues", []):
            if issue.get("delegate"):
                return issue["delegate"]
        return None
