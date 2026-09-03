# Lane 03 — xAI (SpaceXAI) / Google / Cursor / Devin / Factory / Replit / Lovable / Manus

Research note for the "AI-run digital agency" feasibility study. Snapshot date: **2026-09-02**.
Scope: what these vendors actually ship today for autonomous/agentic work, what it costs, and how reliable it is, with an eye on a Linear-driven agency demo.

Method: 20 web searches plus ~60 direct fetches of primary pages (vendor docs, changelogs, pricing pages, launch blogs, METR/arXiv). Every claim below carries a URL and a source date. Confidence is stated honestly; anything I could not open or cross-check is marked `low` or listed under "Not verified".

---

## 0. TL;DR

- **"Grok Bot" is a real product.** xAI (now "SpaceXAI" after the February 2026 SpaceX acquisition, per VentureBeat) launched **Grok Bot** on 2026-08-11: persistent "AI teammate" agents that each run on their own cloud computer, sign into tools/inboxes/websites, run routines on a schedule, coordinate in group chats, and pause for human approval. It is an **early beta**, available to SuperGrok tiers and to **Cursor Pro/Pro+/Ultra and Teams** subscribers; pricing is **not disclosed** and enterprise is waitlist-only. The requester's phrase most likely refers to this, not to Grok-in-X or Grok Build.
- **Grok 4.6** (2026-08-12) is a 500k-context model with `low/medium/high/xhigh` effort, $2/$6 per 1M tokens, "jointly trained by Cursor and SpaceXAI" per Cursor's docs, and sits in Cursor's first-party "Cursor Models" pool. It is competitive on knowledge-work benchmarks (GDPVal-AA, AA-Briefcase) but **trails GPT-5.6 Sol and Fable 5 on agentic coding** (DeepSWE 65.9 vs 73/70; Terminal-Bench v3.0 26% vs 34.6/34.1) on xAI's own launch page.
- **Grok Build** (terminal coding agent) went beta 2026-05 -> open source Apache-2.0 2026-07-16 -> 1.0 on 2026-08-07. Up to 8 parallel subagents in git worktrees, headless mode, MCP, Agent Client Protocol. Self-reported SWE-bench Verified 70.8% (May 2026).
- **Google** has the broadest "agent OS" surface: Antigravity 2.0 desktop + CLI + SDK + a Gemini-API "managed agent" (`antigravity-preview-05-2026`, default Gemini 3.7 Flash, cron triggers, hooks, PAYG ~$0.25–$5+ per interaction), **Teamwork** (`/teamwork-preview`, multi-agent runs "over hours or days", all paid plans), and **Jules** (async coding agent, 15/100/300 tasks per day by tier, scheduled tasks). Google's Pro model line is stuck at **Gemini 3.1 Pro (preview)**; the Flash line moved to **3.7 Flash** (stable, 2026-08-13). Gemini 3.5 Pro was announced at I/O but is not on the model list. Project Mariner was discontinued 2026-05-04.
- **Cursor** is the most Linear-native of the bunch: assign an issue to "Cursor" or `@Cursor` in a comment -> cloud agent -> PR -> status back to Linear. Automations trigger on schedule/Slack/Linear/GitHub/PagerDuty/webhooks with a memory tool. Cloud agents got multi-repo envs (May 13), "Subscriptions" + `/goal` long-lived objectives (Aug 19), no-SCM start (Aug 27), Gmail/Drive/Calendar plugins (Aug 3). Teams: Standard $40, Premium $120 (5x usage).
- **Devin** rule of thumb from its own docs: good for tasks a human does in **~3 hours**; struggles with ambiguous requirements and mid-task scope changes. Cognition reports **67% of Devin PRs merged** (up from 34%). SWE-1.7 (2026-07-08) numbers are self-reported.
- **Factory** (Series C $150M at $1.5B, April 2026) is pushing "software factories": coordinator + specialised droids, Droid Computers, personas for Product/Design/Marketing/Sales/Ops, and connectors incl. **Linear, Slack, Notion, Figma, Stripe, Salesforce**. Its own 2026-08-27 research: single-agent median 56.7% on large tasks (Fable 5) -> 89.3% with an orchestrator + independent validator system, at ~14x the cost.
- **Replit Agent 4** deliberately moved *away* from "runs for hours on its own" (Agent 3) toward human-in-the-loop parallel tasks. **Lovable** is credit-priced, unlimited seats, front-end/Supabase oriented. **Manus** survived a blocked Meta acquisition and is independent again as of 2026-08-11; its reliability/billing reputation is poor (secondary sources).
- **Reliability reality check:** METR's best public 50% time horizon is ~11.3 h for GPT-5.6 Sol (CI 5–40 h), with the highest cheating rate METR has seen in a public model; measurements above ~16 h are unreliable. Princeton (ICML 2026): capability gains have yielded only small reliability gains. Enterprise-task consistency drops from 60% single-run to 25% over 8 runs. TheAgentCompany (simulated software company, 175 tasks): best agent 30.3% full completion. Nobody has published a number for "agents run an agency end to end".

---

## 1. xAI / SpaceXAI

### 1.1 What does "Grok Bot" refer to?

Candidates: (a) Grok in X/X app chatbot, (b) Grok Build (CLI coding agent), (c) **Grok Bot** (persistent cloud agents, launched 2026-08-11), (d) Grok 4.6 inside Cursor.

Verdict: **(c)**. "Grok Bot" is the literal product name of xAI's always-on agent offering, launched three weeks before the requester wrote the prompt, and it is bundled into the Cursor plans the requester already uses. Confidence: high.

### 1.2 Grok Bot (early beta, 2026-08-11)

Source: https://x.ai/news/introducing-grok-bot (2026-08-11); https://www.infoq.com/news/2026/08/grok-bot-agent/ (2026-08-17); https://docs.x.ai/developers/release-notes (Aug 2026); https://composio.dev/content/guide-to-frok-bot (2026-08-20, hands-on, secondary).

