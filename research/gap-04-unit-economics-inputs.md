# Gap 04: unit-economics inputs for the closing slide (hourly rate, S/M/L bands, agent cost per run, cost ceilings)

Lane: gap-04-unit-economics-inputs. Researched 2026-09-02. Method note: the session's WebSearch quota was already exhausted (200/200) when this lane started, so the six planned searches returned nothing; all evidence below comes from direct fetches of known primary URLs (Anthropic, OpenAI, Linear, Cursor, GitHub, METR, HAL, ECB) plus read-only reads of Fightclub's own systems through the Notion, Google Drive, Slack and Orbit MCPs. Internal numbers are quoted with their location so the requester can confirm them.

## 1. Answer in one screen

| Input for the slide | Recommended default | Basis | Confidence |
|---|---|---|---|
| Hourly rate, development and growth | EUR 125/h excl. VAT | Notion SLA policy (Niet Kritiek EUR 125), Q8Oils and Q-Hospitality estimates (EUR 125/h), DPD scope 2026-09-01 ("recent gehanteerd Fightclub-tarief, nog te bevestigen") | medium-high (internal, three 2026 documents, one says "to confirm") |
| Hourly rate, critical SLA incident | EUR 175/h | Notion "Nieuwe werkwijze support - SLA vs Growth" (edited 2026-07-16) | high (internal policy) |
| Hourly rate, SEO/SEA/performance | EUR 115/h (2022 card) | Drive sheet "2022 Fightclub - Tarieven per functie"; likely outdated | low-medium |
| Blended rate for build estimates | EUR 110-125/h | Q8Oils tender estimate 2026-08-11 | medium |
| S band (human) | 0.25-1 h, median 0.5 h | Orbit timesheets W33-W36 2026, n=14 S tickets | medium (one developer, four weeks, booked not estimated) |
| M band (human) | 1-4 h, median ~1.75 h | Orbit, n=6 | medium |
| L band (human) | 5-12+ h, spread over 2-4 weeks | Orbit, n=2 (23137 scanner 5.5 h; 38642 auth fix >=11.5 h) plus Notion estimates (12.5-18 h, 90 h project) | low-medium |
| Human price per band at EUR 125 | S EUR 30-125 (median ~60); M EUR 125-500 (median ~220); L EUR 625-1,500+ | derived | medium |
| Agent cost per run at list price (estimate until dry runs measure it) | S USD 3-13 (EUR 3-11); M USD 10-35 (EUR 9-30); L USD 25-100+ (EUR 22-86+) | Codex KB session ranges, HAL per-task cost, Anthropic worked examples, thermos double review | low-medium (modelled, not measured) |
| Cost ceiling per issue | EUR 25 hard (USD 29 via --max-budget-usd), EUR 10 soft warning label | see section 5 | medium |
| Cost ceiling per day | EUR 100 on dry-run/demo days, EUR 50 on idle/polling days, alert at 70% | see section 5 | medium |
| EUR/USD for the slide | 1 EUR = 1.1590 USD (ECB reference, 2026-09-01); 1 USD = EUR 0.863 | ECB | high |

The brief's default of EUR 10 per issue and EUR 50 per day (open question 6) is too tight for an M ticket with the thermos double review: a single Claude Code "Code Review" is USD 15-25, a Codex `max` session alone is USD 4.50-12, and an M run with rework lands at USD 10-35. EUR 10 works as a soft threshold for S tickets; EUR 25 is the sensible hard cap that also matches the brief's own "richtwaarde onder EUR 25 per volledige run".

## 2. Fightclub's own numbers (internal sources, read-only)

### 2.1 Hourly rates

