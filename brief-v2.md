# Raderwerk: bewijs dat een AI-gedreven bureau kan draaien

*Every part turns the next.*

Versie 2, 2026-09-02. Vervangt brief.md.

## Doel

Aantonen dat een digitaal bureau echt kan draaien met AI-agents als uitvoerders en één mens bij de poorten. Geen presentatie over agents, maar een bureau dat werk aflevert: repo's die builden, sites die live staan, content die gepubliceerd is, designs die kloppen, advertentie- en socialplannen die je aan een klant zou durven geven. Raderwerk is een generiek bureau (web, design, content, ads, social) en staat volledig los van welke bestaande werkgever of klantrelatie dan ook.

Het bewijs krijgt drie deliverables: (1) de werkende loop met vier klantdossiers erin, (2) een tooling-tabel die per stap laat zien welk model of gereedschap de stap draagt, hoe vaak het faalt en wat het kost, en (3) een slotoverzicht met unit economics per ticketgrootte. De vraag die beantwoord moet worden is niet "kan een agent code schrijven" maar "kan de hele keten van aanvraag tot factuur draaien zonder dat een mens het werk overdoet".

## Het bureau en de vier klanten

Raderwerk heeft vier klanten. Alle vier zijn fictief; het werk dat voor ze gedaan wordt is echt.

1. **DTC e-commercemerk op Shopify met ERP-koppeling.** Levert integratiewerk: orders, voorraad en klantgegevens die tussen de webshop en een ERP heen en weer moeten. Genereert een build-epic plus een staart van synchronisatiebugs. Echt: een Shopify development store, een echte connector-repo met CI, een echte order die doorloopt.
2. **B2B-industriebedrijf met een dealercatalogus op de marketingsite.** Levert scoped bouwwerk (genummerde functionele eisen), een catalogus met filters en een dealer-locator, plus SEO- en contentverzoeken. Echt: een werkende site met een werkende catalogus.
3. **Reis- en boekingssite met CMS plus CRM-sync.** Levert retainerwerk: contentbugs, paginafeatures, en de eigenaardigheden van een CRM-gevoede contentstroom. Echt: een draaiende site met een echte sync.
4. **Raderwerk zelf.** Het bureau is zijn eigen vierde klant: eigen site, eigen content, eigen advertentieplan, eigen socialplan. Dit is tegelijk de etalage van het bewijs.

De klantkant (het bedrijf, de contactpersoon, de briefing, het akkoord, de feedback) wordt gesimuleerd binnen Linear, in comments en documenten. Er gaat geen enkel bericht naar een echt mens buiten het project en er is geen echte klant.

## De loop

1. **Intake.** Een aanvraag van een van de vier klanten landt in Triage van het bureau-team, met bronvermelding en klantlabel.
2. **Scoping.** Een agent leest de thread, stelt vragen bij een ontbrekende spec (en wacht daar ook echt op), schrijft spec, Definition of Done, repo en basisbranch.
3. **Schatting.** Urenbandbreedte plus risico, met een grootte-label S/M/L. Mens keurt scope en prijs goed (gate 1).
4. **Uitvoering.** Worktree, feature-branch, PR met bewijs. Voor niet-code-werk (content, design, ads, social): het artefact zelf plus de bron waaruit het is opgebouwd.
5. **Review.** Dubbele agent-review door een ander model dan de uitvoerder. Mens merget (gate 2).
6. **Oplevering.** Concept-opleverbericht als comment op het issue, gericht aan de gesimuleerde klant. Deploy alleen naar preview, staging of development store.
7. **Facturatie.** De agent stelt uren voor en genereert een factuurdocument. Mens keurt goed (gate 3).
8. **Incidenten.** Triage, hypothese, concept-communicatie. Mens beslist.

Sales (aanvraag, concept-offerte) en growth (SEO-kans, contentplan, advertentieplan) volgen dezelfde vorm met eigen gates.

## Menselijke gates

Vier dingen wachten altijd op een menselijke handeling in Linear: **een offerte versturen**, **mergen en deployen**, **elke uiting richting de klant** (opleverbericht, statusupdate, incidentmelding, publicatie op een publiek kanaal) en **facturatie**. Daarbuiten mogen agents alles afronden: scoping, vragen stellen, schatten, code schrijven, PR's openen, CI draaien, content en designs maken, QA uitvoeren, commentaar geven en statussen wisselen tot aan een gate.

Gates zijn geen afspraak maar een structuur: elke gate is een eigen workflow-state waar alleen een mens uit weg beweegt. Agents krijgen geen productiecredentials; writes gaan naar development- en stagingomgevingen.

