# Linear GraphQL API — Exact Cheatsheet for Programmatic Workspace Rebuild

Source: `@linear/sdk@92.0.0` (npm, installed 2026-09-02) — no `.graphql` SDL file ships in the
package; the SDK bundles generated TS types in
`node_modules/@linear/sdk/dist/index-7gZbCe3y.d.mts` (type aliases: `type XCreateInput = {...}`,
`type MutationXArgs = {...}`, `type XPayload = {...}`) and the literal GraphQL operation strings in
`dist/index.mjs`. All field lists below are copy-pasted from that generated file, not guessed.
Endpoint and header semantics cross-checked against developers.linear.app.

Endpoint: `https://api.linear.app/graphql` — single POST endpoint, standard GraphQL over HTTP.

Auth header for personal/workspace API keys (no OAuth): `Authorization: <API_KEY>` — **no `Bearer`
prefix**. OAuth access tokens use the standard `Authorization: Bearer <token>`.

```sh
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: <API_KEY>" \
  --data '{ "query": "{ issues { nodes { id title } } }" }' \
  https://api.linear.app/graphql
```

Legend: `type Foo = { field: T }` = required, `field?: InputMaybe<T>` = optional/nullable.
`Scalars["String"]` etc. shown as `String`. `T` after `Array<>` is a list.

---

## 1. Pagination

Standard Relay-style cursor connections on every list field (`XConnection` = `{ edges { node,
cursor }, nodes, pageInfo }`).

`PageInfo`:
```
type PageInfo = {
  endCursor?: Maybe<String>
  hasNextPage: Boolean
  hasPreviousPage: Boolean
  startCursor?: Maybe<String>
}
```
Args on every connection field (e.g. `QueryTeamsArgs`):
```
type QueryTeamsArgs = {
  after?: InputMaybe<String>
  before?: InputMaybe<String>
  filter?: InputMaybe<TeamFilter>
  first?: InputMaybe<Int>
  includeArchived?: InputMaybe<Boolean>
  last?: InputMaybe<Int>
  orderBy?: InputMaybe<PaginationOrderBy>
}
```
Default page size: **50** if `first`/`last` omitted (confirmed via docs). Forward pagination: pass
`pageInfo.endCursor` as `after`, loop while `pageInfo.hasNextPage`. Default sort: `createdAt`;
`orderBy: updatedAt` also available via `PaginationOrderBy`.

**Exception**: `templates` query returns `Array<Template>` directly (not a connection) — no
pagination, no `first`/`after` on templates.

## 2. Rate limits / complexity (developers.linear.app/docs/graphql/rate-limiting)

| Auth | Requests/hour | Complexity points/hour |
|---|---|---|
| API key | 2,500 | 3,000,000 |
| OAuth app | 5,000 | 2,000,000 |
| Unauthenticated | 600 (per IP) | 100,000 (per IP) |

Single-query max complexity: **10,000 points**. Complexity formula: each scalar property = 0.1 pt,
each object = 1 pt, each connection multiplies its selected children's points by the requested
`first`/`last` (or the default of 50 if unspecified), rounded up.

Response headers: `X-RateLimit-Requests-Limit/Remaining/Reset`, `X-Complexity`,
`X-RateLimit-Complexity-Limit/Remaining/Reset`, `X-RateLimit-Endpoint-Requests-Limit/Remaining/Reset`,
`X-RateLimit-Endpoint-Name`. `*-Reset` values are UTC epoch **milliseconds**.

---

## 3. Team

### `teamCreate`
```
Mutation field:  teamCreate(copySettingsFromTeamId: String, input: TeamCreateInput!): TeamPayload
```
"Creates a new team. The user who creates the team will automatically be added as a member and
owner of the newly created team. Default workflow states, labels, and other team resources are
created alongside the team."

`TeamCreateInput` (all optional except `name`):
```
autoArchivePeriod?: Float          autoClosePeriod?: Float
autoCloseStateId?: String          color?: String
cycleCooldownTime?: Int            cycleDuration?: Int
cycleIssueAutoAssignCompleted?: Boolean
cycleIssueAutoAssignStarted?: Boolean
cycleLockToActive?: Boolean        cycleStartDay?: Float
cyclesEnabled?: Boolean            defaultIssueEstimate?: Float
defaultProjectTemplateId?: String  defaultTemplateForMembersId?: String
defaultTemplateForNonMembersId?: String
description?: String               groupIssueHistory?: Boolean
icon?: String                      id?: String (UUID; server-generated if omitted)
inheritIssueEstimation?: Boolean   inheritProductIntelligenceScope?: Boolean [Internal]
inheritProjectStatuses?: Boolean [Internal]
inheritSlackAutoCreateProjectChannel?: Boolean [Internal]
inheritWorkflowStatuses?: Boolean [Internal]
initiativesEnabled?: Boolean       issueEstimationAllowZero?: Boolean
issueEstimationExtended?: Boolean
issueEstimationType?: String       (one of "notUsed","exponential","fibonacci","linear","tShirt")
issueSharingEnabled?: Boolean      key?: String (auto-generated from name if omitted)
name: String                       parentId?: String
private?: Boolean [Internal]       productIntelligenceScope?: ProductIntelligenceScope [Internal]
requirePriorityToLeaveTriage?: Boolean
setIssueSortOrderOnStateChange?: String
slackAutoCreateProjectChannel?: Boolean [Internal]
timezone?: String                  triageEnabled?: Boolean
upcomingCycleCount?: Float
```
Payload `TeamPayload`: `{ lastSyncId: Float, success: Boolean, team?: Team }`

### `teamUpdate`
```
teamUpdate(id: String!, input: TeamUpdateInput!, mapping?: InheritanceEntityMapping): TeamPayload
```
`TeamUpdateInput` — same shape as create input plus: `aiDiscussionSummariesEnabled?: Boolean`,
`aiThreadSummariesEnabled?: Boolean`, `allMembersCanJoin?: Boolean`, `autoCloseChildIssues?:
Boolean`, `autoCloseParentIssues?: Boolean`, `cycleEnabledStartDate?: DateTime`,
`defaultIssueStateId?: String`, `handleSubTeamsOnRetirement?: TeamRetirementSubTeamHandling`,
`joinByDefault?: Boolean`, `retiredAt?: DateTime`, `scimGroupName?: String`, `scimManaged?:
Boolean`, `securitySettings?: TeamSecuritySettingsInput`, `slackIssueComments/Statuses/NewIssue?:
Boolean`. All fields optional (including `name`). Returns `TeamPayload`.