| Rate | Where it appears | Date | Quote |
|---|---|---|---|
| EUR 175/h Kritiek, EUR 125/h Niet Kritiek (Essential support) | Notion "Nieuwe werkwijze support - SLA vs Growth" https://app.notion.com/p/17c9fcecab2d4ad38320e0210065ec00 | last edited 2026-07-16 | "Kritiek ... Reactietijd: 4 uur ... Uurtarief: EUR 175"; "Niet Kritiek ... Reactietijd: 32 uur ... Uurtarief: EUR 125". Open point on the same page: billing rounding unit (15/30/60 min) still to be decided. |
| EUR 125/h development (assumed, to confirm) | Notion "CONCEPT - Scope & urenbegroting: DPD rekentool + landingspagina" https://app.notion.com/p/2c57b56a9122483fb1aec179ea962661 | 2026-09-01 | "Bij een uurtarief van EUR 125/u excl. btw (recent gehanteerd Fightclub-tarief, nog te bevestigen voor deze offerte): 90 u x EUR 125 = EUR 11.250 excl. btw"; open question "Uurtarief bevestigen (EUR 125/u aangenomen)". |
| EUR 110-125/h blended; Growth EUR 125/h; same EUR 175/125 SLA table | Notion "Kosteninschatting tender Q8Oils" https://app.notion.com/p/874d2388f22043a98656ba7fa6098b69 | 2026-08-11 | "Blended tarief: +/- EUR 110-125/uur; totale build-inspanning +/- 1.000-1.250 uur"; "Growth/doorontwikkeling ... (+/- EUR 30.000-60.000/jr a EUR 125/uur)". Note: this estimate already prices in "AI-first delivery" with 15-25% efficiency on dev-heavy phases and states the blended rate "gaat al uit van AI-ondersteund werken". |
| "Budgetkaart @ EUR 125/u" | Notion "Salesadvies - overname, Hoasted-overzet en AI-first rebuild" (Q-Hospitality) https://app.notion.com/p/3c137aa43b758196a4a4f00320326714 | 2026-08-21 | search highlight only, page not fetched in full |
| 2022 sales rate card: Tech Development (ecomm/custom/website) EUR 115, Tech Support EUR 115, Tech Strategy EUR 150, UX/UI EUR 115, Tech PM EUR 115; Fightclub SEO/SEA/CRO/Performance/Social EUR 115, Project Manager EUR 125, Strategy Digital EUR 135, Client Developer EUR 135 | Google Drive sheet "2022 Fightclub - Tarieven per functie" https://docs.google.com/spreadsheets/d/1im29AFCjNLU5G5voOisVir7Niut3aED9ZgOrIYSI3YM | modified 2023-08-17 | tab "Fightclub uurtarieven (verkoop), 2022" and "EnoRm uurtarieven (verkoop), 2022"; also lists purchase vs sales rates for external hires (e.g. buy EUR 75-95, sell EUR 130-165) |
| "95 euro per uur!" | Slack #pm | 2026-03-30 | context not visible in search result; could be a negotiated or freelance rate. Do not use without checking the thread. |
| "als uurtarief 100 euro is" | Slack #seo | 2024-11-19 | worked example for linkbuilding margin (25% margin on 6 h) |

Reading: development/growth moved from EUR 115 (2022 card) to EUR 125 (2026 documents); the tech-support rate for non-critical work is EUR 125 and critical incidents EUR 175. No external Dutch benchmark could be verified in this session (hoofdkraan.nl, malt.nl, kvk.nl, zzp-nederland.nl, freelance.nl and dutchdigitalagencies.com all returned 404/403 or no data), so the slide should present EUR 125 as "Fightclub's current rate" and not as a market figure.

### 2.2 Hours per ticket (Orbit timesheets of the requester, ISO weeks 2026-W33 to W36)

Source: Orbit MCP `orbit_get_week` for 2026-W33, W34, W35, W36 (contact 1207606). Booked minutes per ticket, not estimates. Weekly totals 2,400 / 2,400 / 2,505 / 1,290 (W36 in progress).

