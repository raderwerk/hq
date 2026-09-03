**Verdict:** A **gated, operator-run ticket mill** for S/M web/e-com work is feasible now. An **AI-run agency** (agents that sell, bind, ship live, talk to clients, and invoice) is not. Treat the percentages as *share of hours a supervised loop can finish to a senior-acceptable bar on typical Shopify/theme/custom tickets*, not “can draft something.”

| Function | Autonomous close | Supervised (human gates) | Notes |
|---|---:|---:|---|
| Sales | **5–10%** | **15–25%** | Drafts and intake routing. Close, price, politics: human. |
| Marketing | **10–20%** | **25–35%** | Semrush → SEO issues and copy drafts. Spend, brand, campaigns: human. |
| PM / scoping | **20–30%** | **40–55%** | Strong at extracting DoD from a thread. Weak at “what they meant.” |
| Dev execution | **35–50%** | **55–70%** | Highest real capability. Falls off on visual/theme/multi-system tickets. |
| QA | **20–30%** | **35–50%** | Second-model code review is useful. Visual/a11y/merchant-feel is not. |
| Delivery / client comms | **5–15%** | **20–35%** | Internal Linear comments: high. External send: drafts only. |
| Finance | **10–20%** | **25–40%** | Runtime → hours proposal + PDF. Orbit booking, VAT, write-offs: human. |

**Agency as a whole:** ~**45% of hours** on bounded S/M tickets with three hard gates. ~**10–15%** if you remove those gates. The sellable product is **one operator replacing 2–3 juniors**, not a firm that runs itself. Your own brief already assumes this (merge / client commitment / invoice stay human). That is the correct shape.

---

### 5 hardest blockers

1. **Ambiguous client spec.** Most agency tickets are under-specified. Agents implement a plausible reading, then the client says “not that.” Scoping agents help; they do not know the merchant. This is the rework engine. No model upgrade deletes it.

2. **Write-scope and identity.** Your Linear inventory (2026-09-02) shows **no agent app users**, MCP under **one human account**, and MCP **cannot** create teams, workflow states, or templates. Agents also must not get prod Shopify/Hyper credentials. Result: they cannot complete many real e-com tickets, and Linear history will look like one person did everything unless you forge identity with labels.

3. **Visual / brand bar.** Theme, Framer, and “make it look like the shop” work is the bulk of a digital agency. Code agents plus Playwright catch functional breaks. They do not reliably hit a designer’s or merchant’s eye. Dual LLM review does not fix that.

4. **Irreversible commitments.** Price, date, “it’s live,” “it’s fixed,” invoices, live store writes. One bad send is a client and a legal problem. Gates are not optional polish; they are the product.

5. **Orchestration reliability, not model IQ.** Polling every 2 minutes, one dispatcher, cost loops, context drift, dual SoT (Orbit tickets/hours vs Linear as agent OS). Agents fail by looping, marking Done without proof, or fighting over the same issue. `agents/pause` and a budget cap are load-bearing. Durable workflows and webhooks are not in the days-scale demo.

---

### What xAI / Grok offers for agentic work (Sept 2026)

**Observed in this session (not a product catalog):**
- Cursor exposes **Grok 4.5 / 4.6** as coding models (this run is Cursor Grok 4.6).
- GitLens changelog lists **Grok 4.6** and a provider rename **xAI → SpaceXAI**.
- Kilo Code changelog implies an **xAI API** with **native tool calling**, models including Grok 4 / 4 Fast / 4.1 Fast / **Grok Code Fast**, and an **xAI Responses**-style API (they mention disabling response storage by default).

**What that means:** Grok is a **worker model inside Cursor (and some other IDEs)**, plus a **hosted API with tool calling**. It is not, from anything I can verify here, an agency OS, a Linear agent runtime, or a Claude Code / Codex-class CLI orchestrator.

**I do not know (web/docs were blocked in this run):** whether xAI ships a first-party Agents SDK, computer-use/browser-use product, scheduled agents, enterprise data-retention / EU processing terms, official Linear integration, or current list prices. Do not plan the firm around Grok-specific agent infrastructure until `https://docs.x.ai` and Cursor model docs say so.

**Practical use in this design:** optional **second dev** or cheap/fast implementer. Orchestration should stay on **Claude Code** (MCP + subagents already match your brief). Codex as **second reviewer** is the diversity that matters; a third coding model is cost, not a new capability.

---

### Demo architecture (days, one design)

Do not build an agency. Build **one state machine**.

```
Orbit/Slack/mail (ingest, mock ok)
        ↓
Linear issue (state = lock, one assignee)
        ↓
Claude Code dispatcher (poll 2 min; only process with Linear MCP)
        ↓
  role prompt + input contract (repo, base branch, size, DoD)
        ↓
  subagent (no Linear tools): Claude/Codex/Cursor-Grok
        ↓
  artefact + signed comment + proposed next state
        ↓
  human gate: scope/price → merge → invoice
```

**Build in this order (nothing else):**
1. GraphQL or UI: DEV workflow with three `Wacht op-*` states; labels `agent/*`, `agents/pause`; fields for tokens/runtime.
2. Tiny demo repo + GitHub Actions + Playwright smoke.
3. Dispatcher: poll Linear, skip if `agents/pause` or budget exceeded, one run per issue.
4. Three jobs only: **scope** (spec + estimate comment), **dev** (worktree, PR, CI), **qa** (second model + required fail-then-pass loop).
5. Slack channel as fake client; invoice = generated PDF. No send, no prod deploy, no Orbit write.

Success is the loop completing with **three clicks** and **zero presenter edits** in Linear. If that fails three dry runs, the agency thesis failed, not the slide.

---

### 10 claims to verify

| # | Claim | Best source |
|---|---|---|
| 1 | Linear has a first-class **Agents** product (agent users, not one MCP human). | [linear.app/docs](https://linear.app/docs) — search “Agents”; changelog |
| 2 | Linear **MCP cannot** create teams/workflow states/templates (workspace rebuild needs GraphQL/UI). | Your inventory `linear/inventory-2026-09-02.md`; Linear GraphQL schema |
| 3 | Claude **Fable 5.1** pricing and **30-day retention / no ZDR**. | [docs.anthropic.com](https://docs.anthropic.com) model + data-retention pages (brief cites cache 2026-06-24; re-check) |
| 4 | **Claude Code** supports MCP, subagents, and unattended dispatch. | Anthropic Claude Code docs |
| 5 | **OpenAI Codex** (here: v0.147.0, `gpt-5.6-sol`) is a usable second reviewer, not just a chat model. | [developers.openai.com](https://developers.openai.com) Codex; local `codex --version` |
| 6 | **Cursor Grok 4.6** is available as an agent worker with tool use. | Cursor model docs; this session (exists). Confirm rate limits/pricing in-product. |
| 7 | xAI offers an API with **tool calling** and possibly **Responses**. | **[docs.x.ai](https://docs.x.ai)** — I could not fetch it this run |
| 8 | AI-generated **public** copy may need **AI Act Art. 50** disclosure. | EUR-Lex, Regulation (EU) 2024/1689 Art. 50 — lawyer, not a blog |
| 9 | Shopify **Admin writes** from an agent require a custom/dev app and still must not hit production. | [shopify.dev](https://shopify.dev) Admin API + app auth |
| 10 | “Agents do ~70% of S/M tickets first-pass.” | **Do not believe vendors.** Measure on 20 real Orbit tickets. METR / SWE-bench are proxies for code, not for theme/client work. |

**Bottom line:** Build the 45-minute gated loop. If unit economics on real S/M tickets beat a junior after supervision minutes, you have a process. You do not have an AI-run agency.
