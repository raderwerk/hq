#!/usr/bin/env python3
"""Read-only full export of the current Linear workspace to a single JSON file.

Exports: organization, users, teams (+ states, team labels, templates, cycles),
workspace issue labels and project labels, templates, initiatives (+ documents,
updates), projects (+ milestones, updates, documents, labels), documents,
issues incl. archived (+ comments), cycles, project statuses.

    python3 backup_linear.py [--out PATH] [--no-archived]

Writes a fresh timestamped file every run and never overwrites an existing one:
after a permanent teardown this file is the only rollback path, so it must not be
possible to replace a good export with a partial one. A run with section errors
writes `<name>.partial` and exits non-zero.

Never mutates anything.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from linear_api import LinearError, gql, page, stats  # noqa: E402

BACKUP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "linear")


def default_out():
    return os.path.join(BACKUP_DIR, time.strftime("backup-%Y-%m-%d-%H%M.json"))

ORG_FIELDS = """
id name urlKey createdAt updatedAt userCount createdIssueCount customerCount
customersEnabled releasesEnabled roadmapEnabled feedEnabled aiAddonEnabled
agentAutomationEnabled linearAgentEnabled codingAgentEnabled codeIntelligenceEnabled
aiThreadSummariesEnabled aiDiscussionSummariesEnabled restrictAgentInvocationToMembers
fiscalYearStartMonth gitBranchFormat trialEndsAt trialStartsAt deletionRequestedAt
periodUploadVolume logoUrl
subscription { id type seats }
"""

USER_FIELDS = """
id name displayName email active admin owner guest app isMe isAssignable isMentionable
supportsAgentSessions timezone lastSeen createdAt archivedAt url avatarUrl description title
"""

TEAM_FIELDS = """
id key name description icon color createdAt updatedAt archivedAt retiredAt
cyclesEnabled cycleStartDay cycleDuration cycleCooldownTime cycleLockToActive
cycleIssueAutoAssignStarted cycleIssueAutoAssignCompleted upcomingCycleCount
issueEstimationType issueEstimationAllowZero issueEstimationExtended defaultIssueEstimate
inheritIssueEstimation inheritWorkflowStatuses inheritProjectStatuses
triageEnabled requirePriorityToLeaveTriage allMembersCanJoin joinByDefault
groupIssueHistory setIssueSortOrderOnStateChange timezone issueCount initiativesEnabled
autoArchivePeriod autoClosePeriod autoCloseStateId
parent { id key } defaultIssueState { id name } triageIssueState { id name }
states { nodes { id name type color position description archivedAt } }
labels { nodes { id name color description isGroup parent { id name } } }
templates { nodes { id name type description templateData } }
cycles { nodes { id number name description startsAt endsAt completedAt } }
memberships { nodes { id owner user { id name email app } } }
"""

STATE_FIELDS = "id name type color position description createdAt archivedAt team { id key }"

LABEL_FIELDS = """
id name color description isGroup createdAt archivedAt retiredAt
parent { id name } team { id key } creator { id name }
"""

TEMPLATE_FIELDS = """
id name type description icon color sortOrder templateData hasFormFields
createdAt archivedAt team { id key } creator { id name }
"""

PROJECT_FIELDS = """
id name description content icon color slugId url priority priorityLabel
startDate targetDate startedAt completedAt canceledAt sortOrder trashed scope progress
createdAt updatedAt archivedAt
status { id name type } lead { id name email } creator { id name }
health
teams { nodes { id key } }
members { nodes { id name } }
labels { nodes { id name } }
projectMilestones { nodes { id name description targetDate sortOrder } }
initiatives { nodes { id name } }
projectUpdates { nodes { id body health createdAt user { id name } } }
documents { nodes { id title } }
"""

INITIATIVE_FIELDS = """
id name description content icon color slugId url priority sortOrder trashed
targetDate startedAt completedAt canceledAt createdAt updatedAt archivedAt
status health owner { id name email } creator { id name }
parentInitiative { id name }
projects { nodes { id name } }
labels { nodes { id name } }
documents { nodes { id title } }
initiativeUpdates { nodes { id body health createdAt user { id name } } }
"""

DOCUMENT_FIELDS = """
id title content icon color slugId url sortOrder trashed hiddenAt createdAt updatedAt archivedAt
creator { id name } owner { id name }
project { id name } initiative { id name } team { id key } issue { id identifier }
"""

ISSUE_FIELDS = """
id identifier number title description priority priorityLabel estimate sortOrder
subIssueSortOrder dueDate url branchName trashed
createdAt updatedAt archivedAt startedAt completedAt canceledAt triagedAt
team { id key } state { id name type } project { id name }
projectMilestone { id name } cycle { id number }
assignee { id name email } delegate { id name email app } creator { id name }
parent { id identifier title } lastAppliedTemplate { id name }
labels { nodes { id name } }
comments(first: 25) { nodes { id body createdAt editedAt url
                              user { id name email app } parent { id } } }