- "Durable AI teammates that work on a persistent cloud computer, with messaging, approvals, connectors, and routines" (xAI release notes).
- Each Bot has its own cloud computer, runs 24/7 independent of the user, works across apps/inboxes/websites incl. tools without clean APIs (browser UI), remembers preferences, can be **taught by observation** (demonstrate once, saved as a reusable routine), runs **routines on a schedule or after an event**, and supports **multi-bot group chats** that divide work and ask the human for decisions.
- **Human approval gates** for sensitive actions (sending messages, publishing, deleting, purchasing, changing production); humans keep passwords/2FA/CAPTCHAs.
- Eligible plans: SuperGrok, SuperGrok Plus, SuperGrok Heavy; **Cursor Pro, Pro+, Ultra; Cursor Teams Standard and Premium**. Usage is metered separately from existing plan allocations. **Price not disclosed.** Enterprise = waitlist.
- Connectors named in hands-on coverage: GitHub, Slack, Gmail, **Linear**, Salesforce, Notion, plus 1,000+ apps via Composio.
- Hands-on caveats (Composio, secondary): weekly usage limit can be exceeded mid-task and the agent **gets stuck**; browser automation hits CAPTCHAs/blocks; all Bots of one user **share one cloud computer** (files, browser sessions, CLI credentials are visible across your Bot roster), so Bots are not security boundaries.
- Third-party claims of "$120 per seat" for Grok Bot appear to conflate it with Cursor's Teams Premium seat. Treat as unverified (low).

### 1.3 Grok 4.6 (2026-08-12)

Sources: https://x.ai/news/grok-4-6 (2026-08-12); https://docs.x.ai/developers/release-notes (Aug 2026); https://cursor.com/blog/grok-4-6 (2026-08-12); https://cursor.com/docs/models/grok-4-6; https://cursor.com/docs/models; https://venturebeat.com/technology/spacexai-debuts-grok-4-6-... (2026-08-12).

- 500k context, text+image in, text out, no output cap. Effort: `low / medium / high (default) / xhigh`.
- Pricing: $2 / $0.50 cached / $6 per 1M tokens under 200k prompt tokens; $4 / $1 / $12 above 200k. "Fast" variant at 2x.
- Available in Cursor (desktop, web, iOS, CLI, SDK), Grok Build, Grok Bot, xAI API, OpenRouter, Vercel, Cloudflare. 2x included usage in Cursor/Grok Build for the first week.
- Cursor docs: Grok 4.6 and 4.5 are "jointly trained by Cursor and SpaceXAI" and live in the first-party **Cursor Models** pool with Composer 2.5. On Cursor Start (India) it is fixed at medium effort.
- Benchmarks on xAI's page (Grok 4.6 high vs GPT-5.6 Sol max vs Fable 5 max): AA Intelligence Index 61 / 61 / 62; GDPVal-AA v2 1753 / 1728 / 1741; CursorBench v3.2 69.9 / 67.2 / 70.5; **DeepSWE v1.1 65.9 / 73 / 70**; FrontierCode 61.3 / 60.6 / 63.6; APEX-Agents 57.5 / 56.7 / 59.2; **Terminal-Bench v3.0 26 / 34.6 / 34.1**; AA-Briefcase 1577 / 1502 / 1574. VentureBeat notes xAI "used the best self-reported or publicly available results", so it is not a controlled comparison.
- Positioning: strong on knowledge-work/document benchmarks and "first passes for visual and interactive projects"; **weaker than the top two on long agentic coding**. For an agency demo Grok 4.6 xhigh is a credible cheap second opinion / knowledge-work worker rather than the primary coding engine.
- Company: xAI was acquired by SpaceX in February 2026 and now brands as SpaceXAI (VentureBeat, 2026-08-12). Confidence: medium-high.

### 1.4 Grok Build (CLI coding agent)

Sources: https://github.com/xai-org/grok-build (Apache-2.0, no external contributions); https://en.wikipedia.org/wiki/Grok_Build; https://www.buildfastwithai.com/blogs/grok-build-xai-cli-ai-agents-2026 (2026-05-26); https://appwrite.io/blog/post/grok-build-open-source; https://pasqualepillitteri.it/en/news/10006/grok-build-1-0-xai-leaves-beta.

- Timeline: early beta 2026-05-14 (SuperGrok Heavy $299/mo) -> 2026-05-25 all SuperGrok / X Premium+ -> open-sourced Apache-2.0 on 2026-07-16 (with data retention off by default) -> **1.0 on 2026-08-07**. ~10 weeks beta, ~100 updates. (Dates from Wikipedia + secondary press; medium.)
- Features (repo README): full-screen TUI, file edit/shell/web search, long-running task management, **headless mode for scripting/CI**, **Agent Client Protocol** (editor embedding), MCP, skills/plugins. Secondary: plan -> search -> build stages, **up to 8 concurrent subagents each in its own git worktree**.
- Self-reported SWE-bench Verified **70.8%** (2026-05-15). Medium confidence; not independently verified.
- Repo accepts no issues/PRs from outside, so "open source" is inspectability, not community.

---

## 2. Cursor

Sources: https://cursor.com/pricing; https://cursor.com/blog/teams-pricing-june-2026 (2026-06-01); https://cursor.com/docs/integrations/linear; https://cursor.com/changelog/03-05-26 (2026-03-05); https://cursor.com/changelog/05-13-26 (2026-05-13); https://cursor.com/changelog (Aug 2026 entries); https://cursor.com/cloud; https://cursor.com/bugbot; https://cursor.com/docs/cli/overview; https://cursor.com/docs/models.

### 2.1 Linear integration (directly relevant to the demo)
- Assign an issue to **"Cursor"** in the assignee field or write `@Cursor <instruction>` in a comment. The cloud agent analyses the issue, **filters out non-development work**, creates a branch/PR automatically, and posts **real-time status updates in Linear**.
- Repo/branch/model selection via inline syntax `[repo=owner/repo]`, parent/child labels, project labels, or dashboard defaults.
- Requirements: Cursor admin installs it, a repository provider connection is required for PR creation, **usage-based pricing must be enabled**. Limitation quoted: "Linear requires a human assignee for rules to fire" (so Linear automations cannot themselves hand work to Cursor without a human assignee in the loop).

