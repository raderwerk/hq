# Raderwerk in Linear — ontwerp 1: Linear-native purist

Datum: 2026-09-02. Architect 1 van 3. Hoek: **maximaal native Linear**. Alles wat Linear zelf kan (delegatie aan Codex en Cursor, Linear Agent, skills, agent guidance, templates, initiatives, projects, milestones, cycles, documents, project updates, workflow-state-semantiek, triage) doet Linear. De orchestrator (Claude Code, headless) vult alleen de gaten: pollen, routeren, poortbewaking, budget en de rollen waarvoor geen app-user bestaat.

Harde randen waarbinnen dit ontwerp valt (Free-plan, geverifieerd 2026-09-02):

| Rand | Waarde | Gevolg voor dit ontwerp |
|---|---|---|
| Teams | max 2 | Eén leverteam, één bureauteam. Alle disciplines delen die twee workflows. |
| Issues | max 250 | Issuebudget is een eersteklas ontwerpprobleem (hoofdstuk 8). Documenten, mijlpalen en checklists vervangen sub-issues. |
| Uploads | 10 MB | Beeld en video via externe URL's (repo, preview-deploy), niet als bijlage. |
| Niet beschikbaar | customers/customer requests, guests, Asks, triage rules, Triage Intelligence, SLA's, Loops, coding sessions, private teams | Intake-routering en herhalende jobs zijn orchestrator-code, geen Linear-automatisering. Klantsimulatie loopt via comments en documenten. |
| Wel beschikbaar | initiatives, projects, milestones, cycles, labels, templates, documents, project- en initiative-updates, triage-inbox, agentplatform (delegatie aan app-users), Linear Agent, agent skills, agent guidance | Dit is de gereedschapskist van dit ontwerp. |
| Agent-identiteiten | Codex (GPT-5.6) en Cursor (Grok 4.6) zijn geïnstalleerd als app-user, kosten geen seat, beantwoorden delegatie binnen seconden. Claude heeft géén Linear-agent-app. | Codex en Cursor krijgen echte native rollen (`delegate`). Alle andere rollen draaien onder de orchestrator met de persoonlijke API-key en tekenen hun comments. |

---

## 1. Teams

Twee teams, twee ritmes. Het onderscheid is niet discipline maar **wie de klok zet**: klantwerk loopt op een weekcadans met drie poorten, bureauwerk loopt continu met één poort.

### 1.1 Team RDW — Raderwerk Delivery

| Instelling | Waarde | Waarom |
|---|---|---|
| `name` | Raderwerk Delivery | |
| `key` | RDW | |
| `description` | Al het klantwerk: web, design, content, ads, social. Van aanvraag tot acceptatie. | |
| `icon` / `color` | `Gear` / `#5E6AD2` | |
| `triageEnabled` | `true` | Elke klantaanvraag (gesimuleerd) landt in Triage. Triage is de voordeur, geen backlog. |
| `requirePriorityToLeaveTriage` | `true` | Dwingt de account-agent een prioriteit te zetten; anders komt niets uit Triage. |
| `cyclesEnabled` | `true`, `cycleDuration: 1` week, `cycleStartDay: 1` (maandag), `cycleCooldownTime: 0`, `upcomingCycleCount: 2` | De cycle is het hartslagritme én de WIP-limiet. Agents werken 24/7; de mens niet. De cycle beperkt hoeveel er per week bij de poort kan aankomen. |
| `cycleIssueAutoAssignStarted` | `true` | Issue dat in uitvoering gaat en geen cycle heeft, rolt automatisch in de actieve cycle. |
| `issueEstimationType` | `tShirt` | XS/S/M/L/XL is tegelijk de ticketgrootte voor de unit economics én het agentbudget (zie 1.3). Linear heeft geen custom fields; de schattingsschaal is het enige native numerieke veld dat we hebben. |
| `issueEstimationAllowZero` | `false` | Geen ongeschat werk in uitvoering. |
| `issueEstimationExtended` | `false` | XS t/m XL is genoeg; XXL bestaat niet omdat XL al "opknippen" betekent. |
| `defaultIssueEstimate` | `S` | |
| `initiativesEnabled` | `true` | |
| `autoArchivePeriod` | 3 maanden | Houdt de views schoon. Let op: archiveren geeft géén issuebudget terug (hoofdstuk 8). |
| `autoClosePeriod` | uit | Niets sluit vanzelf; alleen een poort of een mens sluit werk. |
| `defaultTemplateForMembersId` | template `Klantaanvraag (intake)` | Alles wat in Triage gemaakt wordt, krijgt automatisch de intake-structuur. |

**Workflowstates (volgorde zoals Linear ze toont: backlog → unstarted → started → completed → canceled).** Conventie: **elke poort is geel (`#F2C94C`)**. Geel op het bord betekent altijd en overal: hier staat de machine stil tot een mens iets zegt.

| # | State | Type | Kleur | Betekenis | Wie haalt het eruit |
|---|---|---|---|---|---|
| 1 | Triage | `triage` | `#F2994A` | Nieuwe aanvraag, ongesorteerd, nog geen klant/dienst/prioriteit. | Account-agent |
| 2 | Backlog | `backlog` | `#BEC2C8` | Geaccepteerd, nog niet gescoopt. Geen belofte aan de klant. | PM-agent |
| 3 | Scoping | `backlog` | `#95A2B3` | Agent schrijft spec, DoD, schatting, risico. Nog niet verkocht. | Strateeg/PM-agent |
| 4 | **Wacht op scope-akkoord** | `backlog` | `#F2C94C` | **POORT 1.** Scope, schatting en prijs liggen klaar. | **Mens** |
| 5 | Ready | `unstarted` | `#E2E2E2` | Verkocht en geschat, wacht op capaciteit/cycle. | PM-agent of orchestrator |
| 6 | In uitvoering | `started` | `#5E6AD2` | Gedelegeerd aan een agent (`delegate` gezet) of in behandeling door een orchestrator-rol. | Uitvoerende agent |
| 7 | In kruisreview | `started` | `#26B5CE` | Tweede agent leest tegen: code, tekst, design, campagne. Nooit dezelfde agent als de maker. | Reviewer-agent |
| 8 | **Wacht op oplevering** | `started` | `#F2C94C` | **POORT 2.** Merge, publicatie, deploy, of "artefact mag naar de klant". | **Mens** |
| 9 | Klantacceptatie | `started` | `#8B7CF6` | Bij de (gesimuleerde) klant ter goedkeuring; klantrol schrijft het antwoord als comment. | Mens in klantrol |
| 10 | Geblokkeerd | `started` | `#EB5757` | Werk staat stil op een externe afhankelijkheid of ontbrekend antwoord. Verplicht: reden-comment. | Wie de blokkade opheft |
| 11 | Done | `completed` | `#4CB782` | DoD afgevinkt, bewijs aanwezig, klant akkoord. | — |
| 12 | Canceled | `canceled` | `#95A2B3` | Vervallen. Reden verplicht in comment. | — |
| 13 | Duplicate | `canceled` | `#95A2B3` | Met `issueRelationCreate(type: duplicate)` gekoppeld. | — |

Waarom Scoping en poort 1 `backlog`-type zijn: vóór het scope-akkoord is er geen verplichting. Linear rekent `started` mee als werk in uitvoering; ongeschat, onverkocht werk hoort daar niet. Bijkomend voordeel: de bordvolgorde klopt met de werkelijke flow zonder trucs.

Poort 3 (facturatie) heeft in RDW **geen eigen state**: een gefactureerd klantwerk-issue is klaar. De factuurgoedkeuring leeft als apart issue in BUR (`type/factuur`), gekoppeld met `issueRelationCreate(type: related)`. Reden: één factuur dekt meestal meerdere issues; een state per issue zou liegen.

### 1.2 Team BUR — Raderwerk Bureau

| Instelling | Waarde | Waarom |
|---|---|---|
| `name` | Raderwerk Bureau | |
| `key` | BUR | |
| `description` | Het bureau zelf: sales, offertes, facturatie, eigen merk, handboek, betrouwbaarheid, incidenten. | |
| `icon` / `color` | `Building` / `#0F7488` | |
| `triageEnabled` | `true` | Inbound leads en eigen ideeën landen hier; geen aparte intakelijst nodig. |
| `requirePriorityToLeaveTriage` | `true` | |
| `cyclesEnabled` | `false` | Bureauwerk is continu (offerte volgt lead, factuur volgt oplevering). Cycles zouden hier alleen ruis geven. |
| `issueEstimationType` | `tShirt`, default `S`, geen nul | Eén schattingstaal in de hele workspace. |
| `initiativesEnabled` | `true` | |
| `autoArchivePeriod` | 6 maanden | |
| `defaultTemplateForMembersId` | template `Bureau-taak` | |

**Workflowstates BUR.** Eén poort, maar met een scherpe definitie: **"Wacht op vrijgave" betekent altijd: er gaat iets het pand uit.** Een offerte, een factuur, een gepubliceerd artikel, een live advertentie, een social post, een klantbericht. Welk soort vrijgave het is, staat in het `gate/*`-label.

| # | State | Type | Kleur | Betekenis | Wie haalt het eruit |
|---|---|---|---|---|---|
| 1 | Triage | `triage` | `#F2994A` | Nieuwe lead, idee of signaal. | Account-/strateeg-agent |
| 2 | Backlog | `backlog` | `#BEC2C8` | Erkend, nog niet opgepakt. | PM-agent |
| 3 | Kwalificatie & scope | `backlog` | `#95A2B3` | Lead uitzoeken, of bureau-taak scopen. | Strateeg-agent |
| 4 | Ready | `unstarted` | `#E2E2E2` | Klaar om uitgevoerd te worden. | Orchestrator |
| 5 | In uitvoering | `started` | `#5E6AD2` | Agent maakt het artefact (offerte, factuur, artikel, campagne). | Uitvoerende agent |
| 6 | In review | `started` | `#26B5CE` | Tweede agent leest tegen (inhoud, cijfers, juridisch). | Reviewer-agent |
| 7 | **Wacht op vrijgave** | `started` | `#F2C94C` | **POORT.** Er gaat iets naar buiten. Label zegt wat. | **Mens** |
| 8 | Live / verzonden | `started` | `#B59CD9` | Vrijgegeven en draaiend; meetvenster loopt (advertentie live, offerte verstuurd, factuur open). | Agent na meetvenster |
| 9 | Geblokkeerd | `started` | `#EB5757` | Wacht op iets externs. | — |
| 10 | Afgerond | `completed` | `#4CB782` | Gewonnen, betaald, gepubliceerd en gemeten. | — |
| 11 | Verloren | `canceled` | `#F2994A` | Lead verloren of voorstel afgewezen. Reden verplicht. | — |
| 12 | Canceled | `canceled` | `#95A2B3` | | — |

### 1.3 Schattingsschaal als besturingsinstrument

De t-shirt-schaal is bewust overladen: hij is tegelijk grootte, budgetplafond en autonomiegrens. Dit staat in `06 — Definition of Done per dienst` en wordt door de orchestrator hard afgedwongen.

| Estimate | Agent-wandkloktijd | Kostenplafond per issue | Richtprijs klant | Autonomie |
|---|---|---|---|---|
| XS | ≤ 15 min | $1 | € 60 | Mag door één agent zonder kruisreview, mits `risico/laag`. |
| S | ≤ 1 uur | $3 | € 125 | Kruisreview verplicht. |
| M | ≤ 3 uur | $10 | € 375 | Kruisreview + expliciete DoD-bewijsregel. |
| L | ≤ 8 uur | $30 | € 1.000 | Twee reviewers; verplicht opgeknipt in mijlpalen. |
| XL | — | — | — | **Bestaat niet als uitvoerbaar issue.** XL = terug naar Scoping en opknippen. De orchestrator weigert een XL te delegeren. |

Bij overschrijding van het plafond: orchestrator zet `ops/budget-overschreden`, verplaatst naar Geblokkeerd, en schrijft een comment met de tellerstand. Geen automatische verhoging.

---

## 2. Labeltaxonomie

Alle labels zijn **workspace-labels** (`issueLabelCreate` zonder `teamId`), zodat beide teams dezelfde taal spreken. Groepen zijn labels met `isGroup: true`; kinderen hangen eronder met `parentId`. Binnen een groep kan één label tegelijk (Linear dwingt dat af bij groepen), wat precies de gewenste discipline geeft: één klant, één dienst, één type, één risico.

