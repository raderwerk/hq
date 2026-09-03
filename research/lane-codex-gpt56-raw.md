Reading additional input from stdin...
2026-09-02T12:08:56.918075Z ERROR codex_models_manager::manager: failed to load models cache: missing field `supports_parallel_tool_calls` at line 97 column 5
2026-09-02T12:08:58.075201Z  WARN codex_core_plugins::manifest: ignoring hooks: expected a string, string array, object, or object array; found object
2026-09-02T12:08:58.079100Z  WARN codex_core_plugins::manifest: ignoring hooks: expected a string, string array, object, or object array; found object
2026-09-02T12:08:58.080553Z  WARN codex_core_plugins::manifest: ignoring hooks: expected a string, string array, object, or object array; found object
2026-09-02T12:08:58.081075Z  WARN codex_core_plugins::manifest: ignoring hooks: expected a string, string array, object, or object array; found object
2026-09-02T12:08:58.164190Z  WARN codex_skills::interface: ignoring interface.icon_small: icon path with '..' must resolve under plugin assets/
2026-09-02T12:08:58.164229Z  WARN codex_skills::interface: ignoring interface.icon_large: icon path with '..' must resolve under plugin assets/
OpenAI Codex v0.147.0
--------
workdir: /Users/youp/Developer/Personal/Raderwerk/hq
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: read-only
reasoning effort: xhigh
reasoning summaries: none
session id: 01a06205-bbce-79a2-b1eb-200afc15795c
--------
user
Today is 2026-09-02. You are an independent analyst. Question: how feasible is an AI-run digital agency (agents that manage, execute, deliver, QA, sell and market web/e-commerce work, humans supervise) in September 2026, using Linear as the operating system and Claude/Codex/Cursor agents as workers? Use web search to ground claims in 2026 sources. Give: (1) a feasibility verdict with percentages per function (sales, marketing, PM/scoping, dev execution, QA, delivery/client comms, finance), (2) the 5 hardest blockers with evidence, (3) a concrete demo architecture that could be built in days, (4) 10 verifiable claims with URLs. Be skeptical, concrete, no hype. Answer in English, markdown, max 1200 words.
hook: SessionStart
hook: SessionStart Completed
codex
I’ll use the Context7 skill for current Linear/agent-platform documentation, then cross-check operational claims against 2026 primary sources and clearly label my percentage estimates as analyst judgments rather than measured benchmarks.
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "sed -n '1,240p' /Users/youp/.agents/skills/context7-mcp/SKILL.md" in /Users/youp/Developer/Personal/Raderwerk/hq
 succeeded in 0ms:
---
name: context7-mcp
description: This skill should be used when the user asks about libraries, frameworks, API references, or needs code examples. Activates for setup questions, code generation involving libraries, or mentions of specific frameworks like React, Vue, Next.js, Prisma, Supabase, etc.
---

When the user asks about libraries, frameworks, or needs code examples, use Context7 to fetch current documentation instead of relying on training data.

## When to Use This Skill

Activate this skill when the user:

- Asks setup or configuration questions ("How do I configure Next.js middleware?")
- Requests code involving libraries ("Write a Prisma query for...")
- Needs API references ("What are the Supabase auth methods?")
- Mentions specific frameworks (React, Vue, Svelte, Express, Tailwind, etc.)

## How to Fetch Documentation

### Step 1: Resolve the Library ID

Call `resolve-library-id` with:

- `libraryName`: The library name extracted from the user's question
- `query`: What to look up in the library's documentation (improves relevance ranking)

### Step 2: Select the Best Match

From the resolution results, choose based on:

- Exact or closest name match to what the user asked for
- Higher benchmark scores indicate better documentation quality
- If the user mentioned a version (e.g., "React 19"), prefer version-specific IDs

### Step 3: Fetch the Documentation

Call `query-docs` with:

- `libraryId`: The selected Context7 library ID (e.g., `/vercel/next.js`)
- `query`: What to look up in the library's documentation, scoped to a single concept

If the user's question spans multiple distinct concepts (e.g. routing and auth and caching), make a separate `query-docs` call per concept with the same library ID, unless the question is about how the concepts interact — combined queries dilute ranking and return shallow results for each topic.

### Step 4: Use the Documentation

Incorporate the fetched documentation into your response:

- Answer the user's question using current, accurate information
- Include relevant code examples from the docs
- Cite the library version when relevant

## Guidelines

- **Be specific**: Describe what to look up in the library's documentation, but keep each query to a single concept
- **One topic per query**: Split multi-topic questions into separate `query-docs` calls — resolve the library ID once, then query per concept, unless the question is about how the concepts interact
- **Version awareness**: When users mention versions ("Next.js 15", "React 19"), use version-specific library IDs if available from the resolution step
- **Prefer official sources**: When multiple matches exist, prefer official/primary packages over community forks

hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc 'rg -n -i "ai-agency|AI agency|TowMotive|Linear.*operating|agency" /Users/youp/.codex/memories/MEMORY.md | head -80' in /Users/youp/Developer/Personal/Raderwerk/hq
 succeeded in 0ms:
129:# Task Group: SEO meets Tech Orbit board workflow and internal agency POC
130:scope: MCP-only board planning and sequential ticket execution for the internal SEO meets Tech agency POC; distinct boards are snapshot-specific.
141:- SEO meets Tech - AI, BOQJPAKHTWQTYHT, board-113878, internal agency POC, Batavia, GA4, GSC, client profiles, MCP-only, 39907, 39910
156:- For the internal product, the user said: "het is echt een interne tool voor onze performancecollega's van ons agency" and described "Klant toevoegen → website(s) toevoegen → GA4/GSC koppelen → data synchroniseren → klantdashboard + AI-overzicht bekijken" -> model multi-client as internal client profiles with client/site mapping and server-side separation, not a customer portal. [Task 1]
453:# Task Group: TowMotive ticket 37371 work-order PDF design
455:applies_to: cwd=/Users/youp/Developer/Fightclub/Projects/TowMotive; reuse_rule=Re-fetch live definition; do not represent design as implemented.
461:- rollout_summaries/2026-08-24T08-29-32-6Js0-towmotive_ticket_37371_work_order_design.md (cwd=/Users/youp/Developer/Fightclub/Projects/TowMotive, rollout_path=/Users/youp/.codex/sessions/2026/08/24/rollout-2026-08-24T10-29-32-01a032e3-9c1e-7cd2-89ab-9a25af5cd0bc.jsonl, updated_at=2026-08-24T09:59:24+00:00, thread_id=01a032e3-9c1e-7cd2-89ab-9a25af5cd0bc, design `a5ace02`; no implementation)
473:- TowMotive umbrella is not Git: operate in portal/middleware separately. Workflow `YnAYKSNmZGzoAkwjMHtfL` accepts POST `{ dossierEntityId }`, uses `responseMode: onReceived`, produces `Werkplaatsbon` at `werkplaatsbon`; use middleware `/v2-integrations` base. Safely: baseline IDs, call once, poll read-only executions, resolve trusted URL; reserve `about:blank`, detach opener, then navigate. [Task 1]
505:# Task Group: TowMotive auth/session review
507:applies_to: cwd=/Users/youp/Developer/Fightclub/Projects/TowMotive; reuse_rule=Re-check each current diff/merge-base; findings snapshot-specific.
513:- rollout_summaries/2026-08-17T20-23-35-WD5v-re_review_auth_session_thermos_findings.md (cwd=/Users/youp/Developer/Fightclub/Projects/TowMotive, rollout_path=/Users/youp/.codex/sessions/2026/08/17/rollout-2026-08-17T22-23-35-01a01164-d3bf-7a90-9115-9559490dac41.jsonl, updated_at=2026-08-17T21:16:36+00:00, thread_id=01a01164-d3bf-7a90-9115-9559490dac41, five merge-blocking correctness/availability findings)

hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "sed -n '129,160p' /Users/youp/.codex/memories/MEMORY.md" in /Users/youp/Developer/Personal/Raderwerk/hq
 succeeded in 0ms:
# Task Group: SEO meets Tech Orbit board workflow and internal agency POC
scope: MCP-only board planning and sequential ticket execution for the internal SEO meets Tech agency POC; distinct boards are snapshot-specific.
applies_to: cwd=/Users/youp/Developer/Fightclub/Projects/AI/SEO meets Tech; reuse_rule=Reuse MCP-only, readback, and blocking practices for Orbit work; re-query board IDs, columns, and ticket state before writing.

## Task 1: Rescope the SEO meets Tech board to a small internal multi-client POC, partial

### rollout_summary_files

- rollout_summaries/2026-08-28T12-28-39-328w-orbit_poc_rescope_and_guarded_checklist_mcp.md (cwd=/Users/youp/Developer/Fightclub/Projects/AI/SEO meets Tech, rollout_path=/Users/youp/.codex/sessions/2026/08/28/rollout-2026-08-28T14-28-39-01a04857-f569-78c2-9c2a-b7188508da70.jsonl, updated_at=2026-08-28T14:17:16+00:00, thread_id=01a04857-f569-78c2-9c2a-b7188508da70, proposal only; board rescope not applied)

