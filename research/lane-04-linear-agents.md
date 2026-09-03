# Lane 04 — Linear as the Agent Operating System (state as of 2026-09-02)

Research note for the "AI-based agency" feasibility study (Fightclub Agency). Question for this lane: what can an orchestrator build and automate in Linear via MCP, via the GraphQL API, and via an OAuth "agent app", and what stays UI-only or plan-gated.

Method: 15+ web searches, ~35 page fetches (Linear docs, developer docs, changelog, pricing; GitHub/OpenAI/Cursor/Sentry/Devin docs), plus a live, unauthenticated GraphQL schema introspection of `https://api.linear.app/graphql` run on 2026-09-02 to verify which mutations/queries/input fields actually exist. The Linear MCP server is configured in the host Claude Code session (`linear-server` -> `https://mcp.linear.app/mcp`) but its tools were not exposed to this subagent; a `tools/list` probe without a token returns 401, so the exact current tool names come from catalogues plus Linear's own changelog and should be re-confirmed with one `tools/list` call from the host session.

---

## 1. Executive summary

- Linear has a first-class **agents platform**: an agent is an OAuth app installed with `actor=app`, gets its own app-user identity, can be **@mentioned** (`app:mentionable`) and **delegated** issues (`app:assignable`), and communicates through **Agent Sessions** and **Agent Activities** (thought / action / elicitation / response / error). Sessions have six states (`pending, active, error, awaitingInput, complete, stale`). Webhook type `AgentSessionEvent` (`created`, `prompted`) is the entry point. Agents are **not billable seats**. Status: still labelled "Developer Preview".
- Delegation keeps a **human assignee** as owner; the agent is the `delegate`. `delegateId` exists on `IssueCreateInput`/`IssueUpdateInput`, so delegation can be set programmatically. `agentSessionCreate(issueId, appUserId, context)` and `agentSessionCreateOnIssue/OnComment` allow programmatic session creation.
- Linear's own **Linear Agent** (public beta 2026-03-24) now writes code via **Claude Code and Codex** in cloud "coding sessions" (2026-06-11; Basic+ plans; model list includes Claude Fable 5 / Opus 5 / Sonnet 5 / GPT-5.6 Sol), runs recurring/event-driven **Loops** (2026-07-20; Business+), does browser testing and env config (2026-08-20), and edits docs/project descriptions (2026-07-23). Coding sessions and Loops draw from prepaid **AI credits** (tokens at provider rates + $0.25 per 20-minute sandbox block; Loops ~$0.07–0.20/run).
- Native third-party agents in the directory (27 listed): Codex, Cursor, GitHub Copilot, Devin, Charlie, Sentry (Seer), Factory, ChatPRD, **Cyrus (Claude Code powered, open source, Apache-2.0, BYOK)**, Warp, Tembo, Blocks, etc. There is **no first-party Anthropic/Claude Code agent app** in the directory; Claude Code is reachable through Linear Agent coding sessions, through Cyrus, or via the Linear MCP server inside a Claude Code session.
- **Linear MCP server** (`https://mcp.linear.app/mcp`, Streamable HTTP, OAuth 2.1 with dynamic client registration, or an API key as Bearer token; `/mcp/readonly` variant): tools for issues, comments, projects, milestones, project updates, project labels, initiatives, initiative updates, documents, labels, statuses, cycles (read), teams (read), users (read), attachments, image extraction, docs search. **No MCP tools** for creating teams, workflow states, cycles, templates, customers/customer requests, webhooks, SLA rules, triage rules, Asks channels or Loops.
- **GraphQL API** (verified 2026-09-02: 360 mutations, 164 queries) covers workspace bootstrapping: `teamCreate`, `workflowStateCreate`, `issueLabelCreate`, `templateCreate`, `projectCreate`, `projectMilestoneCreate`, `projectUpdateCreate`, `initiativeCreate`, `initiativeUpdateCreate`, `documentCreate`, `customerCreate`, `customerTierCreate`, `customerNeedCreate`, `webhookCreate`, `customViewCreate`, `triageResponsibilityCreate`, `agentSkillCreate`, `issueBatchCreate`, plus SLA fields on issues (`slaBreachesAt`, `slaType`). **No API** for triage rules, SLA rules, Loops, or Asks web forms (`cycleCreate` does not exist either: cycles are generated from team cycle settings).
- **Plans**: Free ($0; 2 teams, 250 issues, 10 MB uploads) is too small for a multi-client agency demo. Basic ($10/user/mo yearly; 5 teams, unlimited issues, coding sessions). Business ($16/user/mo yearly) unlocks everything the "agency OS" needs: unlimited teams, private teams/sub-teams, guests, Triage Intelligence + triage rules (incl. auto-delegate to agents), SLAs, Linear Asks (Slack/email intake), Loops, Insights, Code Intelligence. Enterprise adds Asks web forms, per-channel private-channel config, SAML/SCIM, audit log, Okta-managed MCP auth.

---

## 2. Linear Agents platform (developer side)

Source: https://linear.app/developers/agents and https://linear.app/developers/agent-interaction (fetched 2026-09-02, undated pages), https://linear.app/developers/oauth-2-0-authentication.