### 2.1 `klant` — `#5E6AD2`

| Label | Betekenis |
|---|---|
| `klant/duinbrand` | Duinbrand Coffee (DTC e-commerce, Shopify + ERP) |
| `klant/hovex` | Hovex Aandrijvingen (B2B industrie, dealercatalogus) |
| `klant/wildernest` | Wildernest Reizen (travel/booking, CMS + CRM) |
| `klant/raderwerk` | Eigen merk |
| `klant/prospect` | Nog geen klant; lead in kwalificatie |
| `klant/geen` | Bureauwerk zonder klant (handboek, evals, infrastructuur) |

### 2.2 `dienst` — `#26B5CE`

`dienst/web` · `dienst/design` · `dienst/content` · `dienst/ads` · `dienst/social` · `dienst/strategie`

Dit is de dienstenlijn waarop gerapporteerd en gefactureerd wordt. Eén per issue. Een issue dat twee diensten raakt, is te groot.

### 2.3 `type` — `#4CB782`

`type/bug` · `type/feature` · `type/contentstuk` · `type/designtaak` · `type/campagne` · `type/socialkalender` · `type/lead` · `type/offerte` · `type/qa-rapport` · `type/incident` · `type/onderzoek` · `type/onderhoud` · `type/factuur`

Eén type per issue, en het type bepaalt welk issue-template gebruikt is. De orchestrator gebruikt dit veld om het juiste rolcontract te kiezen.

### 2.4 `gate` — `#F2C94C`

| Label | Betekenis | Team |
|---|---|---|
| `gate/scope` | Wacht op akkoord op scope, schatting en prijs | RDW |
| `gate/oplevering` | Wacht op akkoord om te mergen, te deployen of op te leveren | RDW |
| `gate/klant` | Wacht op acceptatie door de (gesimuleerde) klant | RDW |
| `gate/vrijgave-offerte` | Offerte mag verstuurd worden | BUR |
| `gate/vrijgave-publicatie` | Content, advertentie of post mag live | BUR + RDW |
| `gate/vrijgave-factuur` | Factuur mag verstuurd worden | BUR |
| `gate/afgekeurd` | Laatste poortpassage was een afkeuring; staat aan tot de herstelronde weer bij de poort komt | beide |
| `gate/tweede-paar-ogen` | Dit issue vereist twee verschillende menselijke goedkeuringen (automatisch gezet bij `risico/hoog`) | beide |

### 2.5 `risico` — `#EB5757`

| Label | Betekenis | Gevolg |
|---|---|---|
| `risico/laag` | Omkeerbaar, intern, geen publiek effect | XS mag zonder kruisreview |
| `risico/midden` | Standaard klantwerk | Normale poorten |
| `risico/hoog` | Onomkeerbaar, publiek, of raakt geld/data | Orchestrator zet automatisch `gate/tweede-paar-ogen`; twee reviewers; het akkoord-token moet het woord `RISICO-GEZIEN` bevatten |
| `risico/klantdata` | Er komt (fictieve) persoonsdata bij kijken | Geen echte persoonsgegevens; check door compliance-rol |
| `risico/juridisch` | AI Act-disclosure, IP, claims in reclame | Compliance-rol verplicht in de keten |
| `risico/merk` | Publieke uiting op naam van Raderwerk of een klant | Strateeg + mens vóór publicatie |

### 2.6 `agent` — `#B59CD9` (routering van rollen zonder eigen app-user)

`agent/account` · `agent/strateeg` · `agent/pm` · `agent/designer` · `agent/dev` · `agent/reviewer` · `agent/content` · `agent/ads` · `agent/social` · `agent/qa` · `agent/finops` · `agent/compliance`

Belangrijk onderscheid, en de kern van de purist-hoek: **voor Codex en Cursor gebruiken we géén label maar het native `delegate`-veld.** Het `agent/*`-label bestaat alleen voor rollen die onder de orchestrator draaien en dus geen eigen identiteit in Linear hebben. Zodra Anthropic een Linear-agent-app levert, verdwijnen de labels `agent/dev`, `agent/reviewer` en `agent/qa` ten gunste van echte delegatie.

### 2.7 `model` — `#95A2B3` (alleen als override)

`model/fable51` · `model/opus5` · `model/sonnet5` · `model/codex-gpt56` · `model/cursor-grok46`

Leeg laten is normaal: het rolcontract bepaalt het model. Dit label zet je alleen om af te wijken, bijvoorbeeld om twee modellen op hetzelfde soort werk te vergelijken in het kostenboek.

### 2.8 `ops` — `#F2994A` (besturing en noodrem)

| Label | Betekenis |
|---|---|
| `ops/pauze` | **Noodrem.** Op een issue: de orchestrator raakt dit issue niet aan. Op het gepinde issue `BUR — Noodstop`: de orchestrator stopt *alle* runs binnen één pollcyclus (≤ 2 min) en schrijft één haltcomment. |
| `ops/mens-vereist` | Ook als het beleid autonomie toestaat, moet hier een mens langs |
| `ops/budget-overschreden` | Kostenplafond geraakt; werk staat stil |
| `ops/droogloop` | Onderdeel van een droogloop-run; telt niet mee in de echte cijfers |
| `ops/opruimen` | Mag verwijderd worden bij de eerstvolgende budgetronde (hoofdstuk 8) |

### 2.9 `billing` — `#0F7488`

`billing/fixed` · `billing/nacalculatie` · `billing/retainer` · `billing/intern` · `billing/gefactureerd` · `billing/niet-factureerbaar`

`billing/niet-factureerbaar` is met opzet aanwezig: herstelwerk na een eigen fout wordt zo zichtbaar en telt mee in de first-pass-acceptatie.

### 2.10 `bron` — `#BEC2C8`

`bron/klant` · `bron/agent` · `bron/scan` · `bron/intern`

`bron/agent` markeert issues die een agent zelf heeft aangemaakt. Dat is de teller waarmee we zien of de machine zichzelf opblaast tegen het issueplafond.

### 2.11 Projectlabels (aparte namespace)

`projectLabelCreate` bestaat wel, `projectLabelDelete` niet. De zes bestaande projectlabels in de workspace worden daarom **hernoemd** in plaats van verwijderd:

| Bestaand | Wordt |
|---|---|
| Shopify | Shopify |
| Concrete CMS | CMS |
| Framer | Site |
| Custom | Integratie |
| Internal | Intern |
| VWO | Retainer |

Nieuw aan te maken: `Content`, `Ads`, `Social`, `Merk`.

---

## 3. Initiatives, projects en mijlpalen

### 3.1 Wat een initiative is

**Initiative = account.** Eén initiative per (fictieve) klant, plus één voor het bureau-apparaat zelf. Reden: het is het enige native niveau boven projecten, en een klant heeft altijd meerdere gelijktijdige engagements (bouw, retainer, groei). De initiative-update (`initiativeUpdateCreate`, met `health: onTrack | atRisk | offTrack`) is het native accountreview: elke vrijdag schrijft de PM-agent er één, met de gezondheid van het account, wat er die week is opgeleverd en wat er bij de poort wacht.

| Initiative | Owner | Status | Betekenis |
|---|---|---|---|
| **Duinbrand Coffee** | mens | Active | Account: DTC-koffiemerk |
| **Hovex Aandrijvingen** | mens | Active | Account: B2B-industrie |
| **Wildernest Reizen** | mens | Active | Account: reisorganisatie |
| **Raderwerk — eigen merk** | mens | Active | Het bureau als eigen klant: site, content, ads, social |
| **Raderwerk OS** | mens | Active | De machine: handboek, rolcontracten, poortbeleid, kostenboek, betrouwbaarheid |

### 3.2 Projecten en mijlpalen

Projecten zijn engagements. Ze kosten geen issuebudget, dus mag je er royaal mee zijn: **liever een extra project met vier mijlpalen dan een parent-issue met tien sub-issues.** Elk project krijgt een lead (mens), een `description` van één zin, een `content` (markdown) met doel, scope, buiten-scope, DoD en dienstenlijnen, en een projectlabel.

| Project | Team | Initiative | Doel (één zin) | Mijlpalen |
|---|---|---|---|---|
| Duinbrand — Storefront & abonnementen | RDW | Duinbrand | Een werkende Shopify-storefront met abonnementsflow op een preview-URL. | M1 Fundament · M2 Abonnementen · M3 Contentlaag · M4 Preview-oplevering |
| Duinbrand — ERP-koppeling | RDW | Duinbrand | Voorraad en orders synchroniseren tussen shop en ERP, idempotent en meetbaar. | M1 Contract & mapping · M2 Voorraadsync · M3 Ordersync · M4 Monitoring |
| Duinbrand — Groei Q4 | RDW | Duinbrand | Content, advertenties en social die de abonnementspropositie verkopen. | M1 Plan · M2 Productie · M3 Publicatiegereed |
| Hovex — Site & dealercatalogus | RDW | Hovex | Een marketingsite met doorzoekbare dealercatalogus en locator. | M1 IA & design · M2 Catalogus · M3 Locator & filters · M4 Opleverpreview |
| Hovex — Kennisbank & SEO | RDW | Hovex | Technische autoriteit opbouwen met kennisartikelen en schone gestructureerde data. | M1 Onderzoek · M2 Productie · M3 Techniek |
| Wildernest — Site & aanvraagflow | RDW | Wildernest | Reizen tonen en boekingsaanvragen betrouwbaar naar het CRM krijgen. | M1 Datamodel · M2 Reispagina's · M3 Aanvraagflow · M4 CRM-sync |
| Wildernest — Contentmotor & e-mail | RDW | Wildernest | Verhalen, e-mailflow en seizoenskalender die aanvragen opleveren. | M1 Verhalen · M2 E-mailflow · M3 Kalender |
| Raderwerk — merk & site v1 | RDW | Eigen merk | Een eigen site die laat zien hoe het bureau werkt, inclusief poorten. | M1 Identiteit · M2 Site · M3 Transparantiepagina's |
| Raderwerk — eigen marketing | RDW | Eigen merk | Zes weken content, social en een advertentieplan voor het eigen merk. | M1 Contentplan · M2 Productie · M3 Publicatiegereed |
| Raderwerk OS — bureauhandboek | BUR | Raderwerk OS | Eén plek waar staat hoe het bureau werkt; alle playbooks hangen hier. | M1 Kernbeleid · M2 Rolcontracten · M3 Dienst-DoD |
| Raderwerk OS — sales & offertes | BUR | Raderwerk OS | Van lead tot verstuurde offerte, met één poort. | M1 Pijplijn · M2 Offertemodel · M3 Prijskaart |
| Raderwerk OS — financiën | BUR | Raderwerk OS | Kostenboek, facturen en unit economics per ticketgrootte. | M1 Kostenboek · M2 Factuurmodel · M3 Unit economics |
| Raderwerk OS — betrouwbaarheid | BUR | Raderwerk OS | Evals, droogloopruns, incidenten en de noodrem, aantoonbaar getest. | M1 Evalset · M2 Droogloop · M3 Incidentdrill |

Projectstatus-updates (`projectUpdateCreate`) zijn verplicht: elke vrijdag 16:00 schrijft de PM-agent per actief project een update met `health`, drie regels voortgang, wat er bij de poort ligt en de kosten van die week. Dat is de native vervanging van een statusmail.

---

## 4. Templates

Templates zijn op Free volledig beschikbaar en worden via `templateCreate(type, teamId, name, templateData)` gemaakt. **Let op:** `templateData` is een ondocumenteerd JSON-veld. Werkwijze: maak eerst met de hand één issue-template, één projecttemplate en één documenttemplate in de UI, lees hun `templateData` uit met de `template(id)`-query, en gebruik exact die JSON-vorm als mal voor de rest. Nooit blind construeren.

Alle templates krijgen `teamId` toegewezen behalve de klantcommunicatie-documenttemplates (die zijn workspace-breed).

### 4.1 `Klantaanvraag (intake)` — RDW, defaulttemplate voor Triage

Preset: state `Triage`, labels `bron/klant`, `risico/midden`, estimate leeg, prioriteit leeg.