### keywords

- SEO meets Tech - AI, BOQJPAKHTWQTYHT, board-113878, internal agency POC, Batavia, GA4, GSC, client profiles, MCP-only, 39907, 39910

## Task 2: Establish safe sequential Orbit ticket processing and handle the first Ready tickets, partial

### rollout_summary_files

- rollout_summaries/2026-08-28T13-25-53-L00K-orbit_sequential_ticket_workflow_and_project_matt_pocock_ski.md (cwd=/Users/youp/Developer/Fightclub/Projects/AI/SEO meets Tech, rollout_path=/Users/youp/.codex/sessions/2026/08/28/rollout-2026-08-28T15-25-53-01a0488c-5de3-7c32-9092-13e35c43b236.jsonl, updated_at=2026-08-28T13:59:06+00:00, thread_id=01a0488c-5de3-7c32-9092-13e35c43b236, ticket 39920 moved to Review; 39921-39923 blocked)

### keywords

- SEO meets Tech - AI, BOYND87NFGYK3ZJ, board-113883, .orbit/config.json, orbit_setup_project, orbit_project_status, Ready, Review, Blocked, 39920, 39921, @[Youp Verkooijen|C1207606]

## User preferences

- When operating Orbit, the user corrected: "gebruik NIET de browser voor orbit, maar altijd MCP" / "je gebruikt de MCP ... je kan NIET browseruse doen" -> use Orbit MCP exclusively for reads and writes; do not fall back to browser automation. [Task 1][Task 2]
- For the internal product, the user said: "het is echt een interne tool voor onze performancecollega's van ons agency" and described "Klant toevoegen → website(s) toevoegen → GA4/GSC koppelen → data synchroniseren → klantdashboard + AI-overzicht bekijken" -> model multi-client as internal client profiles with client/site mapping and server-side separation, not a customer portal. [Task 1]
- The user asked to "rescope het bord ... kleingescopete POC" -> start with Batavia plus one second client, GA4/GSC, one dashboard selector, and bounded AI summaries; defer customer SSO, white-labeling, open AI chat, Semrush production, and heavy orchestration. [Task 1]
- For implementation tickets, the user required "1 voor 1" with subagents, `/code-reviews` and `/deslop` -> process Ready tickets sequentially and complete requested review/cleanup before advancing. [Task 2]
- When credentials or requirements are missing, the user wants a mention and the todo in Blocked -> ask only the missing question, use the official internal mention, and block only the affected todo. [Task 2]


2026-09-02T12:09:19.609327Z  WARN codex_rollout::list: state db discrepancy during find_thread_path_by_id_str_in_subdir: falling_back
hook: PreToolUse
hook: PreToolUse Completed
mcp: context7/resolve-library-id started
mcp: context7/resolve-library-id (completed)
hook: PreToolUse
hook: PreToolUse Completed
mcp: context7/query-docs started
mcp: context7/query-docs (completed)
codex
I’ve confirmed that Linear now exposes agent-session events, webhooks, and MCP-related controls—enough to serve as a control plane. The key question is therefore reliability and governance at the workflow edges, not whether the integrations exist. I’m checking those limits against 2026 evidence now.
hook: PreToolUse
hook: PreToolUse Completed
web search: 
2026-09-02T12:09:41.252868Z ERROR codex_core::tools::router: error=collab spawn failed: no thread with id: 01a06206-0fe7-7b50-901a-7a812816721f
web search: site:linear.app 2026 agents Linear Agent Sessions API webhook 2026 ...
hook: PreToolUse
hook: PreToolUse Completed
web search: 
web search: site:metr.org/blog 2026 coding agents productivity study developers agent July 2026 ...
hook: PreToolUse
hook: PreToolUse Completed
web search: 
web search: 2026 study AI sales agents conversion productivity field experiment sales representatives ...
hook: PreToolUse
hook: PreToolUse Completed
web search: 
web search: 2026 AI accounting agents finance automation study audit errors invoices ...
hook: PreToolUse
hook: PreToolUse Completed
web search: 
web search: 2026 "AI sales agent" field experiment autonomous sales leads paper ...
hook: PreToolUse
hook: PreToolUse Completed
web search: 
web search: site:docs.cursor.com/background-agent/api Cursor Background Agents API create agent webhook 2026 ...
hook: PreToolUse
hook: PreToolUse Completed
web search: 
web search: site:anthropic.com/news 2026 Claude Code agent SDK hooks teams enterprise security ...
hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "nl -ba /Users/youp/.codex/memories/MEMORY.md | sed -n '151,160p'" in /Users/youp/Developer/Personal/Raderwerk/hq
 succeeded in 0ms:
   151	
   152	## Reusable knowledge
   153	
   154	- Use Codex as conductor with bounded workers/review passes and honest fallback reporting. In this run Claude Code `2.1.227` existed, but `claude -p --model opus` and `--model fable` returned `Not logged in`; treat it as unavailable without account action and continue with Codex subagents. [Task 1]
   155	- `/private/tmp/tapps-overnight-awake.sh` used `caffeinate -i -m -s -t` with `launchctl submit`; after stopping, `launchctl` no longer found the job and `pmset -g assertions` showed no `PreventSystemSleep` assertion. [Task 1]
   156	
   157	## Failures and how to do differently
   158	
   159	- `caffeinate`/`launchctl` did not keep this Mac awake in practice -> never claim they guarantee wakefulness. The first attempt turned off the display before the explicit “go”; stage commands and wait for the final gate. [Task 1]
   160	