### 2.2 Automations and cloud agents
- **Automations** (2026-03-05): always-on agents in cloud sandboxes triggered by **schedule, Slack, Linear, GitHub, PagerDuty, webhooks**; use configured MCPs/models; a **memory tool** retains learnings across runs; marketplace templates.
- **Cloud agents** (May 13, 2026, v3.4): multi-repo environments, Dockerfile builds with scoped build secrets, 70% faster layer caching, environment version history + rollback, audit log, per-environment secrets and egress controls, agent-led setup.
- Aug 2026: Aug 3 Google Workspace plugins (**Gmail, Drive, Calendar**); Aug 13 3x faster time-to-first-token; Aug 17 "Origin" code hosting (early beta); Aug 19 **Subscriptions** (monitor PRs / Slack threads) and **`/goal`** long-lived objectives; Aug 27 cloud agents no longer need a connected SCM.
- Cloud agents can be spawned from desktop, mobile, Slack/Teams, Linear/Jira, Automations; they can control remote desktops, test their own work, and return videos/screenshots as artifacts.
- Cursor CLI: interactive plus `print` mode for CI (`agent -p "..." --output-format text`), `--model` flag, plan mode.
- Bugbot: "70%+ of flags get resolved before merge", "more than half of the bugs we find are ultimately fixed". A changelog-derived figure of 0.7 bugs/run at 79% resolution (default effort) appeared in search results but I could not open the entry: low.

### 2.3 Pricing (verified pieces)
- Hobby free; **Pro $20/mo**; Pro+ (3x agent limits) and Ultra (20x) exist (their prices were not captured in my fetch; widely reported as $60/$200: low).
- **Teams Standard $40/mo** ($32 annual); **Teams Premium $120/mo** ($96 annual) with 5x the included usage; two separate usage pools (first-party Auto/Composer 2.5 vs third-party API models); effective July 1, 2026 for renewals.
- Model prices inside Cursor: Grok 4.6/4.5 $2/$6, Composer 2.5 $0.5/$2.5, third-party models at API rates plus a **$0.25/1M Cursor Token Rate surcharge**. Third-party list includes Claude Opus 5/Sonnet 5, GPT-5.4/5.5, Gemini up to 3.7 Flash, Kimi K3, GLM 5.2.
- Grok Bot is listed as included with the Individual tiers on the pricing page.

---

## 3. Google

Sources: https://antigravity.google/blog/google-io-2026 (2026-05-19); https://antigravity.google/blog/changes-to-antigravity-plans (2026-05-19); https://antigravity.google/blog/introducing-google-antigravity-cli (2026-05-19); https://antigravity.google/blog/teamwork-when-ai-becomes-a-research-partner (2026-08-27); https://blog.google/innovation-and-ai/technology/developers-tools/antigravity-teamwork-multi-agent/ (2026-08-31); https://antigravity.google/blog/gemini-3-7-flash-in-google-antigravity (2026-08-13); https://ai.google.dev/gemini-api/docs/antigravity-agent (updated 2026-08-26); https://blog.google/innovation-and-ai/technology/developers-tools/expanding-managed-agents-gemini-api-3-6-flash-hooks/ (2026-07-28); https://ai.google.dev/gemini-api/docs/models; https://jules.google/docs/usage-limits/; https://developers.googleblog.com/jules-gemini-3/ (2025-11-19); https://blog.google/innovation-and-ai/technology/developers-tools/jules-proactive-updates/ (2025-12-10); https://one.google.com/intl/en/about/google-ai-plans/; https://en.wikipedia.org/wiki/Project_Mariner; https://en.wikipedia.org/wiki/Google_Antigravity.

### 3.1 Models (Gemini 3.x)
- Current Gemini API list: **Gemini 3.7 Flash (stable, "latest and most capable Flash, built for complex coding")**, 3.6 Flash, 3.5 Flash, 3.5 Flash-Lite, 3.1 Flash-Lite, **3.1 Pro (preview)**, 3 Flash (preview). **No Gemini 3.5 Pro on the list** even though the 3.5 series was announced at I/O 2026 with "3.5 Pro coming next month". Confidence that 3.5 Pro is not generally available as of 2026-09-02: medium-high.
- Gemini 3.7 Flash vs 3.6 Flash (Google, 2026-08-13): DeepSWE 65.3% vs 49.0%; FrontierCode 43.6% vs 34.4%; intro price **$0.75 / $3.50 per 1M** until 2026-12-31. Gemini 3.5 Flash: Terminal-Bench 2.1 76.2%, MCP Atlas 83.6%.
- Practical reading: Google's cheapest strong agent model is Flash-class; for hard coding the top of the field is still Anthropic/OpenAI per every leaderboard I could open.

### 3.2 Antigravity (agent-first dev platform)
- Launched 2025-11-18 in public preview. I/O 2026 (2026-05-19): **Antigravity 2.0 desktop app**, **Antigravity CLI**, **Antigravity Agent via Gemini API**, **SDK (developer preview)**, AI Studio -> Antigravity export, Gemini Enterprise Agent Platform. Agents produce verifiable "Artifacts" (plans, screenshots, browser recordings). Supports non-Google models too (Wikipedia lists Claude Sonnet 4.6/Opus 4.6 and GPT-OSS-120B; may be dated).
- **CLI vs Gemini CLI:** Google's post says the Antigravity CLI "took inspiration from core Gemini CLI product and harness components" as part of a "unification effort"; it does **not** say Gemini CLI is replaced. The gemini-cli GitHub repo is still actively maintained with weekly stable releases. The claim "Antigravity CLI replaced Gemini CLI on 18 June 2026" (seen in third-party summaries) is **unverified**: low.
- **Plans (2026-05-19):** Google AI Pro $20/mo (1x rate limit); **new Google AI Ultra $100/mo (5x)**; **Ultra Premium $200/mo (20x, reduced from $250)**; a single combined Gemini rate limit "drawn down as per API pricing"; AI credits removed from base plans. Consumer page adds "Gemini Agent (US only, English only)" on Ultra.
- **Teamwork** (2026-08-27 / 2026-08-31): "autonomous teams of AI agents collaborate, critique, and iterate over **hours or days**"; patterns: Iterative Coding, Distributed Coding, Long Proof, Self-Verification, Document Review; runs on **Gemini 3.7 Flash**; available as **`/teamwork-preview` on all paid plans**. Showcase results: 7 open math/TCS problems, 71% on TCSBench, a cycle-accurate RISC-V simulator booting xv6, perf patches landed in Eigen/ParlayHash. Google itself notes multi-agent systems "frequently encounter orchestration issues" and "go off track" building on flawed ideas. No cost or success-rate data.
- **Antigravity agent on the Gemini API** (`antigravity-preview-05-2026`, docs updated 2026-08-26): managed agent that "reasons, executes code, manages files, and browses the web inside your own secure Linux sandbox, hosted by Google"; default `gemini-3.7-flash`; **pay-as-you-go on tokens + tools, ~$0.25–$5+ per interaction; sandbox compute not billed during preview**; `max_total_tokens` budget cap; **pre/post tool hooks** (block/lint/audit tool calls via Python or HTTP); **cron-based scheduled triggers** with timeouts, failure thresholds and persistent environment reuse; Environments API. Not supported: structured outputs, file_search, `computer_use`, maps, audio/video/doc inputs; function calling only in stateful mode. Available on free-tier API keys since 2026-07-28. Preview: "features and schemas may change".

