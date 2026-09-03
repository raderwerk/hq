# Gap 02 - Shopify execution modality for loop steps 4-6, and which real ticket runs spoor A

Date: 2026-09-02. Author: research subagent (Claude). Scope: how a GitHub Actions job without production credentials pushes a theme change to a Shopify development/acceptance store and returns a clickable preview URL; how visual/brand QA runs on that preview; and which real Orbit ticket and repo should run spoor A.

Method: WebSearch budget for this session was exhausted (200/200), so every web claim below comes from a direct fetch of an official page (shopify.dev, shopify.com/legal, help.shopify.com, github.com/Shopify, playwright.dev, docs.github.com), plus local verification against the installed Shopify CLI 4.7.0 (`shopify theme push --help`, `shopify store --help`), the GitHub API via `gh` (release dates, repo contents of Fightclub's own theme repos) and the Orbit MCP (boards 23223 "TowMotive | Verzoeken board" and 65722 "TowMotive Phase 3"). 12 primary sources read; 6 local/API verifications. Confidence is per claim. Nothing was executed against a real store: no dev store credentials are in this session and the Shopify MCP is unauthenticated.

## 1. Short answer

The delivery step ("deploy alleen naar preview of dev store") has a boring, fully documented tool behind it and Fightclub already runs it for one client: `shopify theme push` from GitHub Actions with a Theme Access password, `--json` output that contains `theme.preview_url` (`https://<store>/?preview_theme_id=<id>`) and `theme.editor_url`. Nothing about it needs production credentials if the store is the dev/acceptance store and the token is that store's Theme Access password. What is missing at Fightclub is (a) the per-PR preview variant (`--unpublished` or the new `--development-context <PR>` flag) and (b) any QA on top of the preview; both are documented and cheap. The visual bar (lane 10 blocker 3) is only partly tool-solvable: Theme Check, Lighthouse and Playwright screenshot diffs give deterministic evidence, but "does it look like the shop" still needs a human or a browser-driving reviewer (claude-in-chrome) on the preview URL.

For spoor A the honest finding is: on 2026-09-02 there is no clean, open, S/M Shopify theme ticket for TowMotive. The two most recent THL theme tickets (39450, 39617) were both done on 2026-08-24 in about 15 minutes each, with PR + screenshot + a development-theme preview for client sign-off, and closed on 2026-08-28. They are the exact shape spoor A needs; the trekhaakland repo they live in has no CI at all. The open TowMotive items are middleware/Hyper-shaped (39996, 39868) or not Shopify (39557 TowCenter, 40044 THM). Recommendation and options in section 8.

## 2. The verified push-and-preview pipeline

### 2.1 Command surface (verified on local Shopify CLI 4.7.0, 2026-09-02; npm latest is 4.7.1 published 2026-09-02)

- `shopify theme push --unpublished --theme "<name>" --json --store <store> --password $SHOPIFY_CLI_THEME_TOKEN` creates a new unpublished theme and returns JSON. The `--help` text of 4.7.0 literally shows `$ shopify theme push --unpublished --json` as the second usage example and this output shape:
  `{"theme": {"id": 108267175958, "name": "MyTheme", "role": "unpublished", "shop": "mystore.myshopify.com", "editor_url": "https://mystore.myshopify.com/admin/themes/108267175958/editor", "preview_url": "https://mystore.myshopify.com/?preview_theme_id=108267175958"}}`.
- `--development-context <value>` (env `SHOPIFY_FLAG_DEVELOPMENT_CONTEXT`): "Unique identifier for a development theme context (e.g., PR number, branch name). Reuses an existing development theme with this context name, or creates one if none exists." This is the per-PR preview primitive: one development theme per PR, re-pushed on every commit, no theme-library clutter. Development themes "don't count toward your theme limit" and are "deleted from the store after seven days of inactivity" (shopify.dev/docs/storefronts/themes/tools/cli).
- `--strict`: "Require theme check to pass without errors before pushing. Warnings are allowed."
- `--allow-live`: "Required in non-interactive environments when targeting the live theme." Absence of this flag is the safety rail: a CI job without it cannot overwrite the live theme even if the token allows it.
- `--nodelete`, `--only`, `--ignore`, `--path` (needed for trekhaakland, whose theme root is `src/`).
- `shopify theme share` uploads as a new unpublished theme with a randomized name and "returns a preview link that you can share with others" (docs), but has no `--json` flag, so `theme push --unpublished --json` is the better CI primitive.
- `shopify theme preview -t <theme> --overrides <json> --json` applies JSON setting overrides and returns a preview URL (4.x, local help). Useful for QA variants without pushing.
- `shopify theme check --fail-level error --output json` for CI linting (local help; docs confirm `--fail-level` = "Minimum severity for exit with error code").

Sources: https://shopify.dev/docs/api/shopify-cli/theme/theme-push (fetched 2026-09-02, undated page); https://shopify.dev/docs/api/shopify-cli/theme/theme-share; https://shopify.dev/docs/api/shopify-cli/theme/theme-check; local `shopify theme push --help` (4.7.0); https://github.com/Shopify/cli/releases (4.7.1 published 2026-09-02, 4.0.0 on 2026-05-21 dropped Node 20; npm engines `node >=22.12.0`).

### 2.2 CI authentication without production credentials

Shopify documents three env vars for CI: `SHOPIFY_CLI_THEME_TOKEN` ("The Theme Access password that you generated or were given by a merchant"), `SHOPIFY_FLAG_STORE`, and optional `SHOPIFY_FLAG_FORCE=1` to disable prompts, with a GitHub Actions example that installs `@shopify/cli` globally and runs `shopify theme push --json --theme ... --store ${{ secrets.SHOPIFY_FLAG_STORE }} --password ${{ secrets.SHOPIFY_CLI_THEME_TOKEN }}` (https://shopify.dev/docs/storefronts/themes/tools/cli/ci-cd).

Options, in order of fit for the demo:

| Option | What it is | Scope / blast radius | Verified? |
|---|---|---|---|
| Theme Access app password (`shptka_...`) | Merchant installs the free Theme Access app, generates a password per developer; link expires after 7 days or first view; deleting the password revokes access | "only write access to themes (`write_themes`)". Store-scoped. Can write the live theme, so the CI job must never pass `--allow-live` | High: https://shopify.dev/docs/storefronts/themes/tools/theme-access |
| Dev Dashboard app + client credentials grant | Server-side app in your own Shopify organization; POST `/admin/oauth/access_token` with `grant_type=client_credentials`; token "Always 86399 (24 hours)"; scopes are whatever the app version has | Works only for stores in the same organization, and dev stores must be "created via the Dashboard's Dev stores page". This is what Shopify's Lighthouse action now uses | High for mechanics: https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/client-credentials-grant. Whether Fightclub's existing dev stores qualify: not verified |
| Legacy custom app access token | Admin API token from a store-level custom app | Full scopes you grant; "As of January 1, 2026 Shopify no longer allows creating new custom apps. Existing custom apps continue to work" (lighthouse-ci-action README) | Medium (third-party statement in a Shopify repo) |
| Store auth session cache (CLI 4.4.0+) | `shopify store auth --store X --scopes write_themes` stores an online token; theme commands fall back to it when `--password` is absent (PR #7783, merged 2026-06-29) | Interactive login; not for headless CI | High for existence, not for CI use |
| GitHub theme integration ("Connect from GitHub") | Shopify admin connects a branch to a theme; two-way sync; commits made in the admin are written back to the branch (batched ~10 s); since 2026-08-26 "GitHub commits now name the last theme editor" | No CI needed, but two-way sync means agent branches would receive merchant commits; "GitHub outside collaborators can't connect branches" | High: https://shopify.dev/docs/storefronts/themes/tools/github; changelog 2026-08-26 |

Rule for the agency loop: one Theme Access password per store, stored as a GitHub Environment secret on the dev/acceptance environment only; the production environment secret is never readable by the PR-preview workflow. Agents never see the token; only the runner does.

### 2.3 Fightclub already has this workflow in-house (Dreambaby)

`fightclub-dreambaby/dreambaby-shopify/.github/workflows/deploy-shopify-theme.yml` (read via `gh api`, repo pushed 2026-08-27) is a `workflow_dispatch`-only workflow with GitHub Environments `develop`, `acceptance`, `production`, per-environment `SHOPIFY_STORE`, `SHOPIFY_THEME_ID`, `SHOPIFY_CLI_THEME_TOKEN`, an `--allow-live` gate (`SHOPIFY_ALLOW_LIVE` only on non-prod, always on prod), a typed `DEPLOY_PRODUCTION` confirmation, Node 22 + `@shopify/cli@latest`, `shopify theme push --json | tee shopify-theme-push.json`, the JSON uploaded as a 14-day artifact and a step summary. The README names `acc2-dreambaby.myshopify.com` as the acceptance store. Theme Check is present but commented out ("Re-enable it once the theme passes the configured checks consistently").

Delta needed to make it the agency preview step: add a `pull_request` trigger that runs on the `develop` environment with `--development-context "pr-${{ github.event.number }}"` (or `--unpublished --theme "pr-<n>-<sha>"`), parse `.theme.preview_url` from the JSON, post it as a PR comment / job summary, and let the orchestrator copy that URL into the Linear comment. That is roughly 25 lines of YAML on top of an existing, proven file.

### 2.4 The preview URL and the password page

- The preview URL is `https://<store>/?preview_theme_id=<id>`; Shopify's own Lighthouse action appends `&_fd=0&pb=0` to disable redirects and the preview bar (entrypoint.sh line 235).
- Dev stores are always password-protected: "You can't remove the password page or show a custom password page" (shopify.dev/docs/api/development-stores); help center: "can't deactivate private mode for the online store". So a clickable preview on a dev store needs the storefront password once per browser; Shopify's Lighthouse action handles this with a Puppeteer script that submits `form[action*=password]` before auditing. For a human reviewer in the demo this is one extra field; for an acceptance store (like Dreambaby's `acc2-`) it depends on whether that store is password-protected.
- Dev-store constraints that matter: "Dev stores can't be transferred to a client"; "You can only install free apps and partner-friendly apps. Custom and draft apps can't be installed" (help.shopify.com dev stores page). Whether the Theme Access app is installable on a dev store is not stated on the pages read; confidence low. The Dev Dashboard app + client-credentials path is the documented alternative for stores in your own organization.

### 2.5 Provisioning a store programmatically

- Dev stores: documented creation is manual in the Dev Dashboard ("Select Stores ... Select Create store"). No Partner API or GraphQL mutation for creating dev stores was found on the pages read; treat "Partner API provisioning" as not available (confidence low, absence of evidence).
- New in CLI 4.5.0 (2026-07-13): `shopify store create preview --name "..." --country NL --json` "Creates a new Shopify store, with no need for an existing account." `shopify store create dev` exists but "intentionally remains hidden and is not part of this release" (Shopify/cli PR #7976, merged 2026-07-09). Preview stores persist an Admin API token in the CLI's store-auth cache and `theme push`/`theme pull` fall back to it (PR #7783). 4.7.1 (2026-09-02) fixes "claimed preview store auth recovery", implying preview stores are meant to be claimed later. Lifetime, limits and whether a preview store is acceptable for client-facing previews are not documented on the fetched page; confidence medium for existence, low for suitability. For the demo, a preview store is a plausible zero-friction sandbox for spoor B; for spoor A use the client's existing dev/acceptance store.
- TowMotive already has a dev store: `trekhaakland-devstore.myshopify.com` is referenced in `fightclub-connector-backend/README.md:124` as the place where the Fightclub Connector app is installed. Whether it carries a current copy of the trekhaakland theme, who has Theme Access on it, and whether it is still alive was not verified (no credentials in this session). Confidence medium that it exists, low that it is demo-ready.

### 2.6 Deprecation that affects Fightclub laptops and CI

Changelog 2026-08-27 (action required): theme commands on CLI "3.83.x and earlier" using legacy storefront authentication for password-protected storefronts stop working on "October 1, 2026"; required is "3.84.0 or later", latest recommended 4.7.0; affects `theme dev`, `theme console`, `app dev` with theme app extensions. The local machine is on 4.7.0 and Dreambaby's workflow pins `@latest`; trekhaakland's README only demands Node >= 20 while CLI 4.x needs Node >= 22.12. Source: https://shopify.dev/changelog/password-protected-shop-dev-flows-on-shopify-theme-cli-v3-83-x-and-older-to-be-deprecated.

## 3. QA on the preview: what is deterministic and what is not

| Layer | Tool | Evidence it produces | Status (2026-09-02) |
|---|---|---|---|
| Lint | `shopify theme check --fail-level error --output json`, or `shopify/theme-check-action@v2` (v2.2.0, 2025-10-17; annotations with `token` and `base`) | JSON offenses, PR annotations; `--strict` on push blocks broken Liquid | High. Dreambaby has it commented out because the theme does not pass yet; expect the same on trekhaakland |
| Performance / a11y | `shopify/lighthouse-ci-action@v1` (v1.4.0, 2026-04-13, Docker). It pushes `shopify theme push --development --json`, reads `.theme.preview_url` and `.theme.id`, audits home + first product + first collection at `?preview_theme_id=...&_fd=0&pb=0`, submits the storefront password if given, enforces `lhci_min_score_performance` (default 0.6) and `lhci_min_score_accessibility` (default 0.9), and can post a PR status via `lhci_github_app_token`. Scopes: `read_products`, `write_themes`; auth via Dev Dashboard app `client_id`+`client_secret` or legacy `access_token` | Scores, HTML report, PR check | High (README + entrypoint.sh read) |
| Visual regression | Playwright `expect(page).toHaveScreenshot()` with `maxDiffPixels`; snapshots are per browser and OS (`-chromium-linux.png`); "For consistent screenshots, run tests in the same environment where the baseline screenshots were generated"; upload `playwright-report/` as artifact (retention-days 30) | Pixel diff images, trace viewer | High for the tool; the baseline must be generated on the same runner image, and marketing content changes (banners, prices) create noise on a live-data store |
| Brand / "looks like the shop" | No deterministic tool. Options: (1) LLM reviewer driving claude-in-chrome on the preview URL with the ticket's screenshot as reference (lane 01 section 7; OSWorld 2.0 strict 41.7% for Fable 5.1, so treat as advisory), (2) human at gate 2 with the before/after screenshots attached | Screenshots + rubric verdict | Medium; this stays the blocker lane 10 flagged. The demo should show the deterministic layers as hard gates and the visual judgment as a signed advisory comment, not as a pass/fail |
| Agentic storefront | WebMCP tools "live today on every Liquid storefront" (changelog 2026-08-05, effective 2026-08-21): agents can search catalog, manage cart, checkout, in Chromium origin trial | Not a QA tool yet | Medium; note for the honesty slide, not for the demo |

Cost: the org is on GitHub Free, which includes "2,000" Actions minutes and "500 MB" artifact storage per month for private repos; Linux 2-core is "$0.006" per minute beyond that (docs.github.com billing page). A push + theme check + Lighthouse + Playwright run is a few minutes; the 3 dry runs plus demo fit easily.

## 4. Shopify Dev MCP and agent-side tooling

- `npx -y @shopify/dev-mcp@latest` (npm 1.14.7, modified 2026-08-28) "runs locally and doesn't require authentication"; it is a docs + schema + validation server ("Developer docs and API schemas", "Code validation"), not a store client. Supported clients listed: Claude Code, Codex CLI, Antigravity CLI, Cursor, VS Code. The GitHub repo `Shopify/dev-mcp` returns 404 via the API (moved or private), so tool names could not be verified from source; confidence medium.
- CLI 4.3.0 added `shopify search` and `shopify doc fetch` (JSON documentation search from the terminal); 4.7.0 (2026-08-19) "Emit Claude Code plugin hint on CLI invocations" for the "Shopify AI Toolkit" plugin when `CLAUDECODE` is set (PR #8193). Practical effect: the dev agent can validate Liquid and look up docs offline of the web-search budget.
- The `claude.ai Shopify` MCP in this session is unauthenticated (only `authenticate` tools exposed). It is an Admin API client, not a theme push tool; it is not on the critical path for steps 4-6.

## 5. Shopify's terms on automated access

- API License and Terms of Use, last updated February 27, 2026: 2.1.3 developers must obtain an API client by registering a Partner account; 2.1.5 "you may not share the API Credentials with any third party other than a service provider acting on your behalf"; 2.3.14 "not use the Shopify API to conduct any systematic or automated data collection activities" and request only the minimum data needed; 2.3.24 "not use any information derived from the Shopify API ... to create, develop, train, fine tune, or improve any machine learning or artificial intelligence systems". Source: https://www.shopify.com/legal/api-terms.
- Partner Program Agreement, last updated February 27, 2026: B.5 a Development Store "cannot be used to process orders on behalf of the Partner or the Merchant; provided, however, that Development Stores may be used to process test orders"; 2.5.10 partners may only access Merchant Stores "for the purpose of performing work authorized by the respective Merchant" and "by using any of the permitted tools"; 9.15 no using Merchant Data and Customer Data to train or fine-tune AI systems without consent. Source: https://www.shopify.com/partners/terms.
- Reading for the demo (not legal advice): a CI runner or an agent pushing a theme with a merchant-issued Theme Access password is a "service provider acting on your behalf" doing merchant-authorized work; nothing read prohibits it. The two clauses that bite are 2.3.24 / 9.15 (do not feed store data or API responses into fine-tuning or eval sets; run logs are fine, training is not) and 2.3.14 (an agent must not bulk-scrape catalog data for "context"). Put both on the compliance checklist next to the AI Act art. 50 item.

## 6. What this changes in the brief

- Step 6 gets a real tool: PR-triggered `theme push --development-context pr-<n> --json` on the client's dev/acceptance store, preview URL in the PR and in the Linear comment. Human gate 2 clicks the preview link; nothing reaches the live theme because `--allow-live` is never passed and the token lives only in the non-prod GitHub Environment.
- Step 5 (review) gains three deterministic checks that the QA agent can cite instead of asserting: theme check JSON, Lighthouse scores, Playwright diff. The "QA keurt af, dev herstelt" loop in spoor B can be driven by a real failing check (for instance an intentionally missing `alt` that drops the accessibility score under 0.9) rather than a scripted rejection.
- The unit-economics slide gets a measurable delivery cost: CI minutes at $0.006 after the free 2,000, plus tokens.
- Assumption "er is een Shopify development store, anders wordt de deploystap gemockt" can be sharpened: THL has `trekhaakland-devstore` (unverified state) and Dreambaby has `acc2-dreambaby`; a `shopify store create preview` store is the fallback for spoor B.

## 7. Spoor A: what the Orbit boards actually contain today

Boards inspected 2026-09-02 via Orbit MCP.

TowMotive | Verzoeken board (23223, 12 open of 303): `Fightclub | Backlog`, `Planned`, `Review`, `Client | Review Staging`, `Deploy Staging -> Production` are all empty. Open items: 7 On Hold (2023-2025 vintage, e.g. 29474 filters, 18848 search engine), 1 New request 37573 "TH: Account gedeelte redirecten naar Partner Portal" (empty description, 0 comments), 2 Waiting for input (33510 configurator to Hyper, 14029 "Bestelinstructies" wording from 2023 with an unresolved test-mode discussion), 1 in Running tests (29227 "21360172 geeft geen modellen", data issue). None is a clean S/M theme ticket.

TowMotive Phase 3 (65722, 172 open of 835; column "Hot fix verzoeken" is empty; "New requests (After go live Phase)" has 7):

| extId | Title | Shape | Repo | Fit for spoor A |
|---|---|---|---|---|
| 39996 | THL zakelijk account aanmaken formulier doet het niet (2026-08-31, P3) | Bug: form on trekhaakland.nl/pages/b2b-registreren registers nothing in Shopify or Hyper | trekhaakland theme + fightclub-connector / middleware (memory: this field was missing in Hyper Test) | Real and urgent, but cross-repo (theme + connector + Hyper); this is the ~40% delegable class, not the 70-75% class |
| 39868 | THL order doorschieten ook met catalogusprijs en kortingspercentage | Feature in order sync | connector / middleware | Middleware; no |
| 39627 | THL Hoe wordt filter van geschikte modellen gegenereerd | Question | n/a | No |
| 39557 | TowCenter Cookiebot script laden (owner: requester, P1) | Cookiebot declaration not rendering on towcenter.com/cookies | towcenter.com is not the Shopify theme (Concrete CMS repo `towmotive`) | S-size and real, but not Shopify; possible spoor A on the Concrete stack instead |
| 39748 / 40056 | Tips & Tricks scherm, mail-vinkjes | Portal | partner portal | Middleware/portal; no |
| 40044 | THM Sitemap leeg | Site config | towmotivegroup (Vite/JS) | Not Shopify |

Closed reference tickets, both on the trekhaakland theme, both handled 2026-08-24 by a Fightclub developer in 15-minute slots with an internal spec comment (Wie/Scherm/Rol/Nu/Verwacht/Plan), a PR, a screenshot and a client "Dit is akkoord" on 2026-08-26:

- 39450 "THL | Configurator onthoud keuze niet" (reported 2026-07-29): PR #34 feature/39450 -> development, PR #36 -> main merged 2026-08-28. Delivery comment: "Dit staat nu op het Development Thema in THL. Dit valt in te zien door in Shopify Admin naar het development Thema toe te gaan en te klikken op preview."
- 39617 "THL | Toevoegen kenmerk dwarsbalk bij afbeelding trekhaken" (reported 2026-08-14): PR #35 feature/39617 -> development merged 2026-08-28; badge on PDP for collection trekhaken except zwanenhalskogels.

These two are the template: intake with a screenshot, one-repo change, verifiable on a preview theme, client approves in Orbit. The cadence of new THL theme requests is roughly one every two weeks (07-29, 08-14, 08-31).

Repo facts (via `gh api`, 2026-09-02): `enorm-techhub/trekhaakland` is private, Liquid + Vite (`yarn build` writes `src/assets/fc-*`), theme root `src` in `shopify.theme.toml`, branches `main` (prod) and `development`, no `.github/workflows`, deploys run from a laptop with `yarn deploy:dev|prod` using `.env` (`SHOPIFY_FLAG_STORE`, `SHOPIFY_CLI_THEME_TOKEN`, `SHOPIFY_THEME_ID_DEV|PROD`). Note the release-train rule in the brief says "feature-branch vanaf production"; in this repo the production branch is `main`.

## 8. Recommendation for open question 1

1. Run spoor A on the Shopify theme lane, not on the TowMotive middleware. Lane 09's 70-75% vs ~40% split is visible in the boards: the two THL theme tickets closed in 15 minutes each; the open THL ticket 39996 spans three systems. A middleware ticket would turn the demo into a Hyper debugging session.
2. Concrete candidate: the next THL request that lands on board 65722 "New requests (After go live Phase)" with a screenshot and a single-page scope (badge, wording, section, redirect). Ask Remko/Maurice for consent to run it through the agent loop with a preview theme instead of the manual development theme; the client sign-off step is unchanged ("preview in Shopify Admin"). If nothing arrives before the demo week, fallback (b): re-run 39617 from a branch off `main` with the badge removed first, or (c) 39557 on the Concrete stack if the presenter wants a real ticket at any cost, accepting that it says nothing about Shopify delivery.
3. Preconditions to build now, independent of the ticket: (i) add a PR-preview workflow to trekhaakland modeled on Dreambaby's file, targeting the THL dev or acceptance store with its own Theme Access password, `--path src`, `--development-context pr-<n>`, `--json`, preview URL to PR comment; (ii) confirm `trekhaakland-devstore` is alive, has a current theme copy and can get a Theme Access password (or use a Dev Dashboard app with client credentials); (iii) enable `theme check` in report-only mode and record the baseline offense count; (iv) Playwright baseline on the runner for the 3 pages the ticket touches.
4. Do not merge spoor A. The brief's "nooit gemerged" holds; the preview theme is deleted after 7 days of inactivity on its own.

## 9. Not verified / open

- Theme Access app installability on a dev store (help center says custom and draft apps cannot be installed; Theme Access is Shopify's own app, but the page does not say). Low confidence either way; check in the THL dev store admin.
- Lifetime, limits and claim flow of `shopify store create preview` stores; the docs page only carries the flags.
- Dev store count limits per organization: not on the pages read.
- Whether `trekhaakland-devstore.myshopify.com` still exists and mirrors the theme.
- Dev MCP tool names (repo 404 via API); only the npm package and shopify.dev page were read.
- Nothing was pushed to any store in this session.

## 10. Findings table

| # | Claim | Source | Date | Confidence | Impact |
|---|---|---|---|---|---|
| 1 | `shopify theme push --unpublished --json` returns `theme.preview_url` (`?preview_theme_id=`) and `theme.editor_url`; `--development-context <PR>` reuses one development theme per PR; `--strict` gates on theme check; `--allow-live` is required to touch the live theme non-interactively | https://shopify.dev/docs/api/shopify-cli/theme/theme-push + local CLI 4.7.0 help | 2026-09-02 | high | high |
| 2 | Documented CI auth = `SHOPIFY_CLI_THEME_TOKEN` (Theme Access password) + `SHOPIFY_FLAG_STORE` (+ `SHOPIFY_FLAG_FORCE=1`), with an official GitHub Actions example | https://shopify.dev/docs/storefronts/themes/tools/cli/ci-cd | 2026-09-02 (undated page) | high | high |
| 3 | Theme Access passwords have only `write_themes`, are viewable once, links expire after 7 days, deletion revokes | https://shopify.dev/docs/storefronts/themes/tools/theme-access | 2026-09-02 (undated) | high | medium |
| 4 | Fightclub already runs `shopify theme push --json` from GitHub Actions with environment-scoped Theme Access tokens and an `--allow-live` gate (Dreambaby); missing only the PR-preview trigger and active theme check | fightclub-dreambaby/dreambaby-shopify `.github/workflows/deploy-shopify-theme.yml` (private, read via gh) | 2026-08-27 (repo push) | high | high |
| 5 | trekhaakland (THL theme) has no CI; deploys from laptops via `yarn deploy:*` with a `.env` Theme Access token; theme root `src`, branches `main`/`development` | https://github.com/enorm-techhub/trekhaakland (private, read via gh) | 2026-08-28 (last push) | high | high |
| 6 | THL tickets 39450 and 39617 were each done in ~15 min on 2026-08-24 with PR + screenshot + development-theme preview and client approval 08-26; they are the spoor A template. No clean open S/M Shopify ticket exists on 2026-09-02; open THL item 39996 spans theme + connector + Hyper | Orbit boards 65722 and 23223 (MCP) | 2026-09-02 | high | high |
| 7 | Dev stores are created manually in the Dev Dashboard; password page cannot be removed; cannot be transferred; only free / partner-friendly apps installable | https://shopify.dev/docs/api/development-stores ; https://help.shopify.com/en/partners/dashboard/managing-stores/development-stores | 2026-09-02 (undated) | high | medium |
| 8 | `shopify store create preview --name --json` creates a store "with no need for an existing account" (CLI 4.5.0, 2026-07-13); `store create dev` intentionally hidden; theme push falls back to cached store-auth Admin token | local CLI help; https://github.com/Shopify/cli/pull/7976 ; https://github.com/Shopify/cli/pull/7783 | 2026-07-09 / 2026-06-29 | medium | medium |
| 9 | Client credentials grant: Dev Dashboard apps only, stores in your own organization, token "Always 86399 (24 hours)"; new custom apps cannot be created since 2026-01-01 | https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/client-credentials-grant ; lighthouse-ci-action README | 2026-09-02 / 2026-04-13 | high / medium | medium |
| 10 | `Shopify/lighthouse-ci-action` v1.4.0 (2026-04-13) pushes a development theme, audits home/product/collection at `?preview_theme_id=...&_fd=0&pb=0`, fills the storefront password, enforces min scores, posts PR status | https://github.com/Shopify/lighthouse-ci-action (README + entrypoint.sh) | 2026-04-13 | high | high |
| 11 | `Shopify/theme-check-action` v2.2.0 (2025-10-17) runs `shopify theme check` with PR annotations; `--fail-level` and `--output json` available in CLI | https://github.com/Shopify/theme-check-action ; https://shopify.dev/docs/api/shopify-cli/theme/theme-check | 2025-10-17 | high | medium |
| 12 | Playwright `toHaveScreenshot` with `maxDiffPixels`, per-OS/browser snapshots, must run in the same environment as the baseline; artifacts via `playwright-report` | https://playwright.dev/docs/test-snapshots ; https://playwright.dev/docs/ci-intro | 2026-09-02 (undated) | high | medium |
| 13 | CLI <= 3.83.x password-protected storefront dev flows stop working 2026-10-01; need >= 3.84 (4.7.x recommended); CLI 4.x needs Node >= 22.12 | https://shopify.dev/changelog/password-protected-shop-dev-flows-on-shopify-theme-cli-v3-83-x-and-older-to-be-deprecated ; npm registry | 2026-08-27 | high | medium |
| 14 | API Terms (2026-02-27) 2.3.24 and Partner Agreement (2026-02-27) 9.15 forbid training or fine-tuning AI on API-derived / merchant data; 2.3.14 forbids systematic automated data collection; credential sharing allowed only with a service provider acting on your behalf; dev stores may process test orders only | https://www.shopify.com/legal/api-terms ; https://www.shopify.com/partners/terms | 2026-02-27 | high | medium |
| 15 | Shopify Dev MCP (`@shopify/dev-mcp` 1.14.7, 2026-08-28) is local, unauthenticated, docs + validation only; CLI 4.7.0 emits a Claude Code plugin hint for the Shopify AI Toolkit | https://shopify.dev/docs/apps/build/devmcp ; npm registry ; https://github.com/Shopify/cli/pull/8193 | 2026-08-28 / 2026-07-31 | medium | low |
| 16 | GitHub theme integration syncs a branch two-way with a theme; since 2026-08-26 commits name the last theme editor; outside collaborators cannot connect | https://shopify.dev/docs/storefronts/themes/tools/github ; https://shopify.dev/changelog | 2026-08-26 | high | low |
| 17 | WebMCP agent tools are live on every Liquid storefront (Chromium origin trial) | https://shopify.dev/changelog/webmcp-liquid-hydrogen | 2026-08-05 | medium | low |
| 18 | GitHub Free org: 2,000 Actions minutes and 500 MB artifacts per month on private repos; $0.006/min Linux beyond | https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions | 2026-09-02 (undated) | high | low |
| 19 | `trekhaakland-devstore.myshopify.com` exists as the Fightclub Connector dev install target; current state unknown | fightclub-connector-backend/README.md:124 (local) | 2026-08-05 (file date) | medium | medium |