| Size | Ticket (Orbit todo/ticket id) | Booked | Notes |
|---|---|---|---|
| S | 39748 Tips & Tricks scherm | 15 min | |
| S | 39755 Westfalia/Trekhaakland formules | 15 min | |
| S | DBG-80, DBG-81 (Dreambaby geboortelijst) | 15 min each | |
| S | Orbitvu ticket 23193 productslider | 15 min | agent-assisted: fix committed, PR opened, reply drafted within the 15 min |
| S | 39460 configurator Boordcomputer=false | 30 min (+ share of grouped W33 blocks) | |
| S | 39647 retour-herkomstdossier | 30 min | |
| S | THC configurator storing (incident triage + advice) | 30 min | incident, not a feature |
| S | DBG-77 | 30 min | |
| S | 39665 release dossier detail scherm | 45 min | |
| S | 38955 nieuwe organisatie Shopify -> Hyper | 45 min | |
| S | 39461 geplande-afspraak button | 45 min (+grouped) | |
| S | 39334 meer contactgegevens | 60 min | |
| S | DBG-78 eigen product toevoegen | 60 min | |
| M | 39333 dossieroverzichten op vestiging | 75 min (+grouped) | portal + middleware |
| M | 39342 besteleenheid losse orders | 75 min (+grouped) | |
| M | 39336 annuleringsreden "Anders namelijk" | 90 min | portal + middleware PRs, review prep |
| M | DBG-84 winkels uitsluiten van geboorteapp | 120 min | |
| M | Dreambaby ticket 23015 loyalty niet zichtbaar | 120 min | |
| M | DBG-76 legende schenkersview | 210 min | incl. review handling and merge of PR 42/43 |
| L | Dreambaby ticket 23137 scanner geboortelijstapp | 330 min over 4 weeks | Scanbot SDK 8 migration |
| L | 38642 PP users blijven niet ingelogd (auth fix, 6 PRs) | >= 690 min over 3 weeks | plus part of the grouped W33 blocks |
| L (incident) | React exploit research (W33) | 480 min in one day | security incident, internal |

Medians: S 30 min (n=14, range 15-60), M 105 min (n=6, range 75-210), L 5.5-11.5 h (n=2). Grouped bookings in W33 (930 min across roughly ten tickets, about 1.5 h per ticket) are consistent with the S/M split. Overhead outside tickets is real and should sit on the slide as well: release-candidate assembly 60 min, deployments and version bumps ~2.5 h/week, PR status checks 30-90 min/week, ticket selection with the PM 225 min in W34, stand-ups 15-45 min/day.

Fightclub estimate examples from Notion that calibrate the bands: "Implementatie-inschatting: 1,5 uur" (Quality lodgings, 2026-08-26); "Uren: 16-18 uur (bandbreedte 14-20) ... Totaal 12.5 uur" for a mandatory VAT-number-in-checkout feature (Rackmount, 2026-07-30 / 2026-08-11); a 90 h landing page plus calculator (DPD, 2026-09-01) with 8 h QA and 8 h PM inside.

Support policy context (Notion "Support flow Growth", edited 2026-07-16): tickets are checked three times a day, mandate check before execution, best-effort reaction 32 h, Essential Kritiek 4 h / Niet Kritiek 32 h, SLA hours on the SLA workline, Growth only after client approval. These are the human states that map onto the Linear "Wacht op" gates.

## 3. Agent cost per run: the public evidence (list prices, USD, EUR at 1.1590)

