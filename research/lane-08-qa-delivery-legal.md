# Lane 08 — QA, delivery, accountability and legal (state as of 2026-09-02)

Scope: what an AI-run Dutch digital agency (Fightclub Agency: Shopify, configurators, portals, marketing/SEO) can automate today for code review, QA/E2E, acceptance-criteria verification, deliverable verification and invoicing/admin, and which EU/NL legal obligations are actually in force on 2 September 2026. Research method: 28 web searches plus direct reads of ~35 primary sources (vendor docs, changelogs, pricing pages, EU Commission pages, law-firm analyses). Confidence is marked per claim. Where a page could not be fetched (paywall/403) this is stated.

---

## 1. Executive summary

1. **PR-level automated review is commodity.** Four production-grade reviewers exist and can all run on every PR: Cursor Bugbot (usage-based, roughly $1.00–1.50 per review since June 2026), Claude Code "Code Review" (managed, Team/Enterprise only, $15–25 per review, multi-agent with a verification pass), Codex `@codex review` / `codex review` CLI (included in ChatGPT plan usage) and CodeRabbit (per-seat, $24–72/dev/month, the only one that natively validates a PR against Linear acceptance criteria). None of them blocks merges by default; gating must be built in CI.
2. **Browser QA by agents is real but split across two modes.** Deterministic: Playwright MCP (`@playwright/mcp` 0.0.80) + Playwright Test Agents (planner/generator/healer, `npx playwright init-agents --loop=claude|codex|vscode|opencode`) + Vercel `agent-browser` (Rust CLI, 41.8k stars) all run headless and in CI. Exploratory: Claude in Chrome / `claude --chrome` is GA on Max/Team/Enterprise, reads console/network/DOM, but needs a visible Chrome window and a `/login` session (no API-key/CI use).
3. **Acceptance criteria can be machine-verified only if written that way.** Anthropic's Jan 2026 evals guidance (code graders + human-calibrated LLM rubrics, pass@k / pass^k, grade outcomes not process) is the right template; CodeRabbit's Linear integration and Claude Code Review's machine-readable severity JSON are the two off-the-shelf gates.
4. **Invoicing/admin is fully API-able.** Teamleader Focus (`invoices.draft` → `invoices.book` → `invoices.send`, `timeTracking.add`, `tickets.*`), Moneybird v2 (OAuth/token, sandbox administrations, webhooks, UBL 2.1) and Exact Online (OData REST, 60/min and 5,000/day, app-review gate) all support end-to-end quote-to-cash. No Dutch B2B e-invoicing mandate exists yet; ViDA cross-border B2B starts 1 July 2030.
5. **EU AI Act on 2026-09-02:** Article 5 prohibitions and Article 4 AI-literacy (since 2 Feb 2025), GPAI provider obligations (since 2 Aug 2025) and **Article 50 transparency (since 2 Aug 2026)** are in force. The Digital Omnibus on AI, Regulation (EU) 2026/1744 (OJ 24 Jul 2026, in force 27 Jul 2026), deferred **high-risk** obligations to 2 Dec 2027 (Annex III) and 2 Aug 2028 (Annex I), softened Article 4 to an effort obligation and gave only a narrow Art. 50(2) marking grace period to 2 Dec 2026. For an agency this means: AI-disclosure on chatbots, labelling of deepfakes and of unreviewed AI text on matters of public interest, AI-literacy measures, and no high-risk paperwork for normal agency work.
6. **Liability/IP:** purely AI-generated output has no copyright under Dutch/EU law (no personal stamp), so the agency cannot assign what does not exist; the AI Liability Directive was withdrawn (OJ 6 Oct 2025), so Dutch contract and tort law (art. 6:74 / 6:162 BW) govern; the new Product Liability Directive (software and AI as products) applies from 9 Dec 2026 to natural-person damage, not to B2B loss. The Dutch AI Act implementing law (Uitvoeringswet AI-verordening) was only in consultation (20 Apr–1 Jun 2026) so NL enforcement of Art. 50 is not yet operational, but the obligation is binding.

---

## 2. Automated code review (as of 2026-09-02)

### 2.1 Cursor Bugbot
- Pricing changed from $40/seat/month to usage-based: average run "$1.00–1.50 depending on PR size and complexity"; effective for existing customers at the first renewal after 8 June 2026, immediately for new customers. Individuals bill from included usage, Teams from on-demand spend. Source: cursor.com blog, 11 May 2026.
- June 2026 update: reviews ~90 s (down from ~5 min), 22% cheaper per run, 10% more bugs found (0.62 vs 0.56 average per review), powered by Composer 2.5; `/review` runs Bugbot and Security Review pre-push in Cursor 3.7+; incremental reviews skip already-reviewed diffs. Source: cursor.com changelog, 10 June 2026.
- Quality claims (vendor): 80% of found bugs are resolved by merge; High effort finds 35% more bugs. Effort levels Low / Default / High / Smart.
- Mechanics: GitHub, GitLab, Bitbucket, Azure DevOps; per-repo enable in "Automations"; automatic on each PR update, manual via `cursor review` or `bugbot run`; rules in `.cursor/BUGBOT.md` (30k chars per file, 100k combined) plus `@cursor remember`; Autofix spawns Cloud Agents (max 3 attempts/PR). The Bugbot docs do not mention a Linear integration.

