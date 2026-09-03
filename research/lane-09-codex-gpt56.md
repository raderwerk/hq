# Lane 09 - Independent second opinion from GPT-5.6 Sol (Codex CLI, xhigh reasoning, web search on)

Date: 2026-09-02
Runner: Claude subagent, no own web research (by design of this lane)
Raw transcript: `/Users/youp/Developer/Personal/Raderwerk/research/lane-codex-gpt56-raw.md`
Codex session id: `01a06205-bbce-79a2-b1eb-200afc15795c` (codex-cli 0.147.0, model `gpt-5.6-sol`, reasoning `xhigh`, sandbox read-only, tokens used 128,302)

## Method

The exact prompt from the task was run once. The prescribed invocation failed (`codex exec --search` -> `error: unexpected argument '--search'`); in codex-cli 0.147.0 `--search` is a top-level flag, so the successful invocation was `codex --search exec --skip-git-repo-check -s read-only -c 'notify=[]' -m gpt-5.6-sol -c model_reasoning_effort=xhigh '<prompt>'`. The model did perform live web searches (8 distinct queries logged, e.g. `site:linear.app 2026 agents Linear Agent Sessions API webhook`, `site:metr.org/blog 2026 coding agents productivity study`, `2026 "AI sales agent" field experiment`, `2026 AI accounting agents finance automation study`).

After the run, every cited URL was checked for HTTP status only (curl, no content read): 11 of 14 return 200; `openai.com` (2 URLs) and `sciencedirect.com` return 403, which is standard bot-blocking on those hosts and not evidence of a hallucinated link; `docs.cursor.com/background-agent` redirects to the generic `cursor.com/docs` landing page, so the specific page may have moved. Claims were not content-verified by this lane; other lanes should cross-check the high-impact ones.

Observation on the raw file: Codex's memory system injected summaries of unrelated earlier Codex sessions (Tapps repo, "SEO meets Tech" Orbit POC) into the transcript (raw lines ~107-190). This is Codex-side context bleed, not part of the answer. Treat the raw file as internal; do not forward it to clients.

## GPT-5.6 verdict (verbatim numbers, GPT's own analyst estimates, not measured benchmarks)

"Commercially feasible for a narrow, productized agency; not feasible as a self-governing company." Estimate: ~60% of total workload safely delegable with human supervision; 70-75% for standardized sites, Shopify builds and maintenance; ~40% for bespoke commerce, legacy integrations or politically complex clients. A lights-out agency: ~20% feasible.

| Function | Delegable (GPT est.) | Human responsibility that remains |
|---|---:|---|
| Sales | 35% | Discovery, trust, pricing, negotiation, closing |
| Marketing | 60% | Positioning, taste, brand approval, claims |
| PM/scoping | 45% | Resolving ambiguity, estimates, scope/change acceptance |
| Development | 75% | Architecture, unusual integrations, merge/release |
| QA | 65% | Exploratory testing, product judgment, final acceptance |
| Delivery/client comms | 50% | Bad news, conflict, scope changes, relationship |
| Finance | 55% | Bank actions, refunds, tax filings, final books |

Percentages mean share of work safely delegated, not model accuracy or headcount eliminated.

## The five hardest blockers (GPT's ranking, with its sources)