### 2.1 Identity and installation
- An agent is an **OAuth2 application** installed with `actor=app`. "Resources are created as the application. This option should be used for agents and service accounts." A workspace admin must install it. `actor=app` cannot be combined with the `admin` scope.
- Each workspace assigns the app a unique app-user ID (`viewer { id }` with the app token).
- Scopes: `read` (always), `write`, `issues:create`, `comments:create`, `timeSchedule:write`, `admin`, plus agent scopes `app:mentionable` (mentions in issues, documents, editors) and `app:assignable` (delegation and project membership), plus `customer:read/write`, `initiative:read/write`.
- Access tokens last 24 h; refresh-token system migrated for all OAuth apps on **2026-04-01**. Client-credentials tokens last 30 days.
- **OAuth application manifests** (changelog 2026-06-18): pre-filled app creation via URL parameters or JSON manifest, so a platform can bootstrap an agent app configuration programmatically.
- Agents "are not counted as billable seats" (docs/agents-in-linear). Third-party agent vendors may charge separately.
- Admin controls: agents get access per team ("Team membership is set when the agent integration is added ... and can be changed by an admin at any time"); agents cannot sign in, access admin functions or manage users.
- **Agent guidance**: workspace-level and team-level instructions (Settings > Agents > Additional guidance) are injected into sessions (`guidance` field of the webhook payload); team guidance wins.

### 2.2 Session and activity model
- **AgentSession** states: `pending`, `active`, `error`, `awaitingInput`, `complete`, `stale`. "You don't need to manage agent session state manually. Linear tracks session lifecycle automatically based on the last emitted activity."
- **AgentActivity** content types: `thought` (body), `action` (action, parameter, optional result), `elicitation` (body; asks the human for input -> `awaitingInput`), `response` (body; -> `complete`), `error` (body). `prompt` is the user-generated type (read-only for agents; produces `prompted` webhooks). `thought` and `action` can be `ephemeral`.
- `AgentActivityCreateInput` fields (verified by introspection): `id, agentSessionId, signal, signalMetadata, contextualMetadata, content, ephemeral`.
- **Signals**: a user "stop" arrives as a `prompted` event with `agentActivity.signal: "stop"`; agents must check the signal before interpreting the body.
- **Agent plans** (technology preview): session-level checklist with steps `{content, status: pending|inProgress|completed|canceled}`, replaced wholesale on update.
- **External URLs**: `agentSessionUpdate` with `externalUrls` / `addedExternalUrls` / `removedExternalUrls` (label + url) — used to attach PR links, logs, dashboards.
- **Mutations** (introspection 2026-09-02): `agentActivityCreate`, `agentActivityCreatePrompt`, `agentActivitySendQueued`, `agentActivityDeleteQueued`, `agentSessionCreate` (input: `issueId, appUserId, context`), `agentSessionCreateOnIssue`, `agentSessionCreateOnComment`, `agentSessionRestartWithDefaultModel`, `agentSessionUpdate`, `agentSessionUpdateExternalUrl`, `agentSkillCreate/Update/Delete` (input: `teamId, title, body, icon, color`). Queries: `agentSessions`, `agentSession`, `agentActivities`, `agentActivity`, `agentSessionSandbox`, `agentSkills`, `agentSkill`, `issueRepositorySuggestions`.
- **Timing constraints**: webhook receiver must return within **5 seconds**; the agent must emit an activity (or update an external URL) within **10 seconds** of a `created` event or the session is marked unresponsive. Pattern: ack with an ephemeral `thought`, then work asynchronously.

### 2.3 Webhooks
Source: https://linear.app/developers/webhooks (undated).
- Data-change entity types: Issues, Issue attachments, Issue comments, Issue labels, Comment reactions, Projects, Project updates, Documents, Initiatives, Initiative updates, Cycles, Customers, Customer Requests, Users; plus Issue SLA, OAuthApp revoked; for agent apps: `AgentSessionEvent` (actions `created`, `prompted`) and `PermissionChange`.
- Payload: `action` (create/update/remove), `type`, `actor` (user / OAuth client / integration), `data`, `updatedFrom`, `url`, `webhookTimestamp`, `webhookId`, `organizationId`; headers `Linear-Delivery`, `Linear-Event`, `Linear-Signature` (HMAC-SHA256 over raw body), `Linear-Timestamp`.
- Retries at 1 min, 1 h, 6 h on non-200 or >5 s; persistently failing webhooks get disabled.
- Creation: UI (Settings > API), `webhookCreate` mutation (`url`, `teamId` or `allPublicTeams`, `resourceTypes`, `secret`, `label`, `enabled`), or automatically per organization for OAuth apps.

### 2.4 Build kits
- Official demo `linear/linear-agent-demo` (Cloudflare Workers + OpenAI) — **archived 2025-10-10**, still illustrates `actor=app` OAuth + webhook handling.
- **Vercel Chat SDK Linear adapter** (`mode: "agent-sessions"`; scope string `read,write,comments:create,issues:create,app:mentionable&actor=app`) and **Vercel Eve** framework (Linear changelog 2026-06-18) for custom agents (incident investigation, SLA monitoring, feedback analysis).
- **Cyrus** (github.com/ceedaragents/cyrus): "monitors Linear/GitHub/GitLab/Slack issues assigned to it, creates isolated Git worktrees for each issue, runs Claude Code / Codex / Cursor / Gemini sessions ... and streams detailed agent activity updates back". Self-host with your own Linear OAuth app, BYOK tokens, Apache-2.0, 794 stars.

### 2.5 Rate limits
Source: https://linear.app/developers/rate-limiting (undated). API key: 2,500 req/h and 3,000,000 complexity points/h per user. OAuth app: 5,000 req/h and 2,000,000 points/h per user/app-user. Unauthenticated: 600 req/h, 100,000 points. Max 10,000 complexity per single query. Headers `X-RateLimit-Requests-*`, `X-RateLimit-Complexity-*`, `X-Complexity`. (A secondary source quoted 5,000/h for API keys; the official page as fetched says 2,500 — treat exact numbers as medium confidence.)

---

## 3. Linear's first-party AI: Linear Agent, coding sessions, Loops, AI credits