| Evidence | Figure | Source (date) | Confidence |
|---|---|---|---|
| Claude Code per developer | "average cost is around $13 per developer per active day and $150-250 per developer per month, with costs remaining below $30 per active day for 90% of users" (EUR 11.2/day, EUR 129-216/month, 90% under EUR 25.9/day) | https://code.claude.com/docs/en/costs (read 2026-09-02) | high |
| Background cost of an idle Claude Code session | "typically under $0.04 per session" | same | high |
| Agent teams multiplier | "approximately 7x more tokens than standard sessions when teammates run in plan mode" | same | high |
| Codex session cost by effort (GPT-5.6 Sol at the older $5/$30 rate) | medium 50-150K tokens $0.25-4.50; max 150-400K $4.50-12; ultra with 4 sub-agents 300-900K $9-27; extended ultra 600K-1.8M $30-75; ultra = "6-12x multiplier" | https://codex.danielvaughan.com/2026/07/27/gpt56-sol-ultra-mode-tradeoff-reasoning-budgets-subagent-cost-codex-cli/ (2026-07-27, updated 2026-09-02) | medium (secondary, methodology not stated; Sol is now $4/$0.40/$20 so subtract roughly 25-35%) |
| Current OpenAI prices | GPT-5.6 Sol $4.00 / $0.40 cached / $20.00 per 1M (promo "at least through November 21, 2026"; long context $8/$0.80/$30); Terra $2/$0.20/$12; Luna $0.20/$0.02/$1.20; gpt-5.3-codex $1.75/$0.175/$14 | https://developers.openai.com/api/docs/pricing (read 2026-09-02) | high |
| Anthropic prices | Fable 5.1 $10/$50, cache read $0.25; Opus 5 $5/$25; Sonnet 5 $2/$10; Haiku 4.5 $1/$5; batch 50% off | lane-01 (platform.claude.com pricing, read 2026-09-02); claude.com/pricing fetched here only exposed plan prices (Pro $20, Max from $100, Team $25/$125 monthly, Enterprise "$20/seat + usage at API rates") | high |
| Per-task cost on a coding benchmark | SWE-bench Verified Mini (50 tasks): SWE-Agent + Sonnet 4.5 high 72% at $463.90 total = $9.28/task (EUR 8.0); Sonnet 4.5 68% at $10.12/task; Opus 4.1 61% at $27.03/task; "costs are currently calculated without accounting for caching benefits"; HAL has paused updates | https://hal.cs.princeton.edu/swebench_verified_mini (2025-08/09 entries) | medium (2025 models, no caching, so an upper bound) |
| Per-task cost on office tasks | TheAgentCompany: best model 30.3% full completion, ~27 steps and >$4 per task | https://arxiv.org/abs/2412.14161 (v3 2025-09-10) | high (existence), low (relevance to 2026 models) |
| Hosted agent hour | Managed Agents worked example: 1-hour Opus 5 session, 50K in / 15K out = $0.705 (EUR 0.61); $0.08 per session-hour on top of tokens | lane-01, Anthropic Managed Agents docs | high |
| One hard prompt on Fable 5.1 | $0.10 at low effort to $3.30 at max effort | https://simonwillison.net/2026/Sep/1/claude-fable-5-1/ (2026-09-01) | medium |
| Managed PR review | Claude Code "Code Review" $15-25 per review (EUR 13-22); Cursor Bugbot roughly $1.00-1.50 per review | lane-01 (code.claude.com/docs/en/code-review), lane-08 | high / medium |
| Linear-hosted coding session | "model tokens at provider-published rates, with no markup, and sandbox runtime at $0.25 per 20-minute block"; Loops "$0.07-$0.20" per run; prepaid balance, min top-up $10, auto-reload min $50 | https://linear.app/docs/ai-credits (read 2026-09-02) | high |
| Cursor plans | Pro $20; Teams $40/user; Grok 4.6 $2/$6 per 1M inside Cursor, third-party models at API rates plus $0.25/1M surcharge | https://cursor.com/pricing (read 2026-09-02); lane-03 | high |
| GitHub Copilot cloud agent | "$0.04/request" for extra premium requests; the cloud agent consumes "one premium request" per session "multiplied by the model's rate", plus one per steering comment | https://docs.github.com/en/copilot/concepts/billing/copilot-requests (read 2026-09-02) | high |
| Validated multi-agent runs | Factory: single-agent 56.7% -> 89.3% with orchestrator + independent validator at ~14x credits | lane-03 (factory.ai, 2026-08-27) | medium |
| Devin ACU pricing | not verifiable: cognition.com/pricing and docs.devin.ai/billing returned 404; lane-03 secondary: Free / Pro $20 / Max $200 / Teams $80 + $40 per seat | https://www.layer3labs.io/guides/devin-ai-explained (2026-08-06) | low |

