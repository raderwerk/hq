# Gap 03: vendor data handling for client code and ticket text

Research note for the AI-agency demo (Fightclub, Linear as operating system). Question: which vendor may see TowMotive's repo and Orbit ticket threads in spoor A, under which DPA / retention / training / EU / IP-indemnity terms, and is the brief's claim "Fable 5.1 requires 30-day retention, no ZDR" still true.

Method: 10 web searches were attempted but the session's WebSearch budget was exhausted, so all evidence comes from direct fetches of official pages (WebFetch, plus curl for pages that block WebFetch) on 2026-09-02. Pages that block both (openai.com, help.openai.com, x.ai) are listed as unverified; web.archive.org is blocked from this tool. Browser automation was not usable from a subagent. Local sources: the `claude-api` skill cache (`~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/claude-api/`, files dated 2026-09-02 09:43) and lanes 01, 02, 04, 08, 10.

## 1. Verdict on the brief's Fable 5.1 retention claim

**True, and verified against live Anthropic pages on 2026-09-02, one day after launch.** The brief's provenance is wrong, not the claim:

- The skill's SKILL.md still carries the header "Current Models (cached: 2026-06-24)", but the skill files on disk were rewritten on 2026-09-02 09:43 and already describe Fable 5.1 (they even note that a draft line about a time-bound enterprise exemption "through 2026-12-31" was removed from the launch docs on Aug 28 and must not be cited). The older cache generation (`cache/anthropic-agent-skills/claude-api/3b3fad96af16/`) applied the identical rule to Fable 5, so the rule predates Fable 5.1 by one generation.
- Live wording, "What's new in Claude Fable 5.1" (platform.claude.com, model released 2026-09-01): "Claude Fable 5.1 and Claude Mythos 5.1 carry 30-day data retention and aren't available under zero data retention unless expressly authorized by Anthropic. Both are Covered Models, like Claude Fable 5 and Claude Mythos 5."
- "API and data retention" (platform.claude.com/docs/en/manage-claude/api-and-data-retention): Fable 5.1, Mythos 5.1, Fable 5, Mythos 5 "require 30-day data retention; ZDR is therefore not available for any of them unless expressly authorized by Anthropic"; a ZDR org gets `400 invalid_request_error` "In order to access this model, your organization or workspace must have data retention enabled." The requirement "applies wherever Covered Models are offered"; on Bedrock and Google Cloud the retained data "stays within your cloud provider's environment".
- Escape hatch on the same page: an org with a ZDR arrangement can enable 30-day retention for one workspace only (Console > Settings > Workspaces > Privacy controls); other workspaces keep ZDR.
- Covered Models support article (support.claude.com/en/articles/15425695, shown as updated 2026-09-02): prompts and completions "are retained for at least 30 days and then automatically deleted, unless they are subject to a safety investigation or we are legally required to maintain them"; "Retained data is assessed by automated safety systems"; standard ZDR unavailable; "Enterprise Frontier Safeguards (EFS)" rolling out from fall 2026 with "the option to keep retained monitoring data in cloud infrastructure the customer controls".
- Claude Code ZDR page (code.claude.com/docs/en/zero-data-retention): under ZDR the Fable models are absent or disabled in `/model`; the `best` alias resolves to Opus. Opus 5 and Sonnet 5 remain available under ZDR.

Consequence for the design: "model choice per client" in the brief is correct in principle, but for the Claude Code cloud paths it is moot, because cloud sessions, routines, Claude Tag and Remote Control are themselves disabled under ZDR (section 2.3). ZDR only buys anything for API-key / local Claude Code use with Opus 5 or Sonnet 5.

## 2. Anthropic (API, Claude Code cloud sessions, routines, Code Review)

### 2.1 Contract layer