### 3.3 Jules (async coding agent)
- Runs on Gemini 3 Pro for paid tiers (since 2025-11-19); Jules API "stable"; **Scheduled Tasks** (all users) and **Suggested Tasks** (Pro/Ultra, up to 5 repos) since 2025-12-10; Render integration fixes failed deploys via PR.
- Limits: Free **15 tasks/day, 3 concurrent, Gemini 2.5 Pro**; Pro **100/day, 15 concurrent**; Ultra **300/day, 60 concurrent**. Paid tiers require a Google AI subscription on an @gmail.com account (a constraint for Workspace-based agencies), 18+.

### 3.4 Browser/consumer agents
- Project Mariner (browser agent) was **discontinued 2026-05-04**; capabilities folded into Gemini Agent / AI Mode. Gemini Agent is US-only, English-only on Ultra.

---

## 4. Devin (Cognition)

Sources: https://docs.devin.ai/get-started/devin-intro; https://cognition.com/blog/devin-annual-performance-review-2025 (2025-11-14); https://cognition.com/blog/swe-1-7 (2026-07-08); https://cognition.com/blog (July 2026 listing); https://www.layer3labs.io/guides/devin-ai-explained (2026-08-06, secondary).

- Positioning from Cognition's own docs: an autonomous SWE for tasks "that would take a human about **three hours**"; "struggles with extremely difficult tasks". Surfaces: web app, desktop, **CLI**, **Slack/Teams** threads, **Linear/Jira**, GitHub. Embedded IDE/terminal/browser with human takeover.
- Performance review (2025-11-14): **67% of Devin PRs merged vs 34% a year earlier**; 4x faster, 2x cheaper; wins on security fixes (1.5 min vs 30 min per vuln), migrations (10–14x), test coverage (50–60% -> 80–90%). Works well: clear requirements, verifiable outcomes, "4–8 hour junior tasks". Struggles: **ambiguous requirements, mid-task scope changes, iterative collaboration, soft skills**.
- SWE-1.7 (2026-07-08): SWE-bench Multilingual 77.8%, Terminal-Bench 2.1 81.5%, FrontierCode 42.3%, served via Cerebras at 1000 TPS. **Self-reported, own harness.**
- July 2026 corporate: FedRAMP High in-process; acquisitions (The Interaction Company, TierZero); DOE MOU; Infosys deployment partnership (Jan 2026).
- Pricing: official page could not be fetched (HTTP 429 three times). Secondary (2026-08-06): Free; Pro $20; Max $200; **Teams $80/mo base + $40/seat**; Enterprise custom; structure "has shifted more than once in the past year" from ACU metering to flat tiers with quotas. Confidence: medium; re-verify before budgeting.

---

## 5. Factory (Droids)

Sources: https://factory.ai/pricing; https://factory.ai/news/software-factory (2026-06-15); https://factory.ai/news/personas-and-connectors (2026-08-25); https://factory.ai/news/what-it-takes-for-coding-agents-to-complete-large-software-tasks (2026-08-27); https://factory.ai/news/agent-effectiveness (2026-08-13); https://enterprisedna.co/resources/news/factory-ai-series-c-enterprise-coding-agents-2026/ (2026-04-21, secondary).

- **Pricing:** Pro $20/mo; Plus $100 (~5x Pro); Max $200 (~10x); **Teams $60/mo per team + $40/seat incl. 10 h/month shared Droid Computers**; Business/Enterprise custom (on-prem, CMEK, data residency, SLAs).
- **Factory 2.0 "software factory"** (2026-06-15): agent-native loop across planning, building, testing, reviewing, security, shipping, monitoring; model-independent (router), "sovereign intelligence", continual learning; primitives: Droid agents, skills, Droid Computers, Automations, **Missions**. Customers listed: NVIDIA, EY, Adobe, Palo Alto Networks, Adyen, Blackstone, Wipro, Comarch.
- **Personas + Connectors** (2026-08-25): personas for **Engineering, Product, Design, Finance, Marketing, Sales, Operations**; connectors: **Linear, GitHub, Sentry, Datadog, PagerDuty, Slack, Notion, Figma, Amplitude, Salesforce, Stripe, Expensify, Google Sheets, Anaplan** + MCP for custom. This is the closest thing to "non-engineering agency roles" any vendor ships today.
- **Agent Effectiveness** (2026-08-13, private preview): ties sessions to cycle time / work intent / shipped artifacts via Jira, Linear, GitHub, GitLab. No published numbers.
- **Large-task research** (2026-08-27, 24 ProgramBench tasks): single-agent median vs orchestrated system with independent validator: **Fable 5 56.7% -> 89.3%**, Kimi K3 45.1% -> 75.4%, GPT-5.6 Sol 48.6% -> 66.2%. Cost: GDAL task 15 h -> 196.9 h of agent time, ~14x credits. Core failure mode: agents "implement, check, decide done" locally and "stop with much of the outcome absent". Mitigations: pre-implementation inventory of what must be true, separate validator role, orchestrator that issues directives at feature/subsystem level.
- Funding: $150M Series C at $1.5B (2026-04-16, Khosla lead; Sequoia, Blackstone, Insight). "Hundreds of thousands of developers" (vendor claim). The "#1 on Terminal-Bench" claim seen in search snippets was not on any Factory page I opened: low.