## Linear-ontwerp op het Free-plan

Harde grenzen: **2 teams, 250 issues, 10 MB per upload**. Klantverzoeken (customer requests), guests, Asks en Triage Intelligence zitten niet in Free. Wel beschikbaar: initiatives, projects, milestones, cycles, labels en labelgroepen, templates, documenten, project- en initiative-updates, en het agent-platform inclusief delegatie.

**Twee teams.**
- **DELIVERY (key DEL)**: al het klantwerk, ongeacht discipline. Web, design, content, ads, social, QA.
- **BUREAU (key BUR)**: intake, new business, offertes, facturatie, incidenten en de bureau-operatie zelf (proces, templates, kostenlog).

**Workflow DELIVERY**: Triage, Scoping, Wacht op scope-akkoord, Ready, In uitvoering, Agent-review, Wacht op merge, Staging/QA, Wacht op klant-akkoord, Done, plus Blocked, Canceled en Duplicate. Uit elke "Wacht op"-state beweegt alleen een mens.

**Workflow BUREAU**: Inbox, Uitwerken, Wacht op verzendakkoord, Verzonden, Done, plus Blocked en Canceled.

**Initiatives = klant** (vier stuks). **Projects = engagement** binnen een klant, met milestones per fase. Cycles staan aan op DELIVERY voor een weekcadans.

**Labelgroepen**: `klant/*` (vier waarden), `type/*` (bug, feature, content, design, ads, social, seo, incident, lead), `kanaal/*` (web, shop, cms, ads, social), `grootte/*` (S, M, L), `risico/*` (hoog dwingt een extra gate af), `agent/*` (routering naar model of runner), `blokkade/*`, en `bureau/pauze` als kill-switch.

**Templates** (via de GraphQL API, niet via MCP): Bug, Build-taak, Content, Ads/Social, SEO, Incident, Lead/Offerte, plus een projecttemplate Engagement.

**Geen custom velden.** Linear kent ze niet, dus grootte gaat via labels, schatting via het native estimate-veld, en runtime, tokens en supervisieminuten via een vast run-log-blok onderaan elke afsluitende agent-comment:

```
[rol / model] status
Gedaan: ...
Bewijs: <URL>
DoD: 4/4
Run: 7m12s · 412k tokens in / 38k uit · $2,14 · supervisie 3 min
Volgende state: Wacht op merge
```

**Issue-budget.** De 250 issues zijn de schaarste in dit project. Beleid: de bestaande workspace-inhoud gaat er eerst uit, elke klant krijgt een vast budget aan issues, droogloop-runs worden na afloop opgeruimd door het reset-script, en de orchestrator stopt met aanmaken zodra er minder dan 20 issues vrij zijn. Bijlagen groter dan 10 MB gaan niet als upload maar als link naar de repo of de previewomgeving.

De bestaande workspace wordt hernoemd en leeggemaakt: alle bestaande issues, projecten, initiatives en labels mogen weg (bevestigd door de aanvrager). Verwijderen is onomkeerbaar; het reset-script logt wat het weghaalt.

## Orchestratie en modelinzet

Eén headless Claude Code-orchestrator pollt Linear (geen webhook-infrastructuur) en start per issue één run met een vast input-contract (de Linear-velden) en output-contract (artefact, comment, voorgestelde state). Alleen de orchestrator schrijft naar Linear; subagents zien de Linear-tools niet en leveren hun resultaat terug aan de orchestrator.

De orchestrator draait op de persoonlijke API-sleutel van de aanvrager, dus writes verschijnen op zijn naam. Daarom begint elke agent-comment met een rolsignatuur (`[QA / Codex GPT-5.6]`) en staat de rol ook in het `agent/*`-label. Voor Codex en Cursor bestaat er wél een echte identiteit: dat zijn geïnstalleerde Linear-agents die via `issueUpdate(delegateId)` gedelegeerd werk krijgen, naast de menselijke assignee.

Modelinzet: **Fable 5.1** voor scoping, review en oordeelswerk; **Opus 5 en Sonnet 5** voor uitvoering; **Codex GPT-5.6 Sol op xhigh** als tweede reviewer en als tweede dev; **Cursor Grok 4.6** als dev. Parallelle sporen (bijvoorbeeld code en content binnen dezelfde milestone) draaien via multi-agent orchestratie.

Harde regel uit het betrouwbaarheidsonderzoek: een agent draait onbewaakt alleen op werk dat een senior mens in **1 tot 2 uur** af zou hebben en dat een **machinaal controleerbare** DoD heeft. Werk van 4 uur of meer valt terug op ongeveer kop-of-munt bij de eerste poging en krijgt een verify-en-retry-lus met een gate. Werk dat langer duurt wordt eerst opgeknipt door een planner en daarna pas uitgevoerd.