| Item | Finding | Source (date) | Confidence |
|---|---|---|---|
| Which terms apply | Commercial Terms cover API keys, Console, Team and Enterprise. Consumer Terms (effective 2025-10-08) cover claude.ai Free/Pro/Max, explicitly including Claude Code used from those accounts. | anthropic.com/legal/commercial-terms; anthropic.com/legal/consumer-terms; code.claude.com/docs/en/data-usage (fetched 2026-09-02) | high |
| Training | Commercial: "Anthropic may not train models on Customer Content from Services." Consumer: "including training our models, unless you opt out of training through your account settings"; retention 5 years with training on, 30 days with it off. | same | high |
| IP indemnity | Commercial Terms section K: Anthropic defends the customer against claims that paid use "in accordance with these Terms or Outputs generated through such authorized use violates any third-party intellectual property right"; excluded: customer modifications, combination with non-Anthropic technology, customer inputs, known infringement, patented inventions in outputs, trademark use. Consumer Terms contain no indemnity from Anthropic. | commercial-terms ("Effective June 17, 2025"); consumer-terms | high |
| DPA | Effective 2025-02-24; SCCs Module 2 and 3 incorporated; "Services in the EU are provided by Anthropic Ireland Limited"; sub-processor list at anthropic.com/subprocessors (redirects to trust.anthropic.com, a Vanta portal that renders only via JavaScript; list not retrievable in this session); 15-day objection window; return or delete Customer Data within 30 days of termination, with exceptions for law, disputes and "harmful use". | anthropic.com/legal/data-processing-addendum | high (list contents: low) |
| Default retention (commercial) | "We automatically delete inputs and outputs on our backend within 30 days"; flagged content up to 2 years, classifier scores up to 7 years; feedback submissions 5 years. | privacy.claude.com article 7996866 (updated 2026-07-01) | high |

### 2.2 EU processing

Anthropic's first-party API has **no EU option**: `inference_geo` accepts only `"global"` (default) and `"us"` (1.1x price, Claude 4.6+); workspace geo (storage and endpoint processing) is "us" only and immutable after creation. EU-region inference exists only on partner platforms (Bedrock regional endpoints, Google Cloud regional/multi-region, +10 %), where the cloud provider is the data processor and Covered-Model retention "stays within your cloud provider's environment". Source: platform.claude.com/docs/en/manage-claude/data-residency and /about-claude/pricing (fetched 2026-09-02). Confidence high. So for EU-only processing of TowMotive data on Claude, the route would be Bedrock eu-* or Vertex europe-west with Claude Code configured for that provider, which in turn disables `--cloud`, routines and teleport (cloud sessions "require an Anthropic account" and are "not available when Claude Code is configured for Amazon Bedrock, Google Cloud's Agent Platform, or another third-party provider").

### 2.3 Claude Code cloud sessions and routines

- Sessions "run in Anthropic-managed virtual machines by default"; "Your repository is cloned to an isolated VM. Code and session data are subject to the retention and usage policies for your account type"; GitHub credentials never enter the sandbox (proxy); all egress through a security proxy; region not stated. Source: code.claude.com/docs/en/data-usage, /claude-code-on-the-web (fetched 2026-09-02). High.
- Retention: commercial 30 days standard; ZDR "available to qualified accounts for Claude Code on Claude for Enterprise", not in the standard Enterprise plan, enabled per organization by the account team. Sessions can be deleted individually ("permanently removes the session's event data").
- Under ZDR these are disabled at the backend: Claude Code on the Web, Desktop cloud sessions, Claude Tag, Artifacts, feedback commands, Remote Control. Routines run as cloud sessions (lane 01), so they fall under the same block. Code Review is "not available with Zero Data Retention" (lane 08). `/web-setup` and "other cloud session features" are unavailable to ZDR orgs.
- A cloud session "can access any repository the connecting GitHub account can see"; App installation is not an access control. Restrict on GitHub itself (a dedicated GitHub account or org membership for the demo).
- Local sessions store plaintext transcripts under `~/.claude/projects/` for 30 days (`cleanupPeriodDays`).

## 3. OpenAI (API, Codex CLI, Codex cloud)

