#!/usr/bin/env python3
"""Read-only checks: the spec against itself, the payloads against the live
schema, and the finished workspace against the spec.

None of this mutates anything, and `validate_spec` runs before the first request
so a contradiction in the spec costs nothing to find.
"""

from linear_api import gql
from linear_common import (ESTIMATION_SCALES, RESERVED_STATE_TYPES, TEAM_SETTINGS,
                           label_key, norm)

INPUT_TYPE_RE = "$input: "


def validate_spec(spec):
    """Fail before the first request on anything the spec contradicts itself on.

    Returns the non-fatal warnings: things Linear will not accept but that only a
    human can resolve, so the build reports them instead of refusing to run.
    """
    problems = []
    warnings = []
    labels = spec.get("labels", [])
    groups = {norm(l["name"]) for l in labels if l.get("isGroup")}
    # Linear label names are unique across the whole workspace, groups included:
    # the second `intern` comes back "duplicate label name" however different its
    # group (probed 2026-09-03). Which of the two keeps the name is a design call,
    # so this is surfaced up front rather than raised 60 labels into the run.
    by_name = {}
    for label in labels:
        by_name.setdefault(norm(label["name"]), []).append(label.get("group") or "(ungrouped)")
    for name, in_groups in sorted(by_name.items()):
        if len(in_groups) > 1:
            users = sorted(
                {i["title"] for i in spec.get("issues", [])
                 for ref in i.get("labels") or [] if norm(ref).endswith("/" + name)})
            warnings.append(
                "label name %r is used by %d groups (%s). Linear label names are unique "
                "workspace-wide, so only the first survives and the rest are dropped, along "
                "with the label on the %d issue(s) that reference them. Rename one in the spec "
                "to keep both." % (name, len(in_groups), ", ".join(in_groups), len(users)))
    keys = {}
    group_of = {}
    for label in labels:
        key = norm(label_key(label["name"], label.get("group")))
        if key in keys:
            problems.append("duplicate label %r" % key)
        keys[key] = label
        if label.get("group"):
            group_of[key] = norm(label["group"])
            if norm(label["group"]) not in groups:
                problems.append("label %r hangs under %r, which is not marked isGroup"
                                % (key, label["group"]))
        elif "/" in label["name"]:
            problems.append("ungrouped label %r contains a slash, which the group/child "
                            "resolver cannot tell apart from a grouped reference"
                            % label["name"])

    def check_label_refs(where, names):
        seen = {}
        for name in names or []:
            key = norm(name)
            if key not in keys:
                problems.append("%s references unknown label %r" % (where, name))
                continue
            group = group_of.get(key)
            if group and group in seen:
                problems.append("%s carries two labels from group %r (%s and %s); Linear groups "
                                "are single-select, so one is silently dropped and every run "
                                "would re-issue the same update"
                                % (where, group, seen[group], name))
            elif group:
                seen[group] = name

    teams = {t["key"]: t for t in spec.get("teams", [])}
    for team in spec.get("teams", []):
        scale = team.get("issueEstimationType")
        if scale not in ESTIMATION_SCALES:
            problems.append("team %s has unknown issueEstimationType %r" % (team["key"], scale))
        names = [s["name"] for s in team.get("states", [])]
        for field in ("defaultState", "autoCloseState"):
            if team.get(field) and team[field] not in names:
                problems.append("team %s %s %r is not one of its states"
                                % (team["key"], field, team[field]))
        if team.get("cyclesEnabled") and team.get("cycleDuration") is None:
            problems.append("team %s enables cycles without a cycleDuration" % team["key"])

    projects = {p["name"]: p for p in spec.get("projects", [])}
    initiatives = {i["name"] for i in spec.get("initiatives", [])}
    for project in spec.get("projects", []):
        if project.get("initiative") and project["initiative"] not in initiatives:
            problems.append("project %r references unknown initiative %r"
                            % (project["name"], project["initiative"]))
        for key in project.get("teamKeys", []):
            if key not in teams:
                problems.append("project %r references unknown team %r" % (project["name"], key))

    for template in spec.get("templates", []):
        check_label_refs("template %r" % template["name"],
                         (template.get("defaults") or {}).get("labels"))
        if template.get("teamKey") and template["teamKey"] not in teams:
            problems.append("template %r references unknown team %r"
                            % (template["name"], template["teamKey"]))

    for document in spec.get("documents", []):
        kind, _, target = (document.get("scope") or "").partition(":")
        if kind == "project" and target not in projects:
            problems.append("document %r is scoped to unknown project %r"
                            % (document["title"], target))
        elif kind == "initiative" and target not in initiatives:
            problems.append("document %r is scoped to unknown initiative %r"
                            % (document["title"], target))
        elif kind not in ("project", "initiative"):
            problems.append("document %r has an unusable scope %r"
                            % (document["title"], document.get("scope")))

    for issue in spec.get("issues", []):
        where = "issue %r" % issue["title"]
        check_label_refs(where, issue.get("labels"))
        team = teams.get(issue.get("teamKey"))
        if not team:
            problems.append("%s references unknown team %r" % (where, issue.get("teamKey")))
            continue
        if issue.get("state") not in [s["name"] for s in team.get("states", [])]:
            problems.append("%s wants state %r, which team %s does not define"
                            % (where, issue.get("state"), team["key"]))
        estimate = issue.get("estimate")
        allowed = ESTIMATION_SCALES.get(team.get("issueEstimationType"), set())
        if estimate is not None and estimate not in allowed:
            problems.append("%s has estimate %s, which the %s scale of team %s cannot store "
                            "(allowed: %s)" % (where, estimate, team.get("issueEstimationType"),
                                               team["key"], sorted(allowed)))
        if issue.get("project") and issue["project"] not in projects:
            problems.append("%s references unknown project %r" % (where, issue["project"]))
        if issue.get("milestone"):
            project = projects.get(issue.get("project") or "")
            names = [m["name"] for m in (project or {}).get("milestones") or []]
            if issue["milestone"] not in names:
                problems.append("%s references milestone %r, which project %r does not have"
                                % (where, issue["milestone"], issue.get("project")))

    if problems:
        raise SystemExit("REFUSING TO RUN: the spec contradicts itself\n  - %s"
                         % "\n  - ".join(sorted(problems)))
    return warnings


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