```markdown
## Wat vraagt de klant
<letterlijke vraag, zonder interpretatie>

## Waar
Klant: <klant> · Dienst: <web/design/content/ads/social/strategie>
URL / pagina / repo: <link>
Rol van de melder: <bezoeker / beheerder / medewerker>

## Huidig gedrag
<wat er nu gebeurt>

## Verwacht gedrag
<wat er zou moeten gebeuren>

## Nog onbekend
- [ ] <vraag 1>
- [ ] <vraag 2>

## Definition of Done (intake)
- [ ] Klantlabel, dienstlabel, typelabel en risicolabel gezet
- [ ] Prioriteit gezet (verplicht om Triage te verlaten)
- [ ] Aan een project en mijlpaal gekoppeld, of bewust in Backlog geplaatst
- [ ] Ontbrekende informatie staat als open vraag in dit issue, niet als aanname
```

### 4.2 `Bug` — RDW

Preset: labels `type/bug`, `dienst/web`, estimate `S`, prioriteit High.

```markdown
## Symptoom
<één zin: wat is er kapot, voor wie>

## Reproductie
1. <stap>
2. <stap>
3. <verwacht vs werkelijk>

Omgeving: <preview-URL / browser / apparaat / datum>

## Reikwijdte
Geraakte pagina's/flows: <lijst>
Sinds: <commit, deploy of datum>

## Oorzaak (in te vullen door de dev-agent)
<één alinea, met bestand:regel>

## Definition of Done
- [ ] Reproductie vóór de fix vastgelegd (screenshot of testoutput)
- [ ] Fix in een PR met een test die zonder de fix faalt
- [ ] Kruisreview afgerond en akkoord
- [ ] Bewijs ná de fix in dit issue (screenshot of testoutput)
- [ ] Geen nieuwe console- of buildwaarschuwingen
- [ ] Regressierisico benoemd of expliciet nihil verklaard
```

### 4.3 `Feature` — RDW

Preset: labels `type/feature`, estimate `M`.

```markdown
## Doel
<welk probleem lost dit op, voor wie, waarom nu>

## Acceptatiecriteria
- [ ] <toetsbaar criterium 1>
- [ ] <toetsbaar criterium 2>
- [ ] <toetsbaar criterium 3>

## Buiten scope
- <expliciet niet>

## Technisch kader
Repo: <github.com/raderwerk/...> · Basisbranch: <main> · Branch: <feature/...>
Afhankelijkheden: <lijst of "geen">

## Definition of Done
- [ ] Alle acceptatiecriteria aantoonbaar gehaald (link per criterium)
- [ ] PR geopend met beschrijving, screenshots of testoutput
- [ ] CI groen (lint, build, tests, performancebudget)
- [ ] Kruisreview door een andere agent, bevindingen verwerkt of beargumenteerd afgewezen
- [ ] Toegankelijkheid: toetsenbordpad en contrast gecontroleerd
- [ ] Preview-URL in dit issue
- [ ] Documentatie of README bijgewerkt als het gedrag verandert
```

### 4.4 `Contentstuk` — RDW

Preset: labels `type/contentstuk`, `dienst/content`, estimate `S`.

```markdown
## Opdracht
Titel (werktitel): <...>
Doelgroep: <...> · Zoekintentie: <...> · Doel: <informeren / converteren / autoriteit>
Kanaal: <blog / landingspagina / kennisbank> · Lengte: <woorden>

## Inhoudelijke eisen
- Kernboodschap: <één zin>
- Verplichte onderwerpen: <lijst>
- Verboden claims: <lijst>
- Bronnen: <lijst met URL's>

## SEO
Hoofdzoekterm: <...> · Nevenzoektermen: <...>
Meta titel (≤ 60 tekens): <...> · Meta omschrijving (≤ 155 tekens): <...>
Interne links naar: <lijst>

## Definition of Done
- [ ] Tekst voldoet aan de merkgids (toon, aanspreekvorm, geen holle superlatieven)
- [ ] Elke feitelijke claim heeft een bron of is verwijderd
- [ ] Unieke H1, koppenstructuur logisch, alt-teksten op alle beelden
- [ ] Meta titel en omschrijving binnen de tekenlimiet
- [ ] Kruisreview op feiten en toon door een tweede agent
- [ ] AI-disclosure toegepast waar het beleid dat eist (zie `04 — Klantcommunicatiebeleid`)
- [ ] Tekst staat als bestand in de repo, niet alleen in Linear
```

### 4.5 `Designtaak` — RDW

Preset: labels `type/designtaak`, `dienst/design`, estimate `M`.

```markdown
## Ontwerpvraag
<wat moet er ontworpen worden, voor welk scherm/moment>

## Kader
Merk: <klant> · Bestaande tokens: <link> · Breekpunten: 375 / 768 / 1280 / 1600
Referenties: <links> · Nadrukkelijk niet: <links>

## Te leveren
- [ ] <component / pagina / staat>
- [ ] Lege staat, laadstaat en foutstaat
- [ ] Mobiel en desktop

## Definition of Done
- [ ] Ontwerp is geïmplementeerd of als code-prototype opgeleverd (geen losse plaatjes)
- [ ] Alle tekstcontrasten ≥ 4.5:1 (grote tekst ≥ 3:1), aantoonbaar gemeten
- [ ] Focusstaten zichtbaar en toetsenbordpad compleet
- [ ] Geen horizontale scroll op 375px
- [ ] Tokens hergebruikt, geen losse hexwaarden in componenten
- [ ] Screenshots van alle staten in dit issue
- [ ] Kruisreview door een tweede agent op merkconsistentie
```

### 4.6 `Campagne` — RDW/BUR

Preset: labels `type/campagne`, `dienst/ads`, estimate `M`, `risico/merk`.

```markdown
## Campagne
Klant: <...> · Periode: <van–tot> · Kanaal: <search / social / display>
Doel: <verkoop / leads / bereik> · KPI: <getal + eenheid>
Budget (fictief): € <...> · Verdeling: <per kanaal/doelgroep>

## Doelgroepen
1. <naam> — <omschrijving> — <boodschap>
2. ...

## Advertenties
| # | Kop | Tekst | CTA | Landingspagina |
|---|---|---|---|---|

## Meetplan
Events: <lijst> · Rapportageritme: <wekelijks> · Beslisregel: <wanneer stoppen/opschalen>

## Definition of Done
- [ ] Minimaal 3 doelgroepen met eigen boodschap
- [ ] Minimaal 9 advertentievarianten, geen dubbele koppen
- [ ] Elke claim juridisch houdbaar (geen superlatieven zonder bron)
- [ ] Landingspagina per advertentie bestaat en is gecontroleerd
- [ ] Meetplan met één expliciete stopregel
- [ ] Geen live uitgaven: dit is een plan tot een mens de poort opent
- [ ] Kruisreview door strateeg-rol
```

### 4.7 `Socialkalender` — RDW/BUR

Preset: labels `type/socialkalender`, `dienst/social`, estimate `M`.

```markdown
## Kalender
Klant: <...> · Maand: <...> · Kanalen: <LinkedIn / Instagram / ...>
Ritme: <x posts per week> · Thema's: <lijst>

## Posts
| Datum | Kanaal | Format | Haakje | Tekst | Asset-brief | CTA |
|---|---|---|---|---|---|---|

## Definition of Done
- [ ] Elke post heeft haakje, tekst, CTA en een concrete asset-brief
- [ ] Minimaal 3 verschillende formats
- [ ] Geen post noemt bestaande personen of echte klanten van derden
- [ ] Hashtag- en taalgebruik volgens merkgids
- [ ] AI-disclosure waar het beleid dat eist
- [ ] Kalender staat als bestand in de repo én als document aan het project
- [ ] Kruisreview op toon en juridische houdbaarheid
```

### 4.8 `Lead` — BUR

Preset: labels `type/lead`, `klant/prospect`, `dienst/strategie`, state `Triage`, estimate `XS`.

```markdown
## Lead
Bedrijf (fictief): <...> · Sector: <...> · Omvang: <...>
Aanleiding: <hoe kwam dit binnen>
Vraag in eigen woorden: <...>

## Kwalificatie
- Past bij ons aanbod: <ja/nee, waarom>
- Urgentie: <...> · Budgetindicatie: <...> · Beslismoment: <...>
- Risico's: <...>

## Voorstelrichting
Diensten: <web/design/content/ads/social> · Grofweg: <S/M/L> · Bandbreedte: € <...>

## Definition of Done
- [ ] Kwalificatie compleet ingevuld, geen aannames zonder markering
- [ ] Go/no-go met één zin motivering
- [ ] Bij go: offerte-issue aangemaakt en gekoppeld (`related`)
- [ ] Bij no-go: state Verloren met reden
- [ ] Geen contact met echte personen of bedrijven
```

### 4.9 `Offerte` — BUR

Preset: labels `type/offerte`, estimate `S`, `risico/hoog`, `gate/vrijgave-offerte`.

```markdown
## Offerte
Klant: <...> · Aanleiding: <link naar lead-issue>
Geldig tot: <datum> · Prijsmodel: <fixed / nacalculatie / retainer>

## Scope
Wel: <lijst> · Niet: <lijst> · Aannames: <lijst>

## Opbouw
| Onderdeel | Grootte | Prijs |
|---|---|---|
| | | |
Totaal excl. btw: € <...>

## Voorwaarden
Doorlooptijd: <...> · Betaling: <...> · Meerwerk: <...>
AI-inzet: <verplichte transparantiezin, zie klantcommunicatiebeleid>

## Definition of Done
- [ ] Elke regel herleidbaar naar een geschat issue of een expliciete aanname
- [ ] Prijs volgt de prijskaart, of afwijking is gemotiveerd
- [ ] Transparantiezin over AI-inzet aanwezig
- [ ] Offertedocument aangemaakt en aan dit issue gekoppeld
- [ ] Kruisreview op cijfers door de finops-rol
- [ ] Bij `RISICO-GEZIEN`-akkoord: verstuurd (gesimuleerd) en state Live/verzonden
```

### 4.10 `QA-rapport` — RDW

Preset: labels `type/qa-rapport`, estimate `S`.

```markdown
## Getest
Issue(s): <links> · Preview-URL: <...> · Commit: <sha> · Datum/tijd: <...>
Testomgeving: <browser, viewport, apparaat>

## Uitkomst
Oordeel: **GOEDGEKEURD** / **AFGEKEURD**

## Acceptatiecriteria
| # | Criterium | Uitkomst | Bewijs |
|---|---|---|---|

## Bevindingen
| Ernst | Bevinding | Waar | Bewijs |
|---|---|---|---|
(blocker / groot / klein / nit)

## Definition of Done
- [ ] Elk acceptatiecriterium afzonderlijk getoetst met bewijs (screenshot, testoutput of log)
- [ ] Randgevallen getest: leeg, maximaal, fout, traag
- [ ] Toetsenbordpad en contrast gecontroleerd
- [ ] Mobiel (375px) en desktop (1280px) gecontroleerd
- [ ] Geen console-fouten
- [ ] Bij afkeuring: elk punt is reproduceerbaar beschreven
```

### 4.11 `Incident` — BUR/RDW

Preset: labels `type/incident`, prioriteit Urgent, `risico/hoog`, estimate `S`.

```markdown
## Incident
Wat is er stuk: <één zin> · Sinds: <tijd> · Impact: <wie merkt wat>
Ontdekt door: <agent/mens/monitor>

## Tijdlijn
| Tijd | Gebeurtenis |
|---|---|

## Hypothese en verificatie
Hypothese: <...>
Weerlegd/bevestigd door: <bewijs>

## Herstel
Directe actie: <...> · Terugdraaien mogelijk: <ja/nee, hoe>

## Definition of Done
- [ ] Tijdlijn compleet van eerste signaal tot herstel
- [ ] Oorzaak bewezen, niet vermoed
- [ ] Herstel geverifieerd met bewijs
- [ ] Preventiemaatregel als apart issue aangemaakt en gekoppeld
- [ ] Klantbericht als concept klaar (verzenden pas na poort)
- [ ] Kosten en duur van het incident in het kostenboek
```

### 4.12 `Bureau-taak` — BUR, defaulttemplate

```markdown
## Wat
<één zin>

## Waarom nu
<één zin>

## Te leveren
- [ ] <artefact>

## Definition of Done
- [ ] Artefact bestaat op de afgesproken plek (document, repo of issue)
- [ ] Kruisreview door een tweede rol
- [ ] Handboek bijgewerkt als dit de werkwijze verandert
```

