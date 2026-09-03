# Lane 10: Independent third opinion from Grok 4.6 (Cursor CLI)

Date: 2026-09-02
Method: one non-interactive run of Cursor CLI (`agent` 2026.08.11-e8db854), model `cursor-grok-4.6-high-fast`, `--mode ask --trust`, from `/Users/youp/Developer/Personal/Raderwerk`. No web research was done in this lane. Raw output: `/Users/youp/Developer/Personal/Raderwerk/research/lane-cursor-grok46-raw.md` (92 lines).

## Independence caveat (read first)

The run was executed with `--trust` inside the project directory, so Grok read local files. Its answer cites `brief.md` (gates, "Wacht op" states, `agents/pause`, 30-day retention line, AI Act art. 50), `linear/inventory-2026-09-02.md` (no agent app users, MCP cannot create teams/states/templates) and local extension changelogs (GitLens 19.1.0, Kilo Code 7.5.6). Grok reported that web access was blocked in the run.

Consequence: the opinion is independent on the verdict, the percentages, the blocker ranking, the xAI section and the demo architecture, but NOT on the gate design and the compliance items, which are echoes of the brief. A grep of the Codex lane raw output (`lane-codex-gpt56-raw.md`) shows no phrase overlap (no "45%", "ticket mill", "state machine", "SpaceXAI", "Kilo", "Art. 50"), so Grok did not copy the Codex lane.

Everything Grok stated that was checkable locally was checked in this lane (see "Local verification"). Everything else is unverified model output and is rated confidence=low.

## Grok's verdict (condensed)

"A gated, operator-run ticket mill for S/M web/e-com work is feasible now. An AI-run agency (agents that sell, bind, ship live, talk to clients, and invoice) is not."

Percentages are defined as share of hours a supervised loop can finish to a senior-acceptable bar on typical Shopify/theme/custom tickets, not "can draft something".

| Function | Autonomous close | Supervised (human gates) | Grok's note |
|---|---:|---:|---|
| Sales | 5-10% | 15-25% | Drafts and intake routing only; close, price, politics human |
| Marketing | 10-20% | 25-35% | Semrush to SEO issues and copy drafts; spend, brand, campaigns human |
| PM / scoping | 20-30% | 40-55% | Strong at extracting DoD from a thread, weak at "what they meant" |
| Dev execution | 35-50% | 55-70% | Highest real capability; falls off on visual/theme/multi-system tickets |
| QA | 20-30% | 35-50% | Second-model code review useful; visual/a11y/merchant-feel not |
| Delivery / client comms | 5-15% | 20-35% | Internal Linear comments high; external send drafts only |
| Finance | 10-20% | 25-40% | Runtime to hours proposal + PDF; Orbit booking, VAT, write-offs human |

Agency as a whole: ~45% of hours on bounded S/M tickets with three hard gates; ~10-15% if gates are removed. Sellable product: one operator replacing 2-3 juniors, not a firm that runs itself.

## Grok's 5 hardest blockers

1. Ambiguous client spec. Agents implement a plausible reading; client says "not that". This is the rework engine; no model upgrade deletes it.
2. Write-scope and identity. Linear MCP runs under one human account, no agent app users, MCP cannot create teams/workflow states/templates. Agents must not hold prod Shopify/Hyper credentials, so many real e-com tickets cannot be completed end-to-end, and Linear history looks like one person did everything unless identity is forged with labels.
3. Visual / brand bar. Theme, Framer and "make it look like the shop" work is the bulk of agency work; Playwright catches functional breaks, not a designer's eye. Dual LLM review does not fix this.
4. Irreversible commitments. Price, date, "it's live", "it's fixed", invoices, live store writes. Gates are the product, not polish.
5. Orchestration reliability, not model IQ. Polling loops, cost loops, context drift, dual source of truth (Orbit vs Linear). Agents fail by looping, marking Done without proof, or fighting over the same issue. `agents/pause` and a budget cap are load-bearing. Durable workflows and webhooks are not in a days-scale demo.

## What Grok says xAI/Grok offers (Sept 2026)

Observed by Grok in local files, not a product catalog:
- Cursor exposes Grok 4.5 and Grok 4.6 as coding models.
- GitLens changelog lists Grok 4.6 and a provider rename xAI to SpaceXAI.
- Kilo Code changelog implies an xAI API with native tool calling (Grok 4 / 4 Fast / 4.1 Fast / Grok Code Fast) and an xAI Responses-style API (response storage disabled by default).