| Item | Finding | Source (date) | Confidence |
|---|---|---|---|
| Training (API) | "As of March 1, 2023, data sent to the OpenAI API is not used to train or improve OpenAI models (unless you explicitly opt in)." | developers.openai.com/api/docs/guides/your-data (fetched 2026-09-02) | high |
| Default retention (API) | "abuse monitoring logs are generated for all API feature usage and retained for up to 30 days, unless longer retention is required by law". | same | high |
| ZDR / MAM | Via sales, eligibility-checked. ZDR-eligible: `/v1/responses`, `/v1/chat/completions`, images, embeddings, audio, realtime, moderations; `store` forced to false. Not eligible: conversations, chatkit threads, assistants/threads, vector stores, files, fine-tuning, evals, batches, videos. "Modified Abuse Monitoring" excludes customer content from logs. | same | high |
| EU processing | Project-level data residency: `eu.api.openai.com` gives regional storage **and** regional processing (EEA + Switzerland); table marks the EU row as requiring MAM/ZDR; "Data residency does not apply to system data". Lane 02 adds per-request regional prefixes since 2026-08-21. | same | high |
| Codex cloud sandbox | Container state "cached for up to 12 hours"; repo checked out per task; secrets encrypted and "removed before the agent phase starts"; agent-phase internet "off by default"; all traffic via HTTP(S) proxy. Region of the sandbox not stated. | learn.chatgpt.com/docs/environments/cloud-environment (fetched 2026-09-02) | high |
| Codex on ChatGPT plans | Codex included in "ChatGPT Free, Go, Plus, Pro, Business, Edu, or Enterprise"; Business: "No training on your business data by default"; Enterprise: "Data retention and data residency controls"; API-key use "pay only for the tokens Codex uses, based on API pricing". Whether Codex cloud tasks fall under ZDR / data residency is not stated on reachable pages. | learn.chatgpt.com/docs/pricing (fetched 2026-09-02) | medium |
| Business Terms IP indemnity ("Copyright Shield"), OpenAI DPA, sub-processor list, Codex-per-plan help article | Not verifiable: openai.com and help.openai.com return 403 to WebFetch and curl; archive blocked. Historically OpenAI's Business Terms include an IP indemnity for API/Enterprise customers; treat as unconfirmed for 2026. | (not fetched) | low |

Decision-relevant nuance: Codex CLI signed in with a personal ChatGPT Plus/Pro account is a consumer relationship (no Business Terms, no DPA); use an API key from an org project (ZDR/EU-eligible) or a ChatGPT Business/Enterprise workspace when client code is involved.

## 4. Linear (coding sessions, Loops sandboxes, MCP)

| Item | Finding | Source (date) | Confidence |
|---|---|---|---|
| Hosting region | "Choose to store your data in the European Union or the United States when creating a Linear workspace." Region is chosen at workspace creation. | linear.app/security (fetched 2026-09-02) | high |
| DPA | Signed 2025-05-31; "Linear's primary processing operations take place in the United States"; EU SCCs + UK Addendum; 30-day notice before new sub-processors; return or delete on termination. | linear.app/dpa | high |
| Sub-processors (from DPA table) | AI: Anthropic (US, EU), OpenAI (US, EU), Google (US, EU), AWS (US, EU), Cohere (US, EU), Fireworks AI (US), Braintrust (US). Compute/code: Modal Labs (cloud provider, US, EU), The Pierre Computer Company (code storage/processing, US, EU), Cloudflare, PlanetScale, turbopuffer. The public linear.app/subprocessors page is JS-only ("Loading…"). | linear.app/dpa | high |
| AI Addendum | Effective 2026-06-09, controls over the Terms for AI Services. "Linear will not use Customer Data, including Prompts or Outputs, to train"; provider agreements "require that Customer Data not be used by such providers to train"; providers must "process Customer Data in a zero-data-retention manner, where such processing is commercially available"; customer owns outputs; outputs "AS IS", no non-infringement warranty. | linear.app/legal/ai-addendum | high |
| Implication for Fable in coding sessions | Because ZDR is "not commercially available" for Covered Models, a coding session on Claude Fable 5 (in the model list; Fable 5.1 not yet listed) runs under Anthropic's 30-day retention. Opus 4.8 (default), Opus 5, Sonnet 5 and GPT-5.6 Sol can be ZDR at the provider. | inference from AI Addendum + Anthropic policy | medium |
| Sandbox disclosure | Coding-sessions docs and the 2026-06-11 / 2026-08-20 changelogs do not name the sandbox provider or region; pricing is $0.25 per 20-minute block plus provider token rates. Modal Labs / Pierre in the DPA are the likely hosts but this is not stated. | linear.app/docs/coding-sessions; changelogs | high (that it is undisclosed) |
| Terms / indemnity | Terms effective 2026-06-09: Linear defends the customer against claims that the Service infringes third-party IP (standard exclusions); this does not extend to AI outputs, which the AI Addendum disclaims. DPA at linear.app/dpa. Delaware law. | linear.app/terms | medium |
| Linear's own statement | "Linear does not train on customer's data. We use models from common model providers, a complete list is available in our DPA." Third-party agents are "3rd party integrations approved by your workspace". | linear.app/docs/agents-in-linear | high |