### 4.13 Projecttemplate `Klantengagement`

`templateCreate(type: "project")` met vaste mijlpaalstructuur en een `content`-skelet:

```markdown
## Doel
<één zin: welk resultaat is dit engagement>

## Scope
Wel: <lijst>
Niet: <lijst>

## Dienstenlijnen
<web / design / content / ads / social / strategie>

## Werkafspraken
Repo(s): <github.com/raderwerk/...> · Basisbranch: main · Preview: <URL>
Poorten: scope-akkoord, oplevering, klantacceptatie
Ritme: weekcycle, projectupdate elke vrijdag 16:00

## Definition of Done (project)
- [ ] Alle mijlpalen afgerond
- [ ] Alle issues Done of expliciet naar een volgend engagement verplaatst
- [ ] Accountdossier bijgewerkt
- [ ] Kostenboek geactualiseerd en unit economics per ticketgrootte berekend
- [ ] Afsluitende projectupdate met health en geleerde lessen
```

Mijlpalen die de template altijd aanmaakt: `M1 Fundament`, `M2 Kern`, `M3 Afronding`, `M4 Oplevering`. De PM-agent hernoemt ze per engagement.

### 4.14 Documenttemplates

| Template | Type | Waar | Skelet |
|---|---|---|---|
| `Accountdossier` | document | Aan elk klantproject | Merk, toon, doelgroep, stack, repo's, contactregels, DoD-afwijkingen, verboden claims, openstaande vragen |
| `Klantbericht (concept)` | document | Aan het issue | Aanhef, aanleiding, wat er is gedaan, wat de klant moet doen, planning, transparantiezin over AI, afsluiting. Eén alinea per blok, geen handmatige regelafbrekingen |
| `Offerte` | document | Aan het offerte-issue | Zie 4.9, uitgeschreven als klantdocument |
| `QA-bewijsbundel` | document | Aan het issue | Screenshots-links, testoutput, meetwaarden |
| `Weekrapport` | document | Aan het project `Raderwerk OS — financiën` | Kosten, doorlooptijd, poortdoorvoer, first-pass-acceptatie |

---

## 5. Documenten en playbooks

Linear-documenten hangen aan precies één ouder. `initiativeId` is in de API als intern gemarkeerd, dus **alle playbooks hangen aan projecten**, niet aan initiatives. Dat is meteen de vindbaarheidsregel: *beleid staat in `Raderwerk OS — bureauhandboek`, klantkennis staat bij het klantproject, bewijs staat bij het issue.*

| # | Document | Hangt aan | Inhoud in het kort |
|---|---|---|---|
| 00 | **Zo werkt Raderwerk** | OS — bureauhandboek | De loop van aanvraag tot factuur, de twee teams, de states, wat een agent wel en niet mag, wat een mens moet doen. Eén pagina die een nieuwe lezer zonder uitleg kan volgen. |
| 01 | **Rolcontracten** | OS — bureauhandboek | Per rol: model, trigger, input, output, mag, mag niet, poort, handtekening (hoofdstuk 6, letterlijk). |
| 02 | **Poortbeleid** | OS — bureauhandboek | De poortmechaniek, de tokens, wie mag goedkeuren, wat er bij afkeuring gebeurt, herinneringsritme (hoofdstuk 7, letterlijk). |
| 03 | **Kostenboek** | OS — financiën | Formaat van het kostenblok per run, de weektabel, de omrekening naar unit economics. |
| 04 | **Klantcommunicatiebeleid** | OS — bureauhandboek | Toon, verboden claims, AI-transparantiezin, absolute regel: er gaat niets naar echte personen; alle klantcommunicatie leeft als comment of document in Linear. |
| 05 | **Merkgids Raderwerk** | Raderwerk — merk & site v1 | Naam, betekenis, tagline, kleur, typografie, toon, wat we nooit zeggen. |
| 06 | **Definition of Done per dienst** | OS — bureauhandboek | Web, design, content, ads, social: het minimum bewijs per dienstenlijn plus de t-shirt-tabel uit 1.3. |
| 07 | **Issuebudget & opruimbeleid** | OS — betrouwbaarheid | Het 250-plafond, de verdeling, de wekelijkse telling, wanneer sub-issues verboden zijn (hoofdstuk 8). |
| 08 | **Noodstop & incidentprocedure** | OS — betrouwbaarheid | Hoe `ops/pauze` werkt, hoe je een lopende Codex- of Cursor-sessie stopt, wie wat doet bij een incident. |
| 09 | **Modelkaart & kostenprijzen** | OS — financiën | Welk model per rol, lijstprijzen per miljoen tokens, wanneer je opschaalt naar een duurder model. |
| 10 | **Evalset** | OS — betrouwbaarheid | Tien historische issues met gouden antwoorden, waartegen elke wijziging in rolcontracten getoetst wordt. |
| A1-A4 | **Accountdossier <klant>** | het eerste project van die klant | Merk, toon, stack, repo's, DoD-afwijkingen, verboden claims. |
| K1-K4 | **Klantpostbus <klant>** | het eerste project van die klant | Chronologisch archief van alle (gesimuleerde) klantberichten die door de poort zijn gekomen. |

Aanvullend, en typisch native: **agent skills** (`agentSkillCreate(teamId, title, body)`) maken herbruikbare instructies aanroepbaar als slash-command bij Linear Agent. Vier skills die de moeite waard zijn:

| Skill | Aanroep | Doet |
|---|---|---|
| `poort` | `/poort` | Schrijft het poortverzoek in het vaste formaat van hoofdstuk 7 met de juiste tokens. |
| `dod` | `/dod` | Haalt de DoD-checklist van het juiste template op en vinkt af wat aantoonbaar is. |
| `scope` | `/scope` | Zet een intake om in spec, acceptatiecriteria, t-shirtschatting en risicolabel. |
| `weekupdate` | `/weekupdate` | Genereert de projectupdate volgens het vaste formaat. |

---

## 6. Agentrooster

Handtekeningconventie, verplicht op **elke** comment die niet van een mens komt. Eerste regel machineleesbaar, daarna pas proza:

```
[RW/<ROL>/<model>/<issue-id>#<runnr>]
```

bijvoorbeeld `[RW/DEV/opus5/RDW-42#3]`. Aan het eind van elke run volgt het vaste slotblok:

```
---
Gedaan: <één zin>
Bewijs: <links>
Kosten: $<bedrag> · <tokens in/uit> · <wandkloktijd>
Volgende state: <state> · Poort: <geen | gate/...>
```

Codex en Cursor tekenen niet zelf: hun activiteit staat native in hun eigen agent-sessie, met hun eigen app-user als auteur. Dat is sterker bewijs dan een handtekening.

| # | Rol | Model / gereedschap | Trigger | Input | Output | Mag | Mag niet | Stopt bij | Handtekening |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **ACCOUNT** | Fable 5.1 (orchestrator) | Poll: RDW/BUR Triage, elke 2 min | Intake-issue, accountdossier, klantpostbus | Getriageerd issue, ontbrekende-vragen-comment, concept-klantbericht | Labels, prioriteit, project/mijlpaal koppelen, vragen stellen als comment, klantbericht als concept schrijven | Klantbericht "versturen", prijs noemen, toezeggen, state voorbij een poort zetten | `gate/klant`, `gate/vrijgave-*` | `[RW/ACCOUNT/fable51/...]` |
| 2 | **STRATEEG** | Fable 5.1 | Poll: state Scoping of Kwalificatie | Intake, accountdossier, marktonderzoek | Spec, acceptatiecriteria, t-shirtschatting, risicolabel, voorstelrichting | Spec en DoD schrijven, opknippen in issues, campagne- en contentstrategie bepalen | Zelf uitvoeren, prijs vaststellen zonder finops-controle | `gate/scope` | `[RW/STRATEEG/fable51/...]` |
| 3 | **PM** | Sonnet 5 (routine), Fable 5.1 (updates) | Cron: ma 08:00 cycleplanning, vr 16:00 updates; poll voor herplanning | Alle open issues, cyclestand, poortwachtrij | Cycle gevuld, projectupdates, initiative-updates, herinneringen | Issues in cycles plaatsen, mijlpalen beheren, `issueReminder` zetten, WIP bewaken | Scope wijzigen, schatting overschrijven, poorten passeren | — (schrijft alleen) | `[RW/PM/sonnet5/...]` |
| 4 | **DESIGNER** | Opus 5 (orchestrator), uitvoering desgewenst gedelegeerd aan Cursor | Poll: `type/designtaak` in Ready | Designtaak, merkgids, tokens | Ontwerp als code, screenshots van alle staten, tokenupdates | Componenten bouwen, tokens uitbreiden, screenshots maken op preview | Merkregels wijzigen, live publiceren | `gate/oplevering` | `[RW/DESIGNER/opus5/...]` |
| 5 | **DEV** | **Native: Cursor (Grok 4.6) via `delegate`** — primair. Codex (GPT-5.6) als tweede dev. Claude Opus 5 onder de orchestrator voor werk dat lokale gereedschappen nodig heeft. | Native delegatie (`delegateId`) door de orchestrator zodra state = In uitvoering | Issue met acceptatiecriteria, repo, basisbranch, agent guidance | Branch, PR, testoutput, preview-URL, agent-sessie met activiteiten | Branchen vanaf main, committen, PR openen, CI draaien, preview pushen, comment schrijven | Mergen, naar productie deployen, secrets aanmaken, dependencies met licentierisico toevoegen | `gate/oplevering` | native app-user |
| 6 | **REVIEWER** | **Native: Codex (GPT-5.6) via `delegate` of `@Codex`** voor de code-review, plus Fable 5.1 onder de orchestrator voor de inhoudelijke tegenlezing (tekst, design, campagne) | Orchestrator zet state In kruisreview en delegeert | PR-diff, acceptatiecriteria, DoD | Reviewcomment met bevindingen per ernst, oordeel | Bevindingen melden, blokkeren, tests eisen | Zelf de fix committen op dezelfde PR, eigen werk reviewen | — (adviseert) | native app-user / `[RW/REVIEWER/fable51/...]` |
| 7 | **CONTENT** | Fable 5.1 (redactioneel), Sonnet 5 (volume) | Poll: `type/contentstuk`, `dienst/content` in Ready | Contentbrief, merkgids, zoekonderzoek, bronnen | Tekstbestand in de repo, meta, interne links | Schrijven, herschrijven, SEO-velden vullen, bronnen opnemen | Feiten verzinnen, claims zonder bron, publiceren | `gate/vrijgave-publicatie` | `[RW/CONTENT/fable51/...]` |
| 8 | **ADS** | Sonnet 5 (productie), Fable 5.1 (strategie) | Poll: `type/campagne` in Ready | Campagnebrief, doelgroepen, zoekonderzoek | Campagneplan, advertentieteksten, meetplan | Plannen, teksten schrijven, budgetten voorstellen, onderzoek doen | Advertentieaccounts aanmaken, geld uitgeven, live zetten | `gate/vrijgave-publicatie` | `[RW/ADS/sonnet5/...]` |
| 9 | **SOCIAL** | Sonnet 5 | Poll: `type/socialkalender` in Ready | Kalenderbrief, merkgids | Kalenderbestand, posts, asset-briefs | Plannen en schrijven | Posten, accounts koppelen, echte personen noemen of taggen | `gate/vrijgave-publicatie` | `[RW/SOCIAL/sonnet5/...]` |
| 10 | **QA** | Opus 5 (orchestrator, browser- en testgereedschap), Codex als tweede mening bij `risico/hoog` | Orchestrator: na kruisreview, vóór poort 2 | PR, preview-URL, acceptatiecriteria | QA-rapport-issue of comment met oordeel en bewijs | Testen, screenshots, Lighthouse, toegankelijkheidschecks, afkeuren | Zelf repareren, oordeel geven zonder bewijs per criterium | — (bepaalt of de poort geopend mag worden) | `[RW/QA/opus5/...]` |
| 11 | **FINOPS** | Sonnet 5 | Cron: dagelijks 07:00 kostentelling, vr 16:30 weekrapport; poll voor `type/factuur` | Kostenblokken uit comments, issueteller, prijskaart | Kostenboek-update, weekrapport, factuurconcepten, budgetwaarschuwingen | Optellen, rapporteren, factuurdocument opstellen, `ops/budget-overschreden` zetten | Factuur versturen, prijzen aanpassen | `gate/vrijgave-factuur` | `[RW/FINOPS/sonnet5/...]` |
| 12 | **COMPLIANCE** | Fable 5.1 | Poll: `risico/juridisch` of `risico/merk` op een issue dat richting een poort gaat | Artefact, klantcommunicatiebeleid, merkgids | Advies-comment met go/no-go per punt | Blokkeren, tekst voorstellen, disclosure eisen | Juridisch advies geven als feit presenteren | — (adviseert de poort) | `[RW/COMPLIANCE/fable51/...]` |
| 13 | **ORCHESTRATOR** | Fable 5.1 (routering en oordeel), Sonnet 5 (mechanische lus) | Continu, pollinterval 2 min + cronjobs | Linear-state via MCP en GraphQL | Alle statuswissels, delegaties, poortcomments, budgetbewaking | Delegeren, state wisselen tot vlak vóór een poort, labels beheren, runs starten en stoppen | Een poortstate verlaten, goedkeuren namens een mens, budget verhogen | alle poorten | `[RW/ORCH/fable51/...]` |
| 14 | **LINEAR-ASSIST** | Linear Agent (inbegrepen op Free, kost geen AI-credits) | `@Linear` in een comment of document, of een `/skill` | Issue- en projectcontext | Samenvattingen, issues uit een document, docupdates | Samenvatten, issues aanmaken uit een goedgekeurde spec, documenten bijwerken | Delegatie ontvangen (coding sessions zijn Basic+ en dus geblokkeerd) | — | native app-user |