Grok's own conclusion: Grok is a worker model inside Cursor and some IDEs plus a hosted API with tool calling. It is not an agency OS, a Linear agent runtime, or a Claude Code / Codex-class CLI orchestrator as far as it could verify.

Grok explicitly does NOT know: whether xAI ships a first-party Agents SDK, computer-use / browser-use, scheduled agents, enterprise data-retention / EU processing terms, official Linear integration, or current list prices. Its advice: do not plan the firm around Grok-specific agent infrastructure until `https://docs.x.ai` and Cursor model docs say so. Practical role in this design: optional second dev or cheap/fast implementer; keep orchestration on Claude Code; Codex as second reviewer is the diversity that matters; a third coding model is cost, not capability.

## Grok's demo architecture ("build one state machine, not an agency")

```
Orbit/Slack/mail (ingest, mock ok)
  -> Linear issue (state = lock, one assignee)
  -> Claude Code dispatcher (poll 2 min; only process with Linear MCP)
  -> role prompt + input contract (repo, base branch, size, DoD)
  -> subagent (no Linear tools): Claude / Codex / Cursor-Grok
  -> artefact + signed comment + proposed next state
  -> human gate: scope/price -> merge -> invoice
```

Build order, nothing else:
1. GraphQL or UI: DEV workflow with three `Wacht op-*` states; labels `agent/*`, `agents/pause`; fields for tokens/runtime.
2. Tiny demo repo + GitHub Actions + Playwright smoke.
3. Dispatcher: poll Linear, skip if `agents/pause` or budget exceeded, one run per issue.
4. Three jobs only: scope (spec + estimate comment), dev (worktree, PR, CI), qa (second model + required fail-then-pass loop).
5. Slack channel as fake client; invoice = generated PDF. No send, no prod deploy, no Orbit write.

Success criterion: the loop completes with three clicks and zero presenter edits in Linear. If that fails three dry runs, the agency thesis failed, not the slide.

## Grok's 10 claims to verify

| # | Claim | Grok's best source |
|---|---|---|
| 1 | Linear has a first-class Agents product (agent users, not one MCP human) | linear.app/docs, search "Agents"; changelog |
| 2 | Linear MCP cannot create teams/workflow states/templates | `linear/inventory-2026-09-02.md`; Linear GraphQL schema |
| 3 | Claude Fable 5.1 pricing and 30-day retention / no ZDR | docs.anthropic.com model + data-retention pages (brief cites cache 2026-06-24; re-check) |
| 4 | Claude Code supports MCP, subagents, unattended dispatch | Anthropic Claude Code docs |
| 5 | OpenAI Codex (v0.147.0, gpt-5.6-sol) is a usable second reviewer | developers.openai.com Codex; local `codex --version` |
| 6 | Cursor Grok 4.6 is available as agent worker with tool use | Cursor model docs; this session; confirm rate limits/pricing in-product |
| 7 | xAI offers an API with tool calling and possibly Responses | docs.x.ai (not fetched in run) |
| 8 | AI-generated public copy may need AI Act Art. 50 disclosure | EUR-Lex, Regulation (EU) 2024/1689 Art. 50; lawyer, not a blog |
| 9 | Shopify Admin writes from an agent require a custom/dev app and must not hit production | shopify.dev Admin API + app auth |
| 10 | "Agents do ~70% of S/M tickets first-pass" | Do not believe vendors; measure on 20 real Orbit tickets; METR / SWE-bench are proxies for code, not theme/client work |

## Local verification performed in this lane (no web)

| Check | Result |
|---|---|
| `agent --list-models` | Lists `cursor-grok-4.6-{low,medium,high,xhigh}[-fast]` and `cursor-grok-4.5-{low,medium,high}[-fast]`. Grok 4.6 availability in Cursor CLI: confirmed. |
| `codex --version` | `codex-cli 0.147.0`. Confirmed. |
| `~/.cursor/extensions/eamodio.gitlens-19.1.0-universal/changelog.md` line 131 | "Adds support for the latest AI models: Claude Opus 5 and Claude Fable 5, GPT-5.6 (Sol, Terra, and Luna), Grok 4.6, Mistral ..., GLM 5.2". Confirmed. |
| Same file line 320 | "renames the xAI provider to SpaceXAI following its rebrand ... adding newer models (... Grok 4.5/4.3)". Confirmed as a GitLens statement; the rebrand itself is secondhand. |
| `~/.cursor/extensions/kilocode.kilo-code-7.5.6-darwin-arm64/CHANGELOG.md` lines 250, 254 | "Improved xAI prompt cache routing and PDF file support in Responses models"; "Disabled response storage by default for xAI Responses". Confirmed. |
| Same file lines 3712, 3714, 4097 | Native tool calling for xAI with Grok 4 Fast and Grok 4.1 Fast; "Default Grok Code Fast to native tools"; grok-4-1-fast-reasoning / non-reasoning models added. Confirmed as third-party changelog statements. |
| `linear/inventory-2026-09-02.md` lines 22, 28-30 | "No agent app users installed"; MCP CANNOT create/update teams, workflow states, templates, cycles, project labels, install agent/app users, delete issues. Confirmed (in-session inventory by the parent workflow). |
| `brief.md` lines 46, 70 | Fable 5.1 30-day retention / no ZDR, AI Act art. 50, gates: present in the brief. Grok's items 3 and 8 are echoes, not independent findings. |