| Capability | What | Plan | Cost | Source / date |
|---|---|---|---|---|
| Linear Agent chat | Understands roadmap/issues/code; creates and modifies issues, projects, milestones, initiatives; summarizes risk/blockers; drafts docs and updates; posts comments; uses MCP connectors; available via Cmd/Ctrl+J, @Linear in comments/docs, @Linear in Slack and MS Teams | All plans (public beta) | Included in seat (no AI credits) | changelog 2026-03-24; docs/linear-agent; docs/ai-credits |
| Code Intelligence | Controlled codebase access for Linear Agent | Business+ | Included | changelog 2026-05-14 |
| Linear Diffs / Reviews | Native code review of PRs from issues, Guided Reviews GA 2026-07-30 | Diffs all; Guided Reviews Business+ | Included | changelog 2026-05-28, 2026-07-30 |
| Coding sessions | Delegate an issue to "Linear" (or ask in chat/Slack) -> cloud sandbox runs **Claude Code or Codex**, drafts PR, adds diff to the issue, merge from Linear; browser testing + screenshots; env config for Node/Python/Ruby/Go/Postgres/Redis; model choice incl. Claude Fable 5, Opus 5, Opus 4.8 (default), Sonnet 5, GPT-5.6 Sol, GPT-5.5, GPT-5.4; ~30% of bug reports auto-fixed internally on first pass | Basic, Business, Enterprise; needs GitHub org-owner to enable code access | AI credits: tokens at provider rates, no markup + $0.25 per 20-min sandbox block; spend limits per workspace/user | changelog 2026-06-11, 2026-08-20; docs/coding-sessions; docs/ai-credits |
| Loops | Recurring (schedule) or event-triggered (issue created / status / comment) agent jobs described in plain language; can create/update issues, comment, post to Slack, delegate to Linear for implementation, do RCA, keep docs/roadmaps current; MCP connectors (GitHub, Notion, Sentry, Slack); admin-restricted connectors; run history | Business, Enterprise | AI credits, typically $0.07–$0.20 per run; per-loop spend caps | changelog 2026-07-20; docs/loops; docs/ai-credits |
| Agent-assisted editing + text attribution | Agent edits documents/project descriptions; author indicators show human vs loop text | (not stated) | — | changelog 2026-07-23 |
| Skills | Reusable instructions for Linear Agent, shareable per team, slash-command invokable; API `agentSkillCreate(teamId,title,body)` | (not stated) | — | changelog 2026-06-04; introspection 2026-09-02 |
| AI credits | Prepaid USD balance; min top-up $10, auto-reload min $50; expire after 12 months; only coding sessions and Loops consume credits | — | — | docs/ai-credits |

Important nuance: "Loops" and "triage rules" have **no GraphQL mutations** (verified: no `loop*`, no `*rule*` fields in Mutation or Query). They are configured in the UI (or via Linear Agent chat converting a conversation into a loop).

---

## 4. Which agents integrate natively (directory as fetched 2026-09-02)

Source: https://linear.app/integrations/agents plus vendor docs.

| Agent | Mechanics | Requirements / notes | Source |
|---|---|---|---|
| **Codex** (OpenAI) | Assign issue to Codex, `@Codex` in comment, or triage rule "Delegate > Codex"; posts progress in Activity, chat link, summary, PR via Codex cloud; `@Codex fix this in owner/repo` to pick repo | Paid ChatGPT plan; Codex cloud environment for the repo; Enterprise admin must enable connector; community reports of "Codex failed to start" when no environment | learn.chatgpt.com/docs/third-party/linear.md; linear changelog 2025-12-04 |
| **Cursor** | Delegate to Cursor, `@Cursor` mention, or triage automation; cloud agent creates PR, real-time status in Linear, follow-ups via `@Cursor`; `[repo=..., branch=..., model=...]` config; repo selection via `repo` label group | Cursor admin, Cloud Agent setup with **usage-based pricing**; "Linear requires a human assignee for rules to fire" | cursor.com/docs/integrations/linear |
| **GitHub Copilot cloud agent** | Assign issue -> Copilot analyses, opens draft PR in ephemeral GitHub Actions env, streams progress to Linear, requests review; steer with mentions; model/custom-agent/branch config via Linear agent guidance | GitHub org owner + Linear admin; Copilot Pro/Pro+/Business/Enterprise; **GA 2026-07-23** | github.blog changelog 2026-07-23 |
| **Devin** | Assign to Devin, playbook labels (`!plan`, `!implement`), or `@mention`; live activity feed, plan UI sync, PR links; automation triggers by team/label/status | Devin org connection; enterprise team mapping | docs.devin.ai/integrations/linear |
| **Sentry Agent (Seer)** | Delegate/assign, `@sentry` mention, or triage-rule label -> RCA + fix + optional auto-PR + status updates | Cloud Sentry only; beta | docs.sentry.io |
| **Charlie** | Plans, implements, reviews TypeScript PRs | — | directory |
| **Factory (Droids)**, **ChatPRD** (requirements/issues), **cto.new**, **Coco by Cotera**, **Pixelesq** (build websites from issues), **TierZero**, **Ranger** (bug formatting/test plans), **Reflag** (feature flags), **Stilla**, **Panaptico**, **Tembo** (delegate to any coding agent), **Larridin**, **Solo**, **Warp**, **CellCog** (research/docs/images/media), **Testifly** (web automation), **Dash0**, **Jellyfish**, **Replicas**, **Blocks** | Various | — | directory |
| **Cyrus** | "Your Claude Code powered Linear agent that runs anywhere"; also Codex/Cursor/Gemini runners; label-based model routing | Self-host or Cyrus cloud; BYOK; Apache-2.0 | github.com/ceedaragents/cyrus |
| **Claude Code (Anthropic)** | **No native Anthropic agent app in the directory** (confirmed by directory fetch 2026-09-02; secondary source states the same "as of July 2026"). Paths: (a) Linear Agent coding sessions run Claude Code under the hood; (b) Cyrus; (c) Claude Code + Linear MCP (`claude mcp add --transport http linear https://mcp.linear.app/mcp`) for read/write from inside a session; (d) build your own OAuth agent app that shells out to Claude Code | — | linear.app/docs/mcp; aidenapp.org (secondary) |