Routeringsregel in één zin: **kan het native, dan native.** Codebasis-werk gaat naar Cursor, code-review naar Codex, samenvatten en document-schrijfwerk naar Linear Agent; al het andere draait onder de orchestrator met een handtekening.

### 6.1 Agent guidance (native, gratis, onderbenut)

Linear injecteert workspace- en teaminstructies in elke agent-sessie (Settings → Agents → Additional guidance; teamniveau wint). Dit is de enige plek waar we Codex en Cursor kunnen sturen zonder eigen code. Voorgestelde tekst op workspaceniveau:

```
Je werkt voor Raderwerk, een digitaal bureau. Nederlands in Linear, Engels in code, commits en PR's.
Regels die altijd gelden:
1. Vertak altijd vanaf main. Merge nooit zelf. Deploy nooit naar productie.
2. Werk alleen aan wat in de acceptatiecriteria van het issue staat. Ontbreekt informatie, stel dan een vraag in een comment en stop.
3. Lever bewijs: PR-link, testoutput, preview-URL, screenshot. Werk zonder bewijs geldt als niet gedaan.
4. Voeg geen dependencies toe zonder dat in de PR-beschrijving te motiveren.
5. Raak geen secrets aan en maak geen accounts aan.
6. Als je klaar bent, schrijf dan één comment met: wat je deed, bewijs, en wat er nog open staat.
7. Verzin geen feiten over de klant. Wat niet in het issue of het accountdossier staat, bestaat niet.
```

Op teamniveau RDW komt daar de repo- en preview-conventie bij; op BUR de regel dat er niets naar buiten gaat zonder poort.

---

## 7. Poortmechaniek

Het doel: een buitenstaander moet in de Linear-historie kunnen zien dat een mens heeft goedgekeurd, wanneer, waarop, en dat de machine daar niet omheen kon.

### 7.1 De vier signalen die samen een poort vormen

1. **State** — het issue staat in een gele state. Dat is de enige plek waar de orchestrator stopt.
2. **Label** — `gate/<soort>` zegt welke beslissing gevraagd wordt.
3. **Assignee en delegate** — bij het betreden van een poort zet de orchestrator `assigneeId` op de goedkeurder (mens) en **maakt `delegateId` leeg**. Een leeg delegate-veld is het machineleesbare "er werkt geen agent aan". De poortwachtrij van de mens is daarmee gewoon zijn eigen "My issues"-view.
4. **Poortcomment** — één comment in vast formaat, geschreven door de orchestrator:

```
[RW/ORCH/fable51/RDW-42#3]

## POORT: oplevering
Gevraagd: mag deze PR gemerged en op preview gezet worden?

Wat er ligt
- PR: https://github.com/raderwerk/duinbrand-theme/pull/12
- Preview: https://duinbrand-preview.vercel.app/producten/huisblend
- QA-rapport: RDW-47 (GOEDGEKEURD, 8/8 criteria met bewijs)
- Kruisreview: Codex, 2 bevindingen, beide verwerkt

Wat het kost
- Tot nu toe: $6,40 · 3 runs · 41 min wandkloktijd
- Schatting: M · plafond $10

Risico
- risico/midden. Omkeerbaar: revert-commit klaar.

Antwoord met precies één van deze regels als eerste regel van je comment:
AKKOORD
AFGEKEURD: <reden>
```

### 7.2 Het antwoord van de mens

De mens hoeft **één** ding te doen: een comment plaatsen waarvan de eerste regel exact `AKKOORD` of `AFGEKEURD: <reden>` is. Niet slepen, niet labelen, niet toewijzen. Dat is bewust: één handeling, één plek, volledig in de historie.

Bij `risico/hoog` (label `gate/tweede-paar-ogen`) moet het akkoord luiden: `AKKOORD RISICO-GEZIEN`. De orchestrator accepteert een kaal `AKKOORD` daar niet en antwoordt met een herhaling van het risico.

### 7.3 Wat de orchestrator doet

Bij elke pollronde leest de orchestrator alle issues in een poortstate en hun nieuwste comments.

**Validatie (alle vier moeten kloppen, anders geen doorgang):**
- `comment.user.app === false` — een app-user kan nooit goedkeuren.
- `comment.user.id` staat in de goedkeurderslijst uit `02 — Poortbeleid`.
- De comment is nieuwer dan het poortverzoek.
- De eerste regel matcht exact `^AKKOORD( RISICO-GEZIEN)?$` of `^AFGEKEURD: .+`.

**Bij AKKOORD:**
1. State naar de volgende state (poort 1 → Ready; poort 2 → Klantacceptatie; poort 3/vrijgave → Live/verzonden).
2. `gate/*`-label eraf, `gate/afgekeurd` eraf als die aanstond.
3. `delegateId` weer zetten als de volgende stap een native agent is; anders `agent/*`-label zetten.
4. Bevestigingscomment: wie, wanneer, welk comment-id, welke state, wat de volgende stap is.
5. Regel in het kostenboek: poort, uitkomst, doorlooptijd van het wachten (dat is de echte supervisiekost).

**Bij AFGEKEURD:**
1. State terug naar de laatste werkstate vóór de poort (poort 1 → Scoping; poort 2 → In uitvoering; vrijgave → In uitvoering).
2. `gate/afgekeurd` erop, `billing/niet-factureerbaar` erbij als de afkeuring een eigen fout betreft.
3. Herstelcomment met de reden letterlijk geciteerd, plus een expliciete lijst van wat er moet veranderen.
4. Opnieuw delegeren naar dezelfde uitvoerder, met de reden als extra instructie. Bij de **derde** afkeuring op hetzelfde issue: naar Geblokkeerd, `ops/mens-vereist`, en een comment dat om een menselijk besluit vraagt. Geen vierde poging.
5. Rondeteller ophogen in de DoD-checklist van het issue (`Herstelronde: 2`), zodat first-pass-acceptatie meetbaar blijft.

**Bij een handmatige statewissel zonder token:** de mens wint altijd. De orchestrator gaat door, maar schrijft `poort handmatig gepasseerd zonder token door <naam> op <tijd>` en markeert de regel in het kostenboek als niet-geattesteerd. Dat is eerlijker dan terugdraaien.

**Bij stilstand:** staat een issue langer dan 24 uur in een poort, dan zet de PM-agent één `issueReminder` en schrijft één herinneringscomment. Daarna niets meer: geen herhaald porren.

### 7.4 Noodrem

- `ops/pauze` op een issue: de orchestrator slaat dit issue over en delegeert niet. Loopt er al een Codex- of Cursor-sessie, dan blijft die lopen: die stop je in de Linear-UI met de stopknop in de agent-sessie. Dat staat als handeling in `08 — Noodstop`.
- `ops/pauze` op het gepinde issue `BUR — Noodstop`: alle runs stoppen binnen één pollcyclus (≤ 2 minuten). De orchestrator schrijft één haltcomment op dat issue met het aantal gestopte runs en gaat in leesstand tot het label weg is.
- De noodstop wordt maandelijks getest en het bewijs (tijdstempel eerste stop) staat in `Raderwerk OS — betrouwbaarheid`.

---

## 8. Issuebudget: 250 stuks

Dit is de zwaarste beperking van het hele ontwerp en verdient een eigen beleid.

### 8.1 Uitgangspositie

De bestaande workspace bevat ~130 issues uit een oude bulkimport. Die moeten **verwijderd** worden, niet gearchiveerd: archiveren geeft de teller niet terug. Of verwijderen de teller wél teruggeeft is niet geverifieerd (`organization.createdIssueCount` telt cumulatief aangemaakte issues; de documentatie spreekt over "meer dan 250 issues hebben"). **Dit moet als eerste getest worden** (zie hoofdstuk 10, stap 2). Valt het verkeerd uit, dan is plan B een verse gratis workspace.

### 8.2 Verdeling van 250

| Pot | Aantal | Toelichting |
|---|---|---|
| Zaai-issues Duinbrand | 14 | hoofdstuk 9.1 |
| Zaai-issues Hovex | 14 | hoofdstuk 9.2 |
| Zaai-issues Wildernest | 13 | hoofdstuk 9.3 |
| Zaai-issues Raderwerk (eigen merk) | 12 | hoofdstuk 9.4 |
| Zaai-issues Bureau (BUR) | 18 | hoofdstuk 9.5 |
| **Subtotaal zaai** | **71** | eenmalig, wordt niet opnieuw uitgegeven |
| Agent-gemaakte sub-issues en vervolgwerk | 90 | max 2 per actief zaai-issue; label `bron/agent` |
| QA-rapporten, incidenten en herstelwerk | 25 | |
| Droogloopruns en demo | 30 | label `ops/droogloop`, worden na afloop verwijderd |
| **Harde reserve, nooit uitgeven** | **34** | |
| **Totaal** | **250** | |

### 8.3 Regels die het budget bewaken

1. **Documenten en mijlpalen boven sub-issues.** Een projectfase is een mijlpaal, geen parent-issue. Een deelresultaat is een checklistregel in de beschrijving, geen sub-issue. Alleen werk dat *afzonderlijk gedelegeerd, gereviewd en gepoort* moet worden, verdient een eigen issue.
2. **Bewijs is geen issue.** Screenshots, testoutput en QA-bewijs gaan als comment of document, niet als los issue. Alleen een formeel QA-rapport bij `risico/hoog` krijgt een eigen issue.
3. **Plafonds per fase.** Zodra `createdIssueCount` boven **200** komt, schakelt de orchestrator naar sub-issue-loze modus: agents mogen dan geen nieuwe issues meer aanmaken, alleen comments en checklistregels. Boven **230** mag ook de mens niets meer aanmaken zonder eerst op te ruimen.
4. **Wekelijkse budgetronde (vrijdag, finops-rol).** Telt `createdIssueCount`, telt open issues per pot, markeert kandidaten met `ops/opruimen` en zet de stand in het weekrapport. Kandidaten: alles met `ops/droogloop` ouder dan een week, duplicaten, en Canceled-issues ouder dan een maand.
5. **Opruimen = verwijderen.** `issueDelete` (en zo nodig `permanentlyDelete: true`) voor prullaria; `issueArchive` alleen voor afgerond echt werk dat we als bewijs willen bewaren, in de wetenschap dat het geen ruimte teruggeeft.
6. **Vóór verwijderen: exporteren.** Elke opruimronde schrijft eerst de titels, states en DoD-uitkomsten van de te verwijderen issues weg naar een document in `Raderwerk OS — betrouwbaarheid`. Het bewijs overleeft het issue.

---

## 9. De vier fictieve klanten en hun zaai-issues

