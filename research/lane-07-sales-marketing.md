# Lane 07 — Sales & Marketing Agents (state of the market, 2026-09-02)

Scope: AI SDR / outbound tools (Clay, 11x, Artisan, Apollo, Instantly), proposal/quote generation, CRM automation (HubSpot Breeze, Salesforce Agentforce), content/SEO agents (Semrush, Jasper, Surfer), ad management agents (Google, Meta, Adspirer), inbound intake bots (Fin, HubSpot Customer Agent), and the legal frame for a Dutch agency (GDPR/AVG, Telecommunicatiewet, EU AI Act Art. 50).

Method: 20+ web searches, 25+ primary-source fetches (vendor changelogs, pricing pages, press releases, regulator pages, law-firm notes). Every claim below carries a URL and source date. Confidence is stated per claim. Where I could not reach a primary source (Salesforce pricing page 403, PandaDoc changelog 429, Telecommunicatiewet article text not rendered) I say so.

---

## 1. Executive summary

1. **The autonomous "AI SDR that replaces a human" is the least mature and most reputationally risky category.** The market leader narrative (11x) was publicly discredited in March 2025 (fake customer logos, 70-80% churn per an employee, a ZoomInfo pilot that "performed significantly worse than our SDR employees"). Apollo, the largest mainstream GTM platform, shipped its "agentic" AI Assistant in March 2026 but it explicitly drafts and researches; humans still send and book. Artisan's Ava 2.0 (May 2026) sells "approval gates wherever you want them". HubSpot's Prospecting Agent ships with a "Review before sending" mode and hard caps (1,000 emails/day, 3 agent emails per contact per 90 days). The consensus pattern in 2026 is **AI drafts, human approves, human identity sends**.
2. **Inbound / CRM agents are mature and priced per outcome.** HubSpot Customer Agent $0.50 per resolved conversation, Prospecting Agent $1 per qualified lead (since 14 Apr 2026). Fin (ex-Intercom) $0.99 per resolution, $9.99 per lead qualification, 76% average end-to-end resolution, and Salesforce agreed to buy it for ~$3.6B on 15 Jun 2026. These are real, deployable, and give an AI agency hard cost benchmarks.
3. **Content/SEO agents are mature at the "research + draft + optimise" layer.** Semrush shipped an official Claude connector / MCP on 26 Aug 2026 (included in Semrush One and SEO Classic). Jasper's GEO Agent went GA 16 Jun 2026. Surfer opened a full Content Editor API (25 May 2026) with MCP "in the works". AI-visibility (GEO/AEO) is the new service line: Semrush's index covers 126M prompts; HubSpot sells AEO at $50/month.
4. **Ad management is "agentic" inside the platforms, read-mostly outside them.** Google Marketing Live (20 May 2026) introduced Ask Advisor, AI Max for Shopping/Travel and Asset Studio. Google's *official* Ads MCP server is query-only (search, metadata, list customers); write access needs the API via Google's Agent Skills for Claude Code/Codex/Cursor (updated 19 Aug 2026) or a third party such as Adspirer (400+ MCP tools, approval queue). Meta's "every ad made by AI by end of 2026" is, per agencies interviewed in April 2026, "likely much further off".
5. **Legal frame for a Dutch agency is stricter than US vendor blogs assume.** ACM: commercial e-mail needs prior consent, proof kept 5 years; the existing-customer exception is narrow; ACM's own guidance treats legal entities under the same consent rule (exception only for addresses deliberately published for that purpose). Since 1 Jul 2026 telemarketing soft opt-in is gone for consumers, zzp'ers and vof/maatschap. EU AI Act Art. 50 applies since 2 Aug 2026: any bot or agent that converses with a natural person must disclose it is AI at first contact; guidelines (20 Jul 2026) extend this to agents handling correspondence; fines up to EUR 15M / 3%.

**Bottom line for the demo:** build the sales/marketing lane as *inbound-first, consent-based, human-approved outbound*, with disclosure and editorial-review gates modelled as explicit workflow states in Linear. Do not model the demo on "autonomous cold outbound at scale"; it is both the weakest product category and the one that is illegal-by-default in NL.

---

## 2. AI SDR / outbound tools

### 2.1 Clay (data + enrichment + Claygent + native sequencer)
- Pricing page (fetched 2026-09-02): Free / Launch / Growth / Enterprise. Monthly billing shown as Launch ~$167/mo, Growth ~$446/mo; annual gets 10% off. Launch: 2,500 data credits + 15,000 actions per month; Growth: 6,000 credits + 40,000 actions per month. The annual-per-month figures on the page were parsed inconsistently by my fetch; verify before quoting numbers to a client. Source: https://www.clay.com/pricing
- Claygent ("Clay's AI agent with access to web research") is included on every tier including Free. Clay has a native email sequencer; Growth adds "buy domains and emails for the Clay Sequencer" and unlimited ad-audience pushes to LinkedIn/Meta. Enterprise adds API access.
- Third-party analyses repeatedly warn that real cost is 2-3x the headline because of credit burn (warmly.ai, marketbetter.ai, 2026). Confidence medium (vendor-adjacent blogs).
- Maturity: **mature** as an enrichment/orchestration layer; it is the de facto "data plumbing" for every AI SDR stack. It is *not* an autonomous seller.