hook: PreToolUse
hook: PreToolUse Completed
exec
/bin/zsh -lc "nl -ba /Users/youp/.codex/memories/MEMORY.md | sed -n '110,190p'" in /Users/youp/Developer/Personal/Raderwerk/hq
 succeeded in 0ms:
   110	## Task 1: Harden post-merge delete-option handling, completed
   111	
   112	### rollout_summary_files
   113	
   114	- rollout_summaries/2026-08-28T14-34-17-62z2-tapps_foundation_guardrail_and_overnight_automation.md (cwd=/Users/youp/Developer/Personal/Tapps, rollout_path=/Users/youp/.codex/sessions/2026/08/28/rollout-2026-08-28T16-34-17-01a048ca-facb-7770-a88f-a15cc721f674.jsonl, updated_at=2026-08-30T10:07:16+00:00, thread_id=01a048ca-facb-7770-a88f-a15cc721f674, merged PR #21)
   115	
   116	### keywords
   117	
   118	- block-dangerous-git.sh, check-agent-setup.ts, 5048586, PR-21, clustered delete options, quoted options, separated -o, shellcheck, agents:check
   119	
   120	## User preferences
   121	
   122	- When review kept producing edge cases, the user said: “we blijven oneindig codex review dingen vinden ... ik wil niet 100x op die review shit wachten” -> use one focused review/fix pass and at most one targeted re-review; reject speculative scope expansion. [Task 1]
   123	
   124	## Reusable knowledge
   125	
   126	- `5048586` handles clustered/quoted delete options and separated `-o` values in `.claude/hooks/block-dangerous-git.sh`, with regression coverage in `scripts/check-agent-setup.ts`. Verification passed: `bun run agents:check`, `bun run check-types`, `shellcheck`, `git diff --check`, and GitHub Quality. PR #21 was squash-merged as `f1621175e3af2519f9cc78012cc38f78abfe25b9`; issue #20 closed, Project Done, all PR #19/#21 threads resolved, `initial-setup` unchanged. [Task 1]
   127	- In this repository, live PR/issue state and Project fields are authoritative; verify immediately before merge. [Task 1]
   128	
   129	## Failures and how to do differently
   130	
   131	- Regex-only command analysis can miss wrappers, aliases, `GIT_DIR` redirection, abbreviated options, quoting, and safe pipelines. Those adversarial findings were outside the accepted bounded follow-up scope; do not grow a concrete fix into endless fuzz review without explicit approval. [Task 1]
   132	
   133	# Task Group: Local overnight Codex conductor and macOS power automation
   134	scope: Local-first multi-agent overnight preparation, Claude availability boundaries, and explicitly gated Mac display/sleep changes.
   135	applies_to: cwd=/Users/youp/Developer/Personal/Tapps; reuse_rule=Conductor preferences are reusable; the `caffeinate` result is a Mac/time-specific failed attempt and must not be treated as a reliable wake method.
   136	
   137	## Task 1: Prepare overnight conductor and attempted sleep prevention, partial
   138	
   139	### rollout_summary_files
   140	
   141	- rollout_summaries/2026-08-28T14-34-17-62z2-tapps_foundation_guardrail_and_overnight_automation.md (cwd=/Users/youp/Developer/Personal/Tapps, rollout_path=/Users/youp/.codex/sessions/2026/08/28/rollout-2026-08-28T16-34-17-01a048ca-facb-7770-a88f-a15cc721f674.jsonl, updated_at=2026-08-30T10:07:16+00:00, thread_id=01a048ca-facb-7770-a88f-a15cc721f674, Claude unavailable; wake automation failed and was stopped)
   142	
   143	### keywords
   144	
   145	- overnight conductor, Claude Code, opus, fable, Not logged in, no remote control, caffeinate, launchctl submit, pmset -g assertions, PreventSystemSleep, displaysleepnow
   146	
   147	## User preferences
   148	
   149	- For local conductor work, the user required “niks aanpassen aan accounts ... nooit remote control” -> keep Claude optional; never run `/login`, account-management commands, `--remote-control`, `--cloud`, SSH, VNC, or browser automation. [Task 1]
   150	- “ik wil de ‘go’ geven” -> stage device-side effects and wait for explicit final confirmation before display/power changes. “Ik wil niet dat je het opnieuw probeert” -> stop permanently; do not retry or propose a wake workaround unless later requested. [Task 1]
   151	
   152	## Reusable knowledge
   153	
   154	- Use Codex as conductor with bounded workers/review passes and honest fallback reporting. In this run Claude Code `2.1.227` existed, but `claude -p --model opus` and `--model fable` returned `Not logged in`; treat it as unavailable without account action and continue with Codex subagents. [Task 1]
   155	- `/private/tmp/tapps-overnight-awake.sh` used `caffeinate -i -m -s -t` with `launchctl submit`; after stopping, `launchctl` no longer found the job and `pmset -g assertions` showed no `PreventSystemSleep` assertion. [Task 1]
   156	
   157	## Failures and how to do differently
   158	
   159	- `caffeinate`/`launchctl` did not keep this Mac awake in practice -> never claim they guarantee wakefulness. The first attempt turned off the display before the explicit “go”; stage commands and wait for the final gate. [Task 1]
   160	
   161	# Task Group: SEO meets Tech Orbit board workflow and internal agency POC
   162	scope: MCP-only board planning and sequential ticket execution for the internal SEO meets Tech agency POC; distinct boards are snapshot-specific.
   163	applies_to: cwd=/Users/youp/Developer/Fightclub/Projects/AI/SEO meets Tech; reuse_rule=Reuse MCP-only, readback, and blocking practices for Orbit work; re-query board IDs, columns, and ticket state before writing.
   164	
   165	## Task 1: Rescope the SEO meets Tech board to a small internal multi-client POC, partial
   166	
   167	### rollout_summary_files
   168	
   169	- rollout_summaries/2026-08-28T12-28-39-328w-orbit_poc_rescope_and_guarded_checklist_mcp.md (cwd=/Users/youp/Developer/Fightclub/Projects/AI/SEO meets Tech, rollout_path=/Users/youp/.codex/sessions/2026/08/28/rollout-2026-08-28T14-28-39-01a04857-f569-78c2-9c2a-b7188508da70.jsonl, updated_at=2026-08-28T14:17:16+00:00, thread_id=01a04857-f569-78c2-9c2a-b7188508da70, proposal only; board rescope not applied)
   170	
   171	### keywords
   172	
   173	- SEO meets Tech - AI, BOQJPAKHTWQTYHT, board-113878, internal agency POC, Batavia, GA4, GSC, client profiles, MCP-only, 39907, 39910
   174	
   175	## Task 2: Establish safe sequential Orbit ticket processing and handle the first Ready tickets, partial
   176	
   177	### rollout_summary_files
   178	
   179	- rollout_summaries/2026-08-28T13-25-53-L00K-orbit_sequential_ticket_workflow_and_project_matt_pocock_ski.md (cwd=/Users/youp/Developer/Fightclub/Projects/AI/SEO meets Tech, rollout_path=/Users/youp/.codex/sessions/2026/08/28/rollout-2026-08-28T15-25-53-01a0488c-5de3-7c32-9092-13e35c43b236.jsonl, updated_at=2026-08-28T13:59:06+00:00, thread_id=01a0488c-5de3-7c32-9092-13e35c43b236, ticket 39920 moved to Review; 39921-39923 blocked)
   180	
   181	### keywords
   182	
   183	- SEO meets Tech - AI, BOYND87NFGYK3ZJ, board-113883, .orbit/config.json, orbit_setup_project, orbit_project_status, Ready, Review, Blocked, 39920, 39921, @[Youp Verkooijen|C1207606]
   184	
   185	## User preferences
   186	
   187	- When operating Orbit, the user corrected: "gebruik NIET de browser voor orbit, maar altijd MCP" / "je gebruikt de MCP ... je kan NIET browseruse doen" -> use Orbit MCP exclusively for reads and writes; do not fall back to browser automation. [Task 1][Task 2]
   188	- For the internal product, the user said: "het is echt een interne tool voor onze performancecollega's van ons agency" and described "Klant toevoegen → website(s) toevoegen → GA4/GSC koppelen → data synchroniseren → klantdashboard + AI-overzicht bekijken" -> model multi-client as internal client profiles with client/site mapping and server-side separation, not a customer portal. [Task 1]
   189	- The user asked to "rescope het bord ... kleingescopete POC" -> start with Batavia plus one second client, GA4/GSC, one dashboard selector, and bounded AI summaries; defer customer SSO, white-labeling, open AI chat, Semrush production, and heavy orchestration. [Task 1]
   190	- For implementation tickets, the user required "1 voor 1" with subagents, `/code-reviews` and `/deslop` -> process Ready tickets sequentially and complete requested review/cleanup before advancing. [Task 2]

hook: PreToolUse
hook: PreToolUse Completed
web search: 
web search: 
hook: PreToolUse
hook: PreToolUse Completed
web search: 
web search: 'Coding sessions in Linear'
hook: PreToolUse
hook: PreToolUse Completed
web search: 
web search: 
hook: PreToolUse
hook: PreToolUse Completed
web search: 
web search: 
codex
# Feasibility verdict — 2 September 2026

**Commercially feasible for a narrow, productized agency; not feasible as a self-governing company.** My estimate is **~60% of total workload safely delegable** with human supervision: nearer **70–75%** for standardized sites, Shopify builds and maintenance, but **~40%** for bespoke commerce, legacy integrations or politically complex clients.

Percentages mean *share of work safely delegated*, not model accuracy or headcount eliminated.

| Function | Delegable | Human responsibility that remains |
|---|---:|---|
| Sales | **35%** | Discovery, trust, pricing, negotiation, closing |
| Marketing | **60%** | Positioning, taste, brand approval, claims |
| PM/scoping | **45%** | Resolving ambiguity, estimates, scope/change acceptance |
| Development | **75%** | Architecture, unusual integrations, merge/release |
| QA | **65%** | Exploratory testing, product judgment, final acceptance |
| Delivery/client comms | **50%** | Bad news, conflict, scope changes, relationship |
| Finance | **55%** | Bank actions, refunds, tax filings, final books |

A “lights-out” agency would be only **~20% feasible**. The viable model is **humans managing exceptions, judgment and liability while agents produce most artifacts and first passes**.

## Five hardest blockers

1. **Intent is harder than implementation.** Analysis of roughly 400,000 Claude Code sessions found humans still made most planning decisions; domain expertise improved success and error recovery. Agents execute a clear brief well but cannot reliably discover what the client actually needs. [Anthropic, June 2026](https://www.anthropic.com/research/claude-code-expertise)

2. **Capability benchmarks overstate dependable delivery.** METR found agents capable of some human-weeks-long coding tasks, especially where progress was cheaply verifiable, yet also observed obvious bugs, poor strategic judgment and constraint-violating “cheats.” Its measured early-2026 productivity uplift was only roughly 4–20%, with severe selection uncertainty. [METR risk report](https://metr.org/blog/2026-05-19-frontier-risk-report/), [productivity update](https://metr.org/blog/2026-02-24-uplift-update/)

3. **Permissions create a real attack surface.** Cursor’s own documentation says remote agents can receive GitHub write access, internet access and automatic terminal execution, explicitly warning about prompt-injection-driven exfiltration. Production, client data and credentials therefore require isolated environments, least privilege and approval gates. [Cursor security documentation](https://docs.cursor.com/background-agent); OpenAI describes similar requirements for boundaries, approvals and telemetry. [OpenAI, May 2026](https://openai.com/index/running-codex-safely/)

4. **Client-facing mistakes carry disproportionate cost.** A 2026 Alibaba field experiment found AI-assisted support faster and subjectively better, but no improvement in objective retrial rates; top agents sometimes performed worse. Marketing research also found AI disclosures could produce neutral or negative reactions. EU Article 50 transparency obligations have applied since 2 August 2026. [Alibaba study](https://arxiv.org/abs/2603.29888), [marketing study](https://link.springer.com/article/10.1057/s41270-026-00534-7), [European Commission](https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems)

5. **Supervision and exception-handling determine the economics.** OpenAI reports humans became overloaded beyond roughly three to five concurrent coding sessions. In finance, 86% of surveyed CFOs had encountered inaccurate or hallucinated data, while 97% considered human oversight at least somewhat critical. Cheap generation does not imply cheap accountable delivery. [OpenAI Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/), [Journal of Accountancy](https://www.journalofaccountancy.com/news/2026/feb/agentic-ai-is-handling-more-finance-work-but-can-cfos-trust-it/)

## Demo architecture buildable in 3–5 days

```text
Lead/intake
   ↓
Linear state machine
   ↓ webhook
Small router + idempotency/audit ledger
   ↓
Claude Code | Codex | Cursor Cloud Agent
   ↓
GitHub branch/PR → CI → preview deployment
   ↓
Independent agent QA → Human approval → Client review
   ↓
Delivery → Draft invoice → Human finance approval
```

Use Linear statuses: `Lead → Qualified → Scope Draft → Awaiting Approval → Build → Agent QA → Human QA → Client Review → Delivered → Invoiced`.

Implementation rules:

- Templates require objectives, exclusions, acceptance tests, brand assets, data classification and budget.
- Labels select the worker; each run gets an isolated workspace and writes only branches, PRs, artifacts and Linear updates.
- Deterministic QA runs type-checking, tests, Playwright flows, accessibility, Lighthouse, dependency/secrets scans and screenshot comparison.
- A different agent reviews the builder’s output, but never self-approves it.
- Humans approve the quote/SOW, production merge, non-routine client messages, refunds/payments and tax actions.
- Keep secrets, financial records and execution idempotency outside Linear. Linear is the visible control plane, not the transactional database.
- Do not build a bespoke multi-agent framework initially: Linear already launches Claude Code/Codex sessions, while Cursor Automations can trigger from Linear or webhooks.

## Ten verifiable 2026 claims

1. Linear added native Claude Code and Codex coding sessions in June. [Source](https://linear.app/changelog/2026-06-11-coding-sessions)
2. Linear added environment setup, browser testing and screenshots in August. [Source](https://linear.app/changelog/2026-08-20-coding-environments)
3. OpenAI published a Linear-as-control-plane Codex architecture called Symphony. [Source](https://openai.com/index/open-source-codex-orchestration-symphony/)
4. Cursor Automations can trigger from Linear and webhooks in cloud sandboxes. [Source](https://cursor.com/changelog/03-05-26)
5. METR observed impressive long-horizon ability alongside materially worse judgment than experts. [Source](https://metr.org/blog/2026-05-19-frontier-risk-report/)
6. METR says current developer-productivity magnitude remains difficult to estimate reliably. [Source](https://metr.org/blog/2026-02-24-uplift-update/)
7. Humans still make most planning decisions in typical Claude Code sessions. [Source](https://www.anthropic.com/research/claude-code-expertise)
8. Academic sales literature still lacks mature performance evidence for autonomous sales agents. [Source](https://www.sciencedirect.com/science/article/abs/pii/S0148296325006228)
9. Human-assisted AI improved service speed without improving one objective quality measure. [Source](https://arxiv.org/abs/2603.29888)
10. Most surveyed CFOs report both AI-generated inaccuracies and a need for oversight. [Source](https://www.journalofaccountancy.com/news/2026/feb/agentic-ai-is-handling-more-finance-work-but-can-cfos-trust-it/)


hook: Stop
hook: Stop Completed
tokens used
128.302
# Feasibility verdict — 2 September 2026

**Commercially feasible for a narrow, productized agency; not feasible as a self-governing company.** My estimate is **~60% of total workload safely delegable** with human supervision: nearer **70–75%** for standardized sites, Shopify builds and maintenance, but **~40%** for bespoke commerce, legacy integrations or politically complex clients.

Percentages mean *share of work safely delegated*, not model accuracy or headcount eliminated.

| Function | Delegable | Human responsibility that remains |
|---|---:|---|
| Sales | **35%** | Discovery, trust, pricing, negotiation, closing |
| Marketing | **60%** | Positioning, taste, brand approval, claims |
| PM/scoping | **45%** | Resolving ambiguity, estimates, scope/change acceptance |
| Development | **75%** | Architecture, unusual integrations, merge/release |
| QA | **65%** | Exploratory testing, product judgment, final acceptance |
| Delivery/client comms | **50%** | Bad news, conflict, scope changes, relationship |
| Finance | **55%** | Bank actions, refunds, tax filings, final books |

A “lights-out” agency would be only **~20% feasible**. The viable model is **humans managing exceptions, judgment and liability while agents produce most artifacts and first passes**.

## Five hardest blockers

1. **Intent is harder than implementation.** Analysis of roughly 400,000 Claude Code sessions found humans still made most planning decisions; domain expertise improved success and error recovery. Agents execute a clear brief well but cannot reliably discover what the client actually needs. [Anthropic, June 2026](https://www.anthropic.com/research/claude-code-expertise)

2. **Capability benchmarks overstate dependable delivery.** METR found agents capable of some human-weeks-long coding tasks, especially where progress was cheaply verifiable, yet also observed obvious bugs, poor strategic judgment and constraint-violating “cheats.” Its measured early-2026 productivity uplift was only roughly 4–20%, with severe selection uncertainty. [METR risk report](https://metr.org/blog/2026-05-19-frontier-risk-report/), [productivity update](https://metr.org/blog/2026-02-24-uplift-update/)

3. **Permissions create a real attack surface.** Cursor’s own documentation says remote agents can receive GitHub write access, internet access and automatic terminal execution, explicitly warning about prompt-injection-driven exfiltration. Production, client data and credentials therefore require isolated environments, least privilege and approval gates. [Cursor security documentation](https://docs.cursor.com/background-agent); OpenAI describes similar requirements for boundaries, approvals and telemetry. [OpenAI, May 2026](https://openai.com/index/running-codex-safely/)

4. **Client-facing mistakes carry disproportionate cost.** A 2026 Alibaba field experiment found AI-assisted support faster and subjectively better, but no improvement in objective retrial rates; top agents sometimes performed worse. Marketing research also found AI disclosures could produce neutral or negative reactions. EU Article 50 transparency obligations have applied since 2 August 2026. [Alibaba study](https://arxiv.org/abs/2603.29888), [marketing study](https://link.springer.com/article/10.1057/s41270-026-00534-7), [European Commission](https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems)

5. **Supervision and exception-handling determine the economics.** OpenAI reports humans became overloaded beyond roughly three to five concurrent coding sessions. In finance, 86% of surveyed CFOs had encountered inaccurate or hallucinated data, while 97% considered human oversight at least somewhat critical. Cheap generation does not imply cheap accountable delivery. [OpenAI Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/), [Journal of Accountancy](https://www.journalofaccountancy.com/news/2026/feb/agentic-ai-is-handling-more-finance-work-but-can-cfos-trust-it/)

## Demo architecture buildable in 3–5 days

```text
Lead/intake
   ↓
Linear state machine
   ↓ webhook
Small router + idempotency/audit ledger
   ↓
Claude Code | Codex | Cursor Cloud Agent
   ↓
GitHub branch/PR → CI → preview deployment
   ↓
Independent agent QA → Human approval → Client review
   ↓
Delivery → Draft invoice → Human finance approval
```

Use Linear statuses: `Lead → Qualified → Scope Draft → Awaiting Approval → Build → Agent QA → Human QA → Client Review → Delivered → Invoiced`.

Implementation rules:

- Templates require objectives, exclusions, acceptance tests, brand assets, data classification and budget.
- Labels select the worker; each run gets an isolated workspace and writes only branches, PRs, artifacts and Linear updates.
- Deterministic QA runs type-checking, tests, Playwright flows, accessibility, Lighthouse, dependency/secrets scans and screenshot comparison.
- A different agent reviews the builder’s output, but never self-approves it.
- Humans approve the quote/SOW, production merge, non-routine client messages, refunds/payments and tax actions.
- Keep secrets, financial records and execution idempotency outside Linear. Linear is the visible control plane, not the transactional database.
- Do not build a bespoke multi-agent framework initially: Linear already launches Claude Code/Codex sessions, while Cursor Automations can trigger from Linear or webhooks.

## Ten verifiable 2026 claims

1. Linear added native Claude Code and Codex coding sessions in June. [Source](https://linear.app/changelog/2026-06-11-coding-sessions)
2. Linear added environment setup, browser testing and screenshots in August. [Source](https://linear.app/changelog/2026-08-20-coding-environments)
3. OpenAI published a Linear-as-control-plane Codex architecture called Symphony. [Source](https://openai.com/index/open-source-codex-orchestration-symphony/)
4. Cursor Automations can trigger from Linear and webhooks in cloud sandboxes. [Source](https://cursor.com/changelog/03-05-26)
5. METR observed impressive long-horizon ability alongside materially worse judgment than experts. [Source](https://metr.org/blog/2026-05-19-frontier-risk-report/)
6. METR says current developer-productivity magnitude remains difficult to estimate reliably. [Source](https://metr.org/blog/2026-02-24-uplift-update/)
7. Humans still make most planning decisions in typical Claude Code sessions. [Source](https://www.anthropic.com/research/claude-code-expertise)
8. Academic sales literature still lacks mature performance evidence for autonomous sales agents. [Source](https://www.sciencedirect.com/science/article/abs/pii/S0148296325006228)
9. Human-assisted AI improved service speed without improving one objective quality measure. [Source](https://arxiv.org/abs/2603.29888)
10. Most surveyed CFOs report both AI-generated inaccuracies and a need for oversight. [Source](https://www.journalofaccountancy.com/news/2026/feb/agentic-ai-is-handling-more-finance-work-but-can-cfos-trust-it/)


