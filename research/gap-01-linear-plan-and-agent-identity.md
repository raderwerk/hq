# Gap 01: Linear plan tier and agent identity (verified 2026-09-02)

Closes the contradiction between the brief (assumptions 2 and 3, success criterion 1), lane 04 (Free-plan caps), lane 06 ("Linear cannot delegate to Claude Code") and lane 10 ("no agent app users"). Everything below was checked today against Linear's own pages and against the live workspace `fightclub-techhub` (org id 496f9ed7-9270-4def-9591-617d73915cb1) with the personal API key in `~/.config/linear/api_key`.

Method note: the session's WebSearch budget was already exhausted (200/200), so no new keyword searches were possible. Instead I fetched 25+ primary pages directly (linear.app pricing, docs, developers, changelog; OpenAI, Cursor, GitHub, Cyrus), parsed the raw pricing HTML to decode the per-plan icons, ran live GraphQL introspection and mutations, and called the hosted MCP server (`https://mcp.linear.app/mcp`) with the API key. Where a fact could not be verified it is marked confidence=low.

## 1. Plan caps and feature gating (linear.app/pricing, raw HTML parsed 2026-09-02; page is undated)

Prices shown are the "Billed yearly" figures that are in the static HTML; monthly-billing prices sit behind a client-side toggle and were not captured.

| Feature | Free | Basic $10/user/mo | Business $16/user/mo | Enterprise |
|---|---|---|---|---|
| Members | Unlimited | Unlimited | Unlimited | Unlimited |
| Teams | 2 | 5 | Unlimited | Unlimited |
| Issues | 250 | Unlimited | Unlimited | Unlimited |
| Agent platform (3rd-party agents) | yes | yes | yes | yes |
| Linear Agent (chat, @Linear, skills) | yes | yes | yes | yes |
| Coding sessions (Claude Code / Codex run by Linear) ** | no | yes | yes | yes |
| Loops ** | no | see note | yes | yes |
| Triage rules | no | no | yes | yes |
| Triage responsibility | no | no | yes | yes |
| Triage Intelligence | no | no | yes | yes |
| Issue SLAs | no | no | yes | yes |
| Linear Asks (Slack/email intake) | no | no | yes | yes |
| Private teams, guest accounts | no | no | yes | yes |
| Sub-teams | no | 1 level | 5 levels | 5 levels |
| Admin roles ("on Free plans, all users are Admins") | no | yes | yes | yes |

`**` = "Requires AI credits" (footnote on the pricing page).

Note on Loops: the pricing comparison table marks Loops as available from Basic, but the Business plan card on the same page lists "Loops" as a Business addition, and three doc pages say "Available to workspaces on Business and Enterprise plans" (docs/loops, docs/ai-credits, changelog 2026-07-20). Treat Loops as Business+ until Linear's pages agree. Confidence: high for "not on Free", medium for "Business needed".

Sources: https://linear.app/pricing ; https://linear.app/docs/teams (team limits 2/5/unlimited/unlimited) ; https://linear.app/docs/triage ("Triage Intelligence, Triage Rules and Triage Responsibility are all available on our Business and Enterprise plans") ; https://linear.app/docs/sla ; https://linear.app/docs/linear-asks ; https://linear.app/docs/loops ; https://linear.app/docs/members-roles.

Live confirmation of the team cap: with FC as team 1, `teamCreate` for "ZZ Probe A" succeeded (team 2), `teamCreate` for "ZZ Probe B" returned 403 `FORBIDDEN`: "You have reached the limit of teams allowed in your current plan. Please upgrade to create more teams." ZZ Probe A was deleted again (`teamDelete`, success; Linear keeps a 30-day restore window per docs/teams). Confidence: high.