### 2.2 Claude Code (Anthropic)
- **Code Review (managed):** research preview, only for Team and Enterprise subscriptions, not available with Zero Data Retention. Fleet of agents + a verification step against actual code behaviour, deduplicated and ranked; posts inline comments plus a "Claude Code Review" check run that always completes **neutral** (never blocks). Average cost **$15–25 per review**, billed via usage credits, ~20 min average duration; triggers: once after PR creation / after every push / manual (`@claude review`, `@claude review always`). Tunable via `REVIEW.md`. The check-run output contains a machine-readable `bughunter-severity` JSON (`{"normal":2,"nit":1,"pre_existing":0}`) you can parse with `gh` to gate merges in your own CI. Source: code.claude.com/docs/en/code-review (fetched 2026-09-02).
- **claude-code-action v1 (self-hosted in GitHub Actions):** `/install-github-app` quick setup; authenticates with `ANTHROPIC_API_KEY`, a subscription `CLAUDE_CODE_OAUTH_TOKEN` (Pro/Max/Team/Enterprise) or OIDC federation; the review workflow runs the `code-review` plugin with `--comment`; skips drafts/trivial PRs; fork PRs get no secrets on public repos. Cost = Actions minutes + tokens (or subscription).
- **Local:** `/code-review [low|medium|high|max|ultra] [--fix] [--comment]`, runs as background subagent; `ultra` escalates to cloud ultrareview (claude.ai auth only).
- **claude-code-security-review action:** PR-scoped security review with false-positive filtering; default model in the README is still `claude-opus-4-1-20250805`; README warns it is not hardened against prompt injection (use maintainer approval for external PRs).

### 2.3 OpenAI Codex
- GitHub: `@codex review` on a PR, or enable automatic reviews of every new PR in Codex settings; `@codex security review` is a separate research-preview deep review; repo rules in `AGENTS.md` under `## Code Review Rules`. Source: learn.chatgpt.com/docs/third-party/github.
- Billing: Codex is included in Free/Go/Plus/Pro/Business/Edu/Enterprise; GitHub reviews consume the same Codex usage allowance (no separate bill). Source: learn.chatgpt.com/docs/pricing (promo pricing valid "at least through November 21, 2026").
- CLI: `codex review` is marked Stable, non-interactive, with `--base <branch>`, `--commit <SHA>`, `--uncommitted`, or a custom prompt (mutually exclusive). Source: learn.chatgpt.com/docs/developer-commands.
- Codex Security (repo-wide AppSec agent, sandbox validation of findings, ranked fixes) launched in research preview on 6 March 2026 for Enterprise/Business/Edu (press, medium confidence).

### 2.4 CodeRabbit
- Official pricing page (fetched 2026-09-02): **Essentials** $24/dev/month annual ($30 monthly), **Team** $48 ($60), **Advanced** $72 annual, Enterprise custom; charged only for developers who open PRs; rate limits 5–12 PR reviews/dev/hour; $0.25 per reviewed file beyond allowance. Secondary sites still call the tiers "Pro/Pro Plus"; the docs say "Essentials (formerly Pro)".
- Differentiator for an agency: the Linear integration (OAuth) does **requirement validation** — "assesses whether your code changes properly address the linked issue's acceptance criteria and flags any gaps" — plus Issue Planner and issue creation from review comments. Available from Essentials up. Source: docs.coderabbit.ai/integrations/issue-integrations.

### 2.5 Comparison for the demo

| Reviewer | Trigger | Cost model (2026-09) | Gating | AC-aware | Notes |
|---|---|---|---|---|---|
| Cursor Bugbot | auto per push / `cursor review` | ~$1.00–1.50 per run | no (comments) | no | fastest/cheapest; Autofix |
| Claude Code Review | once / every push / `@claude review` | $15–25 per review, Team/Enterprise | neutral check run; JSON parsable | via REVIEW.md rules | deepest; verification pass |
| claude-code-action | any GH event | tokens or subscription | you decide in workflow | prompt-defined | full control, self-hosted |
| Codex review | `@codex review` / auto | plan usage | no | AGENTS.md rules | plus security review |
| CodeRabbit | auto per PR | $24–72/dev/month | custom pre-merge checks (Team) | yes (Linear AC) | 4 git platforms |

Constraint from memory: the Fightclub GitHub org is on the Free plan (no branch protection/rulesets on private repos), so any "block merge on findings" rule has to be enforced by the orchestrator, not by GitHub.

---

## 3. Automated QA / E2E with browser agents