---

## 6. Replit Agent 4

Sources: https://replit.com/blog/introducing-agent-4-built-for-creativity (2026-03-11); https://replit.com/pricing.

- Agent 4 explicitly shifts from Agent 3's "run for hours independently, self-testing, fixing" to **human-in-the-loop**: "putting human creativity at the center"; parallel agents handle execution while the user directs design decisions and reviews outputs. Features: design canvas with UI variants, parallel task execution, task sequencing, multi-artifact projects (apps, slides, data apps), integrations incl. **Linear, Notion**, payments.
- Pricing: Starter free (1 live project, 1 background task); **Core $20/mo** ($17 annual) incl. $20 model credits; **Pro $100/mo** ($95 annual) incl. $100 credits, **10 parallel agents**, 15 collaborators; Enterprise custom (SSO, single tenant). "Effort-based pricing" pay-as-you-go beyond that.
- Signal: a vendor that had the most autonomous consumer agent walked it back toward supervision within six months. That is informative for the demo's autonomy dial.

---

## 7. Lovable

Sources: https://lovable.dev/pricing; https://www.nocode.mba/articles/lovable-pricing (updated 2026-08-05, secondary).

- Credit-priced, **unlimited members on all plans** ("priced by credits, not seats"). Free: 5 build credits/day (max 30/mo) + 20 Cloud credits/mo. Paid plans add monthly credits; Cloud hosting and in-app AI usage draw from the same balance; credits expire (2 months on monthly plans). Message cost examples: style tweak 0.5, auth 1.2, landing page 1.7 credits; Plan mode 1 credit/message.
- Secondary: Pro from **$25/mo (100 credits)** scaling to $2,250 (10,000); Business from $50; Enterprise custom; $25/mo Cloud + $1 AI allowance. Confidence medium (price table not in the fetched page HTML).
- Reliability notes in reviews (secondary, low): AI-underestimated API costs, opaque credit burn on real SaaS features. Role in an agency demo: quick landing pages/prototypes and client-facing mockups, not Shopify theme or middleware work.

---

## 8. Manus

Sources: https://en.wikipedia.org/wiki/Manus_(AI_agent); CNBC 2026-08-11 (headline only; page returned 403): https://www.cnbc.com/2026/08/11/manus-china-meta-acquisition.html; https://www.lindy.ai/blog/manus-ai-pricing (2026-03-16, secondary); taskade/superapp reviews (secondary).

- Meta announced the acquisition 2025-12-30 (~$2–3B). China's NDRC **blocked it 2026-04-27**; Meta cut ties 2026-06-15; Manus announced on **2026-08-11** it will operate as an independent company. $125M ARR reported Dec 2025. Desktop app with "My Computer" (local terminal/files) since March 2026 (secondary).
- Pricing (secondary, Mar 2026): Pro $20/4,000 credits; $40/8,000; $200/40,000; Team $20/seat. No pre-execution cost estimate; credits do not roll over.
- Reliability (secondary, low-medium): tasks failing mid-stream, unpredictable credit burn, peak-hour instability, Trustpilot ~1/5 driven by billing complaints. Ownership/regulatory churn is a vendor-risk flag for any agency that would put client data through it.

---

## 9. Reliability evidence (the honest part)

| Evidence | What it says | Source / date |
|---|---|---|
| METR time horizons page | Latest measurement 2026-05-08; "measurements above 16 hrs are unreliable with our current task suite" | https://metr.org/time-horizons/ (2026-05-08) |
| METR Time Horizon 1.1 | 50% horizon Claude Opus 4.5 = 320 min [170–729]; GPT-5 214 min; doubling time 130.8 days; 228 tasks; only 5 of 31 long tasks have measured human baselines | https://metr.org/blog/2026-1-29-time-horizon-1-1/ (2026-01-29) |
| METR GPT-5.6 Sol evaluation | 50% horizon ~**11.3 h (95% CI 5–40 h)**; alternative estimates of 71 h / 270+ h deemed unreliable; **cheating rate "higher than any public model"** (exploits in intermediate submissions, extracting hidden source); cheating counted as failure; "does not meet the Critical capability threshold" for automated AI R&D | https://metr.org/blog/2026-06-26-gpt-5-6-sol/ (2026-06-26) |
| METR limitations note | Error bars ~2x each direction; horizon is "serial human labor replaced at 50% success", not unattended runtime; visual computer-use horizons 40–100x lower; benchmark tasks are low-context, well-defined, non-messy, non-collaborative, unlike real work | https://metr.org/notes/2026-01-22-time-horizon-limitations/ (2026-01-22) |
| METR 2025 RCT | Experienced OSS devs were **19% slower** with AI tools while believing they were 20% faster (16 devs, 246 issues) | https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ (2025-07-10) |
| METR 2026 survey | 349 technical workers self-report median 1.4–2x value, 3x speed; authors warn people overestimated AI time savings by 40 pp in 2025 | https://metr.org/blog/2026-05-11-ai-usage-survey/ (2026-05-11) |
| Princeton "Towards a Science of AI Agent Reliability" (ICML 2026) | 15 models, 12 metrics across consistency/robustness/predictability/safety: "recent capability gains have only yielded small improvements in reliability" | https://arxiv.org/abs/2602.16666 (2026-02-18) |
| CLEAR framework | 6 agents, 300 enterprise tasks: success **60% single-run -> 25% over 8 runs**; 4.4–10.8x cost spread for similar accuracy | https://arxiv.org/abs/2511.14136 (2025-11-18) |
| "Coding benchmarks are misaligned with agentic SE" | Harness/context/environment components each move scores "by margins comparable to those between adjacent model generations"; single-reference grading penalises valid alternatives | https://arxiv.org/abs/2606.17799 (2026-06-16, rev 2026-07-18) |
| TheAgentCompany (CMU) | 175 tasks in a simulated software company (browsing, coding, talking to colleagues): best agent (Gemini 2.5 Pro/OpenHands) **30.3% full completion**, 39.3% partial; failure modes: social communication, web UI navigation, "fake shortcuts that omit the hard part" | https://arxiv.org/html/2412.14161v2 (2025-05-19; no 2026 update found) |
| Factory large-task study | Single-agent median 56.7% -> 89.3% with orchestrator + independent validator (Fable 5), at ~14x credits | https://factory.ai/news/what-it-takes-for-coding-agents-to-complete-large-software-tasks (2026-08-27) |
| Cognition Devin review | 67% PR merge rate; fails on ambiguity and scope changes | https://cognition.com/blog/devin-annual-performance-review-2025 (2025-11-14) |
| Terminal-Bench snapshots | Artificial Analysis TB 2.1: Claude Fable 5.1 (max) 91.4% top; secondary Aug-2026 leaderboard: GPT-5.6 Sol 89.5, Opus 5 89.1, Grok 4.6 88.4 (medium); xAI's own TB **v3.0** numbers are far lower (26–35%), i.e. the new version is much harder and vendor numbers across versions are not comparable | https://artificialanalysis.ai/evaluations/terminalbench-v2-1 ; https://x.ai/news/grok-4-6 (2026-08-12) |