### 2.2 11x (Alice)
- Product page (undated, fetched 2026-09-02): Alice "continuously prospects, handles replies, and schedules meetings to build you pipeline 24/7", multi-channel (email, calls), proprietary deliverability engine, "consented outbound calling". Vendor claims: +30% meetings per AE, +80% meeting-to-opportunity conversion, -50% cost per lead. No approval workflow described; no pricing on site. Source: https://www.11x.ai/worker/alice
- TechCrunch, 24 Mar 2025: 11x displayed logos of non-customers (ZoomInfo, Airtable); ZoomInfo's one-month trial "performed significantly worse than our SDR employees" and its lawyers threatened action for deceptive trade practices and trademark infringement; an employee said "we were losing 70-80% of customers that came through the door"; three-month break clauses were counted as annual ARR. 11x said retention had improved to 79%. Source: https://techcrunch.com/2025/03/24/a16z-and-benchmark-backed-11x-has-been-claiming-customers-it-doesnt-have/
- Pricing: third parties report ~$5,000/month billed annually with $50-60k first-year minimum (getbreakout.ai, 2026). Confidence low.
- Maturity: **hype / high-risk**. Useful only as a cautionary reference in the demo.

### 2.3 Artisan (Ava)
- Ava 2.0 launched 26 May 2026 as a ground-up rebuild: outbound "end to end, from lead research to booked meetings", "approval gates wherever you want them", "deployed for thousands of AEs and BDRs at large enterprises". No pricing, no metrics in the launch post. Source: https://www.artisan.co/blog/artisan-launches-ava-2-0-first-autonomous-ai-bdr
- Funding: ~$35-48M total, $25M Series A (Apr 2025), reported ~$6M ARR with 37 staff (third-party, medium confidence).
- Maturity: **emerging**. Notable that even the most "autonomous" positioned vendor now leads with approval gates.

### 2.4 Apollo.io (AI Assistant)
- Press release 4 Mar 2026: AI Assistant GA after beta since Oct 2025; ~20,000 weekly active users; automates prospect discovery, research, enrichment, sequence creation, list building, reporting via natural language; "beta users booking 2.3x more meetings" (vendor). Free introductory offer on Basic/Pro/Org; free plans get 5 chats. It does **not** autonomously send emails or book meetings. Source: https://www.prnewswire.com/news-releases/apolloio-launches-ai-assistant-powering-end-to-end-agentic-workflows-in-the-first-ai-native-all-in-one-gtm-platform-302703896.html
- Maturity: **mature as copilot**, not as autonomous agent. Best "boring" choice for a demo that needs a real contact database + sequencer.

### 2.5 Instantly.ai
- Pricing page (fetched 2026-09-02): Outreach Growth $47/mo with unlimited email accounts and unlimited warmup; Hypergrowth $358/mo; bundles Starter $94, Scale $194, Agency $555/mo; AI Sales Agent and AI Reply Agent on Starter/Scale bundles. Source: https://instantly.ai/pricing
- Instantly's own content markets "unlimited accounts + 4.2M-account warmup network + human-in-the-loop reply handling" and a Deliverability AI Agent on Hypergrowth+. Their 2026 benchmark puts B2B average cold reply rate at 3.43% (vendor data, medium confidence).
- Maturity: **mature sending infrastructure**; it is also the archetype of the "many domains, many mailboxes" pattern that regulators and mailbox providers are targeting (see section 8).

### 2.6 HubSpot Prospecting Agent (see also section 4)
- Knowledge base, updated 14 Aug 2026: researches contacts/companies, composes and sends personalised emails, monitors replies, tracks meetings. Two modes: **"Review before sending"** and **"Send automatically"**. Limits: 1,000 emails/day/account; 10 contacts/minute research; cold outreach capped at **three agent-sent emails per contact per 90 days** without engagement; adaptive enrollments 30 days. Available on all Hubs, all tiers; needs HubSpot Credits. Source: https://knowledge.hubspot.com/prospecting/use-the-prospecting-agent
- Maturity: **mature, opinionated, guard-railed**. The 3-per-90-days cap is a good default policy to copy into the demo.

### 2.7 Salesforce Agentforce SDR
- Help article (published 19 May 2025, still current): Flex Credits $500 per 100,000; one action = 20 credits = $0.10; alternative $2 per conversation; Enterprise Edition gets 100,000 Flex Credits free with Foundations. Source: https://help.salesforce.com/s/articleView?id=004811240&language=en_US&type=1
- Per-user "unlimited" add-on at ~$125/user/month is reported by multiple third parties (coworker.ai, aquiva.com, 2026); the public pricing page returned 403 to my fetch. Confidence medium.
- Third parties estimate realistic first-year cost with Data Cloud at $150k-600k for mid-market. Not a fit for a small-agency demo; relevant as a benchmark only.