## 5. Cursor (cloud agents, Bugbot) and xAI via Cursor

| Item | Finding | Source (date) | Confidence |
|---|---|---|---|
| Privacy Mode | "When enabled, we will not train on your data. We also implement technical controls and contractual requirements with our model providers"; available to all, inheritable org-wide. The security page (updated 2026-08-25) no longer names providers or the phrase "zero data retention"; the enterprise page does: "Cursor also maintains zero data retention agreements with all our model providers." Providers named there: "OpenAI, Anthropic, Gemini, and SpaceXAI". | cursor.com/security; cursor.com/enterprise (fetched 2026-09-02) | high |
| Fable in Cursor | Models page: Claude Fable 5 / 5.1 "Requires data retention approval for Enterprise customers, Teams and individual customers with Privacy Mode enabled"; "Anthropic stores agent input and output data for harm-prevention processes; this data is not used to train". Consistent with the Covered-Model policy. | cursor.com/docs/models | high |
| Grok 4.6 | Listed as provided by Cursor, "Jointly trained by Cursor and SpaceXAI"; "Models are hosted by the model provider, a trusted partner, or Cursor". So the counterparty for Grok data is Cursor, and whether xAI infrastructure sees the data is not disclosed on the page. | cursor.com/docs/models | medium |
| Cloud agents | "isolated VMs in the cloud"; repo cloned via GitHub/GitLab/Bitbucket/Azure DevOps with read-write access; secrets via Settings; outbound domains restrictable; billed at API pricing. Cloud provider, region and repo-retention period not stated. | cursor.com/docs/cloud-agent | high (that it is undisclosed) |
| Terms | Updated 2026-08-13: no IP indemnity from Cursor for outputs; the user indemnifies Anysphere; outputs assigned to user; "ANYSPHERE WILL NOT USE CONTENT TO TRAIN ... UNLESS YOU'VE EXPLICITLY AGREED"; Texas law. | cursor.com/terms-of-service | high |
| Privacy policy | Updated 2025-10-06: EEA data "may be transferred to our United States servers"; no fixed retention periods; sub-processors at trust.cursor.com/subprocessors (Vanta, JS-only, not retrievable here). DPA not found at cursor.com/dpa; presumably on the trust portal. | cursor.com/privacy | high (DPA: low) |
| Certifications | SOC 2 Type II, ISO/IEC 27001:2022, ISO/IEC 42001:2023, AIUC-1; no China infrastructure. | cursor.com/security | high |

xAI direct (relevant only if Grok is called outside Cursor):
- docs.x.ai security FAQ: "xAI never trains on your API inputs or outputs without your explicit permission"; "all API requests and responses are stored on our servers (encrypted at rest) for 30 days for auditing purposes"; ZDR is self-serve per team (Team Settings > Zero Data Retention), confirmed by an `x-zero-data-retention` response header; Grok Build CLI under ZDR retains "no trace or code data"; SOC 2 Type 2. No EU processing or data-residency option is mentioned; the GDPR question is answered only with the SOC 2 statement. Source: docs.x.ai/developers/faq/security (curl, 2026-09-02). Confidence medium-high.
- x.ai/legal/enterprise-terms and the xAI DPA return 403; IP indemnity and DPA terms remain unverified (low), which confirms lane 10's gap.

## 6. Cross-vendor comparison for spoor A

| Vendor path | No training (commercial) | Default retention | ZDR possible | EU processing | IP indemnity | DPA + sub-processor list |
|---|---|---|---|---|---|---|
| Anthropic API / Claude Code, commercial org | yes | 30 days; Fable 5/5.1 always 30 days | yes for Opus 5 / Sonnet 5 (Enterprise or API); disables all cloud features | no (US/global only); EU only via Bedrock/Vertex | yes (Commercial Terms K) | DPA yes; list on JS trust portal |
| Anthropic via Pro/Max seat | only if the training toggle is off | 30 days (off) / 5 years (on) | no | no | no | no (consumer terms) |
| OpenAI API / Codex with API key or Business/Enterprise | yes | 30-day abuse logs | yes (sales), Responses/Chat only | yes, eu.api.openai.com (needs MAM/ZDR) | historically yes; 2026 text unverified | DPA exists; list unverified (403) |
| Codex with personal Plus/Pro sign-in | consumer controls; unverified | unverified | no | no | no | no |
| Linear coding sessions / Loops | yes (AI Addendum) | provider-dependent; Fable = 30 days | "where commercially available" | storage EU-selectable; AI processing by US providers under SCCs | Service only, not AI outputs | DPA yes, table published |
| Cursor cloud agents (Privacy Mode) | yes | undisclosed; Fable = 30 days at Anthropic | claimed for all providers, except Fable | no (US transfer) | none from Cursor | DPA/list on JS trust portal, unverified |
| xAI direct | yes | 30 days | yes, self-serve | not offered | unverified | unverified |