## Echt versus gesimuleerd

**Echt**: de Linear-mutaties, de orchestrator, de repo's onder de GitHub-org `raderwerk`, CI, de PR's, de dubbele review, de code, de sites, de designs, de content, de advertentie- en socialplannen, de Shopify development store, de QA-runs, en het kostenlog.

**Gesimuleerd**: de klanten zelf (bedrijf, contactpersoon, briefing, akkoord, feedback) leven in Linear-comments en -documenten. Offertes en facturen zijn documenten, geen verzonden post. Er is geen betaling, geen advertentiebudget dat echt uitgegeven wordt, en geen deploy naar een klantdomein.

Alles wat gesimuleerd is staat in het eerlijkheidsdocument, per onderdeel benoemd.

## Faalwijzen en afvang

- **Klaar zonder bewijs.** Verplichte DoD-checklist plus artefact-URL in de afsluitende comment; zonder beide blijft het issue in Agent-review staan.
- **De verifier die te snel goedkeurt.** De reviewer is altijd een ander model dan de uitvoerder, en de harde DoD-check draait in CI, niet in de reviewprompt.
- **De gesloten lus.** De agent die de klantrol speelt is niet dezelfde agent (en niet hetzelfde model) als de agent die levert of reviewt.
- **Races.** Eén assignee per issue; de state is het lock.
- **Context-drift.** Repo en basisbranch staan verplicht in het issue; de branchregels staan in de runner-instructie.
- **Kosten en loops.** Er is geen kostenplafond in dit project, maar wel een verplicht kostenlog per run en een dagtotaal. Het label `bureau/pauze` stopt alle runs binnen één poll-interval.
- **Stille integratiefouten.** Writes alleen op development store en staging; nooit op iets wat publiek is.
- **Issue-cap.** Teller bewaken bij elke run; onder 20 vrije issues maakt de orchestrator niets meer aan en meldt hij dat.
- **Ongewilde publicatie.** Publiceren op een publiek kanaal (site, socials) is een gate, ook voor het eigen Raderwerk-materiaal.

## Showcase

De showcase is een live sessie van 45 minuten over twee sporen, zodat modellatentie (2 tot 8 minuten per fase) nooit een leeg scherm oplevert.

- **Spoor 1**: een engagement dat een uur eerder is gestart en bij aanvang in Agent-review staat, op een echte branch met een echte PR.
- **Spoor 2**, live vanaf minuut 3: een nieuwe aanvraag van een van de vier klanten komt binnen in de BUREAU-inbox, wordt gescoped, krijgt een offerte (gate 1), wordt een project met 5 tot 8 issues, gaat in uitvoering met één bewust dubbelzinnige eis, QA keurt af, de dev herstelt, QA keurt goed, mens merget (gate 2), opleverbericht en factuur (gate 3).
- **Incident-drill** als extra scène als er tijd over is.
- **Slot**: de cijfers per run, de tooling-tabel, en het eerlijkheidsdocument.

De echte etalage is niet de sessie maar wat er dan al staat: vier klantdossiers met echte artefacten.

## Meten

Per issue: tokens tegen API-lijstprijs, wall-clock runtime, supervisieminuten, schatting tegen werkelijke runtime, first-pass-acceptatie, aantal reviewrondes. Per engagement: totale kosten en doorlooptijd. Per klant: aantal issues, aantal interventies.

Slotoverzicht: kosten per run, doorlooptijd, interventies, en unit economics per S/M/L tegen het gekozen prijsmodel. Prijsreferenties voor het kostenlog: Fable 5.1 $10 per MTok in en $50 uit met cache-read $0,25; Opus 5 $5/$25; Sonnet 5 $2/$10. Codex loopt binnen het ChatGPT-plan, Cursor Cloud Agents zijn usage-based; beide worden apart genoteerd omdat ze niet per token afrekenen.

Compliance-checklist als bijlage, te toetsen door een jurist, geen blocker: sub-verwerkers Anthropic, OpenAI, xAI en Linear; Fable 5.1 vereist 30 dagen dataretentie en is niet beschikbaar onder zero-data-retention; AI Act artikel 50 (van kracht sinds 2026-08-02) raakt elke publieke AI-gegenereerde uiting en elke bot die met een mens praat; puur AI-gegenereerd werk kent geen auteursrecht, wat betekent dat een bureau niet kan overdragen wat niet bestaat.

## Bouwvolgorde