- **Playwright MCP** (`@playwright/mcp` 0.0.80, depends on `playwright 1.63.0-alpha-2026-08-31`, Apache-2.0, 36.7k stars): accessibility-tree snapshots (deterministic, no vision needed; `--caps=vision` optional), 40+ tools, network mocking, tracing, video; one-line install for Claude Code (`claude mcp add playwright npx @playwright/mcp@latest`), Cursor, Codex, VS Code. The README itself notes coding agents increasingly prefer CLI workflows over MCP for token efficiency.
- **Playwright Test Agents** (playwright.dev/docs/test-agents): planner (explores app → Markdown plan in `specs/`), generator (plan → tests in `tests/`), healer (runs suite, repairs failures, with loop guardrails). `npx playwright init-agents --loop=claude|codex|vscode|opencode`; seed tests provide fixtures/auth.
- **Vercel agent-browser** (github.com/vercel-labs/agent-browser): Rust CLI with daemon, `snapshot`/`click @ref`/`fill`/`screenshot`, Apache-2.0, 41.8k stars, Browserbase/Browserless support, skill install `npx skills add vercel-labs/agent-browser`. Suits long autonomous sessions where context budget matters.
- **Claude in Chrome / Claude Code `--chrome`**: available on all paid plans (Pro/Max/Team/Enterprise); GA on Max/Team/Enterprise, Pro side-panel still beta; scheduled recurring browser tasks; admin site allow/blocklists (Team/Enterprise). Claude Code integration reads console errors, network requests and DOM, uploads files, records GIFs, and pauses on login/CAPTCHA. Limits that matter for an agency pipeline: needs a visible Chrome window, `/login` session (API keys and `setup-token` tokens disable it), not available through Bedrock/Vertex/Foundry, not in WSL. Therefore: good for exploratory QA and demos on a dev machine, not for headless CI.
- Practical stack for the demo: Playwright Test Agents generate specs from Linear acceptance criteria → Playwright runs in CI (GitHub Actions) → healer keeps them green → Claude/Chrome only for exploratory acceptance and screenshot evidence attached to the Linear issue.

---

## 4. Acceptance-criteria automation and deliverable verification

- **Anthropic, "Demystifying evals for AI agents" (9 Jan 2026):** three grader types (code-based: fast/objective but brittle; model-based LLM rubrics: flexible but must be "closely calibrated with human experts"; human: gold standard). Track pass@k and pass^k for non-deterministic agents; "grade what the agent produced, not the path it took"; read transcripts on failure.
- **Linear as the system of record:** agents are workspace members; when an issue is delegated "the human user remains the primary assignee, while the agent is added as a contributor"; agent sessions expose thoughts/actions/reasoning; agents must emit a `thought` within 10 s of a delegation webhook (`app:assignable`, `app:mentionable` scopes). Listed agents on linear.app/agents: Linear Agent, Cursor, OpenAI Codex, Devin, Sentry, ChatPRD, Oz by Warp, Factory, Charlie, Ranger, Tembo (Claude Code is not on that page; Claude Code reaches Linear via MCP).
- **Off-the-shelf AC gates:** CodeRabbit requirement validation against Linear issue AC; Claude Code Review severity JSON in the check run; Playwright specs one-to-one with AC.
- **Design rule for the demo:** every Linear issue carries (a) machine-checkable AC (test names, Lighthouse/Core Web Vitals thresholds, Shopify theme-check clean, Playwright spec IDs), (b) rubric AC for an LLM judge calibrated on 20–30 human-graded samples, (c) a human "editorial responsibility" checkbox for anything public-facing (this also secures the Art. 50(4) exception below).

---

## 5. Invoicing / admin automation (NL stack)

| System | Auth | Key endpoints | Limits / notes | Source (date) |
|---|---|---|---|---|
| Teamleader Focus API | OAuth2 (`focus.teamleader.eu/oauth2/authorize`) | `invoices.draft` → `invoices.book` → `invoices.send`; `invoices.registerPayment`, `invoices.credit`, `invoices.updateBooked`; `quotations.create/send/accept`; `timeTracking.add`; `tickets.list/info/create/update/addReply/addInternalMessage` | sliding-window rate limit, `X-RateLimit-*` headers, HTTP 429; booked invoices cannot be edited except via `updateBooked` | github.com/teamleadercrm/api apiary.apib (fetched 2026-09-02) |
| Teamleader Orbit | OAuth SSO; "open API" advertised for Orbit Suite (marketing) | Invantive lists an Orbit API driver with 8 tables (2023); Orbit = planning/resources/projects for agencies 20+, invoicing from quote/project, client portal with Peppol | Orbit and Focus are different products; do not reuse Focus routes. The developer.orbit.teamleader.eu URL returned nothing; Orbit API scope unverified | teamleader.eu/orbit (2026), forums.invantive.com (8 Sep 2023) |
| Moneybird API v2 | OAuth2 or personal API token | `POST /{administration_id}/sales_invoices`, send (`sends_an_invoice`), `send_reminders`, `download_ubl` (UBL 2.1), webhooks `POST /webhooks` (scope `settings`) | 150 requests / 5 min per IP (50 for reports), HTTP 429; sandbox administrations with watermarked invoices; docs last modified 2 Sep 2026 | developer.moneybird.com (2026-09-02) |
| Exact Online REST | OAuth2, regional endpoints, division id per call | `/api/v1/{division}/salesinvoice/SalesInvoices` GET/POST/PUT/DELETE; POST requires `InvoiceTo`, `OrderedBy`, `Journal`, `SalesInvoiceLines`; webhook topic `SalesInvoices` | 60 calls/min and 5,000/day per app-company; no `$expand`; until Exact reviews the app it only connects to the creating instance | start.exactonline.nl docs; apideck guide (27 Jan 2026, upd. 13 May 2026) |