---

## 3. Proposal / quote generation
- Landscape (listicles 2026): PandaDoc, Proposify (~$49/user/mo), Qwilr, Responsive, Conga; "AI-assisted content generation has become a standard feature across most platforms in 2026". Confidence medium (secondary).
- PandaDoc: search results describe an MCP server letting Claude Desktop/Cursor create documents and send for signature, CRM-driven proposal assembly (Salesforce, HubSpot, Pipedrive, Dynamics two-way sync). I could not load the June 2026 changelog or the AI-information page (HTTP 429 twice). Confidence **low** until verified. URL to verify: https://www.pandadoc.com/blog/whats-new-on-pandadoc-june-2026/
- Practical read: for an agency demo, proposal generation is best done in-house (Claude + a template + a pricing model in Linear/Notion) and pushed to PandaDoc/Qwilr only for e-signature. No vendor offers a differentiated "agentic" quote engine that would justify a licence in a demo.

---

## 4. CRM automation
### 4.1 HubSpot Breeze
- Company news, 13 Apr 2026 (effective 14 Apr 2026): outcome-based pricing. Customer Agent **$0.50 per resolved conversation** (was $1.00/conversation); Prospecting Agent **$1 per lead recommended for outreach** (was recurring per enrolled contact). Customer Agent "already resolves 65% of conversations and cuts resolution time by 39%"; Prospecting Agent activations +57% QoQ. Source: https://www.hubspot.com/company-news/hubspots-customer-agent-and-prospecting-agent-now-you-pay-when-the-task-is-complete
- Spring 2026 Spotlight (14 Apr 2026): Prospecting Agent "handles the full prospecting lifecycle" (buying signals from job postings/funding/tech adoption, buying-committee discovery, agent-drafted emails reviewed by reps), early users "2x the industry benchmark" response rate (vendor); Customer Agent resolves ~70% average, top teams 90%, now on email; **HubSpot AEO** at $50/month standalone. Source: https://www.hubspot.com/company-news/spring-2026-spotlight
- Maturity: **mature**. Clear cost model, clear human-review mode, native to the CRM most Dutch SMB agencies already use.

### 4.2 Salesforce Agentforce + Fin
- Investor release 15 Jun 2026: definitive agreement to acquire Fin (formerly Intercom) for ~$3.6B; Fin "resolving on average 76% of support volume end-to-end"; 30,000+ customers; close expected Q4 FY2027; positioned as packaged SMB path alongside customisable Agentforce. Source: https://investor.salesforce.com/news/news-details/2026/Salesforce-Signs-Definitive-Agreement-to-Acquire-Fin/default.aspx
- Signal: the two largest CRM vendors have converged on **per-outcome pricing for inbound agents** ($0.50-$0.99 per resolution). An AI agency can price its own inbound service against these numbers.

---