`InheritanceEntityMapping` (used for cascading label/state renames when re-parenting a team):
```
type InheritanceEntityMapping = {
  issueLabels?: InputMaybe<JSONObject>
  projectLabels?: InputMaybe<JSONObject>
  projectStatuses?: InputMaybe<JSONObject>   // [Internal]
  workflowStates: JSONObject                  // required
}
```

### `teamDelete`
```
teamDelete(id: String!): DeletePayload
```
Doc string (verbatim): "Archives a team and schedules its data for deletion. Requires team owner
or workspace admin permissions." `DeletePayload = { entityId: String, lastSyncId: Float, success:
Boolean }`.

**Deleting a team that still has issues**: the schema does **not** require emptying the team
first — `teamDelete` archives the team and schedules a cascading async deletion of its data
(issues included). It can be reversed with `teamUnarchive(id): TeamArchivePayload` ("Unarchives a
team and cancels deletion") before the grace period elapses. The exact grace-period duration is
**NOT FOUND** in the schema (support-article territory, not GraphQL-visible). If you need issues
preserved, move them to another team first via `issueUpdate(teamId: ...)` /
`issueBatchUpdate` before calling `teamDelete`.

Related team mutations found in schema (for completeness): `teamCyclesDelete(id): TeamPayload`
(wipes all cycle data), `teamKeyDelete(id): DeletePayload` (deletes a *retired* team key; the
active key can't be deleted this way), `teamMembershipDelete(id): DeletePayload`,
`teamMembershipUpdate`, `teamUnarchive(id): TeamArchivePayload`.

### `teamMembershipCreate`
```
teamMembershipCreate(input: TeamMembershipCreateInput!): TeamMembershipPayload
```
"Creates a new team membership, adding a user to a team. Validates that the user is not already a
member, the team is not archived or retired, and the requesting user has permission to add
members."
```
TeamMembershipCreateInput = {
  id?: String
  owner?: Boolean          // [Internal]
  sortOrder?: Float
  teamId: String            // required
  userId: String             // required
}
```
Payload: `{ lastSyncId: Float, success: Boolean, teamMembership?: TeamMembership }`

---

## 4. Workflow states

### `workflowStateCreate`
```
workflowStateCreate(input: WorkflowStateCreateInput!): WorkflowStatePayload
```
```
WorkflowStateCreateInput = {
  color: String                              // required
  description?: String
  id?: String
  name: String                                // required
  position?: Float
  teamId: String                               // required
  type: String                                  // required; one of
                                                  // "backlog","unstarted","started","completed","canceled"
                                                  // (note: "triage" and "duplicate" also appear as
                                                  //  read-only state types elsewhere in the schema,
                                                  //  but this create-input doc comment only lists the 5 above)
}
```
Payload: `{ lastSyncId: Float, success: Boolean, workflowState: WorkflowState }` (non-nullable
`workflowState`).

### `workflowStateUpdate`
```
workflowStateUpdate(id: String!, input: WorkflowStateUpdateInput!): WorkflowStatePayload
```
```
WorkflowStateUpdateInput = {
  color?: String
  description?: String
  name?: String
  position?: Float
}
```
Note: `type` and `teamId` are **not updatable** after creation.

### `workflowStateArchive`
```
workflowStateArchive(id: String!): WorkflowStateArchivePayload
```
"Archives a state. Only states with issues that have all been archived can be archived." —
i.e. you must archive/move all issues out of a state before archiving the state itself.
`WorkflowStateArchivePayload = ArchivePayload & { entity?: Maybe<WorkflowState>, lastSyncId:
Float, success: Boolean }`.

`WorkflowState` type (query shape): `id, name, color, description?, position, type: String
("triage"|"backlog"|"unstarted"|"started"|"completed"|"canceled"|"duplicate" per the type field's
own doc comment), team: Team, inheritedFrom?: WorkflowState, issues: IssueConnection, createdAt,
updatedAt, archivedAt?`.

---

## 5. Issue labels / project labels

### `issueLabelCreate` / `issueLabelUpdate` / `issueLabelDelete`
```
issueLabelCreate(input: IssueLabelCreateInput!, replaceTeamLabels?: Boolean): IssueLabelPayload
issueLabelUpdate(id: String!, input: IssueLabelUpdateInput!, replaceTeamLabels?: Boolean): IssueLabelPayload
issueLabelDelete(id: String!): DeletePayload
```
```
IssueLabelCreateInput = {
  color?: String
  description?: String
  id?: String
  isGroup?: Boolean
  name: String                 // required
  parentId?: String
  retiredAt?: DateTime          // set null to restore a retired label
  teamId?: String               // omit = workspace-level label
}
IssueLabelUpdateInput = {
  color?: String  description?: String  isGroup?: Boolean
  name?: String  parentId?: String  retiredAt?: DateTime
}
```
Payload: `{ issueLabel: IssueLabel, lastSyncId: Float, success: Boolean }`.

### `projectLabelCreate` (exists — separate label namespace for projects)
```
projectLabelCreate(input: ProjectLabelCreateInput!, replaceTeamLabels?: Boolean): ProjectLabelPayload
```
```
ProjectLabelCreateInput = {
  color?: String  description?: String  id?: String  isGroup?: Boolean
  name: String                          // required
  parentId?: String  retiredAt?: DateTime
  teamId?: String                        // [Internal]
}
```
Payload: `{ lastSyncId: Float, projectLabel: ProjectLabel, success: Boolean }`. There is also
`projectLabelUpdate(id, input: ProjectLabelUpdateInput): ProjectLabelPayload` (not expanded here,
mirrors `IssueLabelUpdateInput` shape) and no `projectLabelDelete` was found in the searched
mutation list (**NOT FOUND** — only create/update confirmed).

---

## 6. Templates

### `templateCreate` / `templateUpdate` / `templateDelete`
```
templateCreate(input: TemplateCreateInput!): TemplatePayload
templateUpdate(id: String!, input: TemplateUpdateInput!): TemplatePayload
templateDelete(id: String!): DeletePayload
```
```
TemplateCreateInput = {
  color?: String
  description?: String
  icon?: String
  id?: String
  name: String                    // required
  pipelineId?: String              // required IF type == "releaseNote", forbidden otherwise
  sortOrder?: Float
  teamId?: String                  // omit = shared across all teams
  templateData: JSON               // required, opaque JSON scalar (see below)
  type: String                     // required, e.g. "issue" | "project" | "document"
}
TemplateUpdateInput = {
  color?: String  description?: String  icon?: String  name?: String
  sortOrder?: Float  teamId?: String  templateData?: JSON
}
```
Payload: `{ lastSyncId: Float, success: Boolean, template: Template }`.

**`templateData` structure**: the GraphQL schema types it only as an opaque `JSON` scalar — "The
template data as a JSON-encoded string containing the pre-filled attributes for the entity type
(e.g., issue fields, project configuration, or document content)." **The schema does not expose a
typed shape for it.** In practice (per Linear's app behavior, not the schema) it mirrors the
corresponding `*CreateInput` field names for the entity `type`:
- `type: "issue"` → JSON object with issue-like keys (`title`, `description`, `priority`,
  `estimate`, `labelIds`, `assigneeId`, `stateId`, etc. — subset of `IssueCreateInput`).
  Wrapped by the SDK/app as `{ variant, ... }` in places; **exact key list is NOT FOUND in the
  schema** — reverse-engineer by reading `templateData` off an existing template via the
  `template(id)` query before writing new ones.
- `type: "project"` → subset of `ProjectCreateInput` fields.
- `type: "document"` → subset of `DocumentCreateInput` fields (title/content).
Because this is unenforced JSON, the safest rebuild strategy is: query existing templates'
`templateData` first (`template { templateData }`), and reuse that exact JSON shape rather than
constructing it from the input-type field lists.

`Template` type (query shape): `id, name, description?, color?, icon?, type: String, templateData:
JSON, sortOrder: Float, team?: Team (null = workspace-level), pipeline?: ReleasePipeline,
creator?: User, lastUpdatedBy?: User, inheritedFrom?: Template, hasFormFields: Boolean,
lastAppliedAt?: DateTime, createdAt, updatedAt, archivedAt?`.

Query: `templates: Array<Template>` — **not paginated**, returns every template (team-scoped +
workspace-level) in one call. Also `template(id: String!): Template`.

---

## 7. Projects

### `projectCreate`
```
projectCreate(aiConversationId?: String, input: ProjectCreateInput!, projectDraftId?: String, slackChannelName?: String): ProjectPayload
```
```
ProjectCreateInput = {
  color?: String  content?: String (markdown)  convertedFromIssueId?: String
  description?: String  icon?: String  id?: String
  labelIds?: Array<String>  lastAppliedTemplateId?: String
  leadId?: String  leadTeamId?: String [Internal]  memberIds?: Array<String>
  name: String                          // required
  priority?: Int (0=None,1=Urgent,2=High,3=Medium,4=Low)
  prioritySortOrder?: Float  sortOrder?: Float
  startDate?: TimelessDate  startDateResolution?: DateResolutionType
  statusId?: String  targetDate?: TimelessDate  targetDateResolution?: DateResolutionType
  teamIds: Array<String>                // required
  templateId?: String                   // overrides useDefaultTemplate if both given
  useDefaultTemplate?: Boolean
}
```
Payload: `{ lastSyncId: Float, project?: Project, success: Boolean }`.

### `projectUpdate`
```
projectUpdate(id: String!, input: ProjectUpdateInput!): ProjectPayload
```
`ProjectUpdateInput` — same optional fields as create, minus `teamIds` required, plus:
`canceledAt?/completedAt?: DateTime`, `frequencyResolution?: FrequencyResolutionType`,
`projectUpdateRemindersPausedUntilAt?: DateTime`, `slackIssueComments/Statuses/NewIssue?:
Boolean`, `trashed?: Boolean` (true=trash, null=restore), `updateReminderFrequency?/
updateReminderFrequencyInWeeks?: Float`, `updateRemindersDay?: Day`, `updateRemindersHour?: Int`.

### `projectArchive` (deprecated) / `projectDelete`
```
projectArchive(id: String!, trash?: Boolean): ProjectArchivePayload   // @deprecated in favor of projectDelete
projectDelete(id: String!): ProjectArchivePayload
```
Doc string for `projectDelete`: "Deletes (trashes) a project. The project can be restored later
with `projectUnarchive`." `ProjectArchivePayload = ArchivePayload & { entity?: Maybe<Project>,
lastSyncId: Float, success: Boolean }`. Restore via `projectUnarchive(id): ProjectArchivePayload`.

### Project statuses (query only — no `projectStatusCreate` mutation was found)
```
Query: projectStatuses: ProjectStatusConnection   // "Returns all project statuses in the workspace."
Query: projectStatusProjectCount: ProjectStatusCountPayload
```
`ProjectStatus` type: `id, name, description?, color, position: Float, indefinite: Boolean, team?:
Team (null=workspace-level), inheritedFrom?: ProjectStatus, type: ProjectStatusType, createdAt,
updatedAt, archivedAt?`.
`ProjectStatusType` enum: `Backlog="backlog" | Canceled="canceled" | Completed="completed" |
Paused="paused" | Planned="planned" | Started="started"`.
No `projectStatusCreate`/`Update`/`Delete` mutations were found in the extracted Mutation-root
field list — **project statuses appear to be workspace-managed, not creatable via this API
surface** (mark as NOT FOUND / likely UI-only).

### `projectMilestoneCreate`
```
projectMilestoneCreate(input: ProjectMilestoneCreateInput!): ProjectMilestonePayload
```
```
ProjectMilestoneCreateInput = {
  description?: String (markdown)
  descriptionData?: JSONObject     // [Internal] Prosemirror doc
  id?: String
  name: String                      // required
  projectId: String                  // required
  sortOrder?: Float
  targetDate?: TimelessDate
}
```
Payload: `{ lastSyncId: Float, projectMilestone: ProjectMilestone, success: Boolean }`.

### `projectUpdateCreate` (project status-update posts, not `projectUpdate` the mutation)
```
projectUpdateCreate(input: ProjectUpdateCreateInput!): ProjectUpdatePayload
```
```
ProjectUpdateCreateInput = {
  body?: String (markdown)
  bodyData?: JSON                 // [Internal] Prosemirror doc
  health?: ProjectUpdateHealthType   // "atRisk" | "offTrack" | "onTrack"
  id?: String
  isDiffHidden?: Boolean
  projectId: String                  // required
}
```
Payload: `{ lastSyncId: Float, projectUpdate: ProjectUpdate, success: Boolean }`.

---

## 8. Initiatives

### `initiativeCreate` / `initiativeUpdate` / `initiativeArchive` / `initiativeDelete`
```
initiativeCreate(input: InitiativeCreateInput!): InitiativePayload
initiativeUpdate(id: String!, input: InitiativeUpdateInput!): InitiativePayload
initiativeArchive(id: String!): InitiativeArchivePayload
initiativeDelete(id: String!): DeletePayload           // "Deletes (trashes) an initiative."
```
```
InitiativeCreateInput = {
  color?: String  content?: String (markdown)  description?: String  icon?: String  id?: String
  labelIds?: Array<String>  leadTeamId?: String
  name: String                       // required
  ownerId?: String
  priority?: Int (0-4, same scale as project)  prioritySortOrder?: Float  sortOrder?: Float
  status?: InitiativeStatus            // "Active"|"Canceled"|"Completed"|"Planned"|"Proposed"
  targetDate?: TimelessDate  targetDateResolution?: DateResolutionType
}
InitiativeUpdateInput = same fields, all optional, plus:
  customIdentifier?: String [Internal]  frequencyResolution?: FrequencyResolutionType
  trashed?: Boolean  updateReminderFrequency?/InWeeks?: Float
  updateRemindersDay?: Day  updateRemindersHour?: Int