- Fightclub already runs an Orbit MCP (`orbit_book_hours`, `orbit_create_todo`, etc.), so hour booking and ticket flow are demo-ready; invoicing for the demo is easiest via a Moneybird sandbox administration (free, watermarked) or Teamleader Focus `invoices.draft`.
- **E-invoicing:** no Dutch B2B mandate today (B2G since 2017). ViDA makes cross-border B2B e-invoicing mandatory from 1 July 2030; the Dutch government's 10 March 2026 evaluation letter points to mandatory domestic B2B via Peppol phased 2030–2032, cabinet position expected summer 2026 and draft legislation Q4 2026 (secondary sources: peppol.nu, computable.nl; medium confidence). Design invoices as UBL/Peppol-ready now (Moneybird and Orbit already support it).

---

## 6. EU AI Act: what is in force on 2026-09-02

Regulation (EU) 2024/1689, as amended by the **Digital Omnibus on AI, Regulation (EU) 2026/1744** (European Parliament vote 16 Jun 2026, Council 29 Jun 2026, OJ 24 Jul 2026, in force 27 Jul 2026).

| Obligation | Applies since | Status 2026-09-02 | Agency relevance |
|---|---|---|---|
| Art. 5 prohibited practices (manipulative/deceptive techniques, exploiting vulnerabilities, etc.) | 2 Feb 2025 | in force; two new prohibitions (non-consensual intimate imagery, AI CSAM) from 2 Dec 2026 | AI-driven personalisation/marketing must not "materially distort behaviour" causing significant harm; fines €35M / 7% |
| Art. 4 AI literacy | 2 Feb 2025 | in force, **rewritten** by Omnibus: "take measures to support the development of AI literacy", explicitly no guaranteed level (effort obligation); national supervision reported from 3 Aug 2026 | keep a training log for staff and supervising humans |
| Arts. 53–55 GPAI provider obligations; GPAI Code of Practice (10 Jul 2025) | 2 Aug 2025 (new models); 2 Aug 2027 (pre-existing models) | in force; Anthropic, OpenAI, Google, Microsoft full signatories; **xAI signed only the Safety & Security chapter** and must show transparency/copyright compliance "via alternative adequate means" | obligations sit on the model providers, not on the agency as user; vendor selection point for Grok |
| **Art. 50 transparency** | **2 Aug 2026** | in force, **not deferred**; only Art. 50(2) machine-readable marking for generative systems already on the market gets until 2 Dec 2026; Commission guidelines final (updated 6 Aug 2026); Code of Practice on transparency of AI-generated content final 10 Jun 2026 (~190 signatories late Jul 2026; deployers may sign) | see 6.1 |
| Annex III high-risk (Art. 6(2), Arts. 8–27) | ~~2 Aug 2026~~ → **2 Dec 2027** | deferred by Omnibus | not applicable to normal agency work; watch HR/credit/education use-cases |
| Annex I high-risk (AI in regulated products) | ~~2 Aug 2027~~ → **2 Aug 2028** | deferred | n/a |
| Art. 99 fines | 2 Aug 2025 | Art. 5: €35M/7%; Art. 50 and other operator duties: €15M/3%; wrong info to authorities: €7.5M/1%; SMEs pay the **lower** of amount/percentage | agency = SME → lower thresholds |
| Other Omnibus items | 27 Jul 2026 | new Art. 4a (special-category data for bias detection), SMC relief (<750 staff, <€150M), national sandboxes deferred to 2 Aug 2027, AI Office exclusive competence for GPAI-based systems from the same provider | minor for an agency |