"""

CYCLE_FIELDS = """
id number name description startsAt endsAt completedAt createdAt archivedAt
team { id key } isActive isFuture isPast
"""

PROJECT_STATUS_FIELDS = "id name description color position indefinite type team { id key }"


def main():
    parser = argparse.ArgumentParser(description="Export the whole Linear workspace to JSON")
    parser.add_argument("--out", default=None,
                        help="default: linear/backup-<date-time>.json (never overwritten)")
    parser.add_argument("--no-archived", action="store_true", help="skip archived records")
    args = parser.parse_args()
    archived = not args.no_archived
    out_path = args.out or default_out()
    if os.path.exists(out_path):
        sys.stderr.write("REFUSING: %s already exists; backups are never overwritten\n"
                         % out_path)
        return 2

    backup = {
        "_meta": {
            "exportedAt": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "endpoint": "https://api.linear.app/graphql",
            "includeArchived": archived,
            "tool": "backup_linear.py",
        },
        "_errors": {},
    }

    sections = [
        ("organization", lambda: gql("query { organization { %s } }" % ORG_FIELDS)["organization"]),
        ("users", lambda: page("users", USER_FIELDS, archived, 50)),
        ("teams", lambda: page("teams", TEAM_FIELDS, archived, 10)),
        ("workflowStates", lambda: page("workflowStates", STATE_FIELDS, archived, 100)),
        ("issueLabels", lambda: page("issueLabels", LABEL_FIELDS, archived, 100)),
        ("projectLabels", lambda: page("projectLabels", LABEL_FIELDS, archived, 100)),
        ("templates", lambda: gql("query { templates { %s } }" % TEMPLATE_FIELDS)["templates"]),
        ("initiatives", lambda: page("initiatives", INITIATIVE_FIELDS, archived, 10)),
        ("projects", lambda: page("projects", PROJECT_FIELDS, archived, 10)),
        ("projectStatuses", lambda: page("projectStatuses", PROJECT_STATUS_FIELDS, archived, 50)),
        ("documents", lambda: page("documents", DOCUMENT_FIELDS, archived, 25)),
        ("cycles", lambda: page("cycles", CYCLE_FIELDS, archived, 50)),
        ("issues", lambda: page("issues", ISSUE_FIELDS, archived, 25)),
    ]

    for name, fn in sections:
        sys.stderr.write("-> %s ...\n" % name)
        sys.stderr.flush()
        try:
            backup[name] = fn()
        except LinearError as exc:
            sys.stderr.write("   FAILED: %s\n" % exc)
            backup[name] = []
            backup["_errors"][name] = str(exc)

    counts = {}
    for key, value in backup.items():
        if key.startswith("_"):
            continue
        counts[key] = len(value) if isinstance(value, list) else 1
    issues = backup.get("issues") or []
    counts["comments"] = sum(len((i.get("comments") or {}).get("nodes") or []) for i in issues)
    counts["archivedIssues"] = sum(1 for i in issues if i.get("archivedAt"))
    counts["projectMilestones"] = sum(
        len((p.get("projectMilestones") or {}).get("nodes") or []) for p in (backup.get("projects") or [])
    )
    counts["projectUpdates"] = sum(
        len((p.get("projectUpdates") or {}).get("nodes") or []) for p in (backup.get("projects") or [])
    )
    counts["initiativeUpdates"] = sum(
        len((i.get("initiativeUpdates") or {}).get("nodes") or [])
        for i in (backup.get("initiatives") or [])
    )
    backup["_meta"]["counts"] = counts

    # A failed section leaves an incomplete export. Park it under a name the
    # `backup-*.json` glob does not match, so it can never be picked up as the
    # rollback file for a teardown.
    if backup["_errors"]:
        out_path += ".partial"
    out_dir = os.path.dirname(os.path.abspath(out_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(backup, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, out_path)

    print("Backup written to %s (%.1f KB)" % (out_path, os.path.getsize(out_path) / 1024.0))
    print("Counts:")
    for key in sorted(counts):
        print("  %-20s %d" % (key, counts[key]))
    print("API: %d requests, %d retries, %.0f complexity points"
          % (stats()["requests"], stats()["retries"], stats()["complexity"]))
    if backup["_errors"]:
        print("ERRORS in sections: %s -- this export is INCOMPLETE and cannot gate a teardown"
              % ", ".join(sorted(backup["_errors"])))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