Alles hieronder is fictief bedacht. De namen zijn niet gecontroleerd op bestaande bedrijven: dat is een verplichte stap voordat er iets publiek wordt (hoofdstuk 10). Het **werk** is echt: echte repo's onder `github.com/raderwerk`, echte sites op preview-URL's, echte teksten, echte ontwerpen, echte campagne- en socialplannen.

Notatie per issue: `ID · titel` — labels · schatting · project/mijlpaal, gevolgd door de acceptatiecriteria.

### 9.1 Duinbrand Coffee — DTC e-commerce op Shopify met ERP-koppeling

Merk in één zin: *vers gebrande specialty koffie uit een duinroasterij, elke twee of vier weken op de mat.*
Eerste engagement: nieuwe storefront met abonnementen, plus een koppeling tussen shop en ERP voor voorraad en orders.
Repo's: `raderwerk/duinbrand-theme`, `raderwerk/duinbrand-erp-bridge`.

**D-01 · Repo, CI en preview-pijplijn voor de storefront** — `type/feature` `dienst/web` `risico/laag` · S · Storefront/M1
- Repo bestaat onder `github.com/raderwerk` met README die een nieuwe ontwikkelaar in ≤ 5 commando's draaiend krijgt.
- CI draait op elke PR: linter, themacontrole, build. Rode CI blokkeert de PR.
- Elke PR levert automatisch een preview-URL op die in het Linear-issue verschijnt.

**D-02 · Merkfundament: kleur, typografie en tokens** — `type/designtaak` `dienst/design` · M · Storefront/M1
- Alle kleuren en typografie als tokens in één bestand; geen losse hexwaarden in componenten.
- Elk tekstcontrast ≥ 4.5:1, gemeten en genoteerd.
- Drie toepassingen getoond (knop, kaart, koptekst) op mobiel en desktop.

**D-03 · Homepage met abonnementspropositie** — `type/feature` `dienst/web` · M · Storefront/M1
- Boven de vouw staan propositie, prijsindicatie en één primaire CTA.
- Geen horizontale scroll op 375px; LCP op de preview onder 2,5 s.
- Alle beelden hebben alt-tekst en een expliciete breedte/hoogte.

**D-04 · Productpagina met maalgraad- en smaakprofielkiezer** — `type/feature` `dienst/web` · M · Storefront/M3
- Variantkeuze werkt zonder JS-fout in console; prijs en voorraadstatus updaten mee.
- Smaakprofiel toont ten minste vier assen met toegankelijke tekstalternatieven.
- Toetsenbordbediening volledig; focus zichtbaar op elke keuzeknop.

**D-05 · Abonnementsflow: kiezen, pauzeren, wijzigen** — `type/feature` `dienst/web` `risico/hoog` · L · Storefront/M2
- Twee ritmes (2- en 4-wekelijks) selecteerbaar, met zichtbare eerstvolgende leverdatum.
- Pauzeren en wijzigen doorlopen in de dev store, met screenshot per stap.
- Alle foutpaden (mislukte betaling, ongeldige datum) tonen een begrijpelijke Nederlandse melding.
- Testsuite dekt de drie hoofdpaden en faalt zonder de implementatie.

**D-06 · ERP-koppeling: contract en veldmapping** — `type/onderzoek` `dienst/web` · M · ERP/M1
- Document met elk gebruikt veld: bron, doel, type, verplicht, transformatie.
- Alle veldnamen komen uit de daadwerkelijke (mock-)ERP-definitie, niet uit aannames.
- Kruisreview door een tweede agent op volledigheid; openstaande onduidelijkheden staan als vraag.

**D-07 · Voorraadsync ERP → shop** — `type/feature` `dienst/web` `risico/hoog` · L · ERP/M2
- Sync van 50 SKU's draait idempotent: tweemaal draaien geeft identieke eindstand.
- Foutpad gelogd met SKU en oorzaak; één mislukte SKU stopt de rest niet.
- Testsuite met een gesimuleerde ERP-storing en een gesimuleerde partiële respons.

**D-08 · Ordersync shop → ERP met retry** — `type/feature` `dienst/web` `risico/hoog` · L · ERP/M3
- Dubbele order is onmogelijk: idempotentiesleutel per order, aantoonbaar met een dubbele-levering-test.
- Retry-ladder gedocumenteerd en getest, inclusief het moment waarop hij opgeeft.
- Bij definitieve mislukking ontstaat automatisch een incident-issue in Linear met de orderreferentie.

**D-09 · Monitoring en dagrapport van de koppeling** — `type/feature` `dienst/web` · M · ERP/M4
- Dagelijks rapport met aantal gesynchroniseerde SKU's, orders, fouten en duur.
- Rapport is als artefact leesbaar zonder toegang tot de code.
- Drempelwaarde gedefinieerd waarboven een incident-issue ontstaat.

**D-10 · Contentserie "Van boon tot bak" (3 artikelen)** — `type/contentstuk` `dienst/content` · M · Groei/M2
- Drie artikelen van elk ≥ 800 woorden, met unieke H1, meta titel en meta omschrijving.
- Elke feitelijke claim over herkomst of bereiding heeft een bron; claims zonder bron zijn geschrapt.
- Elk artikel linkt naar minimaal twee productpagina's met beschrijvende ankertekst.

**D-11 · SEO-basis: metatitels en omschrijvingen voor 24 pagina's** — `type/contentstuk` `dienst/content` · S · Groei/M2
- 24 unieke titels ≤ 60 tekens en omschrijvingen ≤ 155 tekens.
- Elke titel bevat de zoekterm uit het onderzoek en leest als een zin, niet als een opsomming.
- Opgeleverd als databestand in de repo, niet als losse tekst in Linear.

**D-12 · Advertentieplan Q4: search en social** — `type/campagne` `dienst/ads` `risico/merk` · M · Groei/M1
- Drie doelgroepen met eigen boodschap en eigen landingspagina.
- Negen advertentievarianten zonder dubbele koppen.
- Meetplan met KPI, rapportageritme en één expliciete stopregel.
- Nul euro live uitgegeven: het plan blijft plan tot de poort opengaat.

**D-13 · Socialkalender oktober (12 posts)** — `type/socialkalender` `dienst/social` · M · Groei/M2
- Twaalf posts met haakje, tekst, CTA en asset-brief; minimaal drie formats.
- Publicatiedata verdeeld over de maand, geen twee posts op dezelfde dag.
- Geen post noemt bestaande personen of bedrijven.

**D-14 · QA-ronde: kassa- en abonnementspaden** — `type/qa-rapport` `dienst/web` · M · Storefront/M4
- Acht scenario's geautomatiseerd, groen op de preview, met screenshot per scenario.
- Randgevallen: lege winkelwagen, uitverkochte variant, mislukte betaling, dubbel klikken.
- Rapport bevat een expliciet oordeel en per acceptatiecriterium een bewijslink.

### 9.2 Hovex Aandrijvingen — B2B industrie met dealercatalogus

Merk in één zin: *aandrijftechniek voor de maakindustrie, geleverd via een dealernetwerk in de Benelux.*
Eerste engagement: marketingsite met doorzoekbare productcatalogus, dealerlocator en kennisbank.
Repo: `raderwerk/hovex-site`.

**H-01 · Repo, CI en preview-deploy** — `type/feature` `dienst/web` `risico/laag` · S · Site/M1
- Repo met README, één commando voor lokaal draaien, één voor bouwen.
- CI: linter, typecheck, build, linkcontrole. Rode CI blokkeert.
- Preview-URL per PR, automatisch in het issue.

**H-02 · Informatiearchitectuur en sitemap** — `type/onderzoek` `dienst/strategie` · M · Site/M1
- Sitemap met alle pagina's, hun doel en hun primaire zoekterm.
- Maximaal drie klikken van home naar elke productfamilie.
- Navigatiestructuur getoetst tegen de tien meest waarschijnlijke bezoekersvragen.

**H-03 · Designsysteem: industrieel, hoog contrast** — `type/designtaak` `dienst/design` · L · Site/M1
- Componentenkit met minimaal twaalf componenten, elk met lege, laad- en foutstaat.
- Tokens voor kleur, ruimte, typografie; geen losse waarden in componenten.
- Alles bruikbaar met toetsenbord; contrast overal ≥ 4.5:1.

**H-04 · Datamodel voor de dealercatalogus** — `type/feature` `dienst/web` · M · Site/M2
- Model dekt productfamilie, type, specificaties, datasheet-PDF en dealerbeschikbaarheid.
- Elk veld heeft type, verplichtheid en voorbeeldwaarde.
- Validatie faalt zichtbaar bij ontbrekende verplichte velden.

**H-05 · Productfilter op koppel, vermogen en bouwvorm** — `type/feature` `dienst/web` · L · Site/M3
- Filters combineerbaar; de resultaten kloppen bij elke combinatie in de testset.
- Filterstaat staat in de URL en is deelbaar.
- Nul-resultatenstaat biedt een zinnige vervolgstap.

**H-06 · Dealerlocator met provincie- en afstandsfilter** — `type/feature` `dienst/web` · L · Site/M3
- Veertig fictieve dealers met adres en specialisme, in een databestand.
- Filteren op provincie en op straal rond een postcode werkt aantoonbaar.
- Geen externe kaartdienst nodig om de lijst te kunnen gebruiken (kaart is aanvulling, geen voorwaarde).

**H-07 · Offerte-aanvraagformulier met spamharding** — `type/feature` `dienst/web` `risico/klantdata` · M · Site/M4
- Formulier valideert client- en serverzijde; foutmeldingen in het Nederlands en per veld.
- Honeypot en snelheidslimiet aantoonbaar werkend.
- Verzending gaat naar een testpostbus in de repo; er bereikt niemand een echte persoon.
- Privacytekst aanwezig en juridisch nagelezen.

**H-08 · Contentmigratie van 18 productfamilies** — `type/onderhoud` `dienst/content` · M · Site/M2
- Alle 18 families gemigreerd met specificaties, beelden en datasheet-links.
- Nul dode links, aantoonbaar met de linkcontrole in CI.
- Verschillenrapport tussen bron en resultaat opgeleverd.

**H-09 · Gestructureerde data: Product en Organization** — `type/feature` `dienst/web` · S · Kennisbank/M3
- Schema aanwezig op alle productpagina's en de homepage.
- Validator geeft nul fouten en nul waarschuwingen op vijf steekproefpagina's.
- Geen verzonnen waarden: ontbrekende velden blijven weg in plaats van gevuld.

**H-10 · Kennisbank: vier technische artikelen** — `type/contentstuk` `dienst/content` · L · Kennisbank/M2
- Vier artikelen van ≥ 1.000 woorden, elk met een rekenvoorbeeld of tabel.
- Elke technische bewering is herleidbaar naar een bron of expliciet als vuistregel gemarkeerd.
- Elk artikel linkt naar de bijbehorende productfamilie.

**H-11 · LinkedIn-contentplan voor dealers (8 posts)** — `type/socialkalender` `dienst/social` · M · Kennisbank/M2
- Acht posts gericht op dealers, met haakje, tekst, CTA en asset-brief.
- Toon past bij een technisch B2B-publiek: geen uitroeptekens, geen holle superlatieven.
- Geen post noemt bestaande bedrijven of personen.

**H-12 · Zoekcampagneplan merk en generiek** — `type/campagne` `dienst/ads` `risico/merk` · M · Kennisbank/M1
- Aparte structuur voor merk- en generieke termen met eigen budget en doel.
- Negen advertentievarianten met bijpassende landingspagina's.
- Negatieve zoektermen benoemd; stopregel expliciet. Geen live uitgaven.

**H-13 · Toegankelijkheidsaudit WCAG 2.2 AA op zes sjablonen** — `type/qa-rapport` `dienst/web` `risico/juridisch` · M · Site/M4
- Zes sjablonen getoetst, bevindingen per succescriterium met bewijs.
- Nul blokkerende bevindingen bij oplevering, of elk restpunt heeft een gepland issue.
- Toetsenbordpad van elke sjabloon volledig doorlopen en vastgelegd.

**H-14 · Performancebudget met CI-poort** — `type/feature` `dienst/web` · S · Site/M4
- Budget vastgelegd (bundelgrootte, LCP, CLS) en zichtbaar in de repo.
- CI faalt aantoonbaar bij overschrijding, getest met een opzettelijke overtreding.
- Uitzonderingsprocedure beschreven in de README.

### 9.3 Wildernest Reizen — travel/booking met CMS en CRM-sync