## 7. Requester decision: what may flow where, and is client sign-off needed

1. **Run the demo under commercial accounts only.** A Pro/Max Claude seat or a personal ChatGPT Plus/Pro login puts TowMotive code under consumer terms (training toggle, no DPA, no indemnity). Use a Team/Enterprise org or API keys for Anthropic, an org project or Business workspace for OpenAI. Verify which seat the current Claude Code session uses before spoor A.
2. **Orbit ticket text is the sensitive part, not the repo.** Orbit threads carry customer names, e-mail addresses, licence plates and order data, so they are personal data for which Fightclub acts as processor for TowMotive. Under GDPR Art. 28(2) every vendor that receives that text is a sub-processor needing the client's prior written authorisation (specific or general, per the Fightclub-TowMotive DPA). The repo alone is confidential information governed by the services contract/NDA, not by Art. 28, but most agency contracts still forbid disclosure to third parties without consent.
3. **Recommended split for spoor A on a real repo:** (a) redact the Orbit thread to a spec written by a human (or by a local, API-key Claude call) before it enters any sandbox, so no personal data leaves Fightclub; (b) let the code flow through Anthropic (commercial org, Opus 5 or Sonnet 5 if ZDR matters; Fable 5.1 accepted with 30-day retention) and OpenAI API/Codex Business with ZDR requested; (c) keep Linear coding sessions and Cursor/Grok on the fictional demo repo until TowMotive has accepted the sub-processor list, because Linear adds eight AI/compute sub-processors and Cursor's list and DPA could not be retrieved.
4. **Sub-processor sign-off before spoor A: yes if the ticket text goes in unredacted, advisable in any case.** Send TowMotive a one-page notice naming Anthropic (Anthropic Ireland Limited as EU entity; US processing under SCCs; 30-day safety retention for Fable models), OpenAI (EU region available), Linear (EU workspace region; AI processing by Anthropic/OpenAI/Google/AWS/Cohere/Fireworks; sandboxes via Modal/Pierre) and, only if used, Cursor (US, no indemnity) and SpaceXAI/xAI. Ask for written acknowledgement; a general authorisation with a 30-day objection window mirrors what the vendors themselves offer.
5. **EU-only is not achievable for this stack.** The only true EU inference path is OpenAI's `eu.api.openai.com`; Anthropic first-party is US/global; Linear, Cursor and xAI are US-processing under SCCs. State this plainly on the honesty slide and in the compliance annex, and do not promise EU processing to clients.
6. **Fix the brief's citation.** Replace "cache 2026-06-24" with the live sources above (whats-new-fable-5-1, api-and-data-retention, Covered Models article, Claude Code ZDR page), and add the per-workspace 30-day override plus the fall-2026 Enterprise Frontier Safeguards as the mitigation path.

## 8. Open items that need a human or an authenticated browser

- OpenAI Business Terms (IP indemnity wording and exclusions, 2026 version), OpenAI DPA and sub-processor list, and the Codex-in-ChatGPT help article (per-plan data use). All 403 from this tool.
- xAI Enterprise Terms and DPA (403).
- Anthropic and Cursor sub-processor lists (Vanta trust portals, JavaScript only).
- Cursor DPA location and whether cloud agents are covered by Privacy Mode contractual terms (docs silent).
- Linear: which sub-processor hosts coding-session sandboxes and in which region for an EU workspace (docs silent; Modal Labs and Pierre are the candidates in the DPA table).
- Whether Fightclub's contract/DPA with TowMotive already contains a general sub-processor authorisation.

## 9. Source list