Issue cap consumption: the workspace now has 132 issues including archived (1 archived), `organization.createdIssueCount` = 131. The billing doc says on Free "If you have over 250 issues, you will no longer be able to create new issues" (https://linear.app/docs/billing-and-plans). Whether deleting issues frees capacity was not tested; archiving does not (archived issues still exist). With 130 legacy issues already present, the brief's plan (6 templates, a 5 to 8 issue project per dry run, three dry runs plus the demo) reaches 250 quickly unless the legacy backlog is deleted. Confidence: medium.

## 2. Seats and cost arithmetic

- `users` query: 7 users = 4 humans (Youp, Marijn, Xander, Raf; all `admin: true` because Free) + 3 app users (`app: true`): Linear (created 2026-03-24), Cursor (2026-09-02 12:09, `supportsAgentSessions: true`), Codex (2026-09-02 12:08, `supportsAgentSessions: true`).
- "Agents are not counted as billable seats in Linear. The services that provide the agent may have their own pricing structure." (https://linear.app/docs/agents-in-linear) and "agents installed in your workspace do not count as billable users" (https://linear.app/developers/agents). Billing counts "the number of unsuspended users within a workspace" (docs/billing-and-plans).
- So the requester's "~$16 x 7 users" overcounts. Business = 4 x $16 = $64/month on yearly billing (3 x $16 = $48 if Marijn, last seen 2025-08, is suspended). Basic = 4 x $10 = $40/month. Confidence: high (prices are yearly-billing figures).

## 3. Trial

- GraphQL mutation `organizationStartTrialForPlan(input: { planType: String! })` exists and is not tagged [Internal]: "Starts a trial for the workspace on the specified plan type. The workspace must not already be on a paid plan or in an active trial." Payload: `{ success }`. `organization.trialStartsAt` / `trialEndsAt` are both null today.
- Neither the pricing page (no occurrence of the word "trial" in its HTML) nor docs/billing-and-plans states trial length, eligibility or which plan types are accepted. I did not call the mutation: it is a one-shot state change ("must not already be ... in an active trial") that belongs to the requester. Confidence: high that the mutation exists, low on duration/terms.

## 4. Agent platform on this Free workspace: live delegation probes

Scratch issue FC-148 (now archived), created via GraphQL, then:

1. `issueUpdate(delegateId = Linear app user)` -> 400 `INPUT_ERROR` "cannot delegate to Linear", user message: "Delegating to Linear requires coding sessions to be enabled with GitHub code access. A workspace admin can set this up in workspace AI settings." The internal flag `codingAgentEnabled: true` therefore does not mean coding sessions are usable; the product gate is plan (Basic+) plus GitHub code access. The Linear app user reports `supportsAgentSessions: false`.
2. MCP `tools/call save_issue { id: "FC-148", delegate: "Codex" }` (Bearer = API key) -> success, `delegate: Codex`, `assignee: Youp`. An `AgentSession` was created at 12:47:35.691Z (status `pending`, type `commentThread`, `creator: Youp`, `appUser: Codex`). Codex answered at 12:47:39 (about 4 s): response + elicitation "To use Codex, link your ChatGPT account. Then tag @Codex again on this issue to start the agent." Session status `awaitingInput`.

Scratch issue FC-149 (now archived), created via MCP `save_issue { team, title, description, delegate: "Cursor" }` in one call -> session created 12:49:13.896Z; Cursor answered within about 1 s: "To use Cloud Agents, please link your Cursor account first. [Link your account](https://cursor.com/linear)". Session status `complete`.

Conclusions (confidence high, in-session evidence):
- Third-party agent delegation works on Free: app users, `delegate` field, `AgentSession` and `AgentActivity` records, and the agent's activity feed are all present and populate within seconds. No seat, no webhook infrastructure and no plan upgrade is needed for this identity model.
- Both installed agents are blocked only by per-user account linking (ChatGPT account for Codex, Cursor account for Cursor), not by Linear.
- The delegation is attributed to the API-key owner (`creator: Youp`); the agent's own activities are attributed to the app user. That is exactly the identity split the brief wanted to fake with `agent/*` labels.

## 5. Linear coding sessions (Linear runs Claude Code or Codex itself)

- "When you delegate an issue to Linear, we start a secure coding session through Claude Code or Codex ... Coding sessions are supported on Basic, Business and Enterprise plans. Usage draws from your workspace's AI credits." Setup: Linear owner/admin with GitHub org-owner access grants code access in the GitHub integration, then enables Coding sessions; each member links a GitHub account. Model is chosen workspace-wide: "We currently support Claude Fable 5, Claude Opus 5, Claude Opus 4.8, Claude Sonnet 5, GPT-5.6 Sol, GPT-5.5 and GPT-5.4" (default "Auto" = Claude Opus 4.8). Coding environments (runtimes, env vars, prepare scripts) are configured under Workspace settings > AI & Agents > Coding sessions > Environments. Source: https://linear.app/docs/coding-sessions (verbatim via Linear's `search_documentation`, undated); launch: https://linear.app/changelog/2026-06-11-coding-sessions (2026-06-11); environments, browser testing and screenshots: https://linear.app/changelog/2026-08-20-coding-environments (2026-08-20).
- Pricing: "Tokens are charged at the provider's published rates, with no markup" plus "sandbox runtime at $0.25 per 20-minute block"; ad-hoc top-up minimum $10, auto top-up minimum $50, funds expire 12 months after purchase; workspace, per-user and per-loop spend limits with daily/weekly/monthly reset. Loops: "Typical runs without a coding session cost $0.07-$0.20." Source: https://linear.app/docs/ai-credits (undated, fetched 2026-09-02).
- Implication: no Anthropic or OpenAI subscription is needed for coding sessions; Linear bills the tokens. Note the model list has "Claude Fable 5", not Fable 5.1, and the model is one setting for the whole workspace. Confidence: high.
- On this workspace today: not runnable (Free plan + GitHub code access not granted), see section 4.

## 6. Loops

- "Loops automate work in Linear by executing instructions based on triggers" (schedule or event), Business and Enterprise, require AI credits since 2026-07-20 ("$20 per seat in promotional credits ... expire on August 20, 2026", already lapsed). Permissions per loop include teams access, web access, Code Intelligence, coding sessions, MCP connectors (GitHub, Notion, Slack, Sentry); run history and versioning. Sources: https://linear.app/docs/loops ; https://linear.app/changelog/2026-07-20-introducing-loops (2026-07-20).
- No public API surface: schema introspection shows no `loop*` query or mutation; only `agentSkills` / `agentSkillCreate|Update|Delete` and internal `AgentAutomation*` types. Loops are configured in the UI. Not testable on Free; not attempted. Confidence: high for plan gate, medium for "UI only".

## 7. Linear MCP from the host session (tools/list run 2026-09-02)

- `https://mcp.linear.app/mcp` accepts `Authorization: Bearer <personal API key>` (docs/mcp: "You can also authenticate directly with a bearer token or Linear API key"). The bare `Authorization: <key>` form used by GraphQL returns 401 on MCP. Read-only endpoint: `/mcp/readonly`.
- 62 tools. Write tools: save_issue, save_project, save_initiative, save_milestone, save_document, save_release, save_release_note, save_status_update, save_comment, create_issue_label, create_initiative_label, attachments, diff review tools (save_diff_comment, submit_diff_review, merge_diff), share_issue/unshare_issue. Read-only for teams, templates, issue statuses, users, cycles, project labels. No tool creates teams, workflow states, templates, cycles, project labels or webhooks, and there is no delete_issue.
- `save_issue` accepts `delegate` (agent name or id) and `assignee`; `list_issues` filters by `delegate`. So the dispatcher can delegate to Codex/Cursor and poll for issues by delegate purely through MCP. Confidence: high.

## 8. Claude Code identity in Linear

- There is no first-party Claude Code agent: https://linear.app/integrations/claude-code and https://code.claude.com/docs/en/linear both 404; the agents directory (https://linear.app/integrations/agents) lists 27 agents (Codex, Cursor, GitHub Copilot, Factory, Sentry, Devin, ChatPRD, Charlie, ..., Cyrus, ...) and the only Claude Code entry is Cyrus: "Your Claude Code powered Linear agent that runs anywhere" (Apache-2.0, self-hostable, needs a Claude subscription or API key and its own Linear OAuth app; https://github.com/ceedaragents/cyrus). Confidence: high.
- Four ways to get Claude Code work attributed to a non-human identity, in increasing build effort:
  1. Linear coding sessions (section 5): Linear's own sandbox runs Claude Code; identity = "Linear" app user; needs Basic+, GitHub code access, AI credits. Zero build.
  2. Codex/Cursor/Copilot app users for the coding steps (already installed; Copilot cloud agent for Linear GA since 2026-07-23 on Copilot Pro/Pro+/Business/Enterprise, https://github.blog/changelog/2026-07-23-copilot-cloud-agent-for-linear-is-now-generally-available/), Claude Code only as local orchestrator under the human MCP user.
  3. Own OAuth app installed with `actor=app` (https://linear.app/developers/agents, "Developer Preview"): free to build, seat-free, gets its own app user; the dispatcher writes with that app token so comments and state changes carry the agent identity. If it also requests `app:assignable`, Linear expects "an activity or update your external URL within 10 seconds" after a `created` AgentSessionEvent (https://linear.app/developers/agent-interaction), which a 2-minute poller cannot meet; so either run a small webhook receiver or keep the app mentionable-only and let the dispatcher poll. Confidence: medium (attribution-by-app-token is per docs; the "poll instead of webhook" variant is my inference, not tested).
  4. Cyrus as a hosted bridge (external dependency, extra infra).
- Lane 06's "Linear cannot delegate to Claude Code" is wrong for coding sessions (Linear runs Claude Code) and right only in the sense that Anthropic ships no Linear agent app.

## 9. Vendor tiers actually held (local machine evidence, no secrets read out)

| Vendor | Evidence | What it enables |
|---|---|---|
| Anthropic | Claude Code keychain metadata: `subscriptionType: max`, `rateLimitTier: default_claude_max_20x`; account mcc@fightclubagency.com, org "mcc@fightclubagency.com's Organization", stripe subscription. Not a Claude Team/Enterprise org. | Claude Code CLI orchestrator and Linear MCP under the human account. Linear coding sessions do not need it (Linear bills credits). |
| OpenAI | `~/.codex/auth.json`: `auth_mode: chatgpt`, JWT claim `chatgpt_plan_type: pro`, personal gmail account. Codex CLI 0.147.0. | "Codex in Linear is available on paid plans" (https://learn.chatgpt.com/docs/third-party/linear, undated). Pro qualifies; the Linear user must link that ChatGPT account (the exact elicitation Codex returned), and Codex cloud needs GitHub + an environment. |
| Cursor | `cursor-agent status`: logged in as the same gmail account; plan tier not readable locally. Default model `grok-4.6` (Cursor Grok 4.6 High Fast); `--list-models` includes cursor-grok-4.6-high-fast, cursor-grok-4.6-low(-fast), gpt-5.6-sol-xhigh, claude-fable-5-thinking-xhigh (NO ZDR), claude-opus-5-thinking-high, composer-2.5. | Cloud Agents (what Linear delegation triggers) need "a paid Cursor plan" and a Cursor admin must connect source control and enable usage-based pricing (https://cursor.com/docs/cloud-agent, https://cursor.com/docs/integrations/linear). Bugbot is "on usage-based billing" for Pro/Pro+/Ultra/Teams (https://cursor.com/pricing). "Grok Bot" as a product name could not be verified anywhere; treat it as Grok 4.6 inside Cursor. Confidence: low on Cursor tier. |
| GitHub Copilot | not checked | alternative delegable coding agent, Copilot Pro+ |

"Claude Tag / Claude Code Review" from the requester's note could not be mapped to a product page in this session; confidence low, not used in the recommendation.

## 10. Corrections to earlier lanes

- Lane 04: Free caps (2 teams, 250 issues, no triage rules/SLAs/Asks/Loops/guests) confirmed by pricing page, docs and a live 403. Coding sessions are Basic+, not Business+.
- Lane 10 "no agent app users installed": stale since 12:08 today; Codex and Cursor app users exist and answer delegations within seconds.
- Lane 06 "Linear cannot delegate to Claude Code": Linear's coding sessions run Claude Code (Fable 5 / Opus 5 / Sonnet 5) on Basic+; only a first-party Anthropic agent app is missing.
- Brief assumption 2 ("one user account, no agent seats"): still true that no seats are needed, but false that identity must be faked with labels; app users are free on every plan.
- Brief assumption 3 ("no webhooks, polling"): compatible with the native path as long as the dispatcher delegates to installed agents and polls `list_issues(delegate=...)` / `agentSessions`; only a self-built assignable agent app needs a webhook receiver.

## 11. Recommendation for the three decisions

(a) Plan: the brief's criterion 1 (5 teams) is impossible on Free (2 teams, live-verified). Basic ($10/user, 4 humans = $40/month yearly billing) gives exactly 5 teams, unlimited issues, admin roles and coding sessions, which covers the brief. Business ($16, $64/month) adds unlimited teams, triage rules, SLAs, Asks, guests, Triage Intelligence and (per docs) Loops; none of those is on the brief's critical path because the dispatcher does the routing. Cheapest path that meets the brief: Basic. If the requester wants Loops or triage rules to auto-delegate on intake, Business. Try `organizationStartTrialForPlan` only as a deliberate one-shot; terms are undocumented. Shrinking to 2 teams is the only zero-cost option and breaks criterion 1.

(b) Identity: use the native path for identity, keep the brief's polling for orchestration. Concretely: dispatcher = Claude Code under the human MCP user (API key as Bearer works for MCP); coding steps delegated to app users (Codex now, Cursor after account linking, Linear coding sessions once on Basic with GitHub code access); the dispatcher polls `list_issues(delegate=...)` and reads `agentSessions.activities` for evidence. Keep `agent/*` labels only for the roles that stay human-account work (scoping, review, QA comments signed "[QA-agent / Codex]"). Do not build a webhook receiver for the demo.

(c) Vendor tiers: nothing needs buying for Linear itself. Link the ChatGPT Pro account in Linear (Codex) and the Cursor account (Cursor) from the requester's Linear profile; confirm the Cursor plan is paid before promising the Cursor lane. Fund Linear AI credits (minimum $10) only if coding sessions are part of the demo. Claude Max 20x is sufficient for the orchestrator.

## 12. Probe log (all side effects)

- Created team "ZZ Probe A" (key ZZA, id 5f339642-05ae-4fdc-aeee-55091f7e9e18), deleted immediately; "ZZ Probe B" refused by plan limit.
- Created FC-148 (delegate Linear -> refused; delegate Codex -> session 5e01ce95-9dd1-4cab-bbc3-8d6f3044d058, awaitingInput) and FC-149 (delegate Cursor -> session complete). Both issues archived (`issueArchive` success); sessions remain visible in the UI as evidence.
- No trial started, no plan changed, no credits bought, no webhooks created.