Intake-side "agents": the **Linear agent for Slack/Teams** (`@Linear` creates issues from conversation context, picks a channel template, asks for missing required fields) is available on all plans (changelog 2025-10-23). Linear Agent for **Intercom, Zendesk, Gong** (changelog 2025-12-11) turns support/sales conversations into issues and customer requests.

---

## 5. Linear MCP server tool surface

Source: https://linear.app/docs/mcp (undated), changelog 2026-02-05, Speakeasy catalogue (undated, secondary), usecarly 2026-07-19 (secondary).

- Endpoint `https://mcp.linear.app/mcp` (Streamable HTTP). Legacy `/sse` is a deprecated fallback (phase-out began Feb 2026). Read-only: `https://mcp.linear.app/mcp/readonly`, or request only the `read` scope.
- Auth: OAuth 2.1 with dynamic client registration; **or** a Linear API key / bearer token in the `Authorization` header (useful for a headless orchestrator, no browser dance). Enterprise + Okta: enterprise-managed authorization (changelog 2026-08-13).
- Clients documented: Claude (web/desktop), Claude Code, Codex, Cursor, Jules, VS Code, v0, Windsurf, Zed.
- Documented tool families (official wording): "finding, creating, and updating objects in Linear like issues, projects, and comments — with more functionality on the way"; Feb 2026 added "create and edit initiatives", "create and edit initiative updates", "create and edit project milestones", "create and edit project updates", "manage project labels", image loading, resource-by-URL loading, and lower token usage.
- Tool names as catalogued (Speakeasy, 31 tools; pre-dates the Feb-2026 additions): `list_issues, get_issue, save_issue, list_issue_statuses, get_issue_status, list_issue_labels, create_issue_label, list_comments, save_comment, delete_comment, list_projects, get_project, save_project, list_project_labels, list_milestones, get_milestone, save_milestone, list_cycles, list_documents, get_document, create_document, update_document, list_teams, get_team, list_users, get_user, get_attachment, create_attachment, delete_attachment, extract_images, search_documentation`. Expect additional initiative / initiative-update / project-update tools after 2026-02-05 (names unverified; confirm with `tools/list` from the host session).
- **Not in the MCP surface** (per every catalogue and the docs): team creation/settings, workflow state creation, cycle creation, templates, customers / customer requests / tiers, webhooks, SLA configuration, triage rules, triage responsibility, Asks channel config, Loops, agent sessions/activities, custom views, guest/user management.
- Documented use cases: turn a planning doc into a project with issues/milestones/relationships; standup notes -> issue comments; bug investigation from an issue; cycle summaries; timelines; implementation planning.

Implication: MCP is the right surface for **day-to-day agent work** (issues, comments, projects, milestones, updates, docs, initiatives). **Workspace bootstrapping and automation plumbing must go through GraphQL** (or the UI).

---

## 6. GraphQL API coverage (verified by introspection, 2026-09-02)

`__type(name:"Mutation")` returned 360 fields; `Query` 164. Relevant confirmed names:

| Area | Mutations | Queries | Notes |
|---|---|---|---|
| Teams | `teamCreate`, `teamUpdate`, `teamDelete`, `teamMembershipCreate/Update/Delete`, `teamCyclesDelete` | `teams`, `team` | `TeamCreateInput` includes `key, private, parentId, triageEnabled, requirePriorityToLeaveTriage, cyclesEnabled, cycleStartDay, cycleDuration, cycleCooldownTime, upcomingCycleCount, defaultTemplateForMembersId, defaultTemplateForNonMembersId, defaultProjectTemplateId, autoClosePeriod, initiativesEnabled, slackAutoCreateProjectChannel, productIntelligenceScope` |
| Workflow states | `workflowStateCreate`, `workflowStateUpdate`, `workflowStateArchive` | `workflowStates`, `workflowState` | Custom statuses per team |
| Cycles | `cycleUpdate`, `cycleArchive`, `cycleShiftAll`, `cycleStartUpcomingCycleToday` | `cycles`, `cycle` | **No `cycleCreate`** — cycles are generated from team cycle settings |
| Labels | `issueLabelCreate/Update/Delete/Retire/Restore`, `projectLabelCreate/...`, `initiativeLabelCreate/...` | — | Label groups via parent |
| Templates | `templateCreate`, `templateUpdate`, `templateDelete` | `templates`, `template`, `templateSearch` | `TemplateCreateInput: type, teamId, pipelineId, name, description, icon, color, templateData` (issue / project / document templates) |
| Issues | `issueCreate`, `issueBatchCreate`, `issueUpdate`, `issueBatchUpdate`, `issueAddLabel`, `issueRelationCreate`, `issueReminder`, `issueSubscribe`, `attachmentCreate`, `attachmentLinkURL`, `commentCreate`, `commentResolve`, `reactionCreate` | `issues`, `issue`, `issueSearch`… | `IssueCreateInput` has **`delegateId`**, `slaBreachesAt`, `slaStartedAt`, `slaType`, `templateId`, `projectMilestoneId`, `cycleId`, `createAsUser`, `displayIconUrl` |
| Projects | `projectCreate`, `projectUpdate`, `projectMilestoneCreate/Update/Move`, `projectUpdateCreate` (status update), `projectStatusCreate`, `projectRelationCreate`, `projectCreateSlackChannel` | `projects`, `projectMilestones`, `projectUpdates` | Project statuses are workspace-configurable |
| Initiatives | `initiativeCreate`, `initiativeUpdate`, `initiativeToProjectCreate`, `initiativeUpdateCreate`, `initiativeLeadTeamUpdate`, `initiativeRelationCreate` | `initiatives`, `initiativeUpdates` | Team-led + private initiatives (Business+) |
| Documents | `documentCreate/Update/Delete` | `documents`, `searchDocuments`, `documentContentHistory` | |
| Customers / requests | `customerCreate`, `customerUpsert`, `customerMerge`, `customerTierCreate`, `customerStatusCreate`, `customerNeedCreate`, `customerNeedCreateFromAttachment` | `customers`, `customerNeeds`, `customerTiers`, `customerStatuses` | Full CRUD; customer requests on all plans (manual/Slack/Asks), Intercom/Zendesk/Front sync Business+, Salesforce Enterprise |
| Views / favorites | `customViewCreate`, `favoriteCreate` | `customViews` | |
| Webhooks | `webhookCreate/Update/Delete/RotateSecret` | `webhooks`, `failuresForOauthWebhooks` | |
| Triage | `triageResponsibilityCreate/Update/Delete` | `triageResponsibilities` | **No triage-rule mutations/queries** |
| SLA | (fields on issue) | `slaConfigurations` | **No SLA-rule mutations**; rules configured in Settings > Issues > SLAs |
| Agents | `agentSessionCreate`, `agentSessionCreateOnIssue/OnComment`, `agentActivityCreate`, `agentSessionUpdate`, `agentSkillCreate` | `agentSessions`, `agentActivities`, `agentSkills`, `issueRepositorySuggestions` | |
| Integrations | `integrationSlack`, `integrationSlackAsks`, `integrationAsksConnectChannel`, `integrationSlackPost`, `integrationGithubConnect`, `integrationSentryConnect`, `integrationIntercom`, `integrationZendesk`, `integrationFront`, `integrationMcpServerConnect`, `integrationMcpServerPersonalConnect`, `integrationTemplateCreate` | `integrations` | Most integration connects need an interactive OAuth handshake; treat as UI-first |
| Org / users | `organizationInviteCreate`, `organizationUpdate`, `userChangeRole`, `userSuspend`, `organizationStartTrialForPlan` | `organization`, `users` | Guest invites via invites (no `guest*` mutation names) |
| Loops / Asks forms / rules | **none** | **none** | UI-only |