```
`InitiativeArchivePayload = ArchivePayload & { entity?: Maybe<Initiative>, lastSyncId: Float,
success: Boolean }`. `InitiativePayload = { initiative: Initiative, lastSyncId: Float, success:
Boolean }`.

### `initiativeToProjectCreate`
```
initiativeToProjectCreate(input: InitiativeToProjectCreateInput!): InitiativeToProjectPayload
```
"Associates a project with an initiative. A project can only appear once in an initiative
hierarchy."
```
InitiativeToProjectCreateInput = {
  id?: String
  initiativeId: String    // required
  projectId: String        // required
  sortOrder?: Float
}
```
Payload: `{ initiativeToProject: InitiativeToProject, lastSyncId: Float, success: Boolean }`.
Also: `initiativeToProjectDelete(id): DeletePayload`, `initiativeToProjectUpdate(id, input)`.

### `initiativeUpdateCreate` (initiative status updates — exists)
```
initiativeUpdateCreate(input: InitiativeUpdateCreateInput!): InitiativeUpdatePayload
```
```
InitiativeUpdateCreateInput = {
  body?: String (markdown)
  bodyData?: JSON               // [Internal]
  health?: InitiativeUpdateHealthType    // "atRisk"|"offTrack"|"onTrack"
  id?: String
  initiativeId: String            // required
  isDiffHidden?: Boolean
}
```
Payload: `{ initiativeUpdate: InitiativeUpdate, lastSyncId: Float, success: Boolean }`. Also
`initiativeUpdateArchive(id): InitiativeUpdateArchivePayload`.

---

## 9. Cycles

### `cycleCreate`
```
cycleCreate(input: CycleCreateInput!): CyclePayload
```
```
CycleCreateInput = {
  completedAt?: DateTime
  description?: String
  endsAt: DateTime      // required
  id?: String
  name?: String
  startsAt: DateTime     // required
  teamId: String          // required
}
```
Payload: `{ cycle?: Cycle, lastSyncId: Float, success: Boolean }`. Also `cycleArchive(id):
CycleArchivePayload`, `cycleUpdate(id, input)`, `teamCyclesDelete(id): TeamPayload` (wipes all
cycles for a team at once).

---

## 10. Documents

### `documentCreate`
```
documentCreate(input: DocumentCreateInput!): DocumentPayload
```
```
DocumentCreateInput = {
  color?: String  content?: String (markdown)
  cycleId?: String [Internal]  icon?: String  id?: String
  initiativeId?: String [Internal]
  issueId?: String                    // accepts UUID or identifier like "LIN-123"
  lastAppliedTemplateId?: String
  ownerId?: String                     // null = no owner
  projectId?: String  releaseId?: String
  resourceFolderId?: String [Internal]  sortOrder?: Float
  subscriberIds?: Array<String> [Internal]
  teamId?: String [Internal]
  title: String                        // required
}
```
Payload: `{ document: Document, lastSyncId: Float, success: Boolean }` (non-nullable `document`).
A document attaches to exactly one parent entity (issue/project/initiative/team/cycle/release).

---

## 11. Issues

### `issueCreate`
```
issueCreate(input: IssueCreateInput!): IssuePayload
```
```
IssueCreateInput = {
  assigneeId?: String
  completedAt?: DateTime           // must be in the past, after createdAt
  createAsUser?: String             // OAuth actor=app only — display name override
  createdAt?: DateTime              // backfill timestamp
  cycleId?: String
  delegateId?: String               // "The identifier of the agent user to delegate the issue to."
  description?: String (markdown)   descriptionData?: JSON [Internal]
  displayIconUrl?: String            // pairs with createAsUser, actor=app only
  dueDate?: TimelessDate
  estimate?: Int
  id?: String
  inheritsSharedAccess?: Boolean [Internal]
  labelIds?: Array<String>
  lastAppliedTemplateId?: String
  parentId?: String                  // UUID or "LIN-123"
  preserveSortOrderOnCreate?: Boolean
  priority?: Int (0=None,1=Urgent,2=High,3=Medium,4=Low)
  prioritySortOrder?: Float
  projectId?: String
  projectMilestoneId?: String
  referenceCommentId?: String
  releaseIds?: Array<String>
  slaBreachesAt?: DateTime [Internal]
  slaStartedAt?: DateTime [Internal]
  slaType?: SLADayCountType           // "all" | "onlyBusinessDays"
  sortOrder?: Float
  sourceCommentId?: String
  sourcePullRequestCommentId?: String [Internal]
  stateId?: String
  subIssueSortOrder?: Float
  subscriberIds?: Array<String>
  teamId: String                       // required
  templateId?: String                   // template values act as defaults, explicit input overrides
  title?: String                        // NOTE: optional in the schema (template can supply it)
  useDefaultTemplate?: Boolean
}
```
Payload: `IssuePayload = { issue?: Maybe<Issue>, lastSyncId: Float, success: Boolean }`.

There is **no separate `delegate` argument outside the input** — delegation to an agent is done
purely via `delegateId` in `IssueCreateInput`/`IssueUpdateInput`. On the `Issue` type itself the
field is `delegate?: Maybe<User>` — "The agent user that is delegated to work on this issue. Set
when an AI agent has been assigned to perform work on this issue." This is a **separate field from
`assignee`** — an issue can have both a human `assignee` and an agent `delegate` simultaneously
(per the Agent Interaction Guidelines: agents should set themselves as `delegate`, and leave
`assignee` for humans unless explicitly assigned).

### `issueBatchCreate`
```
issueBatchCreate(input: IssueBatchCreateInput!): IssueBatchPayload
```
```
IssueBatchCreateInput = { issues: Array<IssueCreateInput> }   // "Creates a list of issues atomically."
```
Payload: `{ issues: Array<Issue>, lastSyncId: Float, success: Boolean }`.

### `issueUpdate`
```
issueUpdate(id: String!, input: IssueUpdateInput!): IssuePayload
```
`IssueUpdateInput` — same optional superset as create input, minus `createAsUser`/
`displayIconUrl`/`createdAt`/`useDefaultTemplate`/`referenceCommentId`/`sourceCommentId`/
`sourcePullRequestCommentId`, plus: `addedLabelIds?/removedLabelIds?: Array<String>`,
`addedReleaseIds?/removedReleaseIds?: Array<String>`, `autoClosedByParentClosing?: Boolean`,
`snoozedById?: String`, `snoozedUntilAt?: DateTime`, `trashed?: Boolean`, `trusted?: Boolean
[Internal]`. `delegateId?: String` present here too, same semantics.

### `issueArchive` / `issueDelete`
```
issueArchive(id: String!, trash?: Boolean): IssueArchivePayload
issueDelete(id: String!, permanentlyDelete?: Boolean): IssueArchivePayload   // "Deletes (trashes) an issue."
```
`IssueArchivePayload = ArchivePayload & { entity?: Maybe<Issue>, lastSyncId: Float, success:
Boolean }`.

### `issueBatchUpdate`
```
issueBatchUpdate(ids: Array<UUID>!, input: IssueUpdateInput!): IssueBatchPayload
```
**There is no separate `IssueBatchUpdateInput` type** — `issueBatchUpdate` reuses
`IssueUpdateInput` applied identically to every ID in `ids` (an array of UUIDs, not
identifier-strings like "LIN-123" — unlike single-issue mutations). Payload: `{ issues:
Array<Issue>, lastSyncId: Float, success: Boolean }`.

---

## 12. Comments

### `commentCreate`
```
commentCreate(input: CommentCreateInput!): CommentPayload
```
```
CommentCreateInput = {
  body?: String (markdown)
  bodyData?: JSON [Internal]              // Prosemirror doc; mutually exclusive with body in practice
  createAsUser?: String                    // actor=app only
  createOnSyncedSlackThread?: Boolean       // fails if no synced Slack thread exists
  createdAt?: DateTime
  displayIconUrl?: String
  doNotSubscribeToIssue?: Boolean
  documentContentId?: String
  id?: String
  initiativeId?: String  initiativeUpdateId?: String
  issueId?: String                          // UUID or "LIN-123"
  parentId?: String                         // parent comment, for threaded replies
  postId?: String
  projectId?: String  projectUpdateId?: String
  quotedText?: String                        // inline-comment anchor text
  subscriberIds?: Array<String> [Internal]
}
```
A comment attaches to exactly one of `issueId`/`projectId`/`projectUpdateId`/`initiativeId`/
`initiativeUpdateId`/`documentContentId`/`postId`. Payload: `{ comment: Comment, lastSyncId:
Float, success: Boolean }`.

---

## 13. Issue relations

### `issueRelationCreate`
```
issueRelationCreate(input: IssueRelationCreateInput!, overrideCreatedAt?: DateTime): IssueRelationPayload
```
```
IssueRelationCreateInput = {
  id?: String
  issueId: String            // required, UUID or "LIN-123"
  relatedIssueId: String      // required
  type: IssueRelationType      // required
}
```
`IssueRelationType` enum — **exactly 4 values**: `Blocks = "blocks"`, `Duplicate = "duplicate"`,
`Related = "related"`, `Similar = "similar"`. There is no separate "blockedBy" type value — that
direction is expressed by creating a `blocks` relation with `issueId`/`relatedIssueId` swapped.
Payload: `{ issueRelation: IssueRelation, lastSyncId: Float, success: Boolean }`.

---

## 14. Attachments

### `attachmentCreate`
```
attachmentCreate(input: AttachmentCreateInput!): AttachmentPayload
```
"Creates a new attachment, or updates existing if the same `url` and `issueId` is used. To create
an integration-aware attachment, use the integration-specific mutations such as
`attachmentLinkZendesk`, `attachmentLinkSlack`, or `attachmentLinkURL` instead."
```
AttachmentCreateInput = {
  commentBody?: String (markdown)          commentBodyData?: JSONObject [Internal, prefer commentBody]
  createAsUser?: String                     // actor=application only
  displayIconUrl?: String
  groupBySource?: Boolean
  iconUrl?: String                           // jpg/png, max 1MB, ideally 20x20px
  id?: String
  issueId: String                             // required
  metadata?: JSONObject
  subtitle?: String
  title: String                                // required
  url: String                                   // required; re-using url+issueId upserts
}
```
Payload: `{ attachment: Attachment, lastSyncId: Float, success: Boolean }`.

### `attachmentLinkURL`
```
attachmentLinkURL(createAsUser: String, displayIconUrl: String, id: String, issueId: String!, title: String, url: String!): AttachmentPayload
```
**There is no `AttachmentLinkUrlInput` wrapper type** — `attachmentLinkURL` takes its arguments
directly (flat args on the mutation field, confirmed via `MutationAttachmentLinkUrlArgs`), unlike
almost every other mutation in this API. "Link any URL to an issue. If the workspace has a
matching integration configured and the URL is recognized (e.g., Zendesk, GitHub, Slack), a rich
attachment will be created that enables features like automated status updates. Otherwise, a
basic attachment is created." Payload: `AttachmentPayload` (same shape as above).

---

## 15. Customers / Customer requests

### `customerCreate` / `customerUpdate`
```
customerCreate(input: CustomerCreateInput!): CustomerPayload
customerUpdate(id: String!, input: CustomerUpdateInput!): CustomerPayload
```
```
CustomerCreateInput = {
  domains?: Array<String>          // no public email domains (gmail.com etc.), default []
  externalIds?: Array<String>       // default []
  id?: String
  logoUrl?: String
  mainSourceId?: String              // must be one of externalIds
  name: String                        // required
  ownerId?: String
  revenue?: Int
  size?: Int
  slackChannelId?: String
  statusId?: String
  tierId?: String
}
CustomerUpdateInput = same fields minus id/name-required — `name` becomes optional; domains/
externalIds are **replace-whole-array** semantics on update, not append (per doc comment: "The
updated list ... Replaces the existing domains.").
```
Payload: `{ customer: Customer, lastSyncId: Float, success: Boolean }` (non-nullable `customer`).
There is also `customerUnsync(...)` (unlinks from an integration) and a confirmed `customerUpsert`
mutation:
```
customerUpsert(input: CustomerUpsertInput!): CustomerPayload
```
"Upserts a customer, creating it if no match is found, or updating it otherwise. Matches against
existing customers using `id`, `externalId`, `slackChannelId`, or `domains`."
```
CustomerUpsertInput = {
  domains?: Array<String>
  externalId?: String            // singular (not externalIds) — used for upsert matching
  id?: String                     // matches an existing customer by id
  logoUrl?: String
  name?: String                    // required when creating a new customer
  ownerId?: String
  revenue?: Int  size?: Int
  slackChannelId?: String
  statusId?: String
  tierId?: String                   // mutually exclusive with tierName
  tierName?: String                  // creates a new tier by this name if it doesn't exist; mutually exclusive with tierId
}
```

### `customerNeedCreate` (customer requests)
```
customerNeedCreate(input: CustomerNeedCreateInput!): CustomerNeedPayload
```
```
CustomerNeedCreateInput = {
  attachmentId?: String              // existing attachment as source
  attachmentUrl?: String              // OR create a new attachment from this URL as source
  body?: String (markdown)             // mutually exclusive with bodyData
  bodyData?: JSON [Internal]
  commentId?: String                    // extra context comment
  createAsUser?: String                  // actor=app only
  createdAt?: DateTime
  customerExternalId?: String             // mutually exclusive with customerId
  customerId?: String
  displayIconUrl?: String
  id?: String
  issueId?: String                          // either issueId or projectId required
  priority?: Float                           // 0 = Not important, 1 = Important
  projectId?: String [Internal]
}
```
Payload: `CustomerNeedPayload = { lastSyncId: Float, need: CustomerNeed, success: Boolean }`. Also
`customerNeedArchive(id): CustomerNeedArchivePayload`.

### Customer status / tier (query + type shape; **no create/update/delete mutations found** for
either — likely workspace-settings-only, same situation as project statuses)
```
Query: customerStatus(id): CustomerStatus
Query: customerStatuses: CustomerStatusConnection
Query: customerTier(id): CustomerTier
Query: customerTiers: CustomerTierConnection
```
`CustomerStatus`: `id, name, displayName, description?, color, position: Float, type?:
CustomerStatusType [deprecated, always null], createdAt, updatedAt, archivedAt?`.
`CustomerTier`: `id, name, displayName, description?, color, position: Float, createdAt,
updatedAt, archivedAt?`.
`Customer` type (query shape): `id, name, domains: Array<String>, externalIds: Array<String>,
mainSourceId?, logoUrl?, revenue?: Int, size?: Float, slackChannelId?, slugId, url,
status: CustomerStatus (non-null!), tier?: CustomerTier, owner?: User, integration?: Integration,
needs: Array<CustomerNeed>, approximateNeedCount: Float, createdAt, updatedAt, archivedAt?`.

---

## 16. Webhooks

### `webhookCreate`
```
webhookCreate(input: WebhookCreateInput!): WebhookPayload
```
"Creates a new webhook subscription for the workspace. Requires specifying a URL, resource types
to subscribe to, and either a specific team or all public teams."
```
WebhookCreateInput = {
  allPublicTeams?: Boolean
  enabled?: Boolean
  id?: String
  label?: String
  resourceTypes: Array<String>      // required; values below
  secret?: String                    // signs the payload
  teamId?: String                     // team scope; use allPublicTeams for org-wide public-team scope
  url: String                          // required
}
```
`WebhookResourceType` enum (valid string values for `resourceTypes`) — 22 values: `AgentSessionEvent
="AgentSessionEvent"`, `AppUserNotification="AppUserNotification"`, `Attachment="Attachment"`,
`Comment="Comment"`, `Customer="Customer"`, `CustomerNeed="CustomerNeed"`, `Cycle="Cycle"`,
`Document="Document"`, `Initiative="Initiative"`, `InitiativeUpdate="InitiativeUpdate"`,
`Issue="Issue"`, `IssueLabel="IssueLabel"`, `IssueSla="IssueSLA"`, `OAuthAuthorization=
"OAuthAuthorization"`, `PermissionChange="PermissionChange"`, `Project="Project"`,
`ProjectLabel="ProjectLabel"`, `ProjectUpdate="ProjectUpdate"`, `Reaction="Reaction"`,
`Release="Release"`, `ReleaseNote="ReleaseNote"`, `User="User"`.
Payload: `{ lastSyncId: Float, success: Boolean, webhook: Webhook }`.

---

## 17. Organization / plan

`Organization` fields relevant to plan/subscription:
```
id, name, urlKey
subscription?: Maybe<PaidSubscription>
trialStartsAt?: DateTime, trialEndsAt?: DateTime
codingAgentEnabled: Boolean [Internal]     // Coding Sessions feature flag
linearAgentEnabled: Boolean [Internal]     // Linear Agent feature flag
customerCount: Int, customersConfiguration: JSONObject
restrictTeamCreationToAdmins?: Boolean
roadmapEnabled, slackProjectChannelsEnabled, pullRequestTourEnabled, hipaaEnabled-ish field
  (HIPAA compliance flag), releaseChannel, themeSettings, hideNonPrimaryOrganizations, ... (many
  more workspace-settings booleans, not all copied here — see Organization type for full list)
```
`PaidSubscription`: `id, type: String (plan tier e.g. basic/business/enterprise), seats: Float,
seatsMinimum?/seatsMaximum?: Float, collectionMethod: String ("automatic"|"send_invoice"),
pendingChangeType?: String, cancelAt?/canceledAt?: DateTime, nextBillingAt?: DateTime, creator?:
User, organization: Organization, createdAt, updatedAt, archivedAt?`.

Query: `organization: Organization` — "The authenticated user's workspace." No `id` arg; always
resolves to the workspace the API key/token belongs to.

---

## 18. Users / app users / agents

`User` type fields relevant to distinguishing human vs. app/agent identity:
```
active: Boolean            // account active vs suspended
admin: Boolean              // workspace admin (Free plan: everyone is treated as admin)
app: Boolean                  // "Whether the user is an app." — TRUE for OAuth-app / agent identities
guest: Boolean                 // limited to a subset of teams
isMe: Boolean                    // is this the authenticated caller
isAssignable: Boolean              // human users always true; app users only if scope app:assignable
                                      // (+ Linear Agent additionally needs coding sessions enabled)
isMentionable: Boolean
owner: Boolean                       // highest permission level
canAccessAnyPublicTeam: Boolean
supportsAgentSessions: Boolean         // whether this (agent) user supports Agent Sessions
delegatedIssues: IssueConnection        // issues where this user is the `delegate`
assignedIssues / createdIssues: IssueConnection
```
**`service` is NOT a field on `User`** in this schema (searched exhaustively — not found). If you
recall a `service` boolean from older docs/other tools, it does not exist in v92 of the schema;
use `app` to detect non-human/agent users instead. There is likewise no separate
`isAgent`/`isBot` field — "agent" is not a distinct type, just a `User` with `app: true` (and
usually `supportsAgentSessions: true`).

Agents are provisioned by installing an OAuth application with `actor=app` on the authorization
URL (deprecated alias: `actor=application`) — this switches the resulting token to act as the app
installation itself rather than the installing human. Requires workspace admin permission to
install. Optional extra capabilities need explicit OAuth scopes: `app:assignable` (can be set as
`assigneeId`) and `app:mentionable`. Every workspace install gets its own unique `User.id` for
that app (same app installed in N workspaces = N different `User` records).

`createAsUser` / `displayIconUrl` (seen on `IssueCreateInput`, `CommentCreateInput`,
`AttachmentCreateInput`, `CustomerNeedCreateInput`, `attachmentLinkURL` args): lets an
`actor=app` OAuth token render an action as `"<createAsUser> (via <AppName>)"` in the UI instead
of the generic app identity — for representing an external, non-Linear user (e.g. a customer who
emailed support) as the visible author.

Queries: `user(id): User`, `users: UserConnection` ("All users in the workspace. Supports
filtering, sorting, and pagination.").

---

## 19. `delegate` field (Issue)

```
Issue.delegate?: Maybe<User>
```
Doc string (verbatim): "The agent user that is delegated to work on this issue. Set when an AI
agent has been assigned to perform work on this issue. Null if no agent is working on the issue."
Set via `delegateId` on `issueCreate`/`issueUpdate`. This is orthogonal to `assignee` — per
Linear's own Agent Interaction Guidelines, an agent that starts work unprompted should set
itself as `delegate` (not touch `assignee`); when a human explicitly delegates to an agent via
Linear's UI, both `delegate` (agent) and often `assignee` can be set, with assignment/triage
left to a human per the guidelines.

---

## 20. Agent Sessions & Agent Activities

Agent Sessions are the unit of "an agent doing work on an issue/comment thread." They are created
automatically when an agent user is `@mentioned` or set as `delegate`, or explicitly via mutation.

### Mutations
```
agentSessionCreate(input: AgentSessionCreateInput!, pullRequestId?: String): AgentSessionPayload
  // [Internal] "Creates a new agent session on behalf of the current user"
agentSessionCreateOnIssue(input: AgentSessionCreateOnIssue!): AgentSessionPayload
agentSessionCreateOnComment(input: AgentSessionCreateOnComment!): AgentSessionPayload
agentSessionUpdate(id: String!, input: AgentSessionUpdateInput!): AgentSessionPayload
agentSessionUpdateExternalUrl(...): AgentSessionPayload   // dedicated helper for the externalUrl field
agentActivityCreate(input: AgentActivityCreateInput!): AgentActivityPayload
agentActivitySendQueued: AgentActivityPayload    // flushes queued activities; args not extracted
```
```
AgentSessionCreateOnIssue = {
  externalLink?: String
  externalUrls?: Array<AgentSessionExternalUrlInput>
  issueId: String        // required, UUID or "LIN-123"
}
AgentSessionCreateOnComment = {
  commentId: String        // required — the root comment to attach the session to
  externalLink?: String
  externalUrls?: Array<AgentSessionExternalUrlInput>
}
AgentSessionExternalUrlInput = { label: String, url: String }   // both required
AgentSessionCreateInput = {
  appUserId: String            // required — the agent (app) user to create the session for
  context?: JSONObject          // [Internal] "No longer supported."
  id?: String
  issueId?: String               // UUID or "LIN-123"
}
AgentSessionUpdateInput = {
  addedExternalUrls?: Array<AgentSessionExternalUrlInput>
  dismissedAt?: DateTime                    // [Internal] null = un-dismiss
  externalLink?: String                       // @deprecated, use externalUrls
  externalUrls?: Array<AgentSessionExternalUrlInput>   // full replace; if set, added/removed* ignored
  removedExternalUrls?: Array<String>          // plain URL strings, NOT {label,url} objects
  plan?: JSONObject                            // "A dynamically updated list of the agent's execution strategy"
}
AgentActivityCreateInput = {
  agentSessionId: String     // required
  content: JSONObject         // required, untyped — see union shapes below
  contextualMetadata?: JSONObject [Internal]
  ephemeral?: Boolean           // only meaningful for "thought" and "action" types; default false
  id?: String
  signal?: AgentActivitySignal    // "auth" | "continue" | "select" | "stop"
  signalMetadata?: JSONObject
}
```
Payloads: `AgentSessionPayload = { agentSession: AgentSession, lastSyncId: Float, success: Boolean
}` (non-nullable). `AgentActivityPayload = { agentActivity: AgentActivity, lastSyncId: Float,
success: Boolean }`.

### `content` shapes for `agentActivityCreate` (the 6 concrete `AgentActivity*Content` types found
in the schema, keyed by `type: AgentActivityType`):
```
AgentActivityType enum: Action="action" | Elicitation="elicitation" | Error="error" |
                         Prompt="prompt" | Response="response" | Thought="thought"

AgentActivityThoughtContent      = { type, body: String (markdown), bodyData: JSONObject [Internal] }
AgentActivityActionContent       = { type, action: String, parameter: String,
                                      result?: String, resultData?: JSONObject [Internal] }
AgentActivityResponseContent     = { type, body: String, bodyData: JSONObject [Internal] }
AgentActivityErrorContent        = { type, body: String, bodyData: JSONObject [Internal],
                                      reasonCode?: String }
AgentActivityElicitationContent  = { type, body: String, bodyData: JSONObject [Internal] }
AgentActivityPromptContent       = { type, body: String, bodyData: JSONObject [Internal],
                                      title?: String }   // this is the *inbound* user-message shape,
                                                           // not something you normally create yourself
```
Only `thought` and `action` support `ephemeral: true` (per docs — disappears once the next
activity lands). `response`/`error`/`elicitation` are terminal/durable activity types per the
Agent Interaction Guidelines (use `response` for finished work, `elicitation` when you need more
input, `error` on failure).

### `AgentSession` type (query shape)
```
id, slugId, status: AgentSessionStatus, type?: AgentSessionType [deprecated], summary?: String,
appUser: User, creator?: User (null if triggered by automation/another agent),
issue?: Issue, comment?: Comment, sourceComment?: Comment,
context: JSON, sourceMetadata?: JSON, plan?: JSON,
externalLink?: String [deprecated], externalLinks: Array<AgentSessionExternalLink>,
externalUrls: JSON [deprecated],
startedAt?/endedAt?/dismissedAt?: DateTime, dismissedBy?: User,
activities: AgentActivityConnection,
pullRequest?: PullRequest, pullRequests: AgentSessionToPullRequestConnection,
url?: String, createdAt, updatedAt, archivedAt?
```
`AgentSessionStatus` enum — **6 values**: `Active="active"`, `AwaitingInput="awaitingInput"`,
`Complete="complete"`, `Error="error"`, `Pending="pending"`, `Stale="stale"`.

### AgentSessionEvent webhook (from `webhookCreate resourceTypes: ["AgentSessionEvent"]`)
Per docs: two `action` values — `created` (new session; agent **must respond within 10 seconds**
with e.g. a `thought` activity) and `prompted` (new user message; text is in
`agentActivity.body`). Payload includes `promptContext` (formatted context string),
`agentSession.issue`, `agentSession.comment`, `guidance`. Activities can continue for up to **30
minutes** before the session is considered stale (sending another activity recovers it).

---

## 21. Queries (root fields, exact)

```
team(id: String!): Team
teams: TeamConnection                    // "All teams whose issues the user can access" (public +
                                           // member-of-private teams; differs from administrableTeams)
administrableTeams: TeamConnection         // teams whose settings the user can change
teamMembership(id): TeamMembership
teamMemberships: TeamMembershipConnection

workflowState(id): WorkflowState
workflowStates: WorkflowStateConnection

issueLabel(id): IssueLabel
issueLabels: IssueLabelConnection          // workspace-level + team-scoped labels, paginated

template(id): Template
templates: Array<Template>                  // NOT a connection — no pagination

project(id): Project                          // "Returns a single project by its identifier or URL slug."
projects: ProjectConnection
projectStatuses: ProjectStatusConnection
projectStatusProjectCount: ProjectStatusCountPayload

initiative(id): Initiative
initiatives: InitiativeConnection
initiativeUpdates: InitiativeUpdateConnection

cycle(id): Cycle
cycles: CycleConnection

user(id): User
users: UserConnection

customer(id or slug): Customer
customers: CustomerConnection
customerStatus(id): CustomerStatus
customerStatuses: CustomerStatusConnection
customerTier(id): CustomerTier
customerTiers: CustomerTierConnection

organization: Organization                    // no id arg — resolves to caller's workspace
```
Args pattern for every `X: XConnection` field is `QueryXArgs = { after?, before?, first?, last?,
orderBy?, filter?, includeArchived? }` (verified concretely for `teams`; consistent naming
convention across the schema's other connection fields per the generated types file, though not
individually re-verified for every single query above — flag as "pattern-confirmed, not
per-field-triple-checked" if you need 100% certainty on an uncommon one).

---

## 22. Things confirmed NOT to exist / NOT FOUND

- `IssueBatchUpdateInput` — does not exist; `issueBatchUpdate` reuses `IssueUpdateInput` + `ids: Array<UUID>`.
- `AttachmentLinkUrlInput` — does not exist; `attachmentLinkURL` takes flat mutation args, not a wrapped input object.
- `User.service` — no such field in this schema version (v92). Use `User.app` for
  app/agent-identity detection.
- `projectStatusCreate` / `projectStatusUpdate` / `projectStatusDelete` — not found in the
  Mutation root field list extracted; project statuses look read-only via this API (workspace
  settings/UI-managed).
- `customerStatusCreate/Update/Delete`, `customerTierCreate/Update/Delete` — same: not found,
  likely workspace-settings/UI-managed only.
- `projectLabelDelete` — not found in the mutation list searched (only `projectLabelCreate`/`Update` confirmed).
- Exact grace-period length before `teamDelete`'s scheduled data deletion becomes irreversible —
  not exposed in the GraphQL schema (support-docs territory).
- Exact JSON key schema inside `Template.templateData` — the GraphQL schema only types it as an
  opaque `JSON` scalar; no typed shape exists to extract. Read existing templates first.

---

## Appendix: extraction method (for reproducibility)

```sh
mkdir -p /tmp/linear-sdk && cd /tmp/linear-sdk
npm init -y && npm i @linear/sdk@latest --no-audit --no-fund
# Package version installed: 92.0.0. No .graphql SDL ships in the package.
# Real type declarations live in (not the top-level index.d.mts, which just re-exports):
#   node_modules/@linear/sdk/dist/index-7gZbCe3y.d.mts
# Pattern used throughout:
grep -n "^type TeamCreateInput = {" node_modules/@linear/sdk/dist/index-7gZbCe3y.d.mts
# → then awk from that line to the matching closing "};"
# Root Mutation/Query field lists (with doc-comments) extracted the same way from:
grep -n "^type Mutation = {" ...   # line 12286
grep -n "^type Query = {" ...      # line 19912
```