Merk in één zin: *kleinschalige wandel- en natuurreizen door Noord-Europa, met gidsen die de route zelf lopen.*
Eerste engagement: nieuwe site met reisaanbod en een betrouwbare aanvraagflow naar het CRM.
Repo's: `raderwerk/wildernest-site`, `raderwerk/wildernest-crm-bridge`.

**W-01 · Repo, headless CMS en CI** — `type/feature` `dienst/web` `risico/laag` · M · Site/M1
- Repo draait lokaal met één commando, inclusief lokale CMS-instantie met voorbeelddata.
- CI: linter, typecheck, build, contentvalidatie.
- Preview-URL per PR.

**W-02 · Reis-datamodel** — `type/feature` `dienst/web` · M · Site/M1
- Model dekt reis, vertrekdatum, prijsstaffel, beschikbaarheid, zwaarte en inbegrepen/niet-inbegrepen.
- Validatie weigert een reis zonder vertrekdatum of prijs.
- Vijf voorbeeldreizen volledig ingevuld als testdata.

**W-03 · Reisoverzicht met filters** — `type/feature` `dienst/web` · L · Site/M2
- Filteren op regio, duur, zwaarte en vertrekmaand, combineerbaar en deelbaar via de URL.
- Sortering op prijs en op vertrekdatum.
- Nul-resultatenstaat met suggestie.

**W-04 · Reisdetailpagina met dagprogramma** — `type/feature` `dienst/web` · L · Site/M2
- Dag-tot-dag-programma uitklapbaar, toetsenbordbedienbaar.
- Prijsstaffel en wat wel/niet inbegrepen is, staan boven de vouw op mobiel bereikbaar.
- Beelden lazy-loaded met alt-teksten; LCP onder 2,5 s op preview.

**W-05 · Boekingsaanvraag naar het CRM** — `type/feature` `dienst/web` `risico/klantdata` · L · Site/M3
- Aanvraag komt idempotent in het (mock-)CRM: dubbel verzenden geeft één record.
- Bevestigingsscherm en bevestigingsmail als concept; er wordt niets naar echte adressen gestuurd.
- Foutpad bij CRM-storing: aanvraag gaat niet verloren, gebruiker krijgt een eerlijke melding.

**W-06 · Beschikbaarheid terugsyncen vanuit het CRM** — `type/feature` `dienst/web` · M · Site/M4
- Vol/vrij-status per vertrekdatum, hooguit vijf minuten oud.
- Bij een mislukte sync toont de site de laatst bekende status met tijdstempel, niet een gok.
- Sync is idempotent en gelogd.

**W-07 · Nieuwsbrief met dubbele opt-in** — `type/feature` `dienst/web` `risico/juridisch` · M · Content/M3
- Dubbele opt-in volledig doorlopen in test, inclusief het verlopen van een bevestigingslink.
- Afmeldlink werkt in één klik.
- Privacytekst nagelezen door de compliance-rol; geen echte adressen in het systeem.

**W-08 · Contentserie: vier reisverhalen en één pilaarpagina** — `type/contentstuk` `dienst/content` · L · Content/M1
- Vier verhalen van ≥ 900 woorden plus één pilaarpagina van ≥ 1.500 woorden.
- Elke plaatsnaam, afstand en seizoensbewering klopt met een controleerbare bron.
- Interne links van elk verhaal naar de pilaarpagina en naar minstens één reis.

**W-09 · Fotorichtlijn en alt-teksten voor 40 beelden** — `type/designtaak` `dienst/design` · M · Content/M1
- Richtlijn beschrijft kadrering, kleurbewerking en wat we nooit tonen.
- Veertig beschrijvende alt-teksten, geen enkele begint met "afbeelding van".
- Bestandsnamen en formaten voldoen aan de richtlijn.

**W-10 · E-mailflow aanvraag → offerte → herinnering** — `type/contentstuk` `dienst/content` · M · Content/M2
- Drie mails als concept, met onderwerpsregels en één duidelijke actie per mail.
- Timing en stopregel beschreven (wanneer stopt de reeks).
- Transparantiezin over AI-inzet waar het beleid dat eist. Niets wordt verstuurd.

**W-11 · Socialkalender en zes storysjablonen** — `type/socialkalender` `dienst/social` · M · Content/M3
- Twaalf posts plus zes sjablonen, met asset-briefs.
- Seizoensopbouw zichtbaar: de kalender volgt de vertrekmomenten.
- Geen echte personen of gidsen bij naam.

**W-12 · QA: aanvraagpad end-to-end** — `type/qa-rapport` `dienst/web` · M · Site/M4
- Zes scenario's inclusief foutstaten, groen op preview met screenshots.
- Formuliervalidatie getest op leeg, te lang, ongeldig e-mailadres en dubbele verzending.
- Rapport met expliciet oordeel per acceptatiecriterium.

**W-13 · Meetplan zonder persoonsgegevens** — `type/onderzoek` `dienst/strategie` `risico/klantdata` · S · Site/M4
- Doelen, events en een dashboardschets, allemaal zonder herleidbare persoonsgegevens.
- Expliciet benoemd wat we níét meten en waarom.
- Nagelezen door de compliance-rol.

### 9.4 Raderwerk zelf — eigen merk als etalage

Merk in één zin: *Raderwerk is een digitaal bureau dat door agents wordt gedraaid; een mens zet de poorten open.* Tagline: *Every part turns the next.*
Repo: `raderwerk/raderwerk-site`.

**R-01 · Merkidentiteit: logo, kleur, typografie, toon** — `type/designtaak` `dienst/design` `risico/merk` · L · Merk/M1
- Logo in SVG, werkt op 24 px en op 240 px, in licht en donker.
- Kleur- en typografiesysteem met contrastbewijs.
- Toonregels met vijf voorbeelden van "wel zo" en vijf van "nooit zo".

**R-02 · Repo, site-fundament en deploy** — `type/feature` `dienst/web` · M · Merk/M2
- Site draait lokaal met één commando en deployt automatisch naar de preview.
- CI met linter, build, linkcontrole en performancebudget.
- Domeinkeuze vastgelegd (raderwerk.ai of raderwerk.agency) met redenering.

**R-03 · Website v1: vijf pagina's** — `type/feature` `dienst/web` · L · Merk/M2
- Home, werkwijze, diensten, cases, contact; elk met eigen meta en een duidelijke primaire actie.
- Volledig toetsenbordbedienbaar; contrast overal ≥ 4.5:1.
- Nul dode links; LCP onder 2,5 s op alle vijf.

**R-04 · Pagina "Hoe wij werken": de poorten uitgelegd** — `type/contentstuk` `dienst/content` · M · Merk/M3
- Legt de drie poorten uit in gewone taal, met een schema.
- Benoemt eerlijk wat een agent doet en wat een mens doet.
- Geen enkele claim die het bureau groter maakt dan het is.

**R-05 · AI-transparantiepagina en contentlabeling** — `type/contentstuk` `dienst/content` `risico/juridisch` · M · Merk/M3
- Legt uit welke content door AI is gemaakt en hoe die wordt nagelezen.
- Labelconventie voor AI-gegenereerde artikelen toegepast op de hele site.
- Nagelezen door de compliance-rol tegen de geldende transparantieplicht.

**R-06 · Drie casusartikelen over de fictieve klanten** — `type/contentstuk` `dienst/content` `risico/juridisch` · L · Merk/M3
- Elk artikel vermeldt zichtbaar en ondubbelzinnig dat de klant fictief is.
- Beschrijft echt uitgevoerd werk met echte artefacten (repo, preview, cijfers).
- Nul claims over resultaat bij echte klanten.

**R-07 · Contentplan zes weken** — `type/contentstuk` `dienst/strategie` · M · Marketing/M1
- Zes weken met per week één artikel en drie posts, elk met onderwerp, doel en zoekterm.
- Onderwerpen sluiten aan op de drie diensten die we willen verkopen.
- Productiecapaciteit per week getoetst aan het issuebudget.

**R-08 · Twaalf social posts over het bouwproces** — `type/socialkalender` `dienst/social` · M · Marketing/M2
- Twaalf posts met haakje, tekst, CTA en asset-brief.
- Geen enkele post benadert of noemt echte personen of bedrijven.
- Transparantielabel op elke post die door AI is geschreven.

**R-09 · Advertentieplan eigen merk** — `type/campagne` `dienst/ads` `risico/merk` · M · Marketing/M3
- Drie doelgroepen, negen advertenties, meetplan met stopregel.
- Landingspagina per doelgroep bestaat en is getest.
- Nul live uitgaven zonder poort.

**R-10 · Prijskaart en dienstenpakketten S/M/L** — `type/onderzoek` `dienst/strategie` · M · Marketing/M3
- Drie pakketten met scope, doorlooptijd, prijs en wat er níét in zit.
- Prijs onderbouwd met de kostprijs per ticketgrootte uit het kostenboek.
- Nagelezen door de finops-rol.

**R-11 · Publiek bouwlogboek, wekelijks** — `type/contentstuk` `dienst/content` · S · Marketing/M2
- Wekelijkse update met wat er gebouwd is, wat er misging en wat het kostte.
- Cijfers komen rechtstreeks uit het kostenboek, geen afronding naar boven.
- Publicatie pas na de vrijgavepoort.

**R-12 · Kostenboek publiceren als openbare pagina** — `type/feature` `dienst/web` `risico/merk` · M · Marketing/M3
- Pagina toont kosten per ticketgrootte en per week, automatisch gevoed vanuit het kostenboek-document.
- Methodologie en beperkingen staan er expliciet bij.
- Geen enkel getal is handmatig gunstig bijgesteld.

### 9.5 Bureau-issues (BUR), 18 stuks

| ID | Titel | Labels | Grootte | Acceptatiecriterium in één zin |
|---|---|---|---|---|
| B-01 | **Noodstop** (gepind) | `ops/*` `klant/geen` | XS | Dit issue bestaat, is gepind, en het aanzetten van `ops/pauze` erop stopt aantoonbaar alle runs binnen 2 minuten. |
| B-02 | Poortbeleid vastleggen | `type/onderzoek` `klant/geen` | S | Document 02 bestaat en bevat de tokens, de goedkeurderslijst en het gedrag bij afkeuring. |
| B-03 | Rolcontracten schrijven | `type/onderzoek` | M | Document 01 bevat alle 14 rollen met model, trigger, mag, mag niet en poort. |
| B-04 | Handboek "Zo werkt Raderwerk" | `type/contentstuk` | M | Een lezer zonder uitleg kan de loop navertellen; getest door een agent die het alleen uit het document mag halen. |
| B-05 | Kostenboek opzetten | `type/onderzoek` `dienst/strategie` | M | Document 03 met formaat, en drie echte runs erin verwerkt. |
| B-06 | Merkgids Raderwerk | `type/designtaak` `klant/raderwerk` | M | Document 05 met toon, kleur, typografie en verboden formuleringen. |
| B-07 | Klantcommunicatiebeleid | `type/onderzoek` `risico/juridisch` | S | Document 04 met transparantiezin en de regel dat er niets naar echte personen gaat. |
| B-08 | Issuebudget & opruimbeleid | `type/onderzoek` | S | Document 07 met de verdeling uit hoofdstuk 8 en de wekelijkse telprocedure. |
| B-09 | Evalset van tien issues | `type/onderzoek` | M | Tien issues met gouden antwoorden en een scorekaart die een wijziging in rolcontracten kan afkeuren. |
| B-10 | Lead: fictief merk in de meubelbranche | `type/lead` `klant/prospect` | XS | Kwalificatie compleet, go/no-go met motivering. |
| B-11 | Lead: fictieve fysiotherapiegroep | `type/lead` `klant/prospect` | XS | Idem. |
| B-12 | Lead: fictieve regionale brouwerij | `type/lead` `klant/prospect` | XS | Idem. |
| B-13 | Offerte Duinbrand groei Q4 | `type/offerte` `klant/duinbrand` `risico/hoog` | S | Elke regel herleidbaar naar een geschat issue; poort met `RISICO-GEZIEN` gepasseerd. |
| B-14 | Offerte Hovex kennisbank | `type/offerte` `klant/hovex` `risico/hoog` | S | Idem. |
| B-15 | Factuurronde september | `type/factuur` `billing/*` | S | Factuurdocument per klant, gebaseerd op Done-issues met een billing-label. |
| B-16 | Droogloop 1 tot en met 3 | `type/onderzoek` `ops/droogloop` | M | Drie opeenvolgende runs zonder handmatige reparatie, met logboek. |
| B-17 | Incidentdrill: sync valt stil | `type/incident` `ops/droogloop` | S | Volledige tijdlijn, bewezen oorzaak, preventie-issue aangemaakt. |
| B-18 | Maandelijkse noodstoptest | `type/onderhoud` | XS | Bewijs met tijdstempel dat alle runs binnen één pollcyclus stopten. |