### 6.1 Article 50 applied to an agency
- **Roles.** If the agency builds and ships an AI feature (e.g. a chatbot on a client webshop) under its own name, the agency is the **provider** and the client is the **deployer**; contracts must state who implements the disclosure. If the agency merely uses Claude/Codex/Grok to produce code or copy, the agency is a deployer of a GPAI system; the deliverable (code, copy) is not itself an "AI system".
- **Art. 50(1)** (provider): chatbots/voice agents must tell people they are talking to AI at first interaction unless obvious. **Art. 50(2)** (provider): machine-readable marking of synthetic audio/image/video/text — this sits on Anthropic/OpenAI/xAI, not on the agency, unless the agency wraps a model into its own generative product.
- **Art. 50(4)** (deployer): (a) deepfakes must be disclosed (artistic/satirical works: lighter disclosure); (b) AI-generated text "published with the purpose of informing the public on matters of public interest" must be disclosed **unless it has been subject to human review or editorial control and a natural or legal person holds editorial responsibility**. The May 2026 practitioner guide reads product/service marketing copy as normally outside "matters of public interest" (trigger is the publisher's purpose), but news-style content, health/finance advice or public-affairs blogs for clients are inside. A documented human editorial sign-off in the Linear workflow is therefore both a quality gate and the legal exception.
- **Disclosure form:** at first interaction/exposure, clear and distinguishable, accessible; footers, faint labels or T&C burial fail. The Commission published an icon set for deployers.
- **Enforcement in NL:** the Uitvoeringswet AI-verordening (consultation 20 Apr–1 Jun 2026) designates the Autoriteit Persoonsgegevens as market-surveillance authority for prohibited practices, Art. 50 transparency and most high-risk systems, with RDI as central contact and AP/RDI coordinating; fines up to the Art. 99 maxima; full entry into force anticipated 2 Aug 2027 (regulations.ai; medium confidence). The Netherlands missed the 2 Aug 2025 designation deadline. Practical reading: binding obligation, low near-term NL enforcement capacity.

---

## 7. Liability and IP of AI-generated deliverables (NL/EU)

- **Copyright.** Dutch Auteurswet / EU standard: protection requires an "eigen oorspronkelijk karakter en persoonlijk stempel" (author's own intellectual creation, free creative choices; CJEU Cofemel 2019, Mio/Konektra 4 Dec 2025). Purely AI-generated output without substantial human creative input is **not** protected; prompts alone or picking one of several outputs are insufficient. The Düsseldorf Regional Court (2 Apr 2026) applied this to AI output (reported by Wisemen; no confirmed EU case yet granting protection). Consequences for the agency: it cannot warrant that copyright subsists in AI-generated code/copy, cannot give exclusivity, and a competitor may reuse the logic. Mitigation: document human creative decisions per deliverable, keep prompt/iteration logs, and draft the IP clause as an assignment "to the extent rights exist".
- **Infringement risk in outputs.** CJEU C-250/25 Like Company v Google (first GenAI/copyright reference; Grand Chamber hearing 10 Mar 2026; Advocate General opinion scheduled 3 Sep 2026) will shape whether reproducing/summarising protected content by an LLM is infringing and where. Outcome pending at the time of writing.
- **AI Liability Directive: withdrawn.** Commission decision 16 Jul 2025, OJ notice 6 Oct 2025. No EU fault-based AI liability regime; national law applies.
- **Dutch law today.** Errors in AI-generated deliverables are handled through contractual liability (art. 6:74 BW), tort (art. 6:162 BW) and, for defective products, product liability. Courts look at whether the deploying party exercised reasonable oversight and verification before publication; disclaimers alone do not remove liability; B2B contracts may allocate risk more freely than consumer contracts (Law & More, 13 Jan 2026).
- **New Product Liability Directive (EU) 2024/2853.** Applies to products placed on the market after **9 Dec 2026**; stand-alone software and AI systems are "products"; software providers/those who substantially modify a product can be "manufacturers"; damages include death/injury, property not used exclusively professionally, and non-professional data loss; burden-of-proof presumptions where the defendant fails disclosure or the product is technically complex. It protects **natural persons**; a client's business loss from a broken webshop is not a PLD claim, but harm to consumers using agency-built software could be. NL: bill amending Books 6 and 7 BW published, pending parliament (business.gov.nl; Inside Privacy, 2026). business.gov.nl explicitly advises reviewing product-liability insurance.
- **Vendor indemnities (unverified in this session):** Anthropic and OpenAI have published IP indemnities for paid/enterprise customers in the past; current 2026 terms and their applicability to a Claude Team subscription vs API were not checked. Confidence low; verify before relying on them in client contracts.

---

## 8. Client contract clauses for an AI-run agency

Baseline in the Dutch market: **NLdigital Voorwaarden 2025** (published Jan 2026; page updated 2 Apr 2026) add AI provisions aligned with the AI Act; per BG.legal (19 Jan 2026) they put **AI literacy and human oversight on the client** and forbid using supplied software/data/reports for training, text/data mining, scraping or model adaptation without supplier permission. The full text is paid; the older Dirkzwager critique (2022) of the standard set (best-effort bug fixing, indicative deadlines, broad exclusion of indirect damage) still applies.

Recommended clause set (synthesis of Law & More Jan 2026, the AI Act analysis above and 2026 agency-contract guidance):

1. **AI disclosure and consent** — which tool classes are used at which stages (code, copy, design, QA), opt-out for named sensitive projects, no silent model switching for regulated content.
2. **Human review and editorial responsibility** — named human signs off public-facing text/visuals; the agency (or client) takes editorial responsibility, which secures the Art. 50(4) exception; review logs retained.
3. **IP** — assignment/licence of all rights "to the extent they exist"; express statement that copyright may not subsist in AI-generated portions; non-infringement warranty limited to commercially reasonable checks (licence scans, similarity checks, no verbatim copying of third-party code/text); indemnity capped at fees.
4. **Data and confidentiality** — client materials not used for model training; enterprise/API terms with zero or limited retention; sub-processor list naming Anthropic, OpenAI, xAI (and Cursor if Bugbot is used); GDPR DPA; note xAI's partial GPAI Code signature when the client asks about copyright/transparency guarantees.
5. **Liability** — cap tied to fees per project/year; indirect damage excluded; Dutch mandatory carve-outs (opzet/bewuste roekeloosheid) respected; separate cap for data loss.
6. **Acceptance procedure** — machine-verifiable acceptance criteria in Linear, acceptance test window, deemed acceptance, defect classes and fix SLAs.
7. **Audit and evidence** — agent transcripts, review outputs, model/version identifiers and test evidence retained for a defined period (supports PLD disclosure duties and any AP inquiry).
8. **AI Act role allocation** — for delivered AI features: who is provider/deployer, who implements Art. 50 disclosures, who handles user complaints; explicit statement that the deliverable is not an Annex III high-risk system (or escalation path if it is).
9. **Model continuity** — right to substitute equivalent models; notice on material capability changes.
10. **Insurance** — beroeps-/productaansprakelijkheid covering software deliverables ahead of 9 Dec 2026.

---

## 9. Findings table

| # | Claim | Source URL | Date of source | Confidence | Impact |
|---|---|---|---|---|---|
| 1 | Cursor Bugbot moved from $40/seat/month to usage billing, ~$1.00–1.50 per review, effective at first renewal after 8 Jun 2026 | https://cursor.com/blog/may-2026-bugbot-changes | 2026-05-11 | high | high |
| 2 | Bugbot June 2026: ~90 s reviews, 22% cheaper, 10% more bugs, Composer 2.5, `/review` in Cursor 3.7+ | https://cursor.com/changelog/bugbot-updates-june-2026 | 2026-06-10 | high | medium |
| 3 | Bugbot rules in `.cursor/BUGBOT.md`, effort levels Low/Default/High/Smart, Autofix via Cloud Agents (max 3 attempts), GitHub/GitLab/Bitbucket/Azure DevOps | https://cursor.com/docs/bugbot | fetched 2026-09-02 | high | medium |
| 4 | Claude Code Code Review: research preview, Team/Enterprise only, not with ZDR, $15–25 per review via usage credits, neutral check run with parsable severity JSON, REVIEW.md tuning | https://code.claude.com/docs/en/code-review | fetched 2026-09-02 (mentions July 2026 update) | high | high |
| 5 | claude-code-action v1 runs the code-review plugin on PR events with API key, subscription OAuth token (Pro/Max/Team/Enterprise) or OIDC federation | https://code.claude.com/docs/en/github-actions | fetched 2026-09-02 | high | high |
| 6 | claude-code-security-review action defaults to claude-opus-4-1 and is not hardened against prompt injection | https://github.com/anthropics/claude-code-security-review | fetched 2026-09-02 | high | medium |
| 7 | Codex: `@codex review`, automatic reviews toggle, `@codex security review` (research preview), rules via `AGENTS.md ## Code Review Rules` | https://learn.chatgpt.com/docs/third-party/github | fetched 2026-09-02 | high | high |
| 8 | Codex included in Free/Go/Plus/Pro/Business/Edu/Enterprise; GitHub reviews draw from the same Codex usage allowance | https://learn.chatgpt.com/docs/pricing | fetched 2026-09-02 (promo through 2026-11-21) | high | medium |
| 9 | `codex review` CLI is Stable, non-interactive, `--base` / `--commit` / `--uncommitted` / custom prompt | https://learn.chatgpt.com/docs/developer-commands?surface=cli | fetched 2026-09-02 | high | medium |
| 10 | Codex Security launched 6 Mar 2026 in research preview for Enterprise/Business/Edu | https://aibusiness.com/agentic-ai/openai-launches-codex-security | 2026-03 | medium | low |
| 11 | CodeRabbit pricing: Essentials $24 (annual)/$30, Team $48/$60, Advanced $72, Enterprise custom; billed per PR-opening dev; 5–12 reviews/dev/hour; $0.25/file overage | https://www.coderabbit.ai/pricing | fetched 2026-09-02 | high | medium |
| 12 | CodeRabbit Linear integration validates whether a PR addresses the linked issue's acceptance criteria and flags gaps; Issue Planner | https://docs.coderabbit.ai/integrations/issue-integrations | fetched 2026-09-02 | high | high |
| 13 | `@playwright/mcp` 0.0.80 on `playwright 1.63.0-alpha-2026-08-31`, Apache-2.0; accessibility-snapshot based, 40+ tools, Claude Code/Cursor/Codex/VS Code | https://unpkg.com/@playwright/mcp/package.json and https://github.com/microsoft/playwright-mcp | fetched 2026-09-02 | high | high |
| 14 | Playwright Test Agents planner/generator/healer, `npx playwright init-agents --loop=claude|codex|vscode|opencode` | https://playwright.dev/docs/test-agents | fetched 2026-09-02 | high | high |
| 15 | Vercel agent-browser: Rust CLI for agents, 41.8k stars, Apache-2.0, snapshot/click/fill/screenshot, Browserbase/Browserless | https://github.com/vercel-labs/agent-browser | fetched 2026-09-02 | high | medium |
| 16 | Claude in Chrome available on all paid plans; GA on Max/Team/Enterprise, Pro side panel beta; scheduled tasks; admin allow/blocklists | https://support.claude.com/en/articles/12012173-getting-started-with-claude-in-chrome | fetched 2026-09-02 | high | medium |
| 17 | Claude Code `--chrome` needs visible Chrome and `/login` (API key / setup-token disable it), not via Bedrock/Vertex/Foundry, reads console/network/DOM | https://code.claude.com/docs/en/chrome | fetched 2026-09-02 | high | high |
| 18 | Anthropic evals guidance: code graders + human-calibrated LLM rubrics + human graders; pass@k and pass^k; grade outcomes not process | https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents | 2026-01-09 | high | high |
| 19 | Linear agents: human stays primary assignee, agent added as contributor/delegate; agent sessions; `thought` within 10 s; directory lists Codex, Cursor, Devin, Sentry, Factory, Charlie, etc. | https://linear.app/developers/agents and https://linear.app/agents | fetched 2026-09-02 | high | high |
| 20 | Teamleader Focus API: `invoices.draft`→`book`→`send`, `registerPayment`, `credit`, `quotations.create/send/accept`, `timeTracking.add`, `tickets.*`; OAuth2; sliding-window rate limits | https://github.com/teamleadercrm/api/blob/master/apiary.apib | fetched 2026-09-02 | high | high |
| 21 | Teamleader Orbit is a separate product with its own (less documented) API; Focus routes do not apply; Invantive driver covers 8 tables | https://forums.invantive.com/t/teamleader-orbit-api-data-model-available-online/3736 ; https://support.focus.teamleader.eu/hc/en-150/articles/25692808751761 | 2023-09-08 / 2026 | low | medium |
| 22 | Moneybird API v2: OAuth2 or token, 150 req/5 min per IP (50 for reports), sandbox administrations, webhooks (`POST /webhooks`, scope `settings`), UBL 2.1 export; docs last modified 2 Sep 2026 | https://developer.moneybird.com/introduction ; https://developer.moneybird.com/api/sales-invoices/ ; https://developer.moneybird.com/api/webhooks/ | 2026-09-02 | high | high |
| 23 | Exact Online SalesInvoices GET/POST/PUT/DELETE, POST requires InvoiceTo/OrderedBy/Journal/SalesInvoiceLines; webhooks topic SalesInvoices | https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=SalesInvoiceSalesInvoices | fetched 2026-09-02 | high | medium |
| 24 | Exact Online limits 60/min and 5,000/day per app-company; no `$expand`; app-review gate before external tenants | https://www.apideck.com/blog/guide-to-exact-online-api-integration | 2026-01-27 (upd. 2026-05-13) | medium | medium |
| 25 | No Dutch B2B e-invoicing mandate yet; ViDA cross-border B2B from 1 Jul 2030; NL heading to domestic Peppol mandate 2030–2032, draft law expected Q4 2026 | https://www.peppol.nu/news-items/e-facturatie-b2b-verplichting-nederland-peppol-2030/ ; https://www.computable.nl/2026/03/17/ey-pleit-voor-verplichte-e%E2%80%91facturatie-nederlandse-ondernemers-vanaf-2030/ | 2026-03 | medium | low |
| 26 | Digital Omnibus on AI = Regulation (EU) 2026/1744; EP vote 16 Jun 2026, Council 29 Jun 2026, OJ 24 Jul 2026, in force 27 Jul 2026 | https://fpf.org/blog/the-ai-act-implementation-timeline-what-changes-under-the-ai-omnibus/ ; https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/ | 2026-07-28 / 2026-05-27 | high | high |
| 27 | High-risk deferred: Annex III → 2 Dec 2027, Annex I → 2 Aug 2028 | same as #26 | 2026-07-28 | high | high |
| 28 | Article 50 transparency applies from 2 Aug 2026, not deferred; only Art. 50(2) marking for pre-existing generative systems until 2 Dec 2026; fines €15M/3% | https://www.cooley.com/news/insight/2026/2026-08-03-eu-ai-act-transparency-obligations-take-effect-2-august-2026 ; https://artificialintelligenceact.eu/transparency-rules-article-50/ | 2026-08-03 / 2026-05-14 | high | high |
| 29 | Art. 50(4) text-disclosure duty only for text meant to inform the public on matters of public interest, and not where human review/editorial responsibility exists; marketing copy normally outside | https://artificialintelligenceact.eu/transparency-rules-article-50/ | 2026-05-14 | high | high |
| 30 | Commission Art. 50 guidelines final (updated 6 Aug 2026); Code of Practice on transparency of AI-generated content final 10 Jun 2026, ~190 signatories late Jul 2026, deployers may sign | https://digital-strategy.ec.europa.eu/en/policies/guidelines-ai-transparency-obligations ; https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content | 2026-08-06 / 2026-06-10 | high | medium |
| 31 | Art. 4 AI literacy rewritten to "take measures to support the development of AI literacy", no guaranteed level; still in force since 2 Feb 2025 | https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/ ; https://lawandtechnology.eu/en/ai-literacy-digital-omnibus-article-4-ai-act/ | 2026-05-27 / 2026 | high | medium |
| 32 | GPAI obligations since 2 Aug 2025; Anthropic, OpenAI, Google, Microsoft full signatories of the GPAI Code (10 Jul 2025); xAI signed only the Safety & Security chapter | https://digital-strategy.ec.europa.eu/en/policies/gpai-code-practice | fetched 2026-09-02 | high | medium |
| 33 | Art. 5 prohibited practices apply since 2 Feb 2025; Art. 99: €35M/7% (Art. 5), €15M/3% (Art. 50 etc.), €7.5M/1% (wrong info); SMEs pay the lower | https://artificialintelligenceact.eu/article/5/ ; https://artificialintelligenceact.eu/article/99/ | fetched 2026-09-02 | high | medium |
| 34 | Dutch Uitvoeringswet AI-verordening: consultation 20 Apr–1 Jun 2026; AP = market surveillance for prohibited practices, transparency and most high-risk; RDI central contact; fines up to Art. 99 maxima; full force anticipated 2 Aug 2027 | https://www.loyensloeff.com/insights/news--events/news/dutch-implementation-of-the-ai-act-decentralised-ai-supervision/ ; https://regulations.ai/regulations/RAI-NL-NA-IMPLEME-2026 | 2026-04-20 / 2026 | medium | high |
| 35 | Purely AI-generated output lacks copyright under Dutch/EU originality test; Düsseldorf court 2 Apr 2026 applied Cofemel/Mio-Konektra to AI output; no EU case yet confirms protection | https://www.wisemen.nl/en/news/can-ai-generated-output-be-protected-by-copyright-/ | 2026 (undated; cites 2026-04-02 ruling) | medium | high |
| 36 | CJEU C-250/25 Like Company v Google: first GenAI copyright reference; hearing 10 Mar 2026; AG opinion scheduled 3 Sep 2026 | https://www.twobirds.com/en/insights/2026/like-company-v-google-cjeu-holds-first-ever-hearing-on-generative-ai-and-copyright-on-10-march-2026 | 2026-03 | medium | medium |
| 37 | AI Liability Directive withdrawn: Commission decision 16 Jul 2025, OJ notice 6 Oct 2025; national tort/contract law governs | https://eapil.org/2025/10/09/european-commission-withdraws-two-proposals-assignments-of-claims-regulation-and-ai-liability-directive/ | 2025-10-09 | high | high |
| 38 | Dutch liability for AI content errors runs via 6:74 BW / 6:162 BW / product liability; human oversight and documented verification reduce exposure; disclaimers alone insufficient | https://lawandmore.eu/blog/ai-generated-content-who-is-liable-for-errors-under-dutch-and-eu-rules/ | 2026-01-13 | medium | high |
| 39 | New PLD 2024/2853 applies to products placed on market after 9 Dec 2026; stand-alone software/AI are products; protects natural persons (professional-use property excluded); NL bill amending Books 6/7 BW pending | https://www.gibsondunn.com/eu-product-liability-directive-responding-to-software-ai-and-complex-supply-chains/ ; https://business.gov.nl/amendments/more-parties-liable-for-defective-products/ ; https://www.insideprivacy.com/european-union-2/eu-member-states-begin-rolling-out-new-product-liability-rules/ | 2026-03-23 / 2026 / 2026 | high | high |
| 40 | NLdigital Voorwaarden 2025 (Jan 2026) add AI provisions: client responsible for AI literacy and human oversight; no training/TDM/scraping on supplied software/data without permission | https://bg.legal/nl/updates/waarom-je-als-afnemer-de-nldigital-voorwaarden-2025-niet-zou-moeten-accepteren ; https://www.nldigital.nl/nldigital-voorwaarden/ | 2026-01-19 / 2026-04-02 | medium | medium |
| 41 | Anthropic/OpenAI IP indemnities for paid customers exist historically but 2026 terms were not verified in this session | (not fetched) | n/a | low | medium |

---

## 10. Gaps and things that could not be verified

- Teamleader Orbit API scope (endpoints for tickets/time/invoices) — developer.orbit.teamleader.eu returned no content; only a 2023 third-party driver listing (8 tables) and marketing "open API" claims. Use the existing Fightclub Orbit MCP as ground truth.
- Bird & Bird's Dutch implementing-law analysis (paywalled, HTTP 402) and the AP's own AI Act page (HTTP 403) could not be read; Loyens & Loeff and regulations.ai were used instead.
- EUR-Lex pages render via JavaScript and returned empty; the Omnibus regulation number 2026/1744 is taken from FPF (which links the EUR-Lex OJ entry) and a secondary blog.
- Whether GitHub Copilot code review or Grok-based reviewers (Cursor "Grok 4.6" in the models pool) add anything beyond the four reviewers above was not researched.
- Vendor IP indemnity terms (Anthropic Commercial Terms, OpenAI enterprise terms) as of 2026 were not fetched.