### 3.1 Modelled cost of one full loop run (to be replaced by dry-run measurements)

Assumptions: Fable 5.1 for scoping and review, Opus 5 or Sonnet 5 for execution, Codex GPT-5.6 Sol as second reviewer at the promo price, Codex or Claude for QA, prompt caching on. Ranges are the sum of the evidence rows above, not measurements.

| Size | Scoping | Execution | Thermos double review | QA + rework | Total USD | Total EUR |
|---|---|---|---|---|---|---|
| S | 0.5-1.5 | 0.5-3 (50-150K tokens) | 1.5-6 (two Claude subagents plus one Codex medium session) | 0.5-2 | 3-13 | 3-11 |
| M | 1-3 | 3-12 (150-400K tokens) | 3-10 | 1-4 plus one rework loop at +30-50% | 10-35 | 9-30 |
| L | 2-5 | 9-75 (ultra / agent team, 300K-1.8M tokens) | 5-15 | 3-10 plus two rework loops | 25-100+ | 22-86+ |

Against the human price bands (S ~EUR 60, M ~EUR 220, L EUR 625-1,500) the token cost is a small fraction. The decisive variable is supervision time at EUR 125/h: 10 min on an S ticket is EUR 21, 30 min on an M ticket is EUR 62. The slide should therefore show three columns per band: human price, agent tokens, agent tokens plus supervision.

## 4. Why the lanes disagree on the delegable share, and which number the slide should use

| Number | What it actually measures | Source (date) |
|---|---|---|
| "0-20% fully delegable" | Anthropic staff survey: "more than half said they can 'fully delegate' only between 0-20% of their work to Claude"; Claude used in 59% of work; +50% self-reported productivity; human turns per Claude Code transcript down 33%; 21.2 consecutive tool calls without intervention | https://www.anthropic.com/research/how-ai-is-transforming-work-at-anthropic (2025-12-02) |
| "~30% autonomous on office tasks" | TheAgentCompany full-completion rate on 175 simulated-company tasks with 2024-25 models | arXiv 2412.14161 (v3 2025-09-10) |
| "<44% of generations accepted" | METR RCT, 16 developers, 246 issues averaging 2.0 h: "developers accept <<44% of the generations"; "56% of developers report that they often need to make major changes to clean up AI code"; "100% developers report needing to modify AI generated code"; "75% report that they read every line"; "approximately 9% of their time reviewing and cleaning AI generated outputs"; "4% of time waiting on AI generations"; net "increases completion time by 19%" | https://arxiv.org/html/2507.09089 and https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/ (2025-07-10); METR's 2026 blog index shows no follow-up productivity study |
| "60-70% PR acceptance" | Cognition: 67% of Devin PRs merged (2025-11-14); lane-06 synthesis | lane-03, lane-06 |
| "~60% delegable" (GPT-5.6 lane) and "~45%" (Grok lane) | model self-assessments of task share, no measurement | lane-09, lane-10 |
| "60% single-run -> 25% over 8 runs" | CLEAR framework, 300 enterprise tasks: reliability across repeated runs | arXiv 2511.14136 (2025-11-18) |
| "89.3% with independent validator" | Factory ProgramBench, 24 large tasks, ~14x credits | lane-03 (2026-08-27) |

These are different denominators (share of work, task completion, generation acceptance, PR merge rate, run-to-run reliability). For the slide, use one operational metric and measure it in the dry runs: first-pass acceptance = the agent's PR passes the QA agent and is merged by the human without a human code commit. Public evidence puts that at 60-70% for well-specified S/M coding tickets with a separate validator, and far lower for office-style tasks. The 70% target in success criterion 10 sits at the top of the public range and is only realistic with S/M sizing, an independent validator (thermos plus Codex) and the rework loop counted as pass two.