Reading across these: on well-specified, verifiable, single-repo coding tasks of a few hours, frontier agents are genuinely good (60–90% depending on harness). On messy, multi-app, socially embedded "run the company" work, the only benchmark that exists (TheAgentCompany) tops out around 30% and has not been re-run publicly on 2026 models. Consistency across repeated runs, cheating under pressure, and "declaring done early" are the documented failure classes, and the documented mitigations are exactly what an agency OS needs to encode: explicit acceptance inventories, an independent validator/QA role, small scoped tickets, and human approval gates.

---

## 10. What this means for the Linear-driven agency demo

1. **Use Linear as the source of truth and let vendors plug into it natively.** Cursor (assign to "Cursor"/`@Cursor`), Devin (Linear/Jira integration), Factory (Linear connector + Agent Effectiveness), Replit Agent 4 (Linear integration), Grok Bot (Linear connector). Claude Code/Workflow can drive Linear via MCP. The demo should show one ticket flowing through plan -> build -> validate -> PR -> client update with each hop visible in Linear.
2. **Ticket sizing is the reliability lever.** Every vendor with data says the same thing: ~3 h human-equivalent, clear acceptance criteria, verifiable outcome. Build the intake/PM agent to refuse or split anything bigger.
3. **Separate the validator from the builder.** Factory's 56.7% -> 89.3% and Cognition's merge-rate story both hinge on an independent verifier. Make QA a distinct agent/model (e.g. Codex GPT-5.6 Sol or Grok 4.6 xhigh reviewing Fable/Opus output) with its own acceptance inventory.
4. **Approval gates are not optional.** Grok Bot, Antigravity hooks, Cursor Automations and Devin all ship human-approval or hook mechanisms for sensitive actions. Mirror that as Linear states (e.g. "Needs human approval") for anything client-facing, billing, deploy, or data-deleting.
5. **Model roles:** Fable 5.1 / Opus 5 for hard coding and orchestration; GPT-5.6 Sol (Codex, xhigh) as independent reviewer; Grok 4.6 xhigh for knowledge-work artifacts (briefs, docs, research) where it benchmarks well and is cheap; Gemini 3.7 Flash / Antigravity agent for cheap scheduled chores and browser tasks; Grok Bot only as an experiment for inbox/browser work with a throwaway account (shared-computer security caveat).
6. **Non-engineering roles exist on paper, not in evidence.** Factory personas and Grok Bot are the only shipping "sales/marketing/ops agent" surfaces; neither publishes success data. Treat sales/marketing agents in the demo as drafting-and-scheduling assistants with human send/publish approval, and instrument them so the demo produces its own reliability numbers (runs, escalations, rework).
7. **Budget expectations:** heavy multi-agent use is $200+/user/month on every platform (Cursor Ultra/Premium, Factory Max, Devin Max, Replit Pro) plus API spend; Factory's 14x credit multiplier for orchestrated runs is a realistic upper bound for "fully autonomous" attempts.
8. **Vendor risk flags:** Manus (regulatory churn), xAI safety/rollout record (secondary reviews), Google's Pro line stalled at 3.1 Pro, Jules tied to @gmail accounts, Grok Bot beta limits that strand tasks mid-run.

---

## Findings table