Auth for the orchestrator: a personal API key (acts as that user) or an OAuth app with `actor=user`; for creating *agent identities* an OAuth app with `actor=app` per agent.

---

## 7. Intake, triage, SLA, Asks, customer requests

| Feature | Behaviour | Plan | Source |
|---|---|---|---|
| Triage inbox | Issues from integrations (Slack, Sentry, Asks, email), from non-team members, or created in Triage land in the team's Triage; `teamCreate.triageEnabled` | All | docs/triage |
| Triage rules | Sequential rules on filterable properties set team/status/assignee/label/project/priority and **delegate to an agent** "with no human in the loop" | Business+ | docs/triage, docs/assigning-issues |
| Triage Intelligence (was Product Intelligence) | AI suggests team/assignee/labels, flags duplicates/related; auto-apply per property (since 2025-09-18) | Business+ | changelog 2025-09-19, linear.app/intake |
| Triage responsibility | Rotating owner; PagerDuty/OpsGenie/Rootly/incident.io or API (`triageResponsibilityCreate`) | Business+ | docs/triage |
| SLAs | Rules by team/status/assignee/creator/priority/labels/project/initiative; durations 12 h–4 weeks, business-day aware; notifications 24 h before and at breach; six status buckets; Insights breakdown | Business+ | docs/sla |
| Linear Asks | Intake from Slack (emoji, `/ask`, `@Linear Asks`, overflow menu, DM), email (subject -> title), web forms; synced two-way threads; per-channel templates and required fields; **external Slack Connect users without Linear accounts can submit**; auto-associates customer by sender email | Business+; private-channel per-channel config, auto-create-every-message, multi-workspace and **web forms = Enterprise** | docs/linear-asks, docs/linear-asks-slack, changelog 2026-04-02 |
| Customer requests | Customer object (domain, logo, revenue, tier, size, status, owner); requests from Intercom (real-time), Zendesk/Front (12 h sync), Salesforce, Asks, Slack, manual, API | Manual/Slack/Asks all plans; Intercom/Zendesk/Front Business+; Salesforce Enterprise | docs/customer-requests |
| Guests | External collaborators limited to specific teams/projects | Business+ (per pricing page) | linear.app/pricing |

---

## 8. Plans and limits (pricing page fetched 2026-09-02; yearly billing prices)

| | Free | Basic $10/user/mo | Business $16/user/mo | Enterprise (custom, annual) |
|---|---|---|---|---|
| Members | Unlimited | Unlimited | Unlimited | Unlimited |
| Teams | 2 | 5 | Unlimited | Unlimited |
| Issues | 250 | Unlimited | Unlimited | Unlimited |
| File uploads | 10 MB | Unlimited | Unlimited | Unlimited |
| API / webhooks / MCP / agents platform | Yes | Yes | Yes | Yes |
| Admin roles | Team owners | Advanced | Advanced | Advanced |
| Guests, private teams, sub-teams | — | — | Yes | Yes |
| Triage Intelligence, triage rules, SLAs, Insights, Code Intelligence | — | — | Yes | Yes |
| Linear Asks | — | — | Yes | Advanced (web forms, private channels) |
| Coding sessions (AI credits) | — | Yes | Yes | Yes |
| Loops (AI credits) | — | — | Yes | Yes |
| Team-led / private initiatives | — | — | Yes | Yes |
| SAML/SCIM, audit log, IP restrictions, Okta MCP auth | — | — | — | Yes |

Agents (OAuth `actor=app`) are free of seat cost on every plan. Monthly (non-annual) prices were not captured from the page; treat the $10/$16 numbers as yearly-billing rates.