1. Intent is harder than implementation. Anthropic's analysis of ~400,000 Claude Code sessions: humans still make most planning decisions; domain expertise improves success and error recovery. Agents execute a clear brief but cannot reliably discover what the client actually needs. Source: https://www.anthropic.com/research/claude-code-expertise
2. Capability benchmarks overstate dependable delivery. METR: agents can do some human-weeks-long coding tasks where progress is cheaply verifiable, but show obvious bugs, poor strategic judgment and constraint-violating "cheats"; measured early-2026 productivity uplift only ~4-20% with severe selection uncertainty. Sources: https://metr.org/blog/2026-05-19-frontier-risk-report/ and https://metr.org/blog/2026-02-24-uplift-update/
3. Permissions create a real attack surface. Cursor's own docs: remote agents can get GitHub write access, internet access and automatic terminal execution, with an explicit prompt-injection exfiltration warning. OpenAI describes the same need for boundaries, approvals and telemetry. Sources: https://docs.cursor.com/background-agent and https://openai.com/index/running-codex-safely/
4. Client-facing mistakes carry disproportionate cost. Alibaba field experiment (2026): AI-assisted support faster and subjectively better, but no improvement in objective retrial rates; top agents sometimes worse. Marketing research: AI disclosure can produce neutral or negative reactions. EU AI Act Article 50 transparency obligations apply since 2 August 2026. Sources: https://arxiv.org/abs/2603.29888 , https://link.springer.com/article/10.1057/s41270-026-00534-7 , https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems
5. Supervision and exception handling determine the economics. OpenAI (Symphony): humans get overloaded beyond ~3-5 concurrent coding sessions. Finance: 86% of surveyed CFOs had encountered inaccurate or hallucinated data; 97% consider human oversight at least somewhat critical. Sources: https://openai.com/index/open-source-codex-orchestration-symphony/ and https://www.journalofaccountancy.com/news/2026/feb/agentic-ai-is-handling-more-finance-work-but-can-cfos-trust-it/

## Demo architecture GPT proposes (buildable in 3-5 days)

```
Lead/intake
   -> Linear state machine
   -> webhook -> small router + idempotency/audit ledger
   -> Claude Code | Codex | Cursor Cloud Agent (isolated workspace per run)
   -> GitHub branch/PR -> CI -> preview deployment
   -> Independent agent QA -> Human approval -> Client review
   -> Delivery -> Draft invoice -> Human finance approval
```

Linear statuses: `Lead -> Qualified -> Scope Draft -> Awaiting Approval -> Build -> Agent QA -> Human QA -> Client Review -> Delivered -> Invoiced`.

Implementation rules GPT insists on:

- Issue templates must require objectives, exclusions, acceptance tests, brand assets, data classification and budget.
- Labels select the worker; each run gets an isolated workspace and may only write branches, PRs, artifacts and Linear updates.
- Deterministic QA: type-check, tests, Playwright flows, accessibility, Lighthouse, dependency/secrets scans, screenshot comparison.
- A different agent reviews the builder's output; an agent never self-approves.
- Humans approve: quote/SOW, production merge, non-routine client messages, refunds/payments, tax actions.
- Keep secrets, financial records and execution idempotency outside Linear. Linear is the visible control plane, not the transactional database.
- Do not build a bespoke multi-agent framework first: Linear already launches Claude Code/Codex sessions natively, and Cursor Automations can trigger from Linear or webhooks.

## Findings table

Confidence rule used: high = official vendor/institution URL that resolved (200); medium = third-party or bot-blocked (403) or redirected page; low = GPT's own estimate without external source. Dates are as stated by GPT or implied by the URL slug; not independently verified.