def verify(spec, builder, org_arg=None):
    """Re-read the workspace and report what the spec wants but does not have."""
    builder.load_snapshot()
    builder.guard_workspace(org_arg)
    rows = []

    def compare(kind, wanted_names, live_names):
        wanted = {norm(n) for n in wanted_names}
        live = {norm(n) for n in live_names}
        missing = sorted(n for n in wanted_names if norm(n) not in live)
        extra = sorted(n for n in live_names if norm(n) not in wanted)
        rows.append((kind, len(wanted), len(live), missing, extra))

    compare("teams", ["%s (%s)" % (t["key"], t["name"]) for t in spec["teams"]],
            ["%s (%s)" % (t["key"], t["name"]) for t in builder.snapshot["teams"]])
    for spec_team in spec["teams"]:
        live_team = builder.by_team_key.get(spec_team["key"]) or {}
        # A reserved state (triage) refuses every update, so it keeps Linear's own
        # name however the spec labels it. Match that one on type -- the thing
        # that actually routes issues. Every other state still compares by name,
        # so the exemption cannot hide real drift.
        reserved = {s["type"]: s["name"] for s in spec_team["states"]
                    if s["type"] in RESERVED_STATE_TYPES}
        # Type matters: a state of the wrong type cannot be repaired by an update.
        live_states = ["%s [%s]" % (reserved.get(s["type"], s["name"]), s["type"])
                       for s in (live_team.get("states") or {}).get("nodes", [])
                       if not s.get("archivedAt")]
        compare("states/%s" % spec_team["key"],
                ["%s [%s]" % (s["name"], s["type"]) for s in spec_team["states"]], live_states)
        settings = {f: spec_team.get(f) for f in TEAM_SETTINGS if spec_team.get(f) is not None}
        drift = builder.diff_fields(live_team, settings)
        if drift:
            rows.append(("settings/%s" % spec_team["key"], len(settings),
                         len(settings) - len(drift), sorted(drift), []))
    compare("labels", [builder.spec_label_key(l) for l in spec["labels"]],
            [builder.live_label_key(l) for l in builder.snapshot["issueLabels"]])
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
    compare("delegates", sorted({i["delegate"] for i in spec["issues"] if i.get("delegate")}),
            sorted({(i.get("delegate") or {}).get("name")
                    for i in builder.snapshot["issues"] if i.get("delegate")}))

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