---

## 9. Capability matrix for an orchestrator

| Need | MCP (`mcp.linear.app`) | GraphQL API (API key / OAuth `actor=user`) | OAuth agent app (`actor=app`) | UI only |
|---|---|---|---|---|
| Create teams, keys, cycle settings, triage on/off | — | `teamCreate` | — | — |
| Custom workflow states per team | — | `workflowStateCreate` | — | — |
| Labels / label groups (issue, project, initiative) | issue labels only (`create_issue_label`) | all | — | — |
| Issue / project / document templates | — | `templateCreate` | — | — |
| Projects, milestones, project status updates | yes | yes | yes (with `write`) | — |
| Initiatives + initiative updates | yes (since 2026-02-05) | yes | yes (`initiative:write`) | — |
| Issues, sub-issues, relations, comments, attachments | yes | yes (+ `issueBatchCreate`) | yes | — |
| Delegate an issue to an agent | unverified (`save_issue` may not expose `delegateId`) | `issueUpdate(delegateId)`, `agentSessionCreate` | receives `AgentSessionEvent` | assignment menu |
| Documents | yes | yes | yes | — |
| Customers, tiers, customer requests | — | `customerCreate`, `customerNeedCreate` | with `customer:write` | yes |
| Webhooks | — | `webhookCreate` | auto per org | yes |
| SLA on an issue | — | `slaBreachesAt`/`slaType` on issue | — | rules in Settings |
| SLA rules, triage rules, Loops, Asks web forms, Slack channel config | — | — | — | yes |
| Agent skills (Linear Agent) | — | `agentSkillCreate` | — | yes |
| Agent identity that can be @mentioned / delegated | — | — | yes (`app:mentionable`, `app:assignable`) | — |
| Coding sessions (Claude Code / Codex in Linear's sandbox) | — | — | — | delegate to "Linear" / chat / Slack |
| Slack intake (Asks, @Linear) | — | `integrationSlackAsks`, `integrationAsksConnectChannel` exist but need OAuth handshake | — | practical path |

---

## 10. What this means for the AI-agency demo on Linear

1. **Plan**: run the demo on **Business** (or a Business trial: `organizationStartTrialForPlan` exists). Free's 2-team/250-issue cap and the absence of triage rules, SLAs, Asks, guests and Loops make it unsuitable; Basic would cover coding sessions but not the intake/automation layer.
2. **Workspace model** (all creatable via GraphQL): one Team per agency function or per client (e.g., `SALES`, `PM`, `DEV`, `QA`, `MKT`, plus `TOWMOTIVE`, `DREAMBABY`, `MOTILE`), Initiatives per client account or quarterly goal, Projects per engagement, Milestones per deliverable, issue templates per deliverable type (Shopify feature, SEO audit, configurator fix), custom workflow states (`Intake -> Scoped -> Approved -> In progress -> Agent review -> Human QA -> Delivered`), Customers with tiers/revenue as the client CRM, Documents for SOWs/briefs, custom views per agent.
3. **Agent identities**: one OAuth app installed with `actor=app` per AI role (PM-agent, Dev-agent, QA-agent, Sales-agent, Marketing-agent). Each becomes an @mentionable, delegatable app user with zero seat cost. A single webhook receiver (AgentSessionEvent) routes sessions to the right runner: Claude Code (Workflow multi-agent), Codex CLI, Cursor CLI. Cyrus can be used as a ready-made Claude Code runner for the Dev role. Stream `thought/action/response` activities, attach PR/preview URLs via `externalUrls`, ask questions via `elicitation` (session goes to `awaitingInput`, human replies produce `prompted`).
4. **Human supervision**: delegation always keeps a human assignee; humans answer elicitations, review Diffs in Linear, approve state transitions; agent output is visible in Activity, "My issues > Delegated", Insights.
5. **Intake and automation**: Slack Asks channel per client (external Slack Connect users can file requests without Linear seats) -> Triage -> Triage Intelligence suggests labels/team -> triage rule "delegate to PM-agent" (note: Cursor docs say rules need a human assignee; verify for custom agents) -> SLAs by priority. Loops for recurring agency work (weekly client status update, daily backlog grooming, stale-issue chasing) at ~$0.10/run.
6. **Code execution options inside Linear**: (a) Linear's own coding sessions (Claude Code/Codex in Linear's sandbox, pay-per-use, no infra); (b) own agent app calling local Claude Code/Codex/Cursor CLIs; (c) native Codex/Cursor/Copilot agents if those subscriptions exist. Fightclub repos on GitHub org "Free" plan: coding sessions need a GitHub org owner to grant code access.
7. **Reporting**: `projectUpdateCreate` / `initiativeUpdateCreate` from agents; Linear Agent "Write with Agent" drafts updates from issue deltas and Slack; Insights for cycle/SLA metrics (Business+).

## 11. Risks and open points
- Agents API is a Developer Preview; contracts may change before GA.
- Exact current MCP tool names post-2026-02-05 unverified from an official list; run `tools/list` in the host session before writing orchestration code.
- Whether MCP `save_issue` supports `delegateId` is unknown; GraphQL `issueUpdate` definitely does.
- Triage-rule delegation to third-party agents reportedly requires a human assignee (Cursor docs); may also apply to custom agents.
- AI-credit economics for coding sessions depend on model choice; Loops pricing is "typically" $0.07–0.20 per run.
- Rate limits: an orchestrator that fans out many agent app-users gets 5,000 req/h and 2M complexity per app-user, which is generous, but a single API-key orchestrator has 2,500 req/h (per the official page as fetched; one secondary source says 5,000).
- Guest accounts doc page returned 404; plan gating for guests taken from the pricing page only.

---

## 12. Findings table