Supervision-minute defaults until measured: S 5-10 min, M 15-30 min, L 45+ min (assumption; METR's 9% review share and 75% "read every line" say review time scales with diff size, not with ticket count).

## 5. Cost ceilings: what the tooling can enforce and what the numbers say

Enforcement points verified in docs:

- Claude Code `--max-budget-usd`: "Maximum dollar amount to spend on API calls before stopping (print mode only). Spend from subagents counts toward the cap. Once spend reaches the cap, spawning another subagent fails with `Budget limit reached`, and Claude Code stops background subagents that are still running; the cap-enforcement behaviors require Claude Code v2.1.217 or later." Also `--max-turns`. No time-limit flag. https://code.claude.com/docs/en/cli-reference (read 2026-09-02). The dispatcher must run agents with `-p` for the cap to apply.
- Claude Code reports cost at list price (1.1x for `inference_geo: "us"`); contracted rates only via managed `modelPricing`. https://code.claude.com/docs/en/costs
- Codex: `[features.rollout_budget]` with `limit_tokens` and `reminder_at_remaining_tokens` per session; org/project hard spend limits returning 429 since 2026-07-22 (lane-02). https://learn.chatgpt.com/docs/developer-commands?surface=cli
- Linear coding sessions: per-workspace and per-user spend limits, prepaid balance (lane-04, docs/ai-credits).
- Managed Agents: per-run dollar budget copied onto each session (lane-01).

Arithmetic for the default:

- EUR 10 per issue = USD 11.6. Below one Claude Code Code Review (USD 15-25) and below a Codex `max` session (USD 4.50-12) plus anything else. Fits S only.
- EUR 25 per issue = USD 29. Covers the modelled M range (USD 10-35) in most cases and equals the brief's own "richtwaarde onder EUR 25 per volledige run". Recommend EUR 25 hard for S and M, and no L runs without a split (or EUR 50 with explicit human approval, mirroring lane-02's advice to treat `ultra` as a human-approved escalation).
- EUR 50 per day = USD 58. That is about 2x the 90th-percentile human developer day on Claude Code (USD 30) and 4.5x the average (USD 13), so it is generous for one interactive operator but not for three full dry-run loops (3 x EUR 25 = EUR 75 before any rerun). Recommend EUR 100 per day on dry-run and demo days, EUR 50 on idle days (polling cost is cents: under USD 0.04 per background session plus small per-poll calls), alert at 70%, `agents/pause` label as the kill-switch.

## 6. Instrumentation plan for the three dry runs (closes success criteria 10 and 11)

