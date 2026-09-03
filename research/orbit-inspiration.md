# Orbit inspiration for a fictional digital agency demo

Anonymised patterns pulled from 8 Teamleader Orbit boards across a range of client accounts. No real client, contact, or company names below.

## Client/project archetypes

1. **Shopify webshops** — new-build and ongoing feedback boards. Ranges from small local-shop launches (branding, theme setup, product/collection creation) to established stores with a steady feedback stream (hero copy, footer, promo landing pages).
2. **Shopify + ERP/CRM backend integrations** — custom middleware/connectors syncing orders, companies, invoices, and stock between Shopify and an ERP or accounting system (e.g. CERM, Exact, AS400-style PIM). Structured as scoped build epics (task-numbered, e.g. "A2. Task 1") plus a long tail of sync bugs after go-live.
3. **Framer marketing sites / migrations** — full-site rebuilds/migrations onto Framer, defined as numbered functional/non-functional requirements (FR/NFR), with a linear Backlog → Planned → In progress → UAT (internal) → UAT (external) → Done flow.
4. **CMS-based corporate or content sites** (Concrete CMS, PIMCORE, a Composer-style CMS) — ongoing retainer support: content edits, page/block features, CRM sync (e.g. Salesforce-fed content), plus a recurring security-hardening stream.
5. **Custom portals / dossier systems** — large, long-running internal-build boards (hundreds of todos) for a bespoke back-office application, closer to product development than website work.
6. **Internal tooling / SEO-tech / AI reporting** — an agency-built POC (GA4 + Search Console → dashboard → AI-generated read-only summary) piloted on one client before wider rollout, scoped in phases (F0 Scope, F1 Client profiles, F2 Google data, F3 Dashboard, F4 AI proof, R MVP roadmap).
7. **Retainer/SLA "Verzoeken" (requests) boards** — the most common board type by far: an always-on queue for a client's ad hoc requests across content, bugs, small features, and security items.

## Recurring work types (rough frequency)

- **Bug/visual fixes on live sites** — most common single category (text overflow, duplicate cards, misaligned images, broken filters).
- **Integration/sync issues** — very common on backend boards: stock/price not syncing, webhooks failing intermittently, metafields not updating, invoice status not flowing back.
- **Feature requests** — new blocks, search bars, filters, locators, PDF attachments, pricing tiers.
- **Security findings** — a recurring cluster, evidently from periodic scans: exposed keys, HTML injection, missing security headers, outdated dependencies, cleartext login.
- **Content/CMS admin requests** — user rights, page attributes, translations, draft/archive handling.
- **SEO/analytics** — GTM containers, GA4/Search Console linking, meta title generation, dashboards.
- **Access management** — small, frequent: add/remove admin users, 2FA settings.
- **Performance/reliability** — occasional but high-impact: slow imports, server crashes under load, slow image loading.

## Board/column patterns

Two dominant templates:

1. **Retainer/support template** (by far the most common), with a double swimlane prefix distinguishing who owns the next step:
   `Client | New requests` → `Client | Waiting for input` → `Fightclub | Backlog` → `Fightclub | Planned` → `Fightclub | Testing Acceptance` → `Client | Testing Acceptance` → `Fightclub | Acceptance akkoord voor Productie` → `Done`. Often with an `On Hold` and a `Debrief/Review` column too.
2. **Scoped-build template**: a simpler linear `Backlog → Planned → In progress → UAT (internal) → UAT (external)/Testing → Done`.

Category tags layer on top of columns, either simple (`Backlog / Development / Priority`) or a richer emoji taxonomy on mature boards: ✨ Feature, 🐛 Issue/Bug, 🔒 Security Issue, 🔄 Maintenance, 📄 Documentation, 📊 Performance Issue, 🛠️ Refactor, 🆕 New Request, ⏳ Blocked. Larger scoped projects number requirements (FR.01/NFR.02, or phase codes like F1/F2/F3) instead of using free-form titles.

## Ticket lifecycle observed

Client reports or requests something → lands in a "new requests"/"feedback" column → triaged into the agency's own backlog → picked up (`Doing`/`In progress`) → internal QA → client review (`Testing Acceptance` / `Waiting for input` if blocked on a client answer) → client sign-off → `Done`. Tickets stall for two typical reasons: waiting on a client decision (`On Hold`, `Waiting for input`) or waiting on an external dependency such as read/write access being granted (`Blocked`).

## 20 anonymised example ticket titles, by type

**Bug / visual**
1. Text overlaps photo on the destination detail page
2. Duplicate item card appears in search results
3. Currency formatting missing on checkout confirmation
4. Body text doesn't wrap correctly in the review block

**Integration / sync**
5. Stock levels stopped syncing from ERP to storefront after last update
6. New-order webhook intermittently fails to fire
7. Product spec metafields aren't populating after CRM export
8. Invoice status isn't reflected back from the accounting system

**Feature request**
9. Add a location filter to the store/dealer locator
10. Add a search bar to the main navigation
11. Support volume-based pricing tiers per customer group
12. Add PDF attachments to itinerary/detail pages

**Security**
13. Rotate an API key exposed in a public repository
14. Fix HTML injection vulnerability in the contact form
15. Add missing HSTS preload header
16. Disable cleartext login on the mail server

**Content / CMS admin**
17. Grant content-editor rights to a new team member
18. Add an FAQ block to the product page template

**SEO / analytics**
19. Auto-generate meta titles for product pages
20. Fix a recurring error in the GA4/Search Console dashboard

## Implications for a fictional agency demo

Four fictional clients would cover the real spread convincingly without copying any real one:

1. **A DTC e-commerce brand** (Shopify + ERP/inventory connector) — generates integration-sync bugs, feature requests, and a build epic; shows backend integration work, not just storefront tweaks.
2. **A B2B/industrial company** with a Framer marketing site and a product/dealer catalog — shows scoped migration work (FR/NFR-numbered epics) plus SEO content requests.
3. **A travel or hospitality booking site** on a CMS with CRM-fed content — a steady "feedback client" retainer board: content bugs, page features, sync quirks from the CRM feed.
4. **An internal/agency-facing SEO-AI reporting tool**, piloted on one client — shows the agency's own product thinking (phased roadmap, dashboarding, AI summary) as a differentiator beyond project delivery.

A fifth, optional recurring-security-retainer client (corporate site, steady drip of header/dependency/injection findings) would add realism to the "boring but essential" side of agency work.