| # | Claim | Source URL | Date | Confidence | Impact |
|---|---|---|---|---|---|
| 1 | Linear added native Claude Code and Codex "coding sessions" (agents launched directly from Linear issues) | https://linear.app/changelog/2026-06-11-coding-sessions | 2026-06-11 | high | high |
| 2 | Linear added environment setup, browser testing and screenshots for coding sessions | https://linear.app/changelog/2026-08-20-coding-environments | 2026-08-20 | high | high |
| 3 | OpenAI published "Symphony", an open-source Linear-as-control-plane orchestration for Codex; humans become overloaded beyond ~3-5 concurrent sessions | https://openai.com/index/open-source-codex-orchestration-symphony/ | 2026 | medium (403 bot-block, not content-checked) | high |
| 4 | Cursor Automations can trigger from Linear and webhooks and run in cloud sandboxes | https://cursor.com/changelog/03-05-26 | 2026-03-05 | high | high |
| 5 | Anthropic analysed ~400k Claude Code sessions: humans still make most planning decisions; domain expertise improves success and error recovery | https://www.anthropic.com/research/claude-code-expertise | 2026-06 | high | high |
| 6 | METR frontier risk report: agents complete some human-weeks-long coding tasks when progress is cheaply verifiable, but show obvious bugs, poor strategic judgment and constraint-violating cheats | https://metr.org/blog/2026-05-19-frontier-risk-report/ | 2026-05-19 | high | high |
| 7 | METR uplift update: early-2026 measured developer productivity uplift roughly 4-20%, magnitude still hard to estimate reliably | https://metr.org/blog/2026-02-24-uplift-update/ | 2026-02-24 | high | high |
| 8 | Cursor background/remote agents can receive GitHub write access, internet access and automatic terminal execution; docs warn about prompt-injection exfiltration | https://docs.cursor.com/background-agent | 2026 | medium (redirects to generic docs landing) | high |
| 9 | OpenAI "Running Codex safely": recommends boundaries, approvals and telemetry for agent deployments | https://openai.com/index/running-codex-safely/ | 2026-05 | medium (403 bot-block) | medium |
| 10 | Alibaba field experiment: AI-assisted customer support faster and subjectively better, but no improvement in objective retrial rate; top agents sometimes worse | https://arxiv.org/abs/2603.29888 | 2026-03 | medium | high |
| 11 | Marketing study: disclosing AI use can produce neutral or negative consumer reactions | https://link.springer.com/article/10.1057/s41270-026-00534-7 | 2026 | medium | medium |
| 12 | EU AI Act Article 50 transparency obligations (disclosure of AI interaction / AI-generated content) apply since 2 August 2026; Commission guidelines published | https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems | 2026-08-02 | high | high |
| 13 | CFO survey: 86% encountered inaccurate or hallucinated AI data; 97% consider human oversight at least somewhat critical | https://www.journalofaccountancy.com/news/2026/feb/agentic-ai-is-handling-more-finance-work-but-can-cfos-trust-it/ | 2026-02 | medium | medium |
| 14 | Academic sales literature still lacks mature performance evidence for autonomous AI sales agents | https://www.sciencedirect.com/science/article/abs/pii/S0148296325006228 | 2025/2026 | medium (403 bot-block) | medium |
| 15 | GPT verdict: ~60% of agency workload safely delegable (70-75% for standardized Shopify work, ~40% bespoke); lights-out agency ~20% feasible; per-function 35-75% | file:///Users/youp/Developer/Personal/Raderwerk/research/lane-codex-gpt56-raw.md | 2026-09-02 | low (analyst estimate) | high |
| 16 | GPT demo design: Linear state machine + webhook router + idempotency ledger + isolated agent runs + GitHub PR/CI/preview + independent agent QA + human gates; reuse native Linear/Cursor integrations instead of a bespoke framework; buildable in 3-5 days | file:///Users/youp/Developer/Personal/Raderwerk/research/lane-codex-gpt56-raw.md | 2026-09-02 | medium (design recommendation) | high |

## What this means for the Fightclub AI-agency demo

- GPT-5.6 independently lands on the same architecture the brief already points at: Linear as control plane, agents as workers, humans as approval gates. It adds two concrete constraints worth adopting: (a) Linear is not the system of record for secrets, money or idempotency; keep a small ledger outside it, and (b) builder and reviewer must be different agents, never self-approval.
- The strongest external evidence is on the dev/QA side (Linear coding sessions, Cursor Automations, METR, Anthropic). Sales, client comms and finance rest on weaker evidence and on legal constraints (EU AI Act Art. 50 disclosure since 2 Aug 2026), so the demo should show those functions as agent-drafted, human-sent.
- The ~3-5 concurrent session supervision ceiling (OpenAI Symphony) is the key economics number: the demo should make the human review queue visible in Linear so the supervisor load is measurable, not hidden.
- Scope recommendation implied by the percentages: pick a productized Shopify workflow (theme fix / feature ticket / SEO content batch) for the demo, not a bespoke configurator integration; GPT puts the delegable share at 70-75% vs ~40% for the latter.
- Do not take GPT's percentages as measured; they are its own estimates. Its sourced claims (rows 1-14) are what other lanes should verify, especially rows 1, 2, 3, 4, 12.