1. Workspace hernoemen naar Raderwerk, leegmaken, en opnieuw opbouwen: 2 teams, workflows, labelgroepen, templates, 4 initiatives, issue-budget. Dit document komt als Linear-document in BUREAU te staan.
2. Tooling-tabel opzetten (leeg, wordt gevuld door de droogloop-runs).
3. Orchestrator plus rolcontracten bouwen: input-contract, output-contract, run-log-formaat, kill-switch, issue-teller.
4. Klantdossiers uitschrijven (bedrijf, merk, doelgroep, briefing, beginbacklog) en de echte omgevingen inrichten: GitHub-org `raderwerk`, repo's per klant, CI, Shopify development store, hosting en previewomgevingen.
5. Drie droogloop-runs zonder handmatige reparatie.
6. Pas daarna de showcase plannen.

## Buiten scope

Echte klanten, echte uitgaande communicatie naar mensen buiten het project, echt advertentiebudget, deploys naar een klantdomein, betalingen, webhook-infrastructuur, extra Linear-seats of een betaald Linear-plan, en een pilot met betalende klanten (dat is de vervolgstap na een go).

## Aannames

- De Linear MCP en de GraphQL API hangen aan de orchestrator-sessie; subagents zien geen Linear-tools. Alleen de orchestrator schrijft naar Linear.
- Workspace-bootstrapping (teams, workflow-states, templates, labelgroepen) kan niet via MCP en gaat via de GraphQL API met de persoonlijke sleutel.
- Er is geen webhook-infrastructuur; de orchestrator pollt. Default-interval 2 minuten, alleen tijdens actieve runs.
- Codex en Cursor zijn geïnstalleerde Linear-agents en kunnen echt gedelegeerd werk krijgen; Claude draait voorlopig als headless orchestrator zonder eigen Linear-identiteit.
- Agents krijgen geen productiecredentials. Writes gaan naar development store, staging en previewomgevingen.
- Linear-inhoud en klantteksten zijn Nederlands; code, commits, PR's en repo-documentatie zijn Engels.
- Elke LLM-fase kost 2 tot 8 minuten wall-clock; de keten serieel 30 tot 40 minuten, vandaar twee sporen in de showcase.
- Er is geen kostenplafond; kosten worden alleen gelogd. Een run die uit de hand loopt wordt gestopt met `bureau/pauze`, niet met een budgetgrens.
- Juridische punten (AVG, AI Act, auteursrecht) zijn hypotheses ter toetsing, geen advies.
- Deliverables zijn echt werk, geen mock-up. Waar iets niet echt kan (betaling, echte klant, echt advertentiebudget) staat dat in het eerlijkheidsdocument.

## Open vragen (gesorteerd op impact)

1. **Gaat Raderwerk publiek live?** Site op raderwerk.github.io (GitHub Pages; voorlopig geen eigen domein) of raderwerk.github.io (GitHub Pages; voorlopig geen eigen domein), echte socialaccounts, publiek vindbare content, of blijft alles op een privé-preview? Waarom: bepaalt of AI Act artikel 50 (disclosure) en de auteursrechtvraag echt spelen, en of "publiceren" een gate is of een non-issue. Opties: (a) volledig privé, alles op preview-URL's; (b) site live op een van de twee vrije domeinen, socials nog niet; (c) alles live inclusief socials, met AI-disclosure in de footer. Default: (b).

2. **Welke echte infrastructuur wordt aangeschaft en op wiens rekening?** Domeinregistratie, hosting voor drie klantsites, Shopify Partner-account met development store, CI-minuten, en het model-API-verbruik zonder plafond. Waarom: zonder dit kan stap 4 van de bouwvolgorde niet starten en is "echt werk" niet waar te maken.

3. **Hoe blijven we binnen 250 issues?** Onbekend is of het verwijderen van de bestaande ~130 issues ruimte teruggeeft, of dat de teller cumulatief is (`createdIssueCount`). Waarom: als de teller cumulatief is, is het plafond binnen enkele droogloop-runs bereikt. Opties: minder en grotere issues met sub-taken als checklist-items; een tweede gratis workspace voor droogloop-runs; het bewijs beperken tot één engagement per klant. Te testen vóór de bouw.

4. **Wie speelt de klant?** Een aparte agent met een eigen klantpersona per dossier, of de aanvrager zelf? Waarom: een agent die de klant speelt maakt de loop volledig autonoom maar riskeert een gesloten lus waarin het systeem zichzelf beoordeelt; een mens die de klant speelt is eerlijker bewijs maar kost supervisietijd die de unit economics vervuilt.