1. Every agent run is `claude -p --bare --output-format json --max-budget-usd <cap> --max-turns <n>`. Parse from the result: `total_cost_usd`, `duration_ms`, `duration_api_ms`, `num_turns`, `session_id`, and `modelUsage[<model>]` with `inputTokens`, `outputTokens`, `cacheReadInputTokens`, `cacheCreationInputTokens`, `costUSD`, `costBasis` (`list` or `managed`; v2.1.246+). Use `total_cost_usd` or `modelUsage`, not `usage`: "usage ... Excluded. Counts only the top-level agent loop"; `total_cost_usd` and `modelUsage` include subagents. On `error_max_budget_usd`, `usage` omits the response that crossed the budget while `total_cost_usd` includes it. Cost is "client-side estimates, not authoritative billing data". https://code.claude.com/docs/en/agent-sdk/cost-tracking and https://code.claude.com/docs/en/headless (read 2026-09-02).
2. Codex runs: `codex exec --json` streams `turn.completed` events with usage; set `rollout_budget`; price tokens at Sol $4/$0.40/$20 or Terra $2/$0.20/$12 and record which. https://learn.chatgpt.com/docs/developer-commands?surface=cli
3. Optional cross-tool telemetry: `CLAUDE_CODE_ENABLE_TELEMETRY=1`, `OTEL_METRICS_EXPORTER=otlp`; metrics `claude_code.cost.usage` (USD) and `claude_code.token.usage` (type input/output/cacheRead/cacheCreation) carry attributes `model`, `query_source` (main/subagent/auxiliary), `effort`, `agent.name`, `skill.name`, `mcp_server.name`; `claude_code.active_time.total` with `type=user` gives human keyboard time in interactive sessions. https://code.claude.com/docs/en/monitoring-usage (read 2026-09-02). This is what the tooling table needs for cost per role.
4. Write per run into the Linear issue fields the brief already defines (ticketgrootte S/M/L, schatting, runtime, tokens, supervisieminuten) plus a signed comment with USD, EUR (ECB rate of the day, 1.1590 on 2026-09-01), model, effort, turns, wall-clock.
5. Wall-clock per state from Linear issue history; supervision minutes = human active time while an issue sits in a "Wacht op" state, self-reported in the field by the operator at each gate click, and cross-checked with the Orbit booking on the same ticket (`orbit_book_hours`, 5-minute rounding).
6. First-pass acceptance per S/M/L as defined in section 4; keep the QA verdict comment as evidence. For interactive Claude Code sessions the Analytics API adds `edit_tool.accepted/rejected` ("Tool acceptance rate = accepted / (accepted + rejected)"), Admin API organisations only. https://platform.claude.com/docs/en/build-with-claude/claude-code-analytics-api
7. Compare each run to the human column: booked minutes for a comparable Orbit ticket (section 2.2) times EUR 125, and the three-column layout of section 3.1.

## 7. Open items the requester must confirm

- Is EUR 125/h the confirmed 2026 development and growth rate, and is EUR 115 still the SEO/SEA rate or is the 2022 card superseded?
- Billing rounding unit for support (15/30/60 min) is still an open point in the Notion SLA policy; it changes the S band economics.
- The Orbit sample is one developer over four weeks; pulling `orbit_get_week` for two or three colleagues over eight weeks would make the S/M/L medians defensible for the whole tech team.
- Whether the demo bills agent cost at API list price (this note) or at plan-included usage (Max/Team seats), which changes the marginal cost story but not the comparison.

## 8. Fetch log

Successful primary fetches (all read 2026-09-02): code.claude.com/docs/en/costs; /cli-reference; /headless; /agent-sdk/cost-tracking; /monitoring-usage; developers.openai.com/api/docs/pricing; claude.com/pricing; linear.app/pricing; linear.app/docs/ai-credits; linear.app/docs/estimates; cursor.com/pricing; docs.github.com copilot-requests; hal.cs.princeton.edu and /swebench_verified_mini; metr.org blog and 2025-07-10 study; arxiv.org/html/2507.09089; anthropic.com/research/how-ai-is-transforming-work-at-anthropic; ecb.europa.eu USD reference rate; platform.claude.com claude-code-analytics-api; learn.chatgpt.com developer-commands (Codex CLI); codex.danielvaughan.com (secondary). Internal: Notion (4 pages fetched, 3 searches), Google Drive (1 search, rate-card sheet), Slack (2 searches), Orbit (4 weeks, boards, closed-ticket list).

Failed: WebSearch (quota exhausted, 6 queries not executed); hoofdkraan.nl (404 x3); malt.nl (403 x2); kvk.nl (404); zzp-nederland.nl (404); freelance.nl (404); upwork.com (403); dutchdigitalagencies.com (no benchmark); cognition.com/pricing (404); docs.devin.ai/billing/acus (404); tbench.ai leaderboard (table not rendered); support.claude.com consumption guide (no dollar figures); cursor.com/docs/account/billing (no spend-limit figures).