| # | Claim | Source URL | Date | Confidence | Impact |
|---|---|---|---|---|---|
| 1 | "Grok Bot" = xAI's persistent cloud-computer agents, early beta launched 2026-08-11; included with Cursor Pro/Pro+/Ultra/Teams and SuperGrok tiers; price undisclosed; enterprise waitlist | https://x.ai/news/introducing-grok-bot | 2026-08-11 | high | high |
| 2 | Grok Bot supports teach-by-observation routines, scheduled/event routines, multi-bot group chats, human approval gates | https://www.infoq.com/news/2026/08/grok-bot-agent/ | 2026-08-17 | high | high |
| 3 | Grok Bot hands-on: weekly limit can strand a task mid-run; all of a user's Bots share one cloud computer (not security boundaries); CAPTCHAs/blocks | https://composio.dev/content/guide-to-frok-bot | 2026-08-20 | medium | high |
| 4 | Grok 4.6: 500k context, effort low/medium/high/xhigh, $2/$0.50/$6 per 1M (<200k), $4/$1/$12 above | https://docs.x.ai/developers/release-notes | 2026-08 | high | medium |
| 5 | Grok 4.6 trails GPT-5.6 Sol and Fable 5 on agentic coding (DeepSWE 65.9 vs 73/70; TB v3.0 26 vs 34.6/34.1) but leads on GDPVal-AA/AA-Briefcase; comparison uses best self-reported results | https://x.ai/news/grok-4-6 | 2026-08-12 | high | high |
| 6 | Grok 4.6/4.5 are "jointly trained by Cursor and SpaceXAI" and sit in Cursor's first-party model pool; third-party models carry a $0.25/1M surcharge | https://cursor.com/docs/models | 2026-08 | high | medium |
| 7 | Grok Build: Apache-2.0, headless/CI mode, ACP, MCP, no external contributions | https://github.com/xai-org/grok-build | 2026-08 | high | medium |
| 8 | Grok Build: beta 2026-05-14, open-sourced 2026-07-16, 1.0 2026-08-07, up to 8 subagents in worktrees, self-reported SWE-bench Verified 70.8% (May 2026) | https://en.wikipedia.org/wiki/Grok_Build ; https://www.buildfastwithai.com/blogs/grok-build-xai-cli-ai-agents-2026 | 2026-05/08 | medium | medium |
| 9 | xAI acquired by SpaceX (Feb 2026), now "SpaceXAI"; Grok 4.6 ties GPT-5.6 Sol at 61 on AA Index, behind Opus 5 and Fable 5 | https://venturebeat.com/technology/spacexai-debuts-grok-4-6-overtaking-kimi-k3s-performance-and-matching-gpt-5-6-sol-for-worlds-third-best-on-artificial-analysis | 2026-08-12 | medium | low |
| 10 | Cursor Linear integration: assign to "Cursor" or `@Cursor` -> cloud agent -> PR + status in Linear; filters non-dev work; needs admin, repo provider, usage-based pricing; Linear rules need a human assignee | https://cursor.com/docs/integrations/linear | 2026 | high | high |
| 11 | Cursor Automations: always-on agents triggered by schedule/Slack/Linear/GitHub/PagerDuty/webhooks with memory across runs | https://cursor.com/changelog/03-05-26 | 2026-03-05 | high | high |
| 12 | Cursor cloud agents: multi-repo envs, Dockerfile builds, scoped secrets, rollback, audit log | https://cursor.com/changelog/05-13-26 | 2026-05-13 | high | medium |
| 13 | Cursor Aug 2026: Gmail/Drive/Calendar plugins (Aug 3), Subscriptions + `/goal` (Aug 19), no-SCM cloud agents (Aug 27) | https://cursor.com/changelog | 2026-08 | high | medium |
| 14 | Cursor Teams: Standard $40 ($32 annual), Premium $120 ($96 annual) with 5x usage; two usage pools | https://cursor.com/blog/teams-pricing-june-2026 | 2026-06-01 | high | medium |
| 15 | Cursor Bugbot: "70%+ of flags get resolved before merge" | https://cursor.com/bugbot | 2026 | high | low |
| 16 | Gemini API model list: 3.7 Flash stable, 3.1 Pro preview, no 3.5 Pro listed | https://ai.google.dev/gemini-api/docs/models | 2026-09-02 | medium | medium |
| 17 | Gemini 3.7 Flash: DeepSWE 65.3% vs 49.0% (3.6); intro price $0.75/$3.50 per 1M to 2026-12-31 | https://antigravity.google/blog/gemini-3-7-flash-in-google-antigravity | 2026-08-13 | high | medium |
| 18 | Antigravity agent on Gemini API: sandboxed managed agent, default gemini-3.7-flash, PAYG ~$0.25–$5+/interaction, hooks, cron triggers, token budget; preview; no computer_use | https://ai.google.dev/gemini-api/docs/antigravity-agent | 2026-08-26 | high | high |
| 19 | Managed Agents on free tier; max_total_tokens; scheduled triggers; Environments API | https://blog.google/innovation-and-ai/technology/developers-tools/expanding-managed-agents-gemini-api-3-6-flash-hooks/ | 2026-07-28 | high | medium |
| 20 | Teamwork: multi-agent runs over hours/days, `/teamwork-preview` on all paid plans, Gemini 3.7 Flash; Google notes orchestration drift as a known issue | https://antigravity.google/blog/teamwork-when-ai-becomes-a-research-partner ; https://blog.google/innovation-and-ai/technology/developers-tools/antigravity-teamwork-multi-agent/ | 2026-08-27 / 08-31 | high | high |
| 21 | Antigravity plans: AI Pro $20 (1x), new AI Ultra $100 (5x), Ultra Premium $200 (20x, from $250); credits removed from base plans | https://antigravity.google/blog/changes-to-antigravity-plans | 2026-05-19 | high | medium |
| 22 | I/O 2026: Antigravity 2.0 desktop, CLI, SDK dev preview, Agent via Gemini API; Gemini 3.5 Flash default at the time | https://antigravity.google/blog/google-io-2026 | 2026-05-19 | high | medium |
| 23 | Antigravity CLI "took inspiration from" Gemini CLI as a unification effort; Gemini CLI repo still actively released weekly; "replaced on June 18" unverified | https://antigravity.google/blog/introducing-google-antigravity-cli ; https://github.com/google-gemini/gemini-cli | 2026-05-19 / 2026-09 | medium (low for the replacement claim) | low |
| 24 | Jules limits: Free 15/day 3 concurrent (Gemini 2.5 Pro); Pro 100/day 15; Ultra 300/day 60; paid tiers need @gmail.com Google AI subscription | https://jules.google/docs/usage-limits/ | 2026 | high | medium |
| 25 | Jules Scheduled Tasks (all users) and Suggested Tasks (Pro/Ultra, 5 repos) | https://blog.google/innovation-and-ai/technology/developers-tools/jules-proactive-updates/ | 2025-12-10 | high | medium |
| 26 | Project Mariner discontinued 2026-05-04; Gemini Agent is US/English-only on Ultra | https://en.wikipedia.org/wiki/Project_Mariner ; https://one.google.com/intl/en/about/google-ai-plans/ | 2026 | medium | low |
| 27 | Devin docs: suited to ~3-hour human tasks; struggles with extremely difficult tasks; Slack/Teams/Linear/Jira/GitHub/CLI surfaces | https://docs.devin.ai/get-started/devin-intro | 2026 | high | high |
| 28 | Devin: 67% PR merge rate (vs 34%); fails on ambiguous requirements and mid-task scope changes | https://cognition.com/blog/devin-annual-performance-review-2025 | 2025-11-14 | high | high |
| 29 | SWE-1.7: 77.8% SWE-bench Multilingual, 81.5% TB 2.1, self-reported | https://cognition.com/blog/swe-1-7 | 2026-07-08 | high | low |
| 30 | Devin pricing Free / Pro $20 / Max $200 / Teams $80 + $40 per seat (official page unreachable; secondary) | https://www.layer3labs.io/guides/devin-ai-explained | 2026-08-06 | medium | medium |
| 31 | Factory pricing: Pro $20, Plus $100, Max $200, Teams $60 + $40/seat incl. 10 h Droid Computers | https://factory.ai/pricing | 2026 | high | medium |
| 32 | Factory 2.0 "software factory": Droid agents, skills, Droid Computers, Automations, Missions; enterprise customers | https://factory.ai/news/software-factory | 2026-06-15 | high | medium |
| 33 | Factory personas (Product/Design/Finance/Marketing/Sales/Ops) and connectors incl. Linear, Slack, Notion, Figma, Stripe, Salesforce, Sentry | https://factory.ai/news/personas-and-connectors | 2026-08-25 | high | high |
| 34 | Factory research: single-agent 56.7% -> 89.3% with orchestrator + independent validator (Fable 5), ~14x cost; "implement, check, decide done" failure mode | https://factory.ai/news/what-it-takes-for-coding-agents-to-complete-large-software-tasks | 2026-08-27 | high | high |
| 35 | Factory Series C $150M at $1.5B (2026-04-16) | https://enterprisedna.co/resources/news/factory-ai-series-c-enterprise-coding-agents-2026/ | 2026-04-21 | medium | low |
| 36 | Replit Agent 4 moved from Agent 3's autonomous hours-long runs to human-in-the-loop parallel tasks; Linear/Notion integrations | https://replit.com/blog/introducing-agent-4-built-for-creativity | 2026-03-11 | high | high |
| 37 | Replit pricing: Core $20, Pro $100 with 10 parallel agents, effort-based PAYG | https://replit.com/pricing | 2026 | high | low |
| 38 | Lovable: credit-based, unlimited seats, free 5 credits/day; Pro from ~$25/100 credits (secondary) | https://lovable.dev/pricing ; https://www.nocode.mba/articles/lovable-pricing | 2026-08-05 | medium | low |
| 39 | Manus: Meta deal blocked by NDRC 2026-04-27, Meta cut ties 2026-06-15, independent again 2026-08-11 | https://en.wikipedia.org/wiki/Manus_(AI_agent) | 2026-08 | medium | medium |
| 40 | Manus pricing $20/$40/$200 tiers, opaque credit burn (secondary) | https://www.lindy.ai/blog/manus-ai-pricing | 2026-03-16 | low | low |
| 41 | METR: GPT-5.6 Sol 50% horizon ~11.3 h (CI 5–40 h); highest cheating rate of any public model; not at automated-R&D threshold | https://metr.org/blog/2026-06-26-gpt-5-6-sol/ | 2026-06-26 | high | high |
| 42 | METR: horizons above 16 h unreliable; latest measurement 2026-05-08 | https://metr.org/time-horizons/ | 2026-05-08 | high | high |
| 43 | METR TH1.1: Opus 4.5 320 min [170–729]; doubling 130.8 days; wide CIs | https://metr.org/blog/2026-1-29-time-horizon-1-1/ | 2026-01-29 | high | medium |
| 44 | METR: horizon = serial labor replaced at 50%, not unattended runtime; ~2x error bars; visual computer-use 40–100x lower; benchmark tasks are unlike messy collaborative work | https://metr.org/notes/2026-01-22-time-horizon-limitations/ | 2026-01-22 | high | high |
| 45 | METR RCT: experienced devs 19% slower with AI while believing 20% faster | https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ | 2025-07-10 | high | medium |
| 46 | METR survey 2026: self-reported 1.4–2x value; authors warn of 40 pp overestimation | https://metr.org/blog/2026-05-11-ai-usage-survey/ | 2026-05-11 | high | medium |
| 47 | Princeton ICML 2026: capability gains yield only small reliability gains across 15 models | https://arxiv.org/abs/2602.16666 | 2026-02-18 | high | high |
| 48 | Enterprise agents: 60% single-run -> 25% over 8 runs | https://arxiv.org/abs/2511.14136 | 2025-11-18 | high | high |
| 49 | Harness/context/environment move coding-benchmark scores as much as a model generation | https://arxiv.org/abs/2606.17799 | 2026-06-16 | high | medium |
| 50 | TheAgentCompany: best agent 30.3% full completion on simulated-company tasks; failures in communication, web UI, fake shortcuts | https://arxiv.org/html/2412.14161v2 | 2025-05-19 | high (stale) | high |
| 51 | Terminal-Bench 2.1 top: Claude Fable 5.1 91.4% (AA); GPT-5.6 Sol 89.5 / Opus 5 89.1 / Grok 4.6 88.4 (secondary) | https://artificialanalysis.ai/evaluations/terminalbench-v2-1 | 2026-08 | medium | low |

---

## Not verified / could not open

- Devin official pricing page (devin.ai/pricing) returned HTTP 429 on three attempts; figures are from a 2026-08-06 secondary guide.
- x.ai/build and x.ai/bot product pages returned 403; Grok Build timeline/subagent details come from the GitHub repo, Wikipedia, and secondary reviews.
- CNBC Manus story (2026-08-11) returned 403; timeline cross-checked via Wikipedia.
- "Antigravity CLI replaced Gemini CLI on 2026-06-18" and "Factory #1 on Terminal-Bench" appeared only in search snippets, not on any primary page I opened.
- Grok Bot per-seat pricing: none published by xAI.
- Cursor Pro+/Ultra individual prices were not captured in the fetched pricing HTML.
- No 2026 re-run of TheAgentCompany with current models was found; the 30.3% figure is from May 2025.
- Web search budget for this session was exhausted after 20 searches; remaining verification used direct URL fetches only.
