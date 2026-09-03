#!/usr/bin/env python3
"""Vocabulary shared by the builder, the teardown, the probes and the checks."""


def norm(value):
    return " ".join((value or "").split()).strip().lower()


def label_key(name, group):
    """Labels are identified by group -- 'intern' exists under two of them."""
    return "%s/%s" % (group, name) if group else name


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