| # | URL | Date of source | Used for |
|---|---|---|---|
| 1 | https://platform.claude.com/docs/en/models/fable-5-1/whats-new-fable-5-1 | model released 2026-09-01; fetched 2026-09-02 | Covered Model / 30-day / no ZDR |
| 2 | https://platform.claude.com/docs/en/manage-claude/api-and-data-retention | fetched 2026-09-02 | model-specific retention, per-workspace override, ZDR scope |
| 3 | https://support.claude.com/en/articles/15425695-covered-models | updated 2026-09-02 | retention rationale, EFS fall 2026 |
| 4 | https://code.claude.com/docs/en/zero-data-retention | fetched 2026-09-02 | features disabled under ZDR, model availability |
| 5 | https://code.claude.com/docs/en/data-usage | fetched 2026-09-02 | training policy by plan, retention, cloud VM data flow |
| 6 | https://code.claude.com/docs/en/claude-code-on-the-web | fetched 2026-09-02 | cloud sessions, GitHub access scope, ZDR block |
| 7 | https://platform.claude.com/docs/en/manage-claude/data-residency | fetched 2026-09-02 | inference_geo us/global only, workspace geo us only |
| 8 | https://platform.claude.com/docs/en/about-claude/pricing | fetched 2026-09-02 | 1.1x US-only, Bedrock/Vertex regional +10 % |
| 9 | https://www.anthropic.com/legal/commercial-terms | effective 2025-06-17 | no training, indemnity section K |
| 10 | https://www.anthropic.com/legal/consumer-terms | effective 2025-10-08 | consumer training/opt-out, no indemnity |
| 11 | https://www.anthropic.com/legal/data-processing-addendum | effective 2025-02-24 | SCCs, Anthropic Ireland, sub-processor notice, deletion |
| 12 | https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-personal-data | updated 2026-07-01 | 30-day deletion, flagged-content retention |
| 13 | https://developers.openai.com/api/docs/guides/your-data | fetched 2026-09-02 | training, 30-day logs, ZDR endpoints, EU residency table |
| 14 | https://learn.chatgpt.com/docs/environments/cloud-environment | fetched 2026-09-02 | Codex cloud container cache 12 h, secrets, internet |
| 15 | https://learn.chatgpt.com/docs/pricing | fetched 2026-09-02 | Codex plans, Business no-training, Enterprise residency |
| 16 | https://linear.app/security | fetched 2026-09-02 | EU/US workspace region, certifications |
| 17 | https://linear.app/dpa | signed 2025-05-31 | US processing, SCCs, sub-processor table |
| 18 | https://linear.app/legal/ai-addendum | effective 2026-06-09 | no training, provider ZDR where available, output ownership |
| 19 | https://linear.app/terms | effective 2026-06-09 | indemnity scope, DPA reference |
| 20 | https://linear.app/docs/agents-in-linear | fetched 2026-09-02 | "Linear does not train on customer's data" |
| 21 | https://linear.app/docs/coding-sessions, https://linear.app/changelog/2026-06-11-coding-sessions, https://linear.app/changelog/2026-08-20-coding-environments | 2026-06-11 / 2026-08-20 | models, pricing, absence of sandbox disclosure |
| 22 | https://cursor.com/security | updated 2026-08-25 | Privacy Mode, sub-processors on trust portal, certifications |
| 23 | https://cursor.com/enterprise | fetched 2026-09-02 | ZDR agreements claim, provider names |
| 24 | https://cursor.com/docs/models | fetched 2026-09-02 | Fable retention approval, Grok 4.6 provenance/hosting |
| 25 | https://cursor.com/docs/cloud-agent | fetched 2026-09-02 | VM, repo access, secrets, pricing |
| 26 | https://cursor.com/terms-of-service | updated 2026-08-13 | no indemnity, output assignment, no training |
| 27 | https://cursor.com/privacy | updated 2025-10-06 | US transfer, retention, sub-processor link |
| 28 | https://docs.x.ai/developers/faq/security | fetched 2026-09-02 (curl) | no training, 30-day retention, self-serve ZDR |
| 29 | ~/.claude/plugins/marketplaces/anthropic-agent-skills/skills/claude-api/SKILL.md and shared/model-migration.md | files dated 2026-09-02 09:43; header says cached 2026-06-24 | provenance of the brief's claim |