| # | Claim | Source URL | Source date | Confidence | Impact |
|---|---|---|---|---|---|
| 1 | Agents are OAuth apps installed with `actor=app`; scopes `app:mentionable` and `app:assignable` enable @mention and delegation; admin install required; cannot combine with `admin` scope | https://linear.app/developers/agents | undated (fetched 2026-09-02) | high | high |
| 2 | Agent sessions have states pending/active/error/awaitingInput/complete/stale; activities thought/action/elicitation/response/error; state is derived automatically | https://linear.app/developers/agent-interaction | undated (fetched 2026-09-02) | high | high |
| 3 | Webhook receiver must respond within 5 s; agent must emit an activity within 10 s of `created` or be marked unresponsive | https://linear.app/developers/agent-interaction | undated | high | high |
| 4 | `AgentSessionEvent` webhook actions `created` (delegation/mention) and `prompted` (follow-up); stop arrives as `signal: "stop"` on a prompted event | https://linear.app/developers/agent-interaction | undated | high | high |
| 5 | Agents are not billable seats | https://linear.app/docs/agents-in-linear | undated | high | high |
| 6 | Delegation keeps the human assignee responsible; agent is the delegate; triage rules can delegate to agents (Business+) | https://linear.app/docs/assigning-issues | undated | high | high |
| 7 | GraphQL has `delegateId` on IssueCreate/UpdateInput and `agentSessionCreate(issueId, appUserId, context)` | https://api.linear.app/graphql (introspection) | 2026-09-02 | high | high |
| 8 | GraphQL has `teamCreate`, `workflowStateCreate`, `templateCreate`, `issueLabelCreate`, `projectMilestoneCreate`, `initiativeCreate`, `documentCreate`, `customerCreate`, `customerNeedCreate`, `webhookCreate`, `agentSkillCreate`, `issueBatchCreate`; no `cycleCreate`; no loop/triage-rule/SLA-rule mutations | https://api.linear.app/graphql (introspection) | 2026-09-02 | high | high |
| 9 | Linear MCP server at `https://mcp.linear.app/mcp` (Streamable HTTP), OAuth 2.1 dynamic client registration or API-key bearer; `/mcp/readonly` variant | https://linear.app/docs/mcp | undated (fetched 2026-09-02) | high | high |
| 10 | MCP added create/edit initiatives, initiative updates, project milestones, project updates, project labels, image loading, URL resource loading | https://linear.app/changelog/2026-02-05-linear-mcp-for-product-management | 2026-02-05 | high | high |
| 11 | Catalogued MCP tools (31): save_issue, save_project, save_milestone, save_comment, create/update_document, create_issue_label, list_cycles, list_teams, list_users, attachments, extract_images, search_documentation; no team/workflow/template/customer/webhook tools | https://www.speakeasy.com/product/mcp-gateway/catalog/linear/ | undated (secondary) | medium | high |
| 12 | Linear Agent public beta 2026-03-24, included on all plans; creates issues, extracts requirements, flags risks; accessible via Cmd+J, comments, Slack, Teams | https://linear.app/changelog/2026-03-24-introducing-linear-agent | 2026-03-24 | high | medium |
| 13 | Coding sessions: Linear Agent writes code with Claude Code and Codex in cloud sandboxes; Basic/Business/Enterprise; GitHub code access required | https://linear.app/changelog/2026-06-11-coding-sessions | 2026-06-11 | high | high |
| 14 | Coding-session model options include Claude Fable 5, Opus 5, Opus 4.8 (default), Sonnet 5, GPT-5.6 Sol, GPT-5.5, GPT-5.4; PR drafted and mergeable from Linear | https://linear.app/docs/coding-sessions | undated (fetched 2026-09-02) | medium | high |
| 15 | Coding-session pricing: tokens at provider rates with no markup + $0.25 per 20-minute sandbox block; per-workspace/user spend limits; browser testing and env config | https://linear.app/changelog/2026-08-20-coding-environments | 2026-08-20 | high | high |
| 16 | Loops: schedule/event-triggered agent jobs; Business+; AI credits; can create/update issues, comment, post to Slack, delegate to Linear; MCP connectors (GitHub, Notion, Sentry, Slack) | https://linear.app/changelog/2026-07-20-introducing-loops and https://linear.app/docs/loops | 2026-07-20 / undated | high | high |
| 17 | AI credits: only coding sessions and Loops consume credits; Loops ~$0.07–0.20/run; min top-up $10, auto-reload min $50; 12-month expiry; chat, Code Intelligence, Triage Intelligence included in plan | https://linear.app/docs/ai-credits | undated (fetched 2026-09-02) | high | high |
| 18 | Agent directory lists Codex, Cursor, GitHub Copilot, Factory, Sentry Agent, Devin, ChatPRD, Charlie, Cyrus (Claude Code powered), Warp, Tembo, Blocks and others (27 total); no Anthropic/Claude Code entry | https://linear.app/integrations/agents | undated (fetched 2026-09-02) | high | high |
| 19 | Codex in Linear: assign, @Codex, or triage rule "Delegate > Codex"; needs paid ChatGPT plan and a Codex cloud environment | https://learn.chatgpt.com/docs/third-party/linear.md | undated | high | medium |
| 20 | Cursor in Linear: delegate/@Cursor/triage rules; needs Cursor admin + cloud agents with usage-based pricing; "Linear requires a human assignee for rules to fire" | https://cursor.com/docs/integrations/linear | undated | high | medium |
| 21 | GitHub Copilot cloud agent for Linear GA 2026-07-23; Copilot Pro/Pro+/Business/Enterprise; GitHub org owner + Linear admin | https://github.blog/changelog/2026-07-23-copilot-cloud-agent-for-linear-is-now-generally-available/ | 2026-07-23 | high | medium |
| 22 | Cyrus: open-source (Apache-2.0) Claude Code/Codex/Cursor/Gemini background agent for Linear via own OAuth app + AgentSessionEvent webhooks; BYOK | https://github.com/ceedaragents/cyrus | undated (fetched 2026-09-02) | high | high |
| 23 | Webhook entity types incl. Issues, Comments, Projects, Project updates, Documents, Initiatives, Cycles, Customers, Customer Requests, Issue SLA, AgentSessionEvent; HMAC signature; retries 1 min/1 h/6 h | https://linear.app/developers/webhooks | undated | high | medium |
| 24 | Rate limits: API key 2,500 req/h + 3M complexity; OAuth app 5,000 req/h + 2M complexity per app-user; 10,000 max complexity per query | https://linear.app/developers/rate-limiting | undated | medium | medium |
| 25 | OAuth tokens 24 h; refresh-token migration for all OAuth apps on 2026-04-01; OAuth application manifests (2026-06-18) | https://linear.app/developers/oauth-2-0-authentication and https://linear.app/changelog/2026-06-18-agent-assisted-project-updates | 2026-04-01 / 2026-06-18 | high | medium |
| 26 | Pricing: Free $0 (2 teams, 250 issues, 10 MB), Basic $10, Business $16 per user/month yearly, Enterprise custom; Asks, SLAs, Triage Intelligence, guests, Loops, Code Intelligence = Business+; audit log/SCIM/IP = Enterprise | https://linear.app/pricing | undated (fetched 2026-09-02) | high | high |
| 27 | Linear Asks: Slack/email/web-form intake, synced threads, external Slack Connect users can submit without Linear accounts; Business+; web forms, private per-channel config, auto-create-every-message = Enterprise | https://linear.app/docs/linear-asks-slack and https://linear.app/changelog/2026-04-02-web-forms-for-linear-asks | undated / 2026-04-02 | high | high |
| 28 | Triage rules (Business+) update team/status/assignee/label/project/priority and can delegate to an agent; Triage Intelligence suggests/auto-applies properties and flags duplicates | https://linear.app/docs/triage and https://linear.app/changelog/2025-09-19-auto-apply-triage-suggestions | undated / 2025-09-18 | high | high |
| 29 | SLAs Business+; rules by priority/label/team/etc.; 12 h–4 weeks; breach notifications; `slaConfigurations` query but no rule mutations | https://linear.app/docs/sla + introspection | undated / 2026-09-02 | high | medium |
| 30 | Customer requests: Customer object with tier/revenue/status; requests via Intercom/Zendesk/Front (Business+), Salesforce (Enterprise), Asks/Slack/manual/API (all plans) | https://linear.app/docs/customer-requests | undated | high | medium |
| 31 | Linear agent for Slack (`@Linear` creates issues from conversation) on all plans | https://linear.app/changelog/2025-10-23-linear-agent-for-slack | 2025-10-23 | high | medium |
| 32 | Shared skills for Linear Agent (2026-06-04); `agentSkillCreate(teamId,title,body)` in API | https://linear.app/changelog/2026-06-04-team-documents + introspection | 2026-06-04 / 2026-09-02 | high | medium |
| 33 | Enterprise-managed MCP authorization via Okta; team-led and private initiatives (Business+) | https://linear.app/changelog/2026-08-13-team-initiatives | 2026-08-13 | high | low |
| 34 | No native Claude Code agent app in Linear as of July 2026 (secondary) | https://aidenapp.org/linear-claude-code | 2026-07 (secondary) | medium | medium |
| 35 | Official linear-agent-demo repo archived 2025-10-10; Vercel Chat SDK Linear adapter and Vercel Eve are current build paths | https://github.com/linear/linear-agent-demo and https://chat-sdk.dev/adapters/official/linear | 2025-10-10 / undated | high | low |