Totaal zaai: 14 + 14 + 13 + 12 + 18 = **71 issues**.

---

## 10. Checklist voor de mens

Dit zijn de handelingen die geen agent kan of mag doen. In volgorde.

**A. Workspace**

1. **Besluit: hernoemen of nieuw.** De huidige workspace heet nog naar de werkgever van de aanvrager (urlKey `fightclub-techhub`). Die naam mag nergens in Raderwerk-materiaal terugkomen. Aanbeveling: `organizationUpdate` met `name: "Raderwerk"` en `urlKey: "raderwerk"`. Dat behoudt de al geïnstalleerde Codex- en Cursor-app-users en de bestaande API-key. Vereist wel een expliciet "ja" omdat drie collega's admin zijn in dezelfde workspace.
2. **Test het issueplafond vóór alles.** Verwijder tien oude issues, lees `organization.createdIssueCount` opnieuw en probeer een nieuw issue aan te maken. Geeft verwijderen géén ruimte terug, stop dan met deze workspace en maak een verse gratis workspace "Raderwerk" (plan B: nieuwe app-installaties en een nieuwe API-key nodig).
3. **Verwijder de rest van de legacy-inhoud** (≈130 issues, 2 projecten, 1 initiative) pas na stap 2 en na een export van de titels.
4. **Bepaal wie lid blijft.** Collega's die geen rol hebben in Raderwerk, uit de workspace halen of laten staan; op Free kost een seat niets maar iedereen is admin en ziet alles.

**B. GitHub**

5. Maak de repo's aan onder `github.com/raderwerk`: `duinbrand-theme`, `duinbrand-erp-bridge`, `hovex-site`, `wildernest-site`, `wildernest-crm-bridge`, `raderwerk-site`, `raderwerk-os` (voor scripts en het orchestratorcontract).
6. Koppel de GitHub-integratie in Linear aan de org `raderwerk`, zodat branches, PR's en commits native aan issues hangen.

**C. Agents activeren**

7. **Codex:** koppel het ChatGPT-account in het Linear-profiel (Codex vraagt daar zelf om in zijn eerste antwoord), en maak een Codex cloud-environment aan per repo. Zonder environment faalt Codex met "failed to start".
8. **Cursor:** koppel het Cursor-account via `cursor.com/linear`, zet Cloud Agents aan en bevestig dat het Cursor-plan betaald is met usage-based billing. Is dat niet zo, dan valt de native dev-rol weg en moet de orchestrator hem overnemen.
9. **Agent guidance instellen** (Settings → Agents → Additional guidance), workspaceniveau plus per team, met de tekst uit 6.1. Dit is de enige knop waarmee we Codex en Cursor sturen zonder eigen code.
10. **Claude als Linear-agent:** nog niet mogelijk (Anthropic levert geen Linear-agent-app). Tot die tijd draait de orchestrator onder de persoonlijke API-key. Zodra de app er is: installeren met `actor=app` en de rollen DEV, REVIEWER en QA omzetten van label naar echte delegatie.

**D. Templates en bouw**

11. Maak **met de hand** in de UI één issue-template, één projecttemplate en één documenttemplate. De orchestrator leest daarna hun `templateData` uit en gebruikt die vorm als mal. Zonder deze stap is templatecreatie giswerk.
12. Zet de defaulttemplates per team (`defaultTemplateForMembersId`) nadat de templates bestaan.

**E. Buiten Linear**

13. Registreer `raderwerk.ai` en/of `raderwerk.agency` (beide waren vrij op 02-09-2026).
14. Maak een hostingaccount voor preview-deploys en koppel de GitHub-org.
15. Maak een Shopify development store voor Duinbrand.
16. **Controleer de vier verzonnen merknamen** (Duinbrand, Hovex, Wildernest, en Raderwerk zelf) op bestaande bedrijven en merken voordat er iets publiek gaat. Dit ontwerp heeft die controle niet gedaan.
17. Bepaal of er publiek gepubliceerd wordt (echte site, echte social-accounts) of alleen op preview-URL's. Publiceren brengt de transparantieplicht en merkrisico's met zich mee die in `risico/juridisch` en `risico/merk` beschreven staan.

**F. Bewust niet doen**

18. Geen upgrade naar Basic of Business en geen AI-credits kopen: dit ontwerp is expliciet Free-plan. Wil je Linear-coding-sessions, triage rules of Loops, dan is dat een ander ontwerp.
19. Geen advertentieaccounts, geen e-mailverzending, geen contact met echte personen.

---

## 11. Risico's en faalwijzen van deze hoek

Gesorteerd op impact.

1. **Het issueplafond kan de workspace stukmaken.** Als `createdIssueCount` cumulatief telt en verwijderen geen ruimte teruggeeft, is er na de legacy-import nog ruimte voor ~119 issues en past dit ontwerp niet. Dit is de eerste test in de checklist en het enige echte go/no-go-moment. Mitigatie: verse workspace; kosten: opnieuw installeren van Codex en Cursor.
2. **Elke agentactie draagt de naam van een mens.** De orchestrator schrijft met de persoonlijke API-key, dus in de historie staat de aanvrager als auteur van agent-comments én als goedkeurder bij de poort. Precies op het punt waar het bewijs telt ("een mens heeft goedgekeurd") is het bewijs zwak. De handtekeningconventie helpt een lezer, maar houdt geen auditor tegen. Echte oplossing: een eigen OAuth-app met `actor=app` (bouwwerk, plus een webhook-ontvanger vanwege de 10-secondenregel) of wachten op een Claude-agent-app. Dit is de zwaarste concessie van dit ontwerp.
3. **De native dev-lijn hangt aan accounts van derden.** Codex en Cursor antwoorden nu allebei met "koppel eerst je account". Blijkt het Cursor-plan niet betaald, of ontbreekt een Codex-environment, dan valt de hele native uitvoeringslaag weg en wordt dit ontwerp stilletjes een orchestrator-ontwerp met extra stappen.
4. **Twee teams dwingen tot overladen states.** BUR heeft één vrijgavepoort voor vijf verschillende soorten "naar buiten". Verdwijnt het `gate/*`-label (bijvoorbeeld doordat een agent labels overschrijft in plaats van toevoegt), dan is niet meer te zien wát is goedgekeurd. Mitigatie: de orchestrator gebruikt uitsluitend `addedLabelIds`/`removedLabelIds`, nooit `labelIds`, en weigert een poort te openen zonder `gate/*`-label.
5. **`templateData` is ondocumenteerd.** Programmatisch aangemaakte templates kunnen stil kapot zijn (velden die Linear negeert). Mitigatie: eerst met de hand maken en uitlezen; daarna elke aangemaakte template één keer toepassen op een wegwerp-issue om te controleren wat er echt wordt ingevuld.
6. **Geen webhooks, dus poll-latentie.** Alles reageert binnen twee minuten, niet direct. Voor een agentsessie van Codex of Cursor zien we de voortgang alleen als we `agentSessions` uitlezen, en daar heeft de MCP geen gereedschap voor: dat moet via GraphQL. De orchestrator heeft dus twee API-oppervlakken nodig en kan niet MCP-only zijn.
7. **Wat Codex en Cursor doen, sturen we maar beperkt.** Buiten de agent guidance en repo-instructiebestanden hebben we geen greep op hun prompts, modelkeuze of kosten. Hun verbruik loopt buiten ons kostenboek om, dus de unit economics zijn per definitie incompleet zolang die lijn native is.
8. **Cycles op een team dat 24/7 doorwerkt zijn deels theater.** De cycle is hier vooral een WIP-limiet op de poortcapaciteit van één mens. Wordt die mens een dag niet wakker, dan stapelt alles zich op in gele states en zegt de cyclegrafiek niets meer. Mitigatie: de PM-agent stopt met nieuw werk starten zodra er meer dan zes issues in poortstates staan.
9. **Project- en initiative-updates zijn AI-geschreven gezondheidsoordelen.** `health: onTrack` betekent hier "een taalmodel vond van wel". Mitigatie: de update mag alleen `onTrack` claimen als elk actief issue in die week bewijs in het issue heeft; anders `atRisk`.
10. **Publiek werk voor fictieve klanten is een merkrisico en een juridisch randgeval.** Casusartikelen over verzonnen klanten kunnen als misleiding gelezen worden als het fictieve karakter niet overal expliciet is; AI-gegenereerde publieke content valt onder de transparantieplicht die sinds augustus 2026 geldt. Mitigatie: `risico/juridisch` verplicht de compliance-rol in de keten, en R-05 en R-06 maken het fictieve karakter expliciet onderdeel van de DoD.
11. **Geen triage rules op Free betekent dat de "voordeur" orchestrator-code is.** Precies de stap die het meest native had moeten zijn (aanvraag komt binnen, wordt automatisch geclassificeerd en gedelegeerd) is handwerk in onze eigen lus. De purist-hoek stopt hier tegen een plafond dat alleen met geld weggaat.
12. **Kwaliteit van tekst, design en campagnes heeft geen machinale poort.** Voor code is er CI en een tweede reviewer; voor een advertentietekst is er alleen het oordeel van een tweede model. De DoD-checklists in de templates zijn de enige rem, en checklists worden afgevinkt door dezelfde soort agent die ze moet halen ("vroege overwinning"). Mitigatie: de reviewer-rol mag nooit hetzelfde model zijn als de maker, en QA moet per criterium een link als bewijs geven, geen vinkje.
13. **Verwijderen is grotendeels onomkeerbaar.** Team-verwijdering heeft een herstelvenster, issue-verwijdering via de prullenbak ook, maar `permanentlyDelete` niet. De opruimregel "eerst exporteren, dan verwijderen" is de enige vangnet.
14. **Alles hangt aan één pollende orchestrator.** Valt die om, dan gebeurt er niets en merkt niemand het, want er is geen monitoring buiten Linear. Mitigatie: de orchestrator schrijft elke pollronde een tijdstempel in het Noodstop-issue; de FinOps-cron controleert 's ochtends of die tijdstempel vers is.

---

## Bijlage: bouwvolgorde

| Stap | Oppervlak | Waarom |
|---|---|---|
| 1. Workspace hernoemen, legacy verwijderen | GraphQL | MCP kan geen issues verwijderen |
| 2. Teams aanmaken (RDW, BUR) met alle instellingen | GraphQL `teamCreate` | Geen MCP-gereedschap voor teams |
| 3. Workflowstates aanmaken en de standaardstates archiveren | GraphQL `workflowStateCreate` / `workflowStateArchive` | Idem; archiveren kan pas als er geen issues in staan |
| 4. Labelgroepen en labels | GraphQL of MCP `create_issue_label` | Groepen vereisen `isGroup` + `parentId`, dus GraphQL is veiliger |
| 5. Projectlabels hernoemen en aanvullen | GraphQL | Geen delete beschikbaar |
| 6. Templates met de hand maken, uitlezen, dan programmatisch klonen | UI + GraphQL | `templateData` is ondocumenteerd |
| 7. Initiatives, projecten, mijlpalen | MCP of GraphQL | Beide kunnen dit |
| 8. Documenten (playbooks) | MCP `save_document` | Documenten hangen aan projecten |
| 9. Cycles | GraphQL `cycleCreate` (bestaan is in de schema-cheatsheet bevestigd, in een eerdere lane ontkend: één keer verifiëren) | Anders genereert Linear ze zelf uit de teaminstellingen |
| 10. Zaai-issues in batches van 20 | GraphQL `issueBatchCreate` | Atomair, en zuiniger met rate limits |
| 11. Agent skills | GraphQL `agentSkillCreate` | Geen MCP-gereedschap |
| 12. Agent guidance | UI | Geen API |
| 13. Droogloop 1 t/m 3 | orchestrator | Pas daarna is het systeem "aan" |