5. **Blijven de drie andere beheerders in de workspace?** De workspace heeft naast de aanvrager nog drie admins. Waarom: op Free is iedereen admin, dus zij zien en kunnen alles, terwijl Raderwerk expliciet losstaat van de werkgever. Opties: laten staan; suspenden; een nieuwe lege workspace beginnen.

6. **Bouwen we een eigen Raderwerk-agent-app vóór het bewijs, of daarna?** Een OAuth-app met `actor=app` geeft agents een eigen identiteit in Linear (writes niet meer op naam van de aanvrager) en maakt webhook-triggers mogelijk in plaats van polling. Waarom: het raakt de geloofwaardigheid van het bewijs ("wie deed dit nou echt") en de orchestrator-architectuur. Opties: nu bouwen; na de eerste droogloop; helemaal niet, en leunen op gesigneerde comments.

7. **Zijn de betaalde accounts voor Codex en Cursor beschikbaar?** Codex vereist een betaald ChatGPT-plan plus een ingerichte cloudomgeving per repo; Cursor Cloud Agents rekenen usage-based af. Waarom: zonder beide valt de tweede reviewer en de tweede dev weg en draait het bewijs op één leverancier, wat de conclusie zwakker maakt.

8. **Welk prijsmodel komt op het slotoverzicht?** Vast bedrag per S/M/L, uurtarief, of retainer per klant? Waarom: zonder prijs zijn de unit economics alleen kosten en geen marge, en dan zegt het bewijs niets over of dit als bureau kan bestaan.

9. **Wat is de looptijd en de deadline?** Hoeveel weken draait het bureau voordat het bewijs af is, en wanneer staat de showcase? Waarom: bepaalt hoeveel engagements per klant haalbaar zijn en of criterium 2 en 3 realistisch geschaald zijn.

## Succescriteria

1. **Workspace opnieuw opgebouwd**: 2 teams, DELIVERY-workflow met minimaal 3 "Wacht op"-gates, minimaal 6 labelgroepen inclusief `agent/*` en `bureau/pauze`, minimaal 7 templates, 4 initiatives (één per klant) en een vastgelegd issue-budget; beschreven in één Linear-document dat iemand zonder uitleg kan volgen.
2. **Alle vier de klanten hebben minimaal één engagement dat de hele loop heeft doorlopen**, van Triage tot Wacht op klant-akkoord, met in elke state een agent-comment met bewijs (PR-link, testoutput, preview-URL, artefact).
3. **De deliverables zijn echt en klikbaar vanuit Linear**: (a) DTC: een werkende development store plus een connector-repo met groene CI en minimaal één order die end-to-end doorloopt; (b) B2B: een bereikbare marketingsite met een werkende dealercatalogus; (c) reis: een bereikbare boekingssite met een werkende CMS/CRM-sync; (d) Raderwerk: eigen site, minimaal 10 gepubliceerde contentstukken, een advertentieplan en een socialplan.
4. **Elke fase laat een klikbaar artefact achter**: offertedocument, project met minimaal 5 issues met acceptatiecriteria, PR-URL, QA-rapport als comment, opleverbericht als comment, factuurdocument.
5. **De QA-afkeurlus is minstens 3 keer zichtbaar**: afkeur-comment, herstel-commit, goedkeur-comment op hetzelfde issue en dezelfde PR.
6. **0 merges, 0 deploys, 0 verzonden offertes of facturen en 0 publieke publicaties zonder menselijke gate-handeling**, controleerbaar via Linear-history en git log.
7. **100% van de door agents aangeraakte issues** heeft repo, basisbranch, grootte-label, schatting, werkelijke runtime, tokens, supervisieminuten en een afgevinkte DoD-checklist in het run-log-formaat.
8. **Kill-switch getest**: `bureau/pauze` stopt alle lopende runs binnen één poll-interval, gelogd.
9. **3 opeenvolgende droogloop-runs geslaagd zonder handmatige reparatie** vóór de showcase; een reset-script zet workspace, repo's en previewomgevingen binnen 5 minuten terug naar de startstaat en logt wat het verwijdert.
10. **Kosten per volledige run gemeten** en op het slotoverzicht naast doorlooptijd, interventies en unit economics per S/M/L; first-pass-acceptatie over droogloop- en showcase-issues minimaal 70%, mediane supervisietijd per issue gelogd.
11. **Tooling-tabel opgeleverd**: per loop-stap het gekozen model of gereedschap, de faalkans uit de droogloop-runs, en de kosten.
12. **Eerlijkheidsdocument opgeleverd**: elk gesimuleerd onderdeel benoemd, elke agent-comment herleidbaar naar rol en model, en een expliciete conclusie over de hoofdvraag: kan een bureau als dit echt draaien, en waar breekt het.