## 5. Content / SEO agents
### 5.1 Semrush
- News, 26 Aug 2026: official Semrush connector for Claude (Semrush's third MCP integration with a major LLM); keyword strategy, backlink audit with toxic-link classification, competitor gap analysis with content briefs, market research; included for all **Semrush One and SEO Classic** subscribers; 28.8B keywords, 43T backlinks, 317M LLM prompts. Source: https://www.semrush.com/news/469301-semrush-launches-official-connector-for-claude-bringing-marketing-intelligence-into-ai-conversations/
- MCP endpoint for Claude Code: `claude mcp add semrush https://mcp.semrush.com/v2/mcp -t http` (KB, secondary summary, medium confidence). Docs: https://developer.semrush.com/api/v4/introduction/semrush-mcp/
- AI Visibility Index, 26 Jun 2026: 126M US AI prompts (Jan-Apr 2026) across ChatGPT, Gemini, Google AI Mode, AI Overviews; ChatGPT cites ~15 sources per answer vs Gemini ~3; AI traffic to US retail sites +1,324% (Oct 2024 to May 2026); 45% of marketing leaders cannot measure AI visibility. Source: https://www.semrush.com/news/463141-semrush-releases-expanded-2026-ai-visibility-index-analyzing-126-million-ai-search-prompts/
- AI Visibility Toolkit ~ $99/month per domain (third-party, medium confidence).
- Maturity: **mature and already wired into our tooling** (Semrush MCP is connected in this environment).

### 5.2 Jasper
- PR Newswire, 16 Jun 2026: GEO Agent GA; continuously analyses brand visibility across ChatGPT/Gemini/Claude, identifies gaps, "executes optimization workflows"; runs inside Jasper's governance (brand voice, compliance); no pricing or ROI figures. Source: https://www.prnewswire.com/news-releases/jasper-launches-end-to-end-geo-agent-for-enterprise-marketers-302800957.html
- Jasper's 2026 State of AI in Marketing: 91% of marketers use AI (vendor survey, medium confidence).
- Maturity: **mature for enterprise content ops**; overkill for a demo where Claude already drafts.

### 5.3 Surfer
- Update, 25 May 2026: new API exposes full Content Editor customisation (brand knowledge, custom voice, templates, word count, custom instructions) and a unified AI SEO score endpoint; docs "optimised for machine consumption and agent integration"; **Surfer MCP and "Agentic Surfy" in development, no dates**; API requires Peace of Mind or Enterprise plan and manual credential request; closed test group. Source: https://surferseo.com/updates/new-surfer-api-june2026/
- Maturity: **emerging**. Programmatic scoring is usable now; native agent is not.

---

## 6. Ad management agents
### 6.1 Google
- Google Marketing Live, 20 May 2026: **Ask Advisor**, a unified Gemini agent across Google Ads, Analytics, Merchant Center and GMP; Ads Advisor gains three agentic safety/policy features; AI Max expanded to Search, new AI Max for Shopping and for Travel; Asset Studio (brand guidelines to creative); Demand Gen formats; UCP expansion; GA 360 re-positioned. Source: https://blog.google/products/ads-commerce/google-marketing-live-2026-collection/
- "AI Brief" (natural-language guidance for AI Max / PMax) is reported by agencies (Brainlabs, Monks) covering GML; not in the collection page I fetched. Confidence medium.
- **Official Google Ads MCP server** (github.com/googleads): tools are `search` (GAQL), `get_resource_metadata`, `list_accessible_customers`; OAuth proxy / ADC auth; no mutation tools. Source: https://github.com/googleads/google-ads-mcp
- **Google Ads API Agent Skills** (updated 19 Aug 2026): portable skill packages for Claude Code, Antigravity, Codex, Cursor; guide agents to generate GAQL, write client-library scripts to create campaigns, configure OAuth; includes `google-ads-api-mcp-setup` and `google-ads-api-quickstart`. Source: https://developers.google.com/google-ads/api/docs/developer-toolkit/agent-skills
- Read: first-party = safe reads; writes require the API through an agent skill or a third party. Design consequence for the demo: reporting/analysis agents can run on Google's own MCP; any change to spend goes through an approval step and a write path we control.

### 6.2 Meta
- about.fb.com, 28 Jan 2026: video-generation ad tools hit a $10B revenue run-rate in Q4 2025 growing ~3x faster than ads revenue; GEM model +3.5% clicks on Facebook, >1% conversions on Instagram; Meta AI business assistant in test with advertisers. No statement about "every ad made by AI by end of 2026" in that post. Source: https://about.fb.com/news/2026/01/2026-ai-drives-performance/
- Marketing Brew, 7 Apr 2026: agencies say full AI ad creation is "likely much further off"; one agency has no client willing to let Meta generate creative; Advantage+ is 60-70% of another agency's Meta spend, but for audience/budget, not creative. Source: https://www.marketingbrew.com/stories/2026/04/07/meta-ai-ad-creation
- Zuckerberg's June 2025 "fully automated by end of 2026" statement is widely reported (WSJ, secondary); the current status is testing, not launch. Confidence medium.

### 6.3 Adspirer (MCP ad manager, already connected here)
- Docs (undated): MCP server with 400+ tools: Google Ads 147, Meta 60, Amazon 61, ChatGPT Ads 36, LinkedIn 55, TikTok 37; plus GA4 and Klaviyo on Plus/Pro/Max plans; clients include Claude (Chat, Cowork, Code), ChatGPT, Cursor, Codex, Gemini CLI; "autonomous agents propose changes to an approval queue; nothing spends or changes without your OK"; ChatGPT Ads campaigns created paused; REST API alternative. Pricing not on the docs page. Source: https://www.adspirer.com/docs/introduction
- Open-source sibling: github.com/amekala/ads-mcp (100+ tools). Confidence high that it exists; unaudited.
- Maturity: **emerging but demo-ready** because of the approval-queue design. Trust decision: third-party OAuth broker sits between our agent and client ad accounts; needs a DPA before touching real client accounts.

---

## 7. Inbound intake bots
- Fin pricing (fetched 2026-09-02): $0.99 per resolution / procedure handoff / disqualification, **$9.99 per lead qualification**, one outcome billed per conversation, 50-outcomes/month minimum on non-Intercom helpdesks. Source: https://fin.ai/pricing
- Fin resolution: 76% average end-to-end (Salesforce release, 15 Jun 2026); third parties cite 42-50% in published case studies for older periods (medium confidence).
- HubSpot Customer Agent: $0.50 per resolved conversation; 65-70% resolution (section 4.1).
- Maturity: **mature**. For the demo, an intake bot on the agency site + Slack/e-mail that qualifies leads into Linear is the highest-value, lowest-risk sales agent we can show, and there are public price anchors ($9.99 per qualified lead) to benchmark against.

---

## 8. Spam risk (what breaks autonomous outbound)
- Google sender requirements (support.google.com, effective since 1 Feb 2024, still current): 5,000 msgs/day threshold; SPF + DKIM + DMARC (p=none minimum) for bulk; spam rate below 0.10%, never >= 0.30%; one-click unsubscribe (`List-Unsubscribe-Post`) for marketing mail. Source: https://support.google.com/a/answer/81126?hl=en
- Vendor data on AI outbound (firstsales.io, 15 Jun 2026): "AI SDR campaigns ran ~6.4x the volume of manual campaigns at ~38% lower reply rates" (1.5M-email internal dataset, unsourced), average cold reply rate 3.43% (unsourced), inbox placement ~84% (Validity 2025 benchmark, named). Treat as **directional, low confidence**. Source: https://firstsales.io/blog/why-ai-sdrs-get-blocked/
- Structural point that is not in dispute: every vendor that survived 2025-26 moved to human approval before send (HubSpot, Artisan, Apollo, Instantly's "human-in-the-loop reply handling"). The category learned that autonomous volume burns domains and brands.

---

## 9. Legal constraints for a Dutch AI agency

### 9.1 Commercial e-mail (Telecommunicatiewet art. 11.7, ACM)
- ACM guidance "Spam voorkomen in uw reclame" (undated, fetched 2026-09-02): you may send electronic commercial messages only to recipients who gave prior consent; consent must be an explicit choice (no pre-ticked boxes), clearly about commercial messages, and **provable up to 5 years after sending**; existing customers may be mailed about related products/services if they can easily unsubscribe; opt-out must be quick and free. The page applies the same rule to consumers and businesses. Source: https://www.acm.nl/nl/verkoop-aan-consumenten/reclame-en-verleiden/spam-voorkomen-uw-reclame
- Rechtspersonen: ACM's spam topic page (per search extract; the sub-page returned 404 on fetch) states that unsolicited commercial e-mail to legal entities also requires prior consent, with an exception when the company deliberately published an address for that purpose (e.g. sales@...). Confidence **medium**; I could not render art. 11.7 on wetten.overheid.nl. Several vendor blogs (reachiq.nl, legiscope.com) claim B2B e-mail to BV/NV is opt-out; that reading conflicts with ACM's own guidance and should not be relied on without legal review. Historic ACM/OPTA fines for B2B spam exist (Companeo, EUR 100k, acm.nl).
- GDPR/AVG layer (secondary sources, medium confidence): business contact persons and sole-trader addresses are personal data; legitimate interest (art. 6(1)(f), recital 47) is the usual basis for B2B prospecting but needs a documented LIA; the AP interprets legitimate interest strictly and lists data trading as a 2026 enforcement priority. Source: https://www.legiscope.com/blog/avg-marketing-direct-marketing.html
- **Implication:** in NL, cold e-mail is opt-in by default even for companies. A compliant outbound agent must carry a consent basis per contact (opt-in / existing customer / address published for the purpose), a 5-year evidence trail, and an unsubscribe in every message.

### 9.2 Telemarketing (from 1 July 2026)
- ACM, 25 Jun 2026: soft opt-in abolished; companies may no longer call consumers, zzp'ers or vof/maatschap with commercial offers merely because they are or were customers; explicit prior consent required; exceptions only for charities, charity lotteries and newspaper/magazine publishers; ACM will monitor all sectors and warns about last-minute consent grabs. Source: https://www.acm.nl/nl/publicaties/vanaf-1-juli-strengere-regels-voor-telemarketing-alleen-nog-maar-als-klant-toestemming-heeft-gegeven
- Calls to legal entities (BV/NV) are outside this opt-in regime (secondary sources, medium confidence). An AI phone agent (11x "Jordan"-style) targeting Dutch SMBs is therefore effectively limited to legal entities with a documented basis, and still falls under AI Act disclosure (9.3).

### 9.3 EU AI Act, Article 50 (applies since 2 August 2026)
- European Commission FAQ: providers of systems designed for "genuine two-way exchange with people" (chatbots, AI agents, avatars) must ensure people are informed they interact with AI "from the start of the first interaction", unless obvious to a reasonably well-informed person (narrow); providers of generative systems must mark synthetic audio/image/video/text in machine-readable form; deployers must label AI-generated text published on matters of public interest, **waived when a qualified person exercised real editorial control** (fact-checking, authority to approve/alter/reject); fines up to EUR 15M or 3% of worldwide turnover; Guidelines and Code of Practice published. Source: https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act
- Commission Guidelines adopted 20 Jul 2026 (McCann FitzGerald note). Per emailexpert (23 Jul 2026): "a message generated by an AI agent to a natural person should carry an AI notice at the top"; routine marketing copy drafted with AI and under human editorial responsibility is not subject to labelling; audit AI customer communications and document editorial review. Sources: https://www.mccannfitzgerald.com/knowledge/data-privacy-and-cyber-risk/ai-transparency-european-commissions-guidelines-on-article-50-part-1-provider-obligations ; https://emailexpert.com/ai-act-article-50-transparency-guidelines/
- Digital Omnibus on AI: provisionally agreed 6 May 2026 (Gibson Dunn, 27 May 2026), signed 8 Jul, in force 27 Jul 2026 (Usercentrics). Art. 50 unchanged; Art. 50(2) marking grace period to **2 Dec 2026** only for generative systems already on the market before 2 Aug 2026; high-risk Annex III deadline moved to 2 Dec 2027, Annex I to 2 Aug 2028. Sources: https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/ ; https://usercentrics.com/knowledge-hub/eu-ai-act-high-risk-delay-article-50-transparency-consent/
- **Implication:** any inbound bot, reply agent or AI phone agent in the demo must self-identify at first contact and (for agents acting for a client) say on whose behalf it acts. Human-drafted-or-reviewed sales emails need no label; agent-generated replies do. Generated images/video for ads must carry machine-readable marks (model-provider side, but the agency is the deployer and must not strip them).

---

## 10. Maturity matrix

| Category | Mature now | Emerging | Hype / avoid in demo |
|---|---|---|---|
| Data & enrichment | Clay, Apollo | | |
| Outbound drafting w/ approval | HubSpot Prospecting Agent, Apollo AI Assistant, Instantly reply agent | Artisan Ava 2.0 | 11x-style "autopilot" SDR |
| Inbound intake / qualification | Fin, HubSpot Customer Agent | | |
| Proposal / quote | Template + LLM + e-sign (PandaDoc/Qwilr) | PandaDoc MCP (unverified) | |
| SEO research & briefs | Semrush MCP, Surfer API | Surfer MCP / Agentic Surfy | |
| AI visibility (GEO/AEO) | Semrush AI Visibility, HubSpot AEO | Jasper GEO Agent | |
| Ads reporting | Google Ads MCP (read), Supermetrics | | |
| Ads execution | Platform-native (AI Max, Advantage+) | Adspirer MCP w/ approval queue, Google Agent Skills | Meta "URL + budget, walk away" |
| Phone outbound | | | AI cold calling in NL (consent regime) |

---

## 11. Findings table

| # | Claim | Source URL | Source date | Confidence | Impact |
|---|---|---|---|---|---|
| 1 | HubSpot moved Customer Agent to $0.50 per resolved conversation and Prospecting Agent to $1 per qualified lead, effective 14 Apr 2026; Customer Agent resolves 65% of conversations | https://www.hubspot.com/company-news/hubspots-customer-agent-and-prospecting-agent-now-you-pay-when-the-task-is-complete | 2026-04-13 | high | high |
| 2 | HubSpot Prospecting Agent has "Review before sending" and "Send automatically" modes; caps: 1,000 emails/day, 3 agent emails per contact per 90 days | https://knowledge.hubspot.com/prospecting/use-the-prospecting-agent | 2026-08-14 | high | high |
| 3 | HubSpot Spring 2026: Prospecting Agent covers full lifecycle with rep-reviewed drafts; Customer Agent ~70% avg resolution; HubSpot AEO $50/mo | https://www.hubspot.com/company-news/spring-2026-spotlight | 2026-04-14 | high (source) / medium (vendor metrics) | medium |
| 4 | Apollo AI Assistant GA 4 Mar 2026, ~20k weekly users, free intro on paid plans; it drafts/researches but does not autonomously send or book | https://www.prnewswire.com/news-releases/apolloio-launches-ai-assistant-powering-end-to-end-agentic-workflows-in-the-first-ai-native-all-in-one-gtm-platform-302703896.html | 2026-03-04 | high | medium |
| 5 | Clay: Claygent on all tiers incl. Free; native sequencer; Growth adds domain/email purchase for sequencer; Launch ~$167/mo, Growth ~$446/mo monthly (annual figures need re-check) | https://www.clay.com/pricing | fetched 2026-09-02 | medium | medium |
| 6 | 11x publicly listed non-customers as customers; ZoomInfo trial "performed significantly worse than our SDR employees"; employee-reported 70-80% churn; trial contracts counted as ARR | https://techcrunch.com/2025/03/24/a16z-and-benchmark-backed-11x-has-been-claiming-customers-it-doesnt-have/ | 2025-03-24 | high | high |
| 7 | 11x Alice markets 24/7 autonomous prospecting, reply handling and meeting booking; no approval workflow shown; no public pricing | https://www.11x.ai/worker/alice | undated (fetched 2026-09-02) | medium | medium |
| 8 | Artisan Ava 2.0 (rebuild) launched with "approval gates wherever you want them" | https://www.artisan.co/blog/artisan-launches-ava-2-0-first-autonomous-ai-bdr | 2026-05-26 | high | medium |
| 9 | Instantly Growth $47/mo unlimited accounts + warmup; bundles $94/$194/$555 with AI Sales/Reply Agent | https://instantly.ai/pricing | fetched 2026-09-02 | high | medium |
| 10 | Agentforce: $500 per 100k Flex Credits, 20 credits ($0.10) per action, $2/conversation alternative, 100k credits free with Foundations (Enterprise Ed.) | https://help.salesforce.com/s/articleView?id=004811240&language=en_US&type=1 | 2025-05-19 | high | medium |
| 11 | Agentforce per-user unlimited add-on ~$125/user/month | https://aquiva.com/blog/agentforce-pricing-gets-a-long-overdue-fix-flex-credits-are-now-live | 2026 (undated) | medium | low |
| 12 | Salesforce to acquire Fin for ~$3.6B; Fin resolves 76% of support volume end-to-end; 30k+ customers; close Q4 FY27 | https://investor.salesforce.com/news/news-details/2026/Salesforce-Signs-Definitive-Agreement-to-Acquire-Fin/default.aspx | 2026-06-15 | high | medium |
| 13 | Fin pricing: $0.99 per resolution/handoff/disqualification, $9.99 per lead qualification, 50 outcomes/month minimum on non-Intercom helpdesks | https://fin.ai/pricing | fetched 2026-09-02 | high | high |
| 14 | Semrush official Claude connector (MCP) launched; included in Semrush One and SEO Classic; 28.8B keywords, 43T backlinks, 317M LLM prompts | https://www.semrush.com/news/469301-semrush-launches-official-connector-for-claude-bringing-marketing-intelligence-into-ai-conversations/ | 2026-08-26 | high | high |
| 15 | Semrush 2026 AI Visibility Index: 126M prompts; AI traffic to US retail +1,324% Oct 2024-May 2026; 45% of marketing leaders cannot measure AI visibility | https://www.semrush.com/news/463141-semrush-releases-expanded-2026-ai-visibility-index-analyzing-126-million-ai-search-prompts/ | 2026-06-26 | high | medium |
| 16 | Jasper GEO Agent generally available | https://www.prnewswire.com/news-releases/jasper-launches-end-to-end-geo-agent-for-enterprise-marketers-302800957.html | 2026-06-16 | high | low |
| 17 | Surfer new API (full Content Editor control, AI SEO score endpoint); MCP and Agentic Surfy in development, no dates; API needs Peace of Mind/Enterprise | https://surferseo.com/updates/new-surfer-api-june2026/ | 2026-05-25 | high | medium |
| 18 | Google Marketing Live 2026: Ask Advisor unified agent; AI Max for Shopping and Travel; Asset Studio; Ads Advisor agentic safety features | https://blog.google/products/ads-commerce/google-marketing-live-2026-collection/ | 2026-05-20 | high | medium |
| 19 | Google's official Ads MCP server exposes only search / get_resource_metadata / list_accessible_customers (no mutations) | https://github.com/googleads/google-ads-mcp | undated (fetched 2026-09-02) | high | high |
| 20 | Google Ads API Agent Skills for Claude Code, Codex, Cursor, Antigravity, incl. campaign-creation scripts and MCP setup | https://developers.google.com/google-ads/api/docs/developer-toolkit/agent-skills | 2026-08-19 | high | high |
| 21 | Meta: video-gen ad tools $10B run-rate Q4 2025; GEM +3.5% clicks; Meta AI business assistant in test | https://about.fb.com/news/2026/01/2026-ai-drives-performance/ | 2026-01-28 | high | medium |
| 22 | Agencies say Meta's fully AI-created ads by end-2026 is "likely much further off"; Advantage+ is 60-70% of one agency's spend for audience/budget, not creative | https://www.marketingbrew.com/stories/2026/04/07/meta-ai-ad-creation | 2026-04-07 | high | medium |
| 23 | Adspirer: 400+ MCP tools across Google/Meta/Amazon/ChatGPT/LinkedIn/TikTok Ads; approval queue, nothing spends without OK; Claude Code supported | https://www.adspirer.com/docs/introduction | undated (fetched 2026-09-02) | high | high |
| 24 | PandaDoc offers an MCP server for agent-driven document creation and e-sign | https://www.pandadoc.com/blog/whats-new-on-pandadoc-june-2026/ | 2026-06 (not fetched, HTTP 429) | low | medium |
| 25 | ACM: commercial e-mail requires prior explicit consent, provable for 5 years; existing-customer exception for related products with easy opt-out; opt-out must be quick and free | https://www.acm.nl/nl/verkoop-aan-consumenten/reclame-en-verleiden/spam-voorkomen-uw-reclame | undated (fetched 2026-09-02) | high | high |
| 26 | ACM: unsolicited commercial e-mail to rechtspersonen also needs consent unless the address was deliberately published for that purpose (vendor blogs claiming B2B opt-out conflict with this) | https://www.acm.nl/nl/onderwerpen-telecommunicatie-meld-spam-bij-acm/welke-ongewenste-berichten-kan-de-acm-aanpakken | undated (search extract; direct fetch 404) | medium | high |
| 27 | From 1 Jul 2026 telemarketing soft opt-in abolished for consumers, zzp'ers, vof/maatschap; explicit prior consent required; ACM enforces from day one | https://www.acm.nl/nl/publicaties/vanaf-1-juli-strengere-regels-voor-telemarketing-alleen-nog-maar-als-klant-toestemming-heeft-gegeven | 2026-06-25 | high | high |
| 28 | GDPR: B2B contact data is personal data; legitimate interest needs a documented LIA; AP strict; data trading an AP 2026 priority | https://www.legiscope.com/blog/avg-marketing-direct-marketing.html | 2026 (undated) | medium | high |
| 29 | AI Act Art. 50 applies from 2 Aug 2026: AI disclosure at first interaction for chatbots/agents (narrow "obvious" exception); public-interest text labelling waived under real editorial control; fines EUR 15M / 3% | https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act | 2026 (fetched 2026-09-02) | high | high |
| 30 | Commission Art. 50 guidelines adopted 20 Jul 2026; agent-generated messages to natural persons should carry an AI notice; routine AI-assisted marketing copy under human editorial responsibility is exempt from labelling | https://emailexpert.com/ai-act-article-50-transparency-guidelines/ | 2026-07-23 | medium | high |
| 31 | Digital Omnibus on AI in force 27 Jul 2026; Art. 50 unchanged; Art. 50(2) marking grace to 2 Dec 2026 for pre-existing generative systems; high-risk deadlines to Dec 2027 / Aug 2028 | https://usercentrics.com/knowledge-hub/eu-ai-act-high-risk-delay-article-50-transparency-consent/ ; https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/ | 2026-07 / 2026-05-27 | medium | medium |
| 32 | Google bulk-sender rules: 5k/day threshold; SPF+DKIM+DMARC; spam rate <0.10%, never >=0.30%; one-click unsubscribe | https://support.google.com/a/answer/81126?hl=en | effective 2024-02-01 (current) | high | high |
| 33 | Vendor data: AI outbound ran ~6.4x volume at ~38% lower reply rate; 3.43% avg cold reply rate (unsourced) | https://firstsales.io/blog/why-ai-sdrs-get-blocked/ | 2026-06-15 | low | medium |

---

## 12. What this means for the AI-run agency demo (Linear as OS)

**Design principle:** "Inbound-first, consent-based, human-approved outbound, disclosed by default." This is what the market converged on and what NL/EU law requires.

1. **Sales agent = intake + qualification + proposal, not cold blast.**
   - Website/Slack/e-mail intake bot that self-identifies as AI at first message (Art. 50), qualifies against an ICP, and creates a Linear issue in a `Leads` project with fields: source, consent basis (`opt-in` / `klantrelatie` / `published-address` / `inbound`), evidence link, disclosure-shown = true.
   - Price anchor for the demo narrative: HubSpot $1 per qualified lead, Fin $9.99 per qualification. Our agent's cost per qualified lead can be computed from Claude token spend and shown on the Linear issue.
   - Proposal: Claude drafts from a Notion/Linear pricing template; a human `Review` state precedes `Sent`; e-sign via PandaDoc/Qwilr only if needed.
2. **Outbound (if shown at all) is warm and gated.** Copy HubSpot's policy: draft -> human review -> send from a human identity; max 3 touches per contact per 90 days; every contact carries a consent basis; unsubscribe in every message; consent evidence retained 5 years. No cold e-mail to Dutch companies without a documented basis. No AI cold calls to consumers/zzp.
3. **Marketing agent = research + draft + optimise + report.** Semrush MCP (already connected) for keyword/competitor/backlink work and AI-visibility tracking; Claude for drafts; an `Editorial review` state with a named human reviewer (this both improves quality and triggers the Art. 50 labelling exemption); Surfer/Semrush scoring via API before `Approved`.
4. **Ads agent = read freely, write via approval queue.** Google's official Ads MCP for reporting; Supermetrics for cross-platform data; Adspirer (already connected) for proposed changes that land in an approval queue; new campaigns created paused. Model this in Linear as `Proposed change` -> `Approved by human` -> `Applied` with the diff in the issue body.
5. **Compliance is a first-class workflow object.** Labels/custom fields in Linear: `ai-disclosed`, `consent-basis`, `editorial-review`, `synthetic-media-marked`. A weekly "compliance agent" issue that audits open leads/campaigns against these fields is a cheap, visible way to show supervision.
6. **Vendor stack for the demo (minimum):** HubSpot Free/Starter or Linear-only CRM for leads; Semrush MCP; Adspirer MCP; Google Ads MCP; Supermetrics MCP; PandaDoc/Qwilr optional. Do not license 11x/Artisan/Jasper for the demo; they add cost without changing what we can show.

---

## 13. Open questions / not verified
- Exact text of Telecommunicatiewet art. 11.7 for rechtspersonen (wetten.overheid.nl did not render the article in my fetches). Legal review recommended before any outbound e-mail feature goes live for clients.
- PandaDoc MCP server and June 2026 AI features (HTTP 429 on two fetches).
- Salesforce per-user Agentforce pricing (public pricing page 403; third-party figure only).
- Clay annual-billing figures (parsed inconsistently).
- Any independent (non-vendor) 2026 benchmark on AI SDR reply rates; the web-search budget for this session was exhausted before I could find one. All reply-rate figures here are vendor-sourced.
- Whether Semrush MCP "third integration" count includes ChatGPT and Perplexity apps (secondary sources say yes).