## Findings table

Confidence policy: `low` = Grok model output, unverified; `medium` = verified against a local third-party artefact or in-session inventory but the underlying vendor fact is secondhand; `high` = directly observed from an official local tool.

| # | Claim | Source URL | Date | Confidence | Impact |
|---|---|---|---|---|---|
| 1 | Gated, operator-run ticket mill for S/M web/e-com work is feasible now; an AI-run agency that sells, binds, ships live, talks to clients and invoices is not. ~45% of hours automatable on bounded S/M tickets with three hard gates; ~10-15% without gates. | file:///Users/youp/Developer/Personal/Raderwerk/research/lane-cursor-grok46-raw.md | 2026-09-02 | low | high |
| 2 | Per-function autonomous / supervised shares: Sales 5-10 / 15-25; Marketing 10-20 / 25-35; PM 20-30 / 40-55; Dev 35-50 / 55-70; QA 20-30 / 35-50; Delivery 5-15 / 20-35; Finance 10-20 / 25-40. Dev execution is the only function above 50% even supervised. | file:///Users/youp/Developer/Personal/Raderwerk/research/lane-cursor-grok46-raw.md | 2026-09-02 | low | high |
| 3 | Sellable product is one operator replacing 2-3 juniors, not a self-running firm; the brief's shape (merge / client commitment / invoice stay human) is correct. | file:///Users/youp/Developer/Personal/Raderwerk/research/lane-cursor-grok46-raw.md | 2026-09-02 | low | high |
| 4 | Blocker 1: ambiguous client spec is the rework engine; scoping agents help but do not know the merchant; no model upgrade deletes it. | file:///Users/youp/Developer/Personal/Raderwerk/research/lane-cursor-grok46-raw.md | 2026-09-02 | low | high |
| 5 | Blocker 2: Linear MCP runs under one human account, no agent app users installed, MCP cannot create teams / workflow states / templates; full workspace rebuild needs GraphQL with a personal API key or manual UI; agent activity will look like one person unless identity is forged via labels. | file:///Users/youp/Developer/Personal/Raderwerk/linear/inventory-2026-09-02.md | 2026-09-02 | medium | high |
| 6 | Blocker 3: visual / brand bar (theme, Framer, "look like the shop") is the bulk of agency work and is not reliably met by code agents + Playwright; dual LLM review does not fix it. | file:///Users/youp/Developer/Personal/Raderwerk/research/lane-cursor-grok46-raw.md | 2026-09-02 | low | medium |
| 7 | Blocker 4: irreversible commitments (price, date, "live", "fixed", invoices, live store writes) make gates the product, not polish. | file:///Users/youp/Developer/Personal/Raderwerk/research/lane-cursor-grok46-raw.md | 2026-09-02 | low | high |
| 8 | Blocker 5: orchestration reliability, not model IQ, is the failure mode (loops, Done-without-proof, contention, dual SoT Orbit vs Linear); `agents/pause` and a budget cap are load-bearing; durable workflows and webhooks are out of scope for a days-scale demo. | file:///Users/youp/Developer/Personal/Raderwerk/research/lane-cursor-grok46-raw.md | 2026-09-02 | low | high |
| 9 | Grok 4.6 and Grok 4.5 are available in Cursor CLI as worker models with low/medium/high/xhigh and fast variants (`cursor-grok-4.6-high-fast` used in this run). | local: `agent --list-models` (Cursor CLI 2026.08.11-e8db854) | 2026-09-02 | high | medium |
| 10 | GitLens 19.1.0 changelog states the xAI provider was renamed to SpaceXAI "following its rebrand" and adds Grok 4.6, Claude Opus 5 / Fable 5 and GPT-5.6 Sol/Terra/Luna model support. | file:///Users/youp/.cursor/extensions/eamodio.gitlens-19.1.0-universal/changelog.md (lines 131, 320) | 2026-09-02 (file read) | medium | low |
| 11 | Kilo Code 7.5.6 changelog indicates the xAI API supports native tool calling (Grok 4 Fast, Grok 4.1 Fast, Grok Code Fast defaults to native tools) and an xAI "Responses" API where response storage is disabled by default. | file:///Users/youp/.cursor/extensions/kilocode.kilo-code-7.5.6-darwin-arm64/CHANGELOG.md (lines 250, 254, 3712, 3714, 4097) | 2026-09-02 (file read) | medium | medium |
| 12 | Grok could not verify any first-party xAI Agents SDK, computer-use / browser-use product, scheduled agents, EU data-processing terms, Linear integration or list prices; recommends not planning around Grok-specific agent infra, using Grok only as optional second dev, keeping orchestration on Claude Code and Codex as second reviewer. | https://docs.x.ai (not fetched; Grok's pointer) | 2026-09-02 | low | medium |
| 13 | Demo architecture: one state machine. Linear issue state = lock with single assignee; Claude Code dispatcher polls every 2 min and is the only process with Linear MCP; subagents (Claude / Codex / Cursor-Grok) get no Linear tools; three jobs only (scope, dev, qa); three human gates (scope/price, merge, invoice). | file:///Users/youp/Developer/Personal/Raderwerk/research/lane-cursor-grok46-raw.md | 2026-09-02 | low | high |
| 14 | Success criterion for the demo: loop completes with three clicks and zero presenter edits in Linear; if it fails three dry runs the agency thesis failed. | file:///Users/youp/Developer/Personal/Raderwerk/research/lane-cursor-grok46-raw.md | 2026-09-02 | low | high |
| 15 | Build order: (1) DEV workflow + labels + fields via GraphQL/UI, (2) demo repo + GitHub Actions + Playwright smoke, (3) dispatcher with pause/budget/one-run-per-issue, (4) scope/dev/qa jobs with required fail-then-pass QA loop, (5) Slack as fake client and PDF invoice; no send, prod deploy or Orbit write. | file:///Users/youp/Developer/Personal/Raderwerk/research/lane-cursor-grok46-raw.md | 2026-09-02 | low | medium |
| 16 | Do not trust vendor "~70% of S/M tickets first-pass" claims; measure on 20 real Orbit tickets; METR / SWE-bench are proxies for code, not theme/client work. | file:///Users/youp/Developer/Personal/Raderwerk/research/lane-cursor-grok46-raw.md | 2026-09-02 | low | high |
| 17 | Linear may have a first-class Agents product (agent users) distinct from the MCP-under-a-human setup; must be verified before designing agent identity. | https://linear.app/docs (Grok's pointer, unverified) | 2026-09-02 | low | high |
| 18 | Codex CLI 0.147.0 is installed locally and usable as second reviewer. | local: `codex --version` | 2026-09-02 | high | low |
| 19 | Fable 5.1 requires 30-day data retention (no ZDR) and AI-generated public copy may need AI Act Art. 50 disclosure. Echoed by Grok from brief.md lines 46/70, NOT an independent finding. | file:///Users/youp/Developer/Personal/Raderwerk/brief.md | 2026-06-24 (brief's cache date) | low | medium |
| 20 | Shopify Admin writes from an agent require a custom/dev app and must never target production. | https://shopify.dev (Grok's pointer, unverified) | 2026-09-02 | low | medium |

## What this means for the AI-agency demo

- Grok converges with the brief on shape: a gated loop with humans at scope/price, merge and invoice. It is more pessimistic on numbers than a hype narrative: ~45% of hours on bounded S/M tickets, dev execution the only function above 50%. Use these as the honest baseline on the closing slide, not as vendor promises.
- Its most useful additions are process-level: state = lock with one assignee, a single dispatcher holding Linear MCP, workers without Linear tools, a forced fail-then-pass QA loop, and a pass/fail criterion (three clicks, zero presenter edits, three dry runs).
- On xAI/Grok: nothing verifiable beyond "Grok 4.6 is a Cursor worker model and xAI has a tool-calling API". Do not build agency infrastructure on Grok; use it as an interchangeable implementer at most.
- The Linear identity/write-scope blocker is real and in-session verified: workspace rebuild needs the GraphQL API or UI, and agent attribution needs either Linear's Agents product (unverified) or a label convention.
- Treat the percentages, blockers and architecture as one analyst's opinion generated without web access and with the brief in context. Cross-check with the other lanes before they inform a go/no-go.