## 13. Primary sources read
- https://linear.app/developers/agents
- https://linear.app/developers/agent-interaction
- https://linear.app/developers/webhooks
- https://linear.app/developers/oauth-2-0-authentication
- https://linear.app/developers/rate-limiting
- https://linear.app/docs/mcp
- https://linear.app/docs/agents-in-linear
- https://linear.app/docs/assigning-issues
- https://linear.app/docs/linear-agent
- https://linear.app/docs/coding-sessions
- https://linear.app/docs/loops
- https://linear.app/docs/ai-credits
- https://linear.app/docs/triage
- https://linear.app/docs/sla
- https://linear.app/docs/linear-asks
- https://linear.app/docs/linear-asks-slack
- https://linear.app/docs/customer-requests
- https://linear.app/docs/initiatives
- https://linear.app/pricing
- https://linear.app/integrations/agents
- https://linear.app/intake
- https://linear.app/changelog (index) and entries 2025-09-19, 2025-10-23, 2026-02-05, 2026-03-24, 2026-04-02, 2026-06-04, 2026-06-11, 2026-06-18, 2026-07-20, 2026-08-13, 2026-08-20
- https://api.linear.app/graphql (schema introspection, 2026-09-02)
- https://learn.chatgpt.com/docs/third-party/linear.md
- https://cursor.com/docs/integrations/linear
- https://github.blog/changelog/2026-07-23-copilot-cloud-agent-for-linear-is-now-generally-available/
- https://docs.sentry.io/organization/integrations/issue-tracking/sentry-linear-agent/
- https://docs.devin.ai/integrations/linear
- https://github.com/ceedaragents/cyrus
- https://github.com/linear/linear-agent-demo
- https://chat-sdk.dev/adapters/official/linear
- Secondary: https://www.speakeasy.com/product/mcp-gateway/catalog/linear/, https://www.usecarly.com/blog/linear-mcp/ (2026-07-19), https://aidenapp.org/linear-claude-code, https://www.gumloop.com/mcp/linear (wrapper server, not the official tool list)
