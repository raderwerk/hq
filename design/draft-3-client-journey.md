# Raderwerk op Linear — ontwerp 3: de klantreis als besturingssysteem

Auteur: architect 3 van 3. Datum: 2026-09-02. Invalshoek: **client journey first**. Alles in deze workspace is gebouwd rond wat de (fictieve) klant meemaakt: lead, discovery, voorstel, akkoord, kickoff, sprints, QA, oplevering, factuur, retainer. Elke stap laat een aanklikbaar artefact achter in Linear, zodat iemand die niets van code weet het bord van links naar rechts kan lezen en begrijpt wat er gebeurde, wie het deed en waar een mens op de knop drukte.

Raderwerk is een zelfstandig, generiek digitaal bureau (web, design, content, ads, social) dat het bewijs moet leveren dat een door AI gerunde agency kan bestaan. Vier klanten, waarvan drie fictief en één Raderwerk zelf. Al het werk is echt: echte repositories onder github.com/raderwerk, echte sites, echte teksten, echte ontwerpen, echte campagne- en socialplannen. Niets is een mock-up. Alleen de opdrachtgevers zijn verzonnen, en er gaat geen enkel bericht naar een echt mens.

---

## 0. De reis in één regel

`Binnen -> Lead -> Gekwalificeerd -> Discovery -> Voorstel -> POORT 1 -> Kickoff -> Levering -> Klantacceptatie -> POORT 2 -> POORT 3 -> Afgerond -> Retainer`

Drie poorten, drie menselijke klikken per engagement. Daartussen doet de machine alles: scopen, schatten, plannen, ontwerpen, bouwen, schrijven, testen, reviewen, rapporteren, factuurconcept maken.

Elke stap laat precies één artefact achter dat je kunt aanklikken:

| Stap | Artefact in Linear | Vorm |
|---|---|---|
| Lead | Leadscorecard | comment op het lead-issue, vast formaat |
| Discovery | Discovery-verslag | **document** onder het project |
| Voorstel | Voorstel met prijs en planning | **document** onder het project |
| Poort 1 | Beslisblok + akkoordregel | comment + labelwissel + statuswissel |
| Kickoff | Project met milestones en issues | **project** + projectupdate |
| Sprint | PR-link, preview-URL, screenshots | **attachments** op de issues |
| QA | QA-rapport met bewijs per acceptatiecriterium | comment volgens template |
| Oplevering | Opleverrapport | **document** + projectupdate |
| Poort 2 | Beslisblok + akkoordregel | comment + labelwissel |
| Factuur | Factuurconcept met urenspecificatie | **document** |
| Poort 3 | Beslisblok + akkoordregel | comment + labelwissel |
| Retainer | Maandelijkse projectupdate | **projectupdate** op het retainerproject |

---

## 1. Harde randvoorwaarden en wat ze afdwingen

Linear blijft op **Free**. Dat is geen detail maar de vormgevende beperking van dit ontwerp.

| Beperking (Free) | Gevolg voor dit ontwerp |
|---|---|
| Maximaal 2 teams | De hele agency past in twee borden: **Klantreis** (wat de klant meemaakt) en **Werkvloer** (waar het gemaakt wordt). Geen team per discipline; de discipline zit in labels. |
| Maximaal 250 issues | Eén issue per deliverable, nooit per handeling. Stappen worden checklists, geen sub-issues. Zie hoofdstuk 9. |
| Uploads max 10 MB | Screenshots, ontwerpen en PDF's worden gelinkt (attachment naar preview-URL of repo), niet geüpload. |
| Geen customer requests (`customersEnabled=false`) | De "klant" bestaat als **label + initiative + project**, niet als Linear-klantobject. Klantcommunicatie is een comment in een vast formaat op het engagement-issue. |
| Geen guests, geen Asks, geen triage rules, geen SLA's, geen Loops | Alle automatiek komt van de orchestrator (Claude Code headless, poll elke 2 minuten). Er is geen enkele knop in Linear die vanzelf iets doet. |
| Geen coding sessions (Basic+) | Code wordt geschreven door de native agents Codex en Cursor via `Issue.delegate`, en door Claude Code lokaal onder de orchestrator. |
| Alle gebruikers zijn admin | Rechten kunnen niets afdwingen. De poorten worden afgedwongen door **contract + controle achteraf**, niet door permissies. Zie hoofdstuk 8 en 12. |
| Triage-inbox is wél beschikbaar | Beide teams krijgen `triageEnabled: true`. De triage-inbox van Klantreis is de voordeur van het bureau. |
| Cycles, projects, milestones, labels, templates, documents, project/initiative updates, agent-delegatie zijn beschikbaar | Dit is de volledige gereedschapskist die dit ontwerp gebruikt. |

Eén niet-onderhandelbare ontwerpregel volgt uit hoe Linear een bord ordent: **kolommen worden gesorteerd op statustype (triage, backlog, unstarted, started, completed, canceled) en pas daarbinnen op positie.** Wie een poort het type `unstarted` geeft, ziet die kolom links van "Discovery" opduiken en de reis leest niet meer van links naar rechts. Daarom krijgen **alle stappen tussen Discovery en Afgerond het type `started`**, inclusief de drie poorten. Een poort is herkenbaar aan de naam (begint met `Poort`), de rode kleur en het label `poort/*`, niet aan het statustype. `WorkflowState.type` is na aanmaak niet meer te wijzigen, dus dit moet in één keer goed.

---

## 2. De twee teams

### 2.1 Team KR — "Klantreis"

- **Key:** `KR`
- **Naam:** Klantreis
- **Icoon/kleur:** `#5E6AD2`
- **Doel:** één issue per engagement en per klantrelatie, dat de hele reis aflegt. Dit bord is de demo. Een niet-technische kijker opent dit bord, leest de kolommen van links naar rechts en ziet vier klanten door dezelfde molen gaan. Hier staan géén taken; taken staan op Werkvloer.
- **Wat hier hoort:** leads, engagements (één per fase/opdracht), account-issues (retainer), facturen, klantcommunicatie, alle drie de poorten.
- **Wat hier niet hoort:** bugs, features, contentstukken, designtaken. Die horen op Werkvloer.
- **Cycles:** **nee** (`cyclesEnabled: false`). Een klantreis is niet in sprints van twee weken te persen en zou de kolommen vervuilen met sprintstatistiek.
- **Triage:** **ja** (`triageEnabled: true`, `requirePriorityToLeaveTriage: false`). De triage-inbox is de voordeur: elk nieuw klantsignaal landt hier.
- **Schattingsschaal:** `tShirt` (XS/S/M/L/XL), `issueEstimationAllowZero: false`, `issueEstimationExtended: false`. Op dit bord schat je de **omvang van het engagement**, niet de uren. Vertaling naar geld staat in het Kostenboek: XS < €500, S €500-1.500, M €1.500-5.000, L €5.000-15.000, XL > €15.000 (rekentarief Raderwerk: €110/u uitvoering, €150/u strategie).
- **Standaard prioriteit:** geen; de orchestrator zet Urgent zodra een issue in een poort staat.

**Workflowstatussen, in volgorde:**

| # | Naam | Type | Kleur | Betekenis | Wie zet hem |
|---|---|---|---|---|---|
| 1 | Binnen | `triage` | `#95A2B3` | Voordeur. Elk nieuw signaal: lead, klantverzoek, nieuwe fase. Ontstaat automatisch door `triageEnabled`. | mens of orchestrator |
| 2 | Lead | `backlog` | `#BEC2C8` | Signaal is een lead, nog niet gekwalificeerd. | Account-agent |
| 3 | Gekwalificeerd | `unstarted` | `#D0D6E0` | Leadscorecard staat erop, past binnen het profiel, wacht op start. | Account-agent |
| 4 | Discovery | `started` | `#5E6AD2` | Uitvragen, aannames, risico's, scope. Levert het discovery-verslag. | Strateeg |
| 5 | Voorstel | `started` | `#7C87F5` | Prijs, planning, deliverables, voorwaarden. Levert het voorsteldocument. | Voorstelschrijver |
| 6 | **Poort 1 · Voorstel akkoord** | `started` | `#F2453D` | **Menselijke poort.** Voorstel mag pas "verstuurd" heten na akkoord. | mens |
| 7 | Kickoff | `started` | `#26B5CE` | Project, milestones en werkvloer-issues worden aangemaakt. | PM-agent |
| 8 | Levering | `started` | `#F2C94C` | Sprints lopen op Werkvloer. Deze status spiegelt de voortgang. | PM-agent (rollup) |
| 9 | Klantacceptatie | `started` | `#4EA7FC` | Alles klaar op preview, de "klant" beoordeelt. | QA-agent |
| 10 | **Poort 2 · Oplevering akkoord** | `started` | `#F2453D` | **Menselijke poort.** Live zetten, publiceren, opleverbericht. | mens |
| 11 | **Poort 3 · Factuur akkoord** | `started` | `#F2453D` | **Menselijke poort.** Factuurconcept en urenspecificatie. | mens |
| 12 | Retainer | `started` | `#0F7B6C` | Standplaats van het account-issue per klant; blijft open zolang de relatie loopt. | PM-agent |
| 13 | Afgerond | `completed` | `#0F783C` | Opgeleverd én gefactureerd. | orchestrator na Poort 3 |
| 14 | Niet doorgegaan | `canceled` | `#95A2B3` | Lead afgewezen of engagement gestopt, met reden in het laatste comment. | mens |
| 15 | Dubbel | `canceled` | `#95A2B3` | Duplicaat. | orchestrator |

### 2.2 Team WV — "Werkvloer"

- **Key:** `WV`
- **Naam:** Werkvloer
- **Icoon/kleur:** `#0F7B6C`
- **Doel:** al het uitvoerende werk van alle disciplines, voor alle klanten, in één stroom. Eén issue = één deliverable met acceptatiecriteria.
- **Cycles:** **ja** (`cyclesEnabled: true`, `cycleDuration: 2` weken, `cycleStartDay: 1` (maandag), `upcomingCycleCount: 2`, `cycleCooldownTime: 0`, `cycleLockToActive: false`). De sprint is een echte sprint: de PM-agent vult de aankomende cyclus bij kickoff en aan het einde van elke cyclus verschijnt een cyclusrapport als comment op het engagement-issue.
- **Triage:** **ja**. Hier landt werk dat niet uit een kickoff komt: bugmeldingen, spoedverzoeken, incidenten.
- **Schattingsschaal:** `fibonacci` (1, 2, 3, 5, 8), `issueEstimationAllowZero: false`, `issueEstimationExtended: false`. Vertaling: 1 = < 1 uur, 2 = 1-2 uur, 3 = 2-4 uur, 5 = 4-8 uur, 8 = 8-16 uur. **Boven 8 splitsen**, want een issue van meer dan 16 uur is geen deliverable maar een project.
- **Standaardschatting bij aanmaken:** `defaultIssueEstimate: 2`.

**Workflowstatussen, in volgorde:**

| # | Naam | Type | Kleur | Betekenis | Wie zet hem |
|---|---|---|---|---|---|
| 1 | Binnen | `triage` | `#95A2B3` | Ongesorteerd werk. | iedereen |
| 2 | Backlog | `backlog` | `#BEC2C8` | Gescoped, nog niet ingepland. | PM-agent |
| 3 | Wacht op klantinput | `backlog` | `#F2994A` | Geblokkeerd op een antwoord dat alleen de klant kan geven. Vraag staat als comment. | elke agent |
| 4 | Ingepland | `unstarted` | `#D0D6E0` | Zit in de actieve of aankomende cyclus, heeft een agent-label. | PM-agent |
| 5 | In uitvoering | `started` | `#5E6AD2` | Een agent werkt eraan; `delegate` of `agent/*`-label is gezet. | uitvoerende agent |
| 6 | Agentreview | `started` | `#B59AFF` | Tweede agent (ander model) beoordeelt het werk. | reviewagent |
| 7 | **Poort · Merge of publicatie** | `started` | `#F2453D` | **Menselijke poort.** PR mergen, content publiceren, campagne activeren. | mens |
| 8 | QA op preview | `started` | `#4EA7FC` | QA-agent loopt de acceptatiecriteria na op de preview-omgeving en schrijft het QA-rapport. | QA-agent |
| 9 | Klantacceptatie | `started` | `#F2C94C` | Wacht op oordeel namens de klant; gekoppeld aan het engagement-issue op Klantreis. | PM-agent |
| 10 | Klaar | `completed` | `#0F783C` | Acceptatiecriteria afgevinkt met bewijs. | QA-agent |
| 11 | Geannuleerd | `canceled` | `#95A2B3` | Vervallen. | mens |
| 12 | Dubbel | `canceled` | `#95A2B3` | Duplicaat. | orchestrator |

**Waarom "Poort · Merge of publicatie" vóór "QA op preview" staat:** de agent bouwt op een feature branch, een tweede agent reviewt, en pas als een mens de PR mergt ontstaat er een preview-omgeving met het samengevoegde resultaat waarop QA de acceptatiecriteria echt kan controleren. Dat maakt de menselijke handeling ook zichtbaar midden in het uitvoerende proces, niet alleen aan de rand.

---

## 3. Labeltaxonomie

Alle labels worden **workspace-breed** aangemaakt (`issueLabelCreate` zonder `teamId`), zodat ze op beide teams werken. Groepen zijn labels met `isGroup: true`; de leden krijgen `parentId` van de groep. Linear staat per groep één label per issue toe, wat precies is wat we willen voor klant, dienst, soort en risico.

### 3.1 `klant` — voor wie doen we dit (groep `#5E6AD2`)
| Label | Kleur | Gebruik |
|---|---|---|
| `klant/vloedlijn` | `#4EA7FC` | DTC-webshop, Shopify + ERP |
| `klant/kantelbeer` | `#EB5757` | B2B industrie, dealercatalogus |
| `klant/trekvogel` | `#0F7B6C` | Reizen en boekingen, CMS + CRM |
| `klant/raderwerk` | `#5E6AD2` | Eigen merk, site, content, ads, social |
| `klant/prospect` | `#BEC2C8` | Nog geen klant; leads voor akkoord |

### 3.2 `dienst` — welke dienstlijn (groep `#26B5CE`)
| Label | Kleur | Gebruik |
|---|---|---|
| `dienst/web` | `#26B5CE` | Bouw, integratie, techniek |
| `dienst/design` | `#B59AFF` | Visueel ontwerp, designsysteem, UI |
| `dienst/content` | `#F2C94C` | Teksten, artikelen, SEO-content |
| `dienst/ads` | `#F2994A` | Zoek-, display- en socialadvertenties |
| `dienst/social` | `#FC7840` | Organische kanalen, kalenders |
| `dienst/strategie` | `#5E6AD2` | Discovery, positionering, roadmap, meten |

### 3.3 `soort` — wat voor werk (groep `#BEC2C8`)
`soort/lead`, `soort/engagement`, `soort/voorstel`, `soort/bug`, `soort/feature`, `soort/contentstuk`, `soort/designtaak`, `soort/campagne`, `soort/socialkalender`, `soort/qa-rapport`, `soort/incident`, `soort/onderzoek`, `soort/factuur`, `soort/retainerronde`, `soort/bureau` (intern werk aan Raderwerk zelf). Kleur: allemaal `#BEC2C8` behalve `soort/bug` `#EB5757`, `soort/incident` `#F2453D`, `soort/factuur` `#0F783C`.

### 3.4 `poort` — goedkeuring (groep `#F2453D`)
| Label | Kleur | Betekenis |
|---|---|---|
| `poort/voorstel` | `#F2453D` | Staat in Poort 1, wacht op mens |
| `poort/oplevering` | `#F2453D` | Staat in Poort 2 |
| `poort/factuur` | `#F2453D` | Staat in Poort 3 |
| `poort/merge` | `#F2453D` | Staat in de merge-poort op Werkvloer |
| `poort/publicatie` | `#F2453D` | Publiceren of live zetten van content of campagne |
| `poort/akkoord-gegeven` | `#0F783C` | Mens heeft akkoord gegeven; **alleen een mens mag dit label plaatsen** |
| `poort/afgekeurd` | `#F2994A` | Mens heeft afgekeurd; reden staat in het comment eronder |

### 3.5 `risico` (groep `#F2994A`)
| Label | Kleur | Betekenis en gevolg |
|---|---|---|
| `risico/laag` | `#BEC2C8` | Standaard. |
| `risico/midden` | `#F2C94C` | Reviewagent is verplicht een ander model dan de uitvoerder. |
| `risico/hoog` | `#EB5757` | Dubbele review (Claude én Codex) plus expliciete menselijke poort, ook als de stap normaal geen poort heeft. |
| `risico/klantdata` | `#F2453D` | Er is echte persoonsdata in het spel. Agents werken alleen met testdata; productiedata is read-only en verlaat de omgeving niet. |
| `risico/publiek-zichtbaar` | `#FC7840` | Resultaat komt publiek online. Verplicht: menselijke eindredactie plus AI-transparantievermelding (AI Act art. 50). |
| `risico/geen-bewijs` | `#F2994A` | QA-agent zet dit als een acceptatiecriterium is afgevinkt zonder aanklikbaar bewijs. Blokkeert "Klaar". |

### 3.6 `agent` — routering (groep `#4CB782`)
| Label | Kleur | Model/tool | Waarvoor |
|---|---|---|---|
| `agent/fable` | `#4CB782` | Claude Fable 5.1 | Scopen, oordelen, voorstellen, review, alles waar taalgevoel en afweging telt |
| `agent/opus` | `#26B5CE` | Claude Opus 5 | Uitvoering: bouwen, ontwerpen, plannen |
| `agent/sonnet` | `#95A2B3` | Claude Sonnet 5 | Volumewerk: content, kalenders, samenvattingen, logs |
| `agent/codex` | `#0F783C` | Codex (GPT-5.6 Sol, xhigh) via `Issue.delegate` | Dev-lane 1 en tweede reviewer |
| `agent/cursor` | `#B59AFF` | Cursor (Grok 4.6) via `Issue.delegate` | Dev-lane 2, parallel werk |
| `agent/mens` | `#F2453D` | — | Alleen een mens kan dit; agents laten het staan |

### 3.7 `schakelaar` — noodrem en toestand (groep `#EB5757`)
| Label | Kleur | Effect |
|---|---|---|
| `schakelaar/pauze` | `#EB5757` | De orchestrator slaat dit issue over. Werkt binnen één pollronde (2 min). |
| `schakelaar/pauze-alles` | `#F2453D` | Staat op het vastgezette controle-issue `KR-1`. Zolang dit label er staat, doet de orchestrator **niets** behalve loggen. |
| `schakelaar/budget-op` | `#F2994A` | Kostenplafond voor dit issue of deze dag bereikt; alleen lezen, geen nieuwe runs. |
| `schakelaar/wacht-op-mens` | `#F2C94C` | Er is een vraag gesteld aan een mens buiten een poort om; agents blijven af tot het label weg is. |

### 3.8 `facturatie` (groep `#95A2B3`)
`facturatie/fixed-price`, `facturatie/nacalculatie`, `facturatie/retainer`, `facturatie/garantie` (herstelwerk, niet factureerbaar), `facturatie/intern` (Raderwerk zelf, niet factureerbaar). Kleur `#95A2B3`, behalve `facturatie/garantie` `#F2994A`.

**Waarom geen projectlabels:** `projectLabelCreate` bestaat wel, maar projectlabels leven in een aparte namespace en zijn niet zichtbaar op issues. Klantherkenning gebeurt met issuelabels plus de projectnaam; dat is genoeg en scheelt onderhoud.

---

## 4. Initiatives, projects en milestones

### 4.1 Initiatives = klantrelaties, plus één voor de machine

Een initiative is het enige niveau in Linear dat over teams heen gaat en een eigen updatestroom heeft (`initiativeUpdateCreate`). Dat maakt hem geschikt als **de relatie met één klant**: alle engagements, alle dienstlijnen, alle jaren. Een niet-technische kijker klikt op "Vloedlijn" en leest de hele geschiedenis van die klant als een tijdlijn van updates. Dienstlijnen worden géén initiatives; die zitten in labels, anders valt één klant uiteen over vijf tijdlijnen.

| Initiative | Eigenaar | Beschrijving | Updateritme |
|---|---|---|---|
| **Vloedlijn** | Youp (lead), Account-agent (uitvoerend) | DTC-outdoorlabel, Shopify plus ERP. Relatie sinds september 2026. | Elke vrijdag, door de PM-agent |
| **Kantelbeer** | Youp | B2B-fabrikant van hef- en kantelsystemen. Merksite met dealercatalogus. | Elke vrijdag |
| **Trekvogel** | Youp | Slow-travel treinreizen. CMS-site met CRM-koppeling. | Elke vrijdag |
| **Raderwerk** | Youp | Het eigen merk als klant: site, content, ads, social. Etalage en proeftuin tegelijk. | Elke vrijdag |
| **Het raderwerk zelf** | Youp | De machine: playbooks, rolcontracten, poortbeleid, kostenboek, meetresultaten. Geen klant, wel het belangrijkste product. | Elke maandag (weekrapport) |

Initiative-update bevat vast: stand van zaken in drie zinnen, wat er deze week is opgeleverd met links, waar het bureau op wacht, kosten deze week, aantal menselijke handelingen deze week.

### 4.2 Projects = engagements

Een project is één engagement met een begin en een eind, of één doorlopende retainer. **Elk project hangt aan beide teams** (`teamIds: [KR, WV]`), zodat het engagement-issue en alle werkvloer-issues in dezelfde projectweergave zitten. Dat is de kern van deze invalshoek: de projectpagina is het enige scherm dat je een klant zou laten zien.

Alle projecten hebben `leadId` = Youp (een app-user kan geen project lead zijn) en noemen in de projectbeschrijving expliciet welke agent verantwoordelijk is. Projectstatus wordt gezet via de workspace-projectstatussen (Backlog / Planned / In Progress / Completed).

| # | Project | Initiative | Doel (één zin) | Milestones |
|---|---|---|---|---|
| P1 | **Vloedlijn — Fase 1: shop en ERP verbonden** | Vloedlijn | Voorraad en orders lopen automatisch tussen webshop en ERP, zonder handwerk, met bewijs dat het klopt. | M1 Discovery en datacontract · M2 Koppeling werkt op staging · M3 Winkelervaring bijgewerkt · M4 QA, acceptatie en oplevering |
| P2 | **Vloedlijn — Retainer** | Vloedlijn | Doorlopend onderhoud, kleine verbeteringen en maandrapportage. | M1 Ronde oktober · M2 Ronde november · M3 Ronde december |
| P3 | **Kantelbeer — Merksite en dealercatalogus** | Kantelbeer | Eén site waar een inkoper in drie klikken het juiste systeem en de dichtstbijzijnde dealer vindt. | M1 Discovery en informatiestructuur · M2 Designsysteem · M3 Site en catalogus op preview · M4 Toegankelijkheid, QA en oplevering |
| P4 | **Kantelbeer — Zichtbaarheid B2B** | Kantelbeer | Content, SEO en LinkedIn zodat inkopers Kantelbeer vinden voordat ze een dealer bellen. | M1 Zoekwoorden en contentplan · M2 Acht teksten NL/EN · M3 Campagne- en socialplan |
| P5 | **Trekvogel — Boekingssite met CMS en CRM** | Trekvogel | Reizigers vinden en vragen een reis aan; elke aanvraag staat schoon in het CRM. | M1 Discovery en contentmodel · M2 CMS en twaalf reizen · M3 Zoeken, filteren, aanvragen · M4 CRM-sync, QA en oplevering |
| P6 | **Trekvogel — Seizoenscampagne** | Trekvogel | Eén seizoen, één verhaal, over site, ads en social heen. | M1 Concept en beeldrichtlijn · M2 Landingspagina's · M3 Campagne- en socialplan |
| P7 | **Raderwerk — Merk en site** | Raderwerk | raderwerk.ai staat online, legt uit hoe het bureau werkt en toont vier cases. | M1 Merk en tokens · M2 Site live op preview · M3 Cases en transparantiepagina · M4 Publicatie |
| P8 | **Raderwerk — Contentmotor en social** | Raderwerk | Wekelijks een artikel en een socialritme die het bewijs zelf documenteren. | M1 Contentplan en tone of voice · M2 Zes artikelen · M3 Vier weken socialkalender |
| P9 | **Het raderwerk — bureau-OS** | Het raderwerk zelf | De werking van het bureau: playbooks, rolcontracten, poortbeleid, kostenboek, controlescripts. | M1 Playbooks compleet · M2 Poortcontrole aantoonbaar · M3 Kostenboek per issue · M4 Drie droogloopruns geslaagd |

`P9` is ook de **thuisbasis van alle playbook-documenten** (zie hoofdstuk 6): `documentCreate` accepteert `projectId` gewoon, terwijl `initiativeId` in het schema als intern staat gemarkeerd. Documenten hangen dus aan projecten, niet aan initiatives.

### 4.3 Cycles op Werkvloer

Cyclus 1 start maandag 2026-09-07, duur 2 weken. Naamgeving laat Linear zelf doen. De PM-agent vult uitsluitend de **aankomende** cyclus; de actieve cyclus wordt niet meer bijgevuld behalve door een mens. Aan het eind van elke cyclus schrijft de PM-agent één comment per lopend engagement-issue: wat af is, wat doorschuift, en waarom.

---

## 5. Templates

Alle templates worden aangemaakt met `templateCreate`. Voor issue-templates die op beide borden bruikbaar moeten zijn, laat je `teamId` weg (workspace-breed). `templateData` is een ongetypeerde JSON-blob; **maak eerst één template met de hand in de UI, lees `template(id) { templateData }` uit en hergebruik precies die sleutelvorm.** De vorm die de app in de praktijk gebruikt is `{"title": "...", "description": "<markdown>", "labelIds": [...], "priority": n, "estimate": n, "stateId": "...", "assigneeId": null}`.

Alle templates delen drie regels:
1. De omschrijving eindigt altijd met een **Definition of Done** als checklist.
2. Elke DoD-regel eist **aanklikbaar bewijs**: een PR, een preview-URL, een screenshotlink, een document of een testuitvoer. Een vinkje zonder link telt niet en levert `risico/geen-bewijs` op.
3. Bovenaan staat een **Contextblok** met vaste velden, zodat een agent nooit hoeft te raden.

### 5.1 Issue-template `Lead` (team KR)

```markdown
## Context
- Bedrijf:
- Sector:
- Bron van de lead: (website / doorverwijzing / netwerk / inbound e-mail)
- Contactmoment:
- Wat vraagt de klant in eigen woorden:

## Leadscorecard (in te vullen door de Account-agent)
| Criterium | Score 0-5 | Toelichting |
|---|---|---|
| Past binnen ons profiel (web/design/content/ads/social) | | |
| Budgetindicatie realistisch | | |
| Urgentie en tijdlijn | | |
| Complexiteit en risico | | |
| Kans op een doorlopende relatie | | |
| **Totaal (0-25)** | | |

Ondergrens: minder dan 12 punten betekent afwijzen met reden. 12 tot 17 betekent doorvragen. 18 of meer betekent discovery starten.

## Voorstel voor vervolg
- Aanbevolen dienstlijn(en):
- Aanbevolen engagementomvang (XS/S/M/L/XL):
- Eerste inschatting bandbreedte in euro:
- Grootste onzekerheid:

## Definition of Done
- [ ] Scorecard volledig ingevuld met toelichting per regel
- [ ] Aanbeveling doorgaan of afwijzen, met één zin motivatie
- [ ] Bij doorgaan: engagement-issue aangemaakt en gekoppeld als "relates to"
- [ ] Bij afwijzen: status Niet doorgegaan en een afwijsbericht als concept in het comment
- [ ] Label `klant/*` en `dienst/*` gezet
```

### 5.2 Issue-template `Engagement` (team KR) — het hart van de reis

```markdown
## Wat de klant wil bereiken
(één alinea, in de woorden van de klant, geen jargon)

## Wat wij gaan doen
(drie tot vijf bullets, elk een concreet resultaat)

## Wat wij niet doen
(expliciete uitsluitingen; hier voorkom je de helft van alle discussies)

## Kaders
- Klant:
- Dienstlijnen:
- Omvang (t-shirt):
- Indicatie in euro:
- Gewenste opleverdatum:
- Repository/omgeving:
- Projectlink:

## De reis en de artefacten
- [ ] Discovery-verslag (document onder het project)
- [ ] Voorstel met prijs en planning (document onder het project)
- [ ] Poort 1: menselijk akkoord op het voorstel
- [ ] Project met milestones en werkvloer-issues met acceptatiecriteria
- [ ] Sprintrapport per cyclus als comment
- [ ] QA-rapport met bewijs per acceptatiecriterium
- [ ] Poort 2: menselijk akkoord op de oplevering
- [ ] Opleverrapport (document) en opleverbericht als concept
- [ ] Poort 3: menselijk akkoord op de factuur
- [ ] Factuurconcept met urenspecificatie (document)

## Definition of Done
- [ ] Alle drie de poorten aantoonbaar door een mens gepasseerd (`poort/akkoord-gegeven` drie keer in de history)
- [ ] Elk werkvloer-issue in dit project staat op Klaar of Geannuleerd met reden
- [ ] Opleverrapport en factuurconcept bestaan als document onder het project
- [ ] Kosten van dit engagement staan in het Kostenboek
- [ ] Aantal menselijke handelingen geteld en genoteerd in het slotcomment
```

### 5.3 Issue-template `Voorstel` (team KR)

```markdown
## Aanleiding
(twee zinnen: wie vroeg wat, wanneer)

## Ons voorstel
| Onderdeel | Wat je krijgt | Omvang | Prijs |
|---|---|---|---|
| | | | |

Totaal excl. btw:
Geldig tot:

## Planning
| Milestone | Klaar op | Wat je dan kunt zien |
|---|---|---|

## Aannames
(elk punt dat als het niet klopt de prijs verandert)

## Wat wij van jou nodig hebben
(toegangen, materiaal, beslissingen, met een datum)

## Voorwaarden die er hier toe doen
- Inzet van AI: welke stappen door modellen worden gedaan, wie eindredactie voert en wie eindverantwoordelijk is.
- Acceptatie: acceptatiecriteria staan per deliverable in Linear; acceptatie gebeurt op de previewomgeving.
- Meerwerk: alleen na schriftelijk akkoord, als apart engagement.

## Definition of Done
- [ ] Voorsteldocument aangemaakt onder het project en gelinkt als attachment op dit issue
- [ ] Prijs herleidbaar naar uren maal tarief in het Kostenboek
- [ ] Alle aannames expliciet
- [ ] Issue staat in Poort 1 met label `poort/voorstel`, toegewezen aan een mens
- [ ] Beslisblok als comment geplaatst
```

### 5.4 Issue-template `Bug` (team WV)

```markdown
## Wat gaat er mis
(één zin, in gedrag: wat gebeurt er, wat zou er moeten gebeuren)

## Reproductie
1.
2.
3.

- URL/omgeving:
- Browser/apparaat:
- Rol van de gebruiker:
- Eerste keer gezien:

## Bewijs
(screenshot-link, logregel, netwerkrequest, tijdstempel)

## Acceptatiecriteria
- [ ] De reproductiestappen leiden niet meer tot het foute gedrag op preview
- [ ] Regressietest toegevoegd of handmatig testscenario beschreven
- [ ] Geen nieuw gedrag geïntroduceerd buiten de beschreven fout

## Definition of Done
- [ ] Oorzaak in één zin benoemd in een comment (geen "opgelost" zonder oorzaak)
- [ ] PR gelinkt als attachment, review door een ander model dan de uitvoerder
- [ ] Preview-URL gelinkt en QA-rapport geplaatst
- [ ] Kosten en runtime van deze run genoteerd
```

### 5.5 Issue-template `Feature` (team WV)

```markdown
## Wat moet er komen en waarom
(gebruikersdoel in één alinea; geen oplossing, wel het doel)

## Kaders
- Repository:
- Basisbranch:
- Omgeving voor preview:
- Afhankelijkheden:

## Aanpak in stappen
- [ ]
- [ ]
- [ ]

## Acceptatiecriteria (meetbaar, één regel per criterium)
- [ ] Gegeven ... wanneer ... dan ...
- [ ] Gegeven ... wanneer ... dan ...

## Buiten scope
-

## Definition of Done
- [ ] Alle acceptatiecriteria afgevinkt met een link naar bewijs
- [ ] PR gelinkt, groene CI, review door een tweede model
- [ ] Preview-URL werkt en is als attachment gekoppeld
- [ ] Geen geheimen in de repository, geen productiecredentials gebruikt
- [ ] Documentatie of README bijgewerkt als het gedrag verandert
```

### 5.6 Issue-template `Designtaak` (team WV)

```markdown
## Ontwerpvraag
(wat moet de gebruiker kunnen zien of doen, en welk gevoel hoort erbij)

## Kaders
- Merk en tokens:
- Bestaande componenten die je moet hergebruiken:
- Schermformaten:
- Toegankelijkheidseis: WCAG 2.2 AA

## Op te leveren
- [ ] Ontwerp als echte, opvraagbare pagina of component (HTML/CSS in de repo), geen plaatje
- [ ] Lichte en donkere variant, of expliciet beargumenteerd waarom niet
- [ ] Statenoverzicht: leeg, laden, fout, vol
- [ ] Designtokens toegevoegd of hergebruikt

## Acceptatiecriteria
- [ ] Contrastverhouding minimaal 4,5:1 voor tekst, aangetoond met een meting
- [ ] Werkt op 360px, 768px en 1440px zonder horizontaal scrollen
- [ ] Toetsenbordnavigatie volledig, focus zichtbaar

## Definition of Done
- [ ] Preview-URL van de component of pagina gelinkt
- [ ] Drie screenshots gelinkt (mobiel, tablet, desktop)
- [ ] Review door een tweede model op consistentie met het designsysteem
```

### 5.7 Issue-template `Contentstuk` (team WV)

```markdown
## Opdracht
- Onderwerp:
- Doelgroep en wat die persoon al weet:
- Doel van de tekst (informeren, overtuigen, converteren):
- Kanaal en plaats:
- Lengte:
- Zoekwoord of intentie (optioneel):
- Tone of voice: zie het merkdocument van de klant

## Verplichte bronnen
(elke feitelijke bewering heeft een bron; verzin geen cijfers)

## Acceptatiecriteria
- [ ] Kop, inleiding en afsluiting doen elk hun werk (haakje, belofte, vervolgstap)
- [ ] Geen bewering zonder bron; bronnen als voetnoot of link
- [ ] Zoekwoord natuurlijk verwerkt in kop, inleiding en één tussenkop
- [ ] Leesniveau past bij de doelgroep
- [ ] Metatitel (max 60 tekens) en metabeschrijving (max 155 tekens) meegeleverd

## Definition of Done
- [ ] Tekst staat als markdown in de repository, PR gelinkt
- [ ] Menselijke eindredactie gedaan en genoteerd (naam en tijdstip) voordat het publiek gaat
- [ ] Bij publiek zichtbare, informerende content: AI-transparantievermelding geregeld
- [ ] Label `risico/publiek-zichtbaar` gezet als het online komt
```

### 5.8 Issue-template `Campagne` (team WV, dienst/ads)

```markdown
## Campagnedoel
- Wat willen we bereiken (in één meetbare zin):
- Periode:
- Kanalen:
- Budgetindicatie (fictief, er wordt niets uitgegeven):
- Doelgroep en uitsluitingen:

## Structuur
| Campagne | Advertentiegroep | Zoekwoorden of doelgroep | Landingspagina |
|---|---|---|---|

## Advertenties
(minimaal drie varianten per advertentiegroep, met koppen en beschrijvingen voluit)

## Meten
- Conversiedefinitie:
- Wat we na week 1, 2 en 4 bekijken:
- Wanneer we stoppen of bijsturen:

## Acceptatiecriteria
- [ ] Elke advertentiegroep heeft minimaal drie advertenties en één landingspagina die bestaat
- [ ] Geen enkele bewering in een advertentie die de site niet waarmaakt
- [ ] Uitsluitingen en negatieve zoekwoorden ingevuld
- [ ] Plan bevat een expliciete stopregel

## Definition of Done
- [ ] Campagneplan als document onder het project
- [ ] Alle campagnes zouden **gepauzeerd** worden aangemaakt; er wordt in deze demo niets geactiveerd
- [ ] Label `poort/publicatie` als er ooit iets live zou gaan; activeren is altijd een menselijke handeling
```

### 5.9 Issue-template `Socialkalender` (team WV, dienst/social)

```markdown
## Kader
- Kanalen:
- Periode (aantal weken):
- Frequentie per kanaal:
- Vaste rubrieken:
- Wat we nooit doen (onderwerpen, toon, claims):

## Kalender
| Datum | Kanaal | Rubriek | Post (voluit) | Beeld | Link |
|---|---|---|---|---|---|

## Acceptatiecriteria
- [ ] Elke post staat voluit uitgeschreven, geen "idee voor een post"
- [ ] Elk beeld bestaat of is als concrete opdracht beschreven met bronbeeld
- [ ] Geen claim zonder dekking op de site
- [ ] Minimaal twee posts per week verwijzen naar echte content

## Definition of Done
- [ ] Kalender als markdown in de repository, PR gelinkt
- [ ] Menselijke eindredactie voor publicatie
- [ ] Er wordt niets automatisch geplaatst; plaatsen is altijd een menselijke handeling
```

### 5.10 Issue-template `QA-rapport` (team WV)

```markdown
## Wat is getest
- Issue(s):
- Preview-URL:
- Commit of PR:
- Datum en tijd:
- Getest door: (agent en model)

## Resultaat per acceptatiecriterium
| # | Criterium | Uitkomst | Bewijs |
|---|---|---|---|
| 1 | | geslaagd / gezakt | link |

## Gevonden problemen
| Ernst | Wat | Waar | Voorstel |
|---|---|---|---|

## Oordeel
GOEDGEKEURD of AFGEKEURD, met één zin motivatie.

## Definition of Done
- [ ] Elk acceptatiecriterium heeft een uitkomst én een link naar bewijs
- [ ] Bij afkeuring: een concreet herstelvoorstel per probleem
- [ ] Bij goedkeuring: geen enkel criterium zonder bewijs
- [ ] Randgevallen getest: leeg, veel, traag, fout, mobiel
```

### 5.11 Issue-template `Incident` (team WV)

```markdown
## Wat is er aan de hand
- Sinds:
- Wie merkt het:
- Impact (wat kan de klant of bezoeker nu niet):
- Ernst: 1 (alles plat) / 2 (kernfunctie stuk) / 3 (hinderlijk)

## Tijdlijn
| Tijd | Waarneming of handeling | Door |
|---|---|---|

## Hypothesen
| # | Hypothese | Hoe te toetsen | Uitkomst |
|---|---|---|---|

## Beperking van de schade
(wat is er gedaan om het nu draaglijk te maken)

## Definition of Done
- [ ] Oorzaak vastgesteld en met bewijs onderbouwd
- [ ] Herstel via de normale poort (merge door een mens), nooit rechtstreeks op productie
- [ ] Klantbericht als concept klaar, verzenden is een menselijke handeling
- [ ] Preventieve maatregel als apart issue aangemaakt
- [ ] Terugblik in drie regels: wat ging goed, wat ging fout, wat veranderen we
```

### 5.12 Issue-template `Factuur` (team KR)

```markdown
## Factuurgegevens
- Klant:
- Engagement:
- Periode:
- Factuurmodel: fixed-price / nacalculatie / retainer

## Specificatie
| Regel | Omschrijving | Aantal | Tarief | Bedrag |
|---|---|---|---|---|

Subtotaal excl. btw:
Btw 21%:
Totaal:

## Onderbouwing
- Link naar het opleverrapport:
- Link naar de geaccepteerde acceptatiecriteria:
- Afwijking ten opzichte van het voorstel en de reden:
- Niet gefactureerd (garantie of coulance) en waarom:

## Definition of Done
- [ ] Elke regel herleidbaar naar een issue op Werkvloer dat op Klaar staat
- [ ] Afwijking van het voorstel expliciet toegelicht
- [ ] Factuurconcept als document onder het project
- [ ] Issue staat in Poort 3 met label `poort/factuur`, toegewezen aan een mens
- [ ] Er wordt niets verstuurd; versturen is een menselijke handeling buiten Linear
```

### 5.13 Issue-template `Retainerronde` (team WV)

```markdown
## Maand
## Afgesproken omvang deze maand (uren of punten)
## Binnengekomen verzoeken
| # | Verzoek | Soort | Schatting | Wel/niet deze maand |
|---|---|---|---|---|

## Uitgevoerd
## Doorgeschoven en waarom
## Advies voor volgende maand

## Definition of Done
- [ ] Elk verzoek heeft een besluit met motivatie
- [ ] Verbruikte omvang tegenover afgesproken omvang genoemd
- [ ] Maandrapport als projectupdate geplaatst
```

### 5.14 Project-templates

**`Klantengagement`** (`type: "project"`): naam-placeholder `<Klant> — <Fase>`, beschrijving met de vaste kopjes Doel / Deliverables / Buiten scope / Kaders / Verantwoordelijke agent, vier milestones (Discovery en kaders, Bouw op staging, QA en acceptatie, Oplevering en facturatie), teamIds beide teams, lead Youp.

**`Retainer`** (`type: "project"`): naam-placeholder `<Klant> — Retainer`, beschrijving met Afgesproken omvang / Reactietijden / Wat valt eronder / Wat niet, drie maandmilestones, teamIds beide teams.

### 5.15 Document-templates

`type: "document"`, workspace-breed. Vijf stuks: **Discovery-verslag**, **Voorstel**, **Opleverrapport**, **Klantupdate**, **Factuurconcept**. Hun inhoud is één-op-één de markdown uit 5.1 tot 5.12 van het bijbehorende issue-template, uitgeschreven als leesbaar document zonder checkboxen, want een document is voor de klant en een issue is voor de machine.

Skelet van het **Opleverrapport**, omdat dat het document is dat de demo laat zien:

```markdown
# Oplevering — <Klant>, <Fase>

## Wat je nu hebt
(drie tot vijf bullets in gewone taal, elk met een link naar iets dat werkt)

## Wat er is afgesproken en wat we hebben gedaan
| Afspraak uit het voorstel | Resultaat | Bewijs |
|---|---|---|

## Hoe we het hebben getest
(korte samenvatting van het QA-rapport, met link)

## Wat er nog openstaat
| Punt | Waarom niet nu | Voorstel |
|---|---|---|

## Hoe je het beheert
(waar staat het, hoe pas je het aan, wie bel je)

## Verantwoording van de inzet
- Uitgevoerd door: (rollen en modellen)
- Menselijke controlemomenten: (drie poorten, met datum en tijd)
- Menselijke eindredactie op publieke teksten: (naam, datum)
```

---

## 6. Documenten: waar de werking van het bureau vastligt

Een Linear-document hangt aan precies één ouder. Omdat `documentCreate.initiativeId` in het schema als intern staat gemarkeerd, hangen **alle bureau-documenten aan project P9 "Het raderwerk — bureau-OS"** en alle klantdocumenten aan het bijbehorende klantproject.

### 6.1 Onder P9 (bureau-OS) — de playbooks

| Document | Waarover | Wie leest het | Wie onderhoudt het |
|---|---|---|---|
| **Zo werkt Raderwerk** | De hele klantreis in twaalf alinea's, met per stap: wie doet het, welk artefact ontstaat, waar de mens aan zet is. Dit is het eerste document dat je een bezoeker laat lezen. | iedereen | orchestrator, na elke wijziging in de workflow |
| **Poortbeleid** | Wat een poort is, welke er zijn, hoe je goedkeurt, hoe je afkeurt, wat de orchestrator daarna doet, en wat er gebeurt als iemand een poort overslaat. Zie hoofdstuk 8; dit document is de canonieke versie ervan. | iedereen | mens |
| **Rolcontracten** | Per agentrol één pagina: doel, model, trigger, invoer, uitvoer, wat mag, wat nooit mag, bij welke poort hij stopt, hoe hij ondertekent. Zie hoofdstuk 7. | agents en orchestrator | mens |
| **Kostenboek** | Het formaat van de kostenregistratie plus de lopende totalen. Zie 6.3. | mens | orchestrator, elke run |
| **Klantcommunicatiebeleid** | Toon, wat we wel en niet beloven, hoe we slecht nieuws brengen, hoe we AI-inzet benoemen, en de regel dat geen enkel bericht de workspace verlaat zonder menselijke handeling. | agents | mens |
| **Merk en tone of voice — Raderwerk** | Stem, woorden die we wel en niet gebruiken, voorbeelden goed/fout. | content- en socialagent | mens |
| **Definition of Done per dienstlijn** | De minimale DoD voor web, design, content, ads en social, waar elk issue-template op voortbouwt. | agents | mens |
| **AI-inzet en transparantie** | Welke modellen welk werk doen, welke stappen menselijke eindredactie hebben, hoe we dat publiek vermelden bij informerende content, en welke gegevens waar terechtkomen. | iedereen | mens |
| **Bureau-inrichting in Linear** | De technische inrichting: teams, statussen, labels, templates, en de exacte GraphQL-aanroepen om alles opnieuw op te bouwen. | wie het opnieuw bouwt | orchestrator |

### 6.2 Onder elk klantproject

`Discovery-verslag`, `Voorstel`, `Opleverrapport`, `Factuurconcept`, en bij retainers `Maandrapport <maand>`. Deze vijf zijn de documenten die je een klant zou geven. Ze worden aangemaakt door de agent die de stap uitvoert en gelinkt als attachment op het engagement-issue, zodat je vanaf het issue met één klik bij het artefact komt.

### 6.3 Formaat van het Kostenboek

Eén tabel in het document, één regel per run, en per run ook een comment op het issue zelf (zodat de kosten zichtbaar zijn waar het werk staat).

```markdown
| Run | Datum en tijd | Issue | Rol | Model | Invoer-tokens | Uitvoer-tokens | Cache-lees | Kosten USD | Kosten EUR | Wandkloktijd | Menselijke minuten | Resultaat |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0042 | 2026-09-08 09:14 | WV-31 | Developer A | Codex GPT-5.6 Sol xhigh | 184.201 | 12.940 | 96.400 | 4,12 | 3,55 | 11m20s | 0 | PR #7 geopend |
```

Regels: koers 1 EUR = 1,1590 USD (ECB 2026-09-01), tot een nieuwe koers wordt vastgelegd. Kosten per issue tellen op tot een **zacht plafond van €10** (label `schakelaar/budget-op` als waarschuwing plus comment) en een **hard plafond van €25** (orchestrator stopt met dat issue en vraagt een mens). Dagplafond €100 op werkdagen met droogloop of demo, €50 op andere dagen. De plafonds zijn er om te meten, niet om te besparen: het doel van de demo is bewijs, niet zuinigheid, dus overschrijding is toegestaan mits gelogd en zichtbaar op het controle-issue.

---

## 7. De agentbezetting

### 7.1 Hoe identiteit werkt op Free

Er zijn drie soorten uitvoerders in deze workspace:

1. **Native Linear-agents** met een eigen app-user: **Codex** en **Cursor**. Zij worden aangesproken via `Issue.delegate` (naast een menselijke `assignee`). Hun activiteiten verschijnen als Agent Session op het issue en zijn onmiskenbaar van hen. Kosten geen seat.
2. **De orchestrator**: Claude Code headless, draait op de machine van de aanvrager, praat met Linear via de persoonlijke API-sleutel. **Alles wat de orchestrator schrijft, verschijnt op naam van de aanvrager.** Daarom onderschrijft elke agentrol zijn comments met een vaste signatuur, en houdt de orchestrator een eigen logboek bij van elke schrijfactie (zie hoofdstuk 8 en 12).
3. **De mens** (Youp): keurt goed, mergt, publiceert, verstuurt.

Zodra Anthropic een Linear-agent uitbrengt, of zodra er een eigen OAuth-app met `actor=app` is geregistreerd, verhuist categorie 2 naar categorie 1 en verdwijnt het grootste bezwaar van dit ontwerp. Dat is de belangrijkste vervolgstap.

### 7.2 De rollen

Signatuurformaat, verplicht als laatste regel van elk agent-comment:

`— Raderwerk · <Rol> (<model>) · run <nummer> · <duur> · EUR <kosten>`

| # | Rol | Model / tool | Trigger | Invoer | Uitvoer | Mag wel | Mag nooit | Stopt bij |
|---|---|---|---|---|---|---|---|---|
| 1 | **Account** | Claude Fable 5.1 | Orchestrator-poll op KR Binnen en Lead | Lead-issue, publieke bedrijfsinformatie, dienstenaanbod | Leadscorecard als comment, aanbeveling, engagement-issue | Kwalificeren, doorvragen als concept, status naar Gekwalificeerd of Niet doorgegaan | Contact opnemen met wie dan ook; prijzen toezeggen | Geen poort, maar afwijzen mag alleen als concept |
| 2 | **Strateeg** | Claude Fable 5.1 | Status wordt Discovery | Engagement-issue, alle klantcontext, bestaande site of shop | Discovery-verslag als document, aannames, risico's, vragenlijst | Onderzoeken, meten, read-only analyses draaien, vragen stellen via `schakelaar/wacht-op-mens` | Aannames als feiten presenteren; iets bouwen | — |
| 3 | **Voorstelschrijver** | Claude Fable 5.1 | Status wordt Voorstel | Discovery-verslag, tarievenkaart, vergelijkbare engagements | Voorsteldocument, prijstabel, planning, beslisblok | Prijzen berekenen, plannen, voorwaarden invullen | Het voorstel "verstuurd" noemen; korting geven; Poort 1 zelf passeren | **Poort 1** |
| 4 | **PM** | Claude Opus 5 | Poort 1 goedgekeurd, of begin van een cyclus | Voorstel, milestones | Project, milestones, werkvloer-issues met acceptatiecriteria, cyclusvulling, sprintrapport, rollup naar het engagement-issue | Issues maken en verdelen, agents routeren, projectupdates schrijven | Meer issues maken dan het budget uit hoofdstuk 9 toestaat; scope uitbreiden zonder nieuw voorstel | — |
| 5 | **Ontwerper** | Claude Opus 5 (met de frontend-designrichtlijnen) | Issue met `dienst/design` gaat naar In uitvoering | Designtaak, merkdocument, tokens | Werkende componenten of pagina's in de repo, tokens, screenshots, PR | Ontwerpen als echte code, previews maken | Merkregels van de klant negeren; beeldmateriaal gebruiken zonder licentie | **Poort · Merge** |
| 6 | **Developer A** | Codex, GPT-5.6 Sol xhigh, via `Issue.delegate` | `delegateId` = Codex door de orchestrator | Issue met acceptatiecriteria, repo, basisbranch | Branch, PR, testuitvoer, samenvatting in de Agent Session | Code schrijven, tests draaien, PR openen | Mergen; deployen; productiecredentials gebruiken; buiten de genoemde repo werken | **Poort · Merge** |
| 7 | **Developer B** | Cursor, Grok 4.6, via `Issue.delegate` | `delegateId` = Cursor | idem | idem | idem | idem | **Poort · Merge** |
| 8 | **Contentmaker** | Claude Sonnet 5 | Issue met `dienst/content` naar In uitvoering | Briefing, merkstem, bronnen | Markdown in de repo, metatitel en -beschrijving, bronnenlijst, PR | Schrijven, herschrijven, structureren | Cijfers of citaten verzinnen; publiceren | **Poort · Publicatie** |
| 9 | **Advertentieplanner** | Claude Opus 5 | Issue met `dienst/ads` naar In uitvoering | Doel, doelgroep, budgetkader, landingspagina's | Campagneplan als document, advertentieteksten, meetplan | Plannen, teksten schrijven, structuren opzetten, read-only data ophalen | Een campagne activeren; budget wijzigen; geld uitgeven | **Poort · Publicatie** |
| 10 | **Socialplanner** | Claude Sonnet 5 | Issue met `dienst/social` naar In uitvoering | Kanalen, ritme, rubrieken, merkstem | Kalender voluit uitgeschreven in de repo | Plannen, schrijven, beeldopdrachten formuleren | Iets plaatsen of inplannen in een echt kanaal | **Poort · Publicatie** |
| 11 | **Reviewer** | Codex GPT-5.6 Sol xhigh als de uitvoerder een Claude-model was; Claude Fable 5.1 als de uitvoerder Codex of Cursor was | Status wordt Agentreview | PR of deliverable, acceptatiecriteria | Reviewcomment met bevindingen op ernst gesorteerd, oordeel | Afkeuren, terugsturen naar In uitvoering, blokkerende bevindingen markeren | Zijn eigen werk reviewen; goedkeuren zonder de acceptatiecriteria langs te lopen | — |
| 12 | **QA** | Claude Fable 5.1, met browsergereedschap | Status wordt QA op preview | Preview-URL, acceptatiecriteria | QA-rapport als comment volgens template, screenshots, oordeel | Testen, randgevallen proberen, afkeuren en terugzetten | Goedkeuren zonder bewijs per criterium; testen op productie | — |
| 13 | **Financiën en administratie** | Claude Sonnet 5 | Poort 2 goedgekeurd | Alle Klaar-issues van het engagement, kostenboek, voorstel | Factuurconcept als document, urenspecificatie, kostenoverzicht | Rekenen, specificeren, afwijkingen benoemen | Versturen; bedragen aanpassen zonder onderbouwing | **Poort 3** |
| 14 | **Orchestrator** | Claude Fable 5.1 (Claude Code headless) | Poll elke 2 minuten; plus een dagelijkse ronde om 08:00 voor rapportages | De hele workspace | Statuswissels, labels, comments, delegaties, kostenregels, weekrapport | Alles wat een agentrol nodig heeft, binnen de rolcontracten | Een issue uit een poortstatus halen zonder menselijk akkoordsignaal; het label `poort/akkoord-gegeven` plaatsen; een comment plaatsen dat begint met AKKOORD of AFGEKEURD | Elke poort |

### 7.3 Modelkeuze in één regel

Oordelen en taal: Fable 5.1. Bouwen en plannen: Opus 5. Volume: Sonnet 5. Code en tweede mening: Codex GPT-5.6 Sol xhigh. Tweede dev-lane voor parallel werk: Cursor Grok 4.6. De reviewer is **altijd** een ander model dan de uitvoerder; dat is de goedkoopste kwaliteitsmaatregel die er is en hij is met één regel in het rolcontract af te dwingen.

---

## 8. Het poortmechanisme

### 8.1 Wat een poort is

Een poort is een workflowstatus waarvan de naam begint met `Poort`. Er zijn er vier: drie op Klantreis (Voorstel, Oplevering, Factuur) en één op Werkvloer (Merge of publicatie). Een poort is de enige plek waar een mens iets moet doen, en dat is met opzet zo saai mogelijk gehouden: lezen, oordelen, één woord typen.

### 8.2 Wat de orchestrator doet bij het binnenkomen van een poort

Zes handelingen, altijd in deze volgorde, altijd alle zes:

1. `issueUpdate`: status naar de poortstatus.
2. `issueUpdate`: `assigneeId` = de mens (Youp), `delegateId` = null. Een poort heeft altijd een menselijke eigenaar en nooit een agent.
3. `issueAddLabel`: het bijbehorende `poort/*`-label.
4. `issueUpdate`: `priority: 1` (Urgent), zodat de poort bovenaan de inbox van de mens staat.
5. `attachmentCreate` of `attachmentLinkURL`: het artefact waar het besluit over gaat (document, PR, preview-URL).
6. `commentCreate`: het **beslisblok** in exact dit formaat.

```markdown
### BESLISBLOK — Poort 1 · Voorstel akkoord

**Waar gaat dit over**
Vloedlijn, fase 1: shop en ERP verbinden. Voorstel van EUR 8.400 excl. btw, oplevering 10 oktober.

**Wat er gebeurt als je akkoord geeft**
Het voorstel geldt als verstuurd. De PM-agent maakt het project, vier milestones en negen werkvloer-issues aan en vult de eerste cyclus. Geschatte kosten aan modelinzet tot de volgende poort: EUR 18 tot 30.

**Wat er gebeurt als je afkeurt**
Het issue gaat terug naar Voorstel met jouw reden als opdracht. Er wordt niets aangemaakt.

**Waar je op moet letten**
- Prijs is gebaseerd op 68 uur; de discovery noemt twee onzekerheden (ERP-API zonder documentatie, onbekend aantal varianten).
- Opleverdatum gaat uit van akkoord vandaag.

**Bewijs**
- Voorstel: <link naar document>
- Discovery-verslag: <link naar document>
- Kostenregels tot nu: <link naar kostenboek>

**Hoe je antwoordt**
Plaats een comment dat begint met `AKKOORD` (eventueel met een opmerking erachter) of met `AFGEKEURD:` gevolgd door de reden. Of doe hetzelfde met de hand: zet het label `poort/akkoord-gegeven` en verplaats het issue.

— Raderwerk · Voorstelschrijver (Claude Fable 5.1) · run 0031 · 3m41s · EUR 1,12
```

### 8.3 Hoe een mens goedkeurt of afkeurt

Twee manieren, allebei geldig, allebei zichtbaar in de issue-history:

- **Snel**: een comment dat begint met `AKKOORD` of `AFGEKEURD: <reden>`.
- **Met de hand**: het label `poort/akkoord-gegeven` plaatsen en het issue naar de volgende status slepen.

### 8.4 Wat de orchestrator doet bij goedkeuring

1. Controleert dat het akkoordsignaal **niet uit zijn eigen logboek komt** (zie 8.6).
2. Zet `poort/akkoord-gegeven`, haalt het `poort/*`-wachtlabel weg.
3. Zet de status naar de volgende stap: Poort 1 naar Kickoff, Poort 2 naar Poort 3, Poort 3 naar Afgerond, Poort Merge naar QA op preview.
4. Haalt de menselijke assignee weg en zet het juiste `agent/*`-label of `delegateId`.
5. Plaatst een comment: wat er nu gaat gebeuren, welke agent het oppakt, wanneer de volgende poort verwacht wordt.
6. Schrijft een regel in het Kostenboek met het aantal menselijke minuten dat de poort heeft gekost (tijd tussen beslisblok en akkoord).

### 8.5 Wat de orchestrator doet bij afkeuring

1. Zet `poort/afgekeurd`, haalt het wachtlabel weg.
2. Zet de status terug naar de bijbehorende werkstatus: Poort 1 naar Voorstel, Poort 2 naar Klantacceptatie, Poort 3 naar Poort 2, Poort Merge naar In uitvoering.
3. Maakt **geen** nieuw issue aan (dat kost issuebudget); de reden van afkeuring wordt als opdracht bovenaan het bestaande issue in een comment gezet, met een checklist van wat er moet veranderen.
4. Routeert naar dezelfde agent als eerder, met de afkeurreden als extra invoer. Bij een tweede afkeuring op hetzelfde issue routeert hij naar een **ander model** en zet `risico/midden`.
5. Bij een derde afkeuring: `schakelaar/wacht-op-mens` en stoppen. Drie keer fout betekent dat de opdracht niet deugt, niet de uitvoerder.

### 8.6 Waarom dit auditeerbaar is, en waar de zwakte zit

Op Free is elke gebruiker admin en schrijft de orchestrator met de persoonlijke sleutel van de aanvrager. In de Linear-history staat dus bij zowel een agenthandeling als een menselijke handeling dezelfde naam. Dat is de zwakste schakel van het hele ontwerp en wordt op drie manieren afgedekt:

1. **Handelingenlogboek.** De orchestrator schrijft elke schrijfactie weg met tijdstempel, mutatie, entiteit-id en het teruggekregen object-id, lokaal en samengevat in het Kostenboek. Elke statuswissel, elk label en elk comment dat wél in Linear staat maar **niet** in het logboek, is per definitie door een mens gedaan. Een controlescript vergelijkt de Linear-history met het logboek en meldt afwijkingen; dat script draait voor elke demo en het resultaat komt op het controle-issue.
2. **Verboden token.** De orchestrator mag nooit een comment plaatsen dat begint met `AKKOORD` of `AFGEKEURD`, en mag nooit het label `poort/akkoord-gegeven` plaatsen. Dat staat in het rolcontract en wordt in de code als harde controle vlak voor het versturen afgedwongen.
3. **Eigen agentidentiteit, zo snel mogelijk.** Registreer een OAuth-app "Raderwerk-motor" met `actor=app` (gratis, geen seat, developer preview) en laat de orchestrator daarmee schrijven. Dan is het onderscheid tussen mens en machine native, en vervallen punten 1 en 2 als noodverband. Dit is de hoogste prioriteit op de opstartlijst.

### 8.7 De noodrem

Het vastgezette issue `KR-1 "Bedieningspaneel Raderwerk"` staat permanent in Retainer en draagt de labels die de hele workspace besturen. Zet `schakelaar/pauze-alles` op dit issue en de orchestrator doet vanaf de volgende pollronde (maximaal 2 minuten) niets meer dan loggen. Op hetzelfde issue staat in de omschrijving een teller die de orchestrator elke ronde bijwerkt: aantal actieve issues, kosten vandaag, kosten deze week, aantal menselijke handelingen deze week, resultaat van de laatste poortcontrole, en tijdstip van de laatste poll. Eén blik op dit ene issue vertelt of de machine draait en of hij zich gedraagt.

---

## 9. Issuebudget: 250 is de echte begroting

### 9.1 Uitgangspositie

De workspace bevat vandaag ongeveer 130 issues uit een oude bulkimport (`createdIssueCount` = 131). Die mogen weg. **Archiveren geeft geen ruimte terug**; alleen verwijderen mogelijk wel, en of `issueDelete` de teller `createdIssueCount` daadwerkelijk verlaagt is niet geverifieerd. Eerste opstarttaak is daarom: verwijder tien oude issues, lees `createdIssueCount` opnieuw, en bepaal daarmee of het budget 250 of 119 is. Het hele plan hieronder heeft een variant voor beide uitkomsten.

### 9.2 De begroting bij 250 beschikbare issues

| Post | Aantal | Toelichting |
|---|---|---|
| Bedieningspaneel en bureau-OS (P9) | 12 | Controle-issue, playbook-taken, controlescripts, weekrapportage |
| Klantreis-issues: Vloedlijn | 3 | Lead, engagement fase 1, account/retainer |
| Klantreis-issues: Kantelbeer | 3 | idem |
| Klantreis-issues: Trekvogel | 3 | idem |
| Klantreis-issues: Raderwerk | 2 | Engagement merklancering, account |
| Werkvloer-seed: 4 klanten | 37 | 9 + 9 + 9 + 10 |
| **Subtotaal startvulling** | **60** | Dit is wat er staat als de demo begint |
| Reserve voor door agents aangemaakt werk | 60 | Ongeveer 1,5 issue per seed-issue: gevonden bugs, opgesplitste taken, vervolgacties |
| Reserve voor QA-afkeur en herstel | 15 | Herstel gebeurt in principe op hetzelfde issue; alleen echt nieuw werk krijgt een issue |
| Reserve voor incidenten en spoedverzoeken | 10 | De onvermijdelijke realiteit van een agency |
| Reserve voor retainerrondes (3 maanden x 4 klanten) | 12 | Eén issue per klant per maand |
| Facturen (4 klanten x 2 rondes) | 8 | |
| **Subtotaal in gebruik** | **165** | |
| **Vrije ruimte** | **85** | Voor drie droogloopruns en de demo zelf |

### 9.3 De begroting bij 119 beschikbare issues

Als verwijderen geen ruimte teruggeeft: schrap de vierde klant uit de startvulling (Raderwerk krijgt dan 4 in plaats van 12 issues), halveer de werkvloer-seed naar 5 per klant, en houd de reserves op 40. Dat komt uit op ongeveer 95 in gebruik en 24 vrij, wat genoeg is voor één demo maar niet voor drie droogloopruns. In dat geval is upgraden naar Basic (10 dollar per gebruiker per maand, onbeperkt issues) de enige verstandige uitweg, en dat is een besluit van de aanvrager.

### 9.4 Regels die het budget bewaken

1. **Eén issue per deliverable.** Stappen binnen een deliverable zijn checklistregels, geen sub-issues. Dit is de belangrijkste regel en staat in elk rolcontract.
2. **Geen sub-issues voor herstel.** Een afgekeurd issue gaat terug naar In uitvoering met een opdracht in het comment.
3. **De PM-agent mag per kickoff maximaal 12 issues aanmaken.** Meer nodig betekent: het engagement is te groot en moet in fases.
4. **Budgetwacht.** Elke pollronde leest de orchestrator `organization.createdIssueCount`. Bij 200: waarschuwing op het bedieningspaneel. Bij 220: alleen nog issues aanmaken voor incidenten. Bij 240: `schakelaar/budget-op` op het bedieningspaneel en helemaal geen nieuwe issues meer, plus een comment dat een mens om een besluit vraagt.
5. **Opruimbeleid.** Afgeronde demo-issues worden na afloop geëxporteerd naar markdown in de repo `raderwerk/agency-os` (titel, omschrijving, alle comments, alle links) en daarna verwijderd, niet gearchiveerd. Het bewijs blijft bestaan, de teller loopt terug. Archiveren gebruiken we alleen voor issues die we in de UI nog willen kunnen terugvinden tijdens de demoperiode.
6. **Templates kosten niets.** Documenten, projecten, milestones, initiatives en projectupdates tellen niet mee in de 250. Duw daarom zoveel mogelijk inhoud naar documenten en projectupdates in plaats van naar issues. Dat past bovendien precies bij deze invalshoek: de klant leest documenten, niet issues.

---

## 10. De vier klanten en hun startvulling

Alle drie de fictieve klanten zijn verzonnen bedrijven. Het werk is echt: echte repositories onder github.com/raderwerk, echte previewomgevingen, echte teksten, echte ontwerpen, echte plannen. Elke publiek bereikbare pagina van een fictieve klant krijgt in de footer één zin: dat het een demonstratiebedrijf van Raderwerk is. Er gaat geen enkel bericht naar een echt mens.

Notatie hieronder: `[team · status · labels · schatting]`, daaronder de acceptatiecriteria. Waar `AC` staat moeten die criteria letterlijk in het issue komen; ze zijn de basis voor het QA-rapport.

---

### 10.1 Vloedlijn — DTC-webshop op Shopify met ERP-koppeling

**Merkregel:** Vloedlijn maakt zoutwaterbestendige buitenkleding voor mensen die het hele jaar aan het water zijn, en verkoopt uitsluitend direct via de eigen webshop.

**Situatie:** de webshop draait, maar voorraad en orders worden met de hand overgetikt tussen de shop en het ERP. Twee keer per week staat er iets verkeerd op voorraad en wordt er verkocht wat er niet is.

**Eerste engagement (P1):** shop en ERP verbinden, plus de productpagina zo bijwerken dat de nieuwe voorraadinformatie ook iets doet voor de bezoeker. Omvang M, indicatie EUR 7.500 tot 9.500, fixed price.

**Repositories:** `raderwerk/vloedlijn-erp-bridge` (middleware), `raderwerk/vloedlijn-erp-mock` (een echte, kleine ERP-nabootsing met een echte API), `raderwerk/vloedlijn-shop` (Shopify-theme).

| # | Issue | Kaders |
|---|---|---|
| 1 | **Lead: Vloedlijn wil af van overtikken** | `[KR · Lead · klant/prospect, soort/lead, dienst/web, agent/fable · S]` |

AC: leadscorecard volledig ingevuld met toelichting; aanbeveling met één zin motivatie; bij doorgaan een engagement-issue aangemaakt en gekoppeld.

| 2 | **Engagement: Vloedlijn fase 1, shop en ERP verbonden** | `[KR · Binnen · klant/vloedlijn, soort/engagement, dienst/web, facturatie/fixed-price · M]` |

AC: alle tien reisstappen uit het engagement-template afgevinkt met een link; drie poorten aantoonbaar door een mens gepasseerd; opleverrapport en factuurconcept bestaan als document.

| 3 | **Account: Vloedlijn** | `[KR · Retainer · klant/vloedlijn, soort/retainerronde, facturatie/retainer · S]` |

AC: elke maand een projectupdate met verbruikte omvang tegenover afgesproken omvang; openstaande verzoeken met besluit en motivatie.

| 4 | **Development store inrichten met 24 producten en 3 collecties** | `[WV · Backlog · klant/vloedlijn, dienst/web, soort/feature, agent/codex · 3]` |

AC: 24 producten met echte titels, beschrijvingen, prijzen, varianten (maat en kleur) en beeld; 3 collecties met een logische indeling; storefront bereikbaar via een preview-URL die in het issue staat; geen enkel product met placeholdertekst.

| 5 | **ERP-nabootsing als echte service** | `[WV · Backlog · klant/vloedlijn, dienst/web, soort/feature, agent/codex · 5]` |

AC: REST-service met endpoints voor artikelen, voorraadstanden, prijzen en orderstatus; gevuld met dezelfde 24 artikelen; OpenAPI-beschrijving in de repo; draait publiek bereikbaar op een gratis hosting met een gedocumenteerde API-sleutel; foutscenario's (404, 429, 500) opwekbaar met een testparameter.

| 6 | **Voorraadsync ERP naar shop, elke 15 minuten** | `[WV · Backlog · klant/vloedlijn, dienst/web, soort/feature, agent/codex, risico/midden · 5]` |

AC: gegeven een voorraadwijziging in het ERP, wanneer de sync draait, dan staat binnen 15 minuten dezelfde stand in de shop; verschillen worden per artikel gelogd met oude en nieuwe waarde; als het ERP niet bereikbaar is stopt de sync zonder de shop leeg te schrijven en meldt dat in de log; een droogloopstand (`--dry-run`) toont wat er zou gebeuren zonder te schrijven.

| 7 | **Orderdoorgifte shop naar ERP, met retry en idempotentie** | `[WV · Backlog · klant/vloedlijn, dienst/web, soort/feature, agent/cursor, risico/hoog · 8]` |

AC: gegeven een nieuwe bestelling, dan staat die binnen één minuut in het ERP met alle regels, kortingen en verzendkosten; gegeven dat dezelfde webhook twee keer binnenkomt, dan ontstaat er precies één order in het ERP; gegeven dat het ERP een 500 geeft, dan wordt er opnieuw geprobeerd met oplopende wachttijd (1, 5, 25, 125 seconden) en na vier pogingen een issue-waardige foutmelding gelogd; alle drie de scenario's afgedekt met een geautomatiseerde test.

| 8 | **Statuspagina en logging voor de koppeling** | `[WV · Backlog · klant/vloedlijn, dienst/web, soort/feature, agent/opus · 3]` |

AC: publieke statuspagina toont per koppelrichting laatste succesvolle run, aantal fouten laatste 24 uur en huidige achterstand; een niet-technische medewerker kan in één blik zien of het goed gaat; logregels bevatten geen persoonsgegevens.

| 9 | **Productpagina: voorraad- en maatadviesblok** | `[WV · Backlog · klant/vloedlijn, dienst/design, soort/designtaak, agent/opus · 5]` |

AC: bezoeker ziet per maat of die op voorraad is, zonder de pagina te herladen; maatadvies vraagt twee dingen en geeft één antwoord; werkt op 360, 768 en 1440 pixels breed; contrast minimaal 4,5:1 aangetoond met een meting; volledig met toetsenbord bedienbaar.

| 10 | **Zes productteksten en één categorietekst** | `[WV · Backlog · klant/vloedlijn, dienst/content, soort/contentstuk, agent/sonnet, risico/publiek-zichtbaar · 3]` |

AC: elke tekst benoemt materiaal, gebruikssituatie en onderhoud; geen technische claim zonder onderbouwing in de productspecificatie; metatitel maximaal 60 tekens en metabeschrijving maximaal 155 tekens per pagina; menselijke eindredactie genoteerd met naam en tijdstip.

| 11 | **Zoekcampagneplan Q4** | `[WV · Backlog · klant/vloedlijn, dienst/ads, soort/campagne, agent/opus · 3]` |

AC: drie campagnes met samen minimaal zes advertentiegroepen; per advertentiegroep minimaal drie advertenties en een bestaande landingspagina; negatieve zoekwoorden en uitsluitingen ingevuld; expliciete stopregel; er wordt niets geactiveerd en geen euro uitgegeven.

| 12 | **QA-rapport fase 1 en acceptatiebewijs** | `[WV · Backlog · klant/vloedlijn, soort/qa-rapport, agent/fable · 3]` |

AC: elk acceptatiecriterium van issues 4 tot en met 11 heeft een uitkomst en een link naar bewijs; randgevallen getest (leeg, veel, traag, fout, mobiel); één expliciet oordeel goedgekeurd of afgekeurd.

**Bewust ingebouwde afkeurlus voor de demo:** issue 7 wordt in eerste instantie zonder idempotentiecontrole opgeleverd. De reviewer of QA keurt af, de dev herstelt, QA keurt goed. Dat is de enige geënsceneerde stap in het hele ontwerp en hij staat als zodanig in het demoscript.

---

### 10.2 Kantelbeer — B2B-industrie met dealercatalogus

**Merkregel:** Kantelbeer bouwt hydraulische hef- en kantelsystemen voor werkplaatsen en verkoopt uitsluitend via een dealernetwerk.

**Situatie:** de bestaande site is een pdf-folder in webvorm. Inkopers vinden niet welk systeem bij hun werkplaats past, en dealers klagen dat ze geen leads krijgen.

**Eerste engagement (P3):** een merksite waar een inkoper in drie klikken bij het juiste systeem en de dichtstbijzijnde dealer komt. Omvang L, indicatie EUR 12.000 tot 16.000.

**Repository:** `raderwerk/kantelbeer-site` (statische site, gedeployed naar een previewomgeving).

| # | Issue | Kaders |
|---|---|---|
| 1 | **Lead: Kantelbeer zoekt een site die dealers leads oplevert** | `[KR · Lead · klant/prospect, soort/lead, dienst/web · S]` |

AC: scorecard ingevuld; complexiteit en risico expliciet gescoord vanwege de meertaligheid; aanbeveling met motivatie.

| 2 | **Engagement: Kantelbeer merksite en dealercatalogus** | `[KR · Binnen · klant/kantelbeer, soort/engagement, dienst/web, facturatie/fixed-price · L]` |

AC: als het engagement-template; extra: tweetaligheid NL/EN expliciet in scope of buiten scope.

| 3 | **Account: Kantelbeer** | `[KR · Retainer · klant/kantelbeer, soort/retainerronde, facturatie/retainer · S]` |

AC: maandelijkse projectupdate; openstaande verzoeken met besluit.

| 4 | **Merksysteem als designtokens** | `[WV · Backlog · klant/kantelbeer, dienst/design, soort/designtaak, agent/opus · 5]` |

AC: kleur, typografie, ruimte en radius als tokens in de repo; licht en donker; acht kerncomponenten (knop, kaart, tabel, formulierveld, navigatie, voettekst, melding, specificatietabel) als werkende voorbeeldpagina; elke tokenwaarde één keer gedefinieerd en nergens hardgecodeerd.

| 5 | **Merksite: acht pagina's, live op preview** | `[WV · Backlog · klant/kantelbeer, dienst/web, soort/feature, agent/codex · 8]` |

AC: home, drie productcategorieën, over ons, dealer worden, contact en een dealerzoeker; navigatie maximaal drie niveaus diep; elke pagina laadt onder 1 seconde op een snelle verbinding; preview-URL in het issue.

| 6 | **Dealercatalogus met 40 dealers en filters** | `[WV · Backlog · klant/kantelbeer, dienst/web, soort/feature, agent/cursor · 5]` |

AC: 40 dealers met naam, plaats, provincie, type (verkoop, service, beide) en contactvorm; filteren op provincie en type werkt zonder herladen en is deelbaar via de URL; leeg resultaat toont een zinnige boodschap met een alternatief; dealerdata staat als één databestand in de repo, niet verspreid over de opmaak.

| 7 | **Productcatalogus: 12 systemen met specificatietabel en datasheet** | `[WV · Backlog · klant/kantelbeer, dienst/web, soort/feature, agent/codex · 5]` |

AC: 12 producten met dezelfde specificatievelden, zodat vergelijken kan; per product een genereerbare pdf-datasheet met dezelfde gegevens als de pagina; vergelijkweergave voor maximaal drie producten naast elkaar.

| 8 | **Offerteaanvraagformulier met spamfilter** | `[WV · Backlog · klant/kantelbeer, dienst/web, soort/feature, agent/opus, risico/klantdata · 3]` |

AC: verplichte velden gemarkeerd en gevalideerd met begrijpelijke foutteksten; honeypot plus tijdslot tegen bots; bevestigingsmail als sjabloon aanwezig maar **niet verstuurd**; ingevulde gegevens worden alleen in een testopslag gezet, nooit gemaild naar een echt adres.

| 9 | **Acht pagina's copy in Nederlands en Engels** | `[WV · Backlog · klant/kantelbeer, dienst/content, soort/contentstuk, agent/sonnet, risico/publiek-zichtbaar · 5]` |

AC: elke pagina heeft een duidelijke hoofdboodschap in de eerste 40 woorden; geen technische claim zonder onderbouwing in de specificatie; Engelse versie is een vertaling met behoud van betekenis, geen woord-voor-woord; metatitel en metabeschrijving per pagina per taal.

| 10 | **Technische SEO-basis** | `[WV · Backlog · klant/kantelbeer, dienst/content, soort/feature, agent/opus · 3]` |

AC: sitemap en robots.txt correct; gestructureerde data voor Organization en Product valideert zonder fouten; hreflang correct tussen NL en EN; interne links vanaf home naar elke productpagina binnen twee klikken.

| 11 | **LinkedIn-kalender van zes weken** | `[WV · Backlog · klant/kantelbeer, dienst/social, soort/socialkalender, agent/sonnet · 3]` |

AC: twee posts per week voluit uitgeschreven; per post een beeldopdracht en een link naar bestaande content; drie vaste rubrieken; geen claim zonder dekking op de site; er wordt niets geplaatst.

| 12 | **QA en toegankelijkheidscontrole op acht pagina's** | `[WV · Backlog · klant/kantelbeer, soort/qa-rapport, agent/fable · 5]` |

AC: WCAG 2.2 AA gecontroleerd op alle acht pagina's met bewijs per bevinding; toetsenbordnavigatie volledig, focus altijd zichtbaar; alle acceptatiecriteria van issues 4 tot en met 11 nagelopen met bewijs; oordeel met motivatie.

---

### 10.3 Trekvogel — reizen en boekingen op een CMS met CRM-koppeling

**Merkregel:** Trekvogel stelt langzame treinreizen door Europa samen voor mensen die de reis belangrijker vinden dan de bestemming.

**Situatie:** reizen staan in een spreadsheet, de site wordt met de hand bijgewerkt, en aanvragen komen als losse mails binnen waardoor niemand weet wat de status is.

**Eerste engagement (P5):** een site waar reizen uit een CMS komen, bezoekers kunnen zoeken en aanvragen, en elke aanvraag schoon in het CRM landt. Omvang L, indicatie EUR 11.000 tot 15.000.

**Repository:** `raderwerk/trekvogel-web`.

| # | Issue | Kaders |
|---|---|---|
| 1 | **Lead: Trekvogel verzuipt in losse aanvragen** | `[KR · Lead · klant/prospect, soort/lead, dienst/web · S]` |

AC: scorecard ingevuld; het risico van persoonsgegevens expliciet benoemd; aanbeveling met motivatie.

| 2 | **Engagement: Trekvogel boekingssite met CMS en CRM** | `[KR · Binnen · klant/trekvogel, soort/engagement, dienst/web, facturatie/fixed-price, risico/klantdata · L]` |

AC: als het engagement-template; extra: verwerking van persoonsgegevens beschreven in het discovery-verslag.

| 3 | **Account: Trekvogel** | `[KR · Retainer · klant/trekvogel, soort/retainerronde, facturatie/retainer · S]` |

AC: maandelijkse projectupdate met aantal aanvragen en conversie.

| 4 | **Contentmodel en CMS met twaalf reizen** | `[WV · Backlog · klant/trekvogel, dienst/web, soort/feature, agent/codex · 8]` |

AC: contentmodel voor reis, dag, vervoer, verblijf en prijsstaffel; twaalf complete reizen ingevoerd; redacteur kan zonder ontwikkelaar een reis toevoegen; velden hebben hulpteksten; een reis zonder verplichte velden kan niet gepubliceerd worden.

| 5 | **Reisdetailpagina met dagindeling, prijstabel en kaart** | `[WV · Backlog · klant/trekvogel, dienst/web, soort/feature, agent/cursor · 5]` |

AC: dag-voor-dag-indeling uitklapbaar; prijstabel per vertrekmaand en kamertype; kaart met de route zonder externe tracking; downloadbaar reisschema als pdf met dezelfde inhoud als de pagina.

| 6 | **Zoeken en filteren op maand, duur en land** | `[WV · Backlog · klant/trekvogel, dienst/web, soort/feature, agent/codex · 5]` |

AC: filteren op vertrekmaand, reisduur en land, gecombineerd; resultaat deelbaar via de URL; leeg resultaat biedt de dichtstbijzijnde alternatieven; filteren voelt direct (onder 300 milliseconden) op de preview.

| 7 | **Aanvraagformulier met CRM-koppeling en dubbeldetectie** | `[WV · Backlog · klant/trekvogel, dienst/web, soort/feature, agent/cursor, risico/klantdata, risico/hoog · 8]` |

AC: gegeven een ingevulde aanvraag, dan staat er binnen één minuut een contact met de juiste reis in het CRM; gegeven dat hetzelfde e-mailadres binnen 24 uur nogmaals aanvraagt, dan ontstaat er geen tweede contact maar een notitie op het bestaande; gegeven dat het CRM onbereikbaar is, dan gaat de aanvraag niet verloren en probeert het systeem het opnieuw; er worden uitsluitend testgegevens gebruikt en er gaat geen mail naar een echt adres.

| 8 | **Seizoensthema en fotografierichtlijn** | `[WV · Backlog · klant/trekvogel, dienst/design, soort/designtaak, agent/opus · 5]` |

AC: één themalaag over de basisstijl die per seizoen wisselt zonder de componenten aan te passen; richtlijn met vijf goede en drie foute voorbeelden; alle beelden met een controleerbare licentie, herkomst genoteerd in de repo.

| 9 | **Twaalf reisbeschrijvingen** | `[WV · Backlog · klant/trekvogel, dienst/content, soort/contentstuk, agent/sonnet, risico/publiek-zichtbaar · 5]` |

AC: elke beschrijving noemt wat je ziet, wat je doet en wat het niet is; geen bewering over dienstregelingen of prijzen zonder bron; consistente structuur over alle twaalf; menselijke eindredactie genoteerd.

| 10 | **Vier artikelen over langzaam reizen** | `[WV · Backlog · klant/trekvogel, dienst/content, soort/contentstuk, agent/sonnet, risico/publiek-zichtbaar · 3]` |

AC: elk artikel beantwoordt één concrete vraag van een reiziger; elke feitelijke bewering heeft een bron; interne links naar minstens twee reizen; metatitel en metabeschrijving.

| 11 | **Seizoenscampagneplan met landingspaginavarianten** | `[WV · Backlog · klant/trekvogel, dienst/ads, soort/campagne, agent/opus · 5]` |

AC: twee campagnes met samen vier advertentiegroepen; twee landingspaginavarianten die echt bestaan op de preview; meetplan met één conversiedefinitie en drie meetmomenten; stopregel; niets geactiveerd.

| 12 | **QA en snelheid** | `[WV · Backlog · klant/trekvogel, soort/qa-rapport, agent/fable · 5]` |

AC: alle acceptatiecriteria van issues 4 tot en met 11 nagelopen met bewijs; grootste zichtbare element laadt binnen 2,5 seconden op een gesimuleerde trage verbinding, gemeten en gelogd; formulier getest met lege, extreem lange en ongeldige invoer; oordeel met motivatie.

---

### 10.4 Raderwerk — het bureau als eigen klant

**Merkregel:** Raderwerk is een digitaal bureau dat door AI-agents wordt gerund; mensen staan alleen bij de poorten. Every part turns the next.

**Engagement (P7 en P8):** het eigen merk, de eigen site, de eigen content, de eigen advertentie- en socialplannen. Dit is tegelijk de etalage en het bewijsstuk: de site legt uit hoe het bureau werkt en toont de drie andere klanten als casus, met de vermelding dat die fictief zijn.

**Repositories:** `raderwerk/raderwerk-site`, `raderwerk/agency-os` (de orchestrator, controlescripts, exports).

| # | Issue | Kaders |
|---|---|---|
| 1 | **Engagement: merklancering Raderwerk** | `[KR · Binnen · klant/raderwerk, soort/engagement, facturatie/intern · L]` |

AC: als het engagement-template, met de drie poorten ook echt doorlopen (het bureau behandelt zichzelf als klant, anders bewijst de demo niets).

| 2 | **Account: Raderwerk** | `[KR · Retainer · klant/raderwerk, soort/retainerronde, facturatie/intern · S]` |

AC: wekelijkse projectupdate met kosten, menselijke handelingen en opgeleverd werk.

| 3 | **Merk: logo, kleur, typografie en tokens** | `[WV · Backlog · klant/raderwerk, dienst/design, soort/designtaak, agent/opus · 5]` |

AC: logo als vectorbestand in drie varianten (vol, compact, alleen merkteken); kleurpalet met contrastcontrole; typografische schaal; alles als tokens in de repo; gebruiksregels met drie goede en drie foute voorbeelden.

| 4 | **raderwerk.ai: site met vier cases** | `[WV · Backlog · klant/raderwerk, dienst/web, soort/feature, agent/codex · 8]` |

AC: home, werkwijze, cases, transparantie en contact; vier casepagina's (Vloedlijn, Kantelbeer, Trekvogel, Raderwerk zelf) met echte schermafbeeldingen en links naar de previews; elke casepagina vermeldt zichtbaar dat de klant fictief is; site staat op een preview-URL en gaat pas live na een menselijke poort.

| 5 | **Transparantiepagina: welke AI, welke poorten, wie verantwoordelijk** | `[WV · Backlog · klant/raderwerk, dienst/content, soort/contentstuk, agent/fable, risico/publiek-zichtbaar · 3]` |

AC: benoemt per stap in de klantreis welk model het werk doet; benoemt de drie poorten en wie ze bedient; benoemt wie eindverantwoordelijk is voor publieke teksten; voldoet aan de transparantieverplichting voor AI-gegenereerde publieke content; in gewone taal, geen juridisch jargon.

| 6 | **Zes artikelen over hoe dit bureau werkt** | `[WV · Backlog · klant/raderwerk, dienst/content, soort/contentstuk, agent/sonnet, risico/publiek-zichtbaar · 5]` |

AC: elk artikel behandelt één stap van de klantreis met een echt voorbeeld uit deze workspace, inclusief cijfers uit het kostenboek; geen enkel verzonnen cijfer; menselijke eindredactie per artikel genoteerd.

| 7 | **Advertentieplan: zoek en LinkedIn** | `[WV · Backlog · klant/raderwerk, dienst/ads, soort/campagne, agent/opus · 3]` |

AC: twee campagnes met samen vier advertentiegroepen; per groep drie advertenties en een bestaande landingspagina; meetplan en stopregel; niets geactiveerd, geen budget.

| 8 | **Socialkalender van vier weken met twaalf posts** | `[WV · Backlog · klant/raderwerk, dienst/social, soort/socialkalender, agent/sonnet · 3]` |

AC: twaalf posts voluit uitgeschreven, verdeeld over drie rubrieken; elke post verwijst naar echt gepubliceerd werk; beeldopdracht per post; er wordt niets geplaatst.

| 9 | **Kostenboek-verzamelaar** | `[WV · Backlog · klant/raderwerk, soort/bureau, dienst/web, agent/opus · 5]` |

AC: script leest de runlogs van de orchestrator en schrijft per issue een kostenregel weg; totalen per issue, per klant, per dag en per model; draait als onderdeel van elke pollronde; het resulterende document is leesbaar zonder toelichting.

| 10 | **Poortcontrole: bewijs dat geen agent een poort passeerde** | `[WV · Backlog · klant/raderwerk, soort/bureau, dienst/web, agent/codex, risico/hoog · 5]` |

AC: script haalt de volledige history van elk issue op en vergelijkt elke statuswissel uit of naar een poortstatus met het handelingenlogboek van de orchestrator; elke wissel die niet in het logboek staat wordt als menselijk gemarkeerd, elke wissel die er wél in staat en een poort verlaat is een schending en wordt luid gemeld; uitvoer is een tabel met datum, issue, wissel en oordeel; het script draait voor elke demo en het resultaat komt op het bedieningspaneel.

| 11 | **Bedieningspaneel actueel houden** | `[WV · Backlog · klant/raderwerk, soort/bureau, agent/sonnet · 2]` |

AC: elke pollronde werkt de orchestrator de tellers in `KR-1` bij; als de laatste bijwerking ouder is dan tien minuten is dat zichtbaar; de noodrem is getest en het resultaat van die test staat op het issue.

| 12 | **Weekrapport voor de initiative "Het raderwerk zelf"** | `[WV · Backlog · klant/raderwerk, soort/bureau, agent/fable · 2]` |

AC: elke maandag een initiative-update met: opgeleverd werk met links, kosten per klant, aantal menselijke handelingen, eerste-keer-goedpercentage, en de drie grootste risico's van die week; alle cijfers uit het kostenboek, geen schattingen.

---

## 11. Opstartlijst voor de aanvrager

Dit zijn de handelingen die alleen een mens kan doen. Gesorteerd op wat de rest blokkeert.

**Blokkerend voor alles**
1. Bevestig dat de bestaande workspace-inhoud weg mag, en verwijder tien oude issues als proef. Lees daarna `organization.createdIssueCount` opnieuw en meld of het getal daalt. Hiervan hangt het hele issuebudget af (hoofdstuk 9).
2. Hernoem de workspace naar Raderwerk en zet de urlKey om. Dat kan maar één keer zonder rommel, dus doe het voordat er links worden gedeeld.
3. Beslis: blijven we op Free (dit ontwerp) of gaan we naar Basic voor onbeperkte issues en vijf teams. Dit ontwerp werkt op Free; de keuze verandert alleen hoeveel droogloopruns erin passen.

**Blokkerend voor het poortbewijs (hoogste prioriteit na 1 tot 3)**
4. Registreer een OAuth-app "Raderwerk-motor" met `actor=app` en de scopes `read, write, comments:create, issues:create, app:mentionable`, installeer hem in de workspace en geef de orchestrator dat token. Dan schrijft de machine onder een eigen identiteit en is het verschil tussen mens en agent in de history native zichtbaar. Zonder deze stap leunt de auditeerbaarheid volledig op het eigen logboek.

**Blokkerend voor de dev-lanes**
5. GitHub-organisatie `raderwerk`: maak de repositories `vloedlijn-erp-bridge`, `vloedlijn-erp-mock`, `vloedlijn-shop`, `kantelbeer-site`, `trekvogel-web`, `raderwerk-site`, `agency-os`. Zet per repo de standaardbranch en een minimale CI-workflow (build en test).
6. Codex: koppel het ChatGPT-account aan het Linear-profiel (de agent vraagt hier zelf om bij de eerste delegatie) en maak per repository een Codex cloud-omgeving aan op de organisatie. Zonder omgeving faalt de delegatie met "Codex failed to start".
7. Cursor: installeer de Cursor GitHub-app op de organisatie `raderwerk`, zet Cloud Agents aan inclusief verbruiksfacturering, en koppel het Cursor-account aan het Linear-profiel.
8. Controleer of de Cursor- en ChatGPT-abonnementen betaald zijn; beide agents weigeren op een gratis account.

**Nodig voor echte deliverables**
9. Registreer raderwerk.ai (en eventueel raderwerk.agency) en zet DNS klaar.
10. Maak een hostingaccount voor previews (Vercel of Cloudflare Pages) onder de organisatie, en koppel de repositories zodat elke PR automatisch een preview-URL krijgt. Zonder preview-URL werkt de hele QA-stap niet.
11. Maak een Shopify partner-account met een development store voor Vloedlijn.
12. Kies en maak een gratis CRM-omgeving voor Trekvogel (testomgeving, geen echte contacten) en een gratis hostingplek voor de ERP-nabootsing.
13. Zet Search Console en een privacyvriendelijke statistiekentool klaar voor raderwerk.ai.
14. Controleer of de drie verzonnen bedrijfsnamen niet toevallig bestaande Nederlandse bedrijven zijn; wijzig ze anders voordat er iets gepubliceerd wordt.

**Instellingen in Linear zelf**
15. Zet de workspace- en teaminstructies voor agents (Instellingen, Agents, Additional guidance): de kern van het poortbeleid in vijf regels, zodat Codex en Cursor die tekst in elke sessie meekrijgen.
16. Zet jezelf als lead op alle negen projecten en als assignee op het bedieningspaneel-issue.
17. Zet meldingen aan voor issues die aan jou worden toegewezen, want dat is het signaal dat er een poort openstaat.

**Later, als het beschikbaar komt**
18. Installeer de Claude-agent in Linear zodra Anthropic die uitbrengt, en verhuis de orchestratorrollen daarnaartoe. Tot die tijd draait de orchestrator lokaal.

---

## 12. Risico's en faalwijzen van deze invalshoek

Op volgorde van hoe hard ze de demo raken.

**1. Mens en machine zijn niet uit elkaar te houden in de history.** De orchestrator schrijft met de persoonlijke sleutel van de aanvrager, dus in Linear staat overal dezelfde naam. Precies de bewering die deze demo moet bewijzen ("de mens klikte alleen bij de poorten") is daarmee niet uit Linear zelf af te lezen. Afvang: het handelingenlogboek plus het poortcontrolescript (issue 10 bij Raderwerk), en zo snel mogelijk een eigen `actor=app`-identiteit (opstartlijst punt 4). Zolang dat niet is gebeurd, moet de demo eerlijk zeggen dat het bewijs uit het logboek komt en niet uit Linear.

**2. De twee borden lopen uit de pas.** Klantreis toont "Levering" terwijl op Werkvloer alles al klaar of juist geblokkeerd is. Dat is dodelijk voor een demo die juist op leesbaarheid drijft. Afvang: de PM-agent berekent elke pollronde de rollup (aantal issues per status binnen het project) en zet de status van het engagement-issue daarop; bij een afwijking van meer dan één stap plaatst hij een comment in plaats van stilletjes te corrigeren.

**3. De kolomvolgorde valt om.** Linear sorteert kolommen op statustype voordat het op positie sorteert. Eén status met het verkeerde type en de reis leest niet meer van links naar rechts, en `type` is achteraf niet meer te wijzigen. Afvang: statussen in één script aanmaken, direct daarna de volgorde uitlezen en vergelijken met de tabel uit hoofdstuk 2; bij afwijking de status archiveren en opnieuw maken vóór er issues in staan.

**4. Het issueplafond loopt vol midden in de demo.** De klantreis verdubbelt per definitie: één engagement-issue plus alle werkvloer-issues. Bij 250 is dat krap. Afvang: de budgetwacht uit 9.4, de regel "één issue per deliverable", en het exportscript dat afgeronde demo-issues naar markdown wegschrijft en verwijdert.

**5. Alles hangt aan één laptop.** Zonder Loops, triage rules of webhooks is de orchestrator de enige motor. Slaapt de machine, dan bevriest de reis midden in een demo. Afvang: de poll draait als achtergrondproces met herstart bij crash, het bedieningspaneel toont het tijdstip van de laatste poll, en de demo begint met een blik op dat tijdstip.

**6. Een agent keurt zichzelf goed.** Een samenvatting die toevallig met het woord AKKOORD begint, of een agent die het label `poort/akkoord-gegeven` plaatst omdat het "logisch volgt". Afvang: harde controle in de code vlak voor elke schrijfactie, plus het poortcontrolescript dat achteraf elke poortpassage nagaat.

**7. De demo leest mooier dan de werkelijkheid.** Een niet-technische kijker ziet vier klanten netjes door de molen gaan en concludeert dat de AI het bureau runt. Verzwegen blijft dat er drie poorten, tientallen orchestrator-prompts en een handvol handmatige reparaties onder zitten. Dat is precies het soort overtuigingskracht dat later tegen je werkt. Afvang: het bedieningspaneel toont permanent de teller "menselijke handelingen deze week" en de weekrapporten noemen het eerste-keer-goedpercentage. Wie de demo geeft, laat die twee getallen zien voordat hij het bord laat zien.

**8. De native agents doen niet mee.** Codex en Cursor weigeren zonder gekoppeld account en zonder cloud-omgeving; dan blijft de sprintstap steken op een verzoek om in te loggen. Afvang: opstartlijst 6 tot 8 minstens een week voor de demo afronden en de delegatie één keer end-to-end proefdraaien per repository.

**9. De klantstem is verzonnen door dezelfde machine die het werk doet.** Er is geen echte klant die afkeurt, dus de acceptatiestap kan een wassen neus worden waarin het model zijn eigen werk goedkeurt. Afvang: de QA-rol krijgt altijd een ander model dan de uitvoerder, de acceptatiecriteria staan vast vóór de uitvoering begint, en er is minstens één ingebouwde afkeurlus (Vloedlijn issue 7) zodat zichtbaar is dat afkeuren echt gebeurt.

**10. Publiek zichtbaar werk voor verzonnen bedrijven.** Casepagina's, artikelen en socialposts over Vloedlijn, Kantelbeer en Trekvogel komen echt online. Verwarring met bestaande bedrijven of de indruk van valse referenties ligt op de loer, en voor informerende AI-gegenereerde content geldt een transparantieverplichting. Afvang: elke pagina van een fictieve klant draagt zichtbaar de vermelding dat het bedrijf fictief is, de transparantiepagina op raderwerk.ai legt de werkwijze uit, en elke publieke tekst passeert menselijke eindredactie die met naam en tijdstip wordt genoteerd.

**11. Uploads van 10 MB.** Ontwerpen en schermafbeeldingen passen niet als bijlage. Afvang: alles wordt gelinkt (preview-URL of repo-pad) in plaats van geüpload; dat is voor de demo bovendien beter, want een link is aanklikbaar bewijs en een plaatje niet.

**12. Documenten zijn niet doorzoekbaar zoals issues.** Deze invalshoek duwt bewust veel inhoud naar documenten om issuebudget te sparen, maar documenten zijn minder goed te filteren en te rapporteren. Afvang: elk document wordt als attachment aan het bijbehorende issue gehangen, zodat het vanuit de issuestroom altijd één klik weg is.

---

## 13. Bouwvolgorde

1. Opstartlijst 1 tot 3 (opruimen, hernoemen, plankeuze). Meet het issuebudget.
2. Twee teams aanmaken met `teamCreate`, inclusief triage, cycles en schattingsschaal. Statussen aanmaken met `workflowStateCreate` in de volgorde uit hoofdstuk 2, daarna direct de volgorde controleren.
3. Labels aanmaken: eerst de acht groepen (`isGroup: true`), dan de leden met `parentId`.
4. Eén issue-template met de hand in de UI maken, `templateData` uitlezen, en de overige twaalf plus de project- en documenttemplates programmatisch aanmaken.
5. Vijf initiatives, negen projecten met milestones, teams aan de projecten koppelen.
6. Bedieningspaneel-issue `KR-1` aanmaken en vastzetten. Noodrem testen: label plaatsen, één pollronde afwachten, aantonen dat er niets gebeurde.
7. De negen playbook-documenten onder P9 schrijven. Rolcontracten eerst, want de orchestrator leest ze.
8. Orchestrator bouwen: pollronde, rolcontracten, handelingenlogboek, kostenboek, poortlogica, budgetwacht.
9. Startvulling aanmaken: 60 issues volgens hoofdstuk 10, met acceptatiecriteria erin.
10. Opstartlijst 5 tot 13 (GitHub, agents, hosting, domeinen).
11. Eén engagement helemaal doorlopen met de hand, om te zien waar de reis schuurt voordat de machine hem gaat rijden.
12. Drie droogloopruns zonder handmatige reparatie. Pas daarna een demo plannen.

---

## Bijlage: volgorde van GraphQL-aanroepen voor de opbouw

```
organization                       -> lees createdIssueCount, subscription
issueDelete (x N)                  -> oude issues opruimen, daarna createdIssueCount hertellen
organizationUpdate                 -> naam en urlKey naar Raderwerk
teamCreate                         -> KR: triageEnabled true, cyclesEnabled false, issueEstimationType "tShirt"
teamCreate                         -> WV: triageEnabled true, cyclesEnabled true, cycleDuration 2,
                                      cycleStartDay 1, upcomingCycleCount 2, issueEstimationType "fibonacci",
                                      defaultIssueEstimate 2
workflowStates(team)               -> lees de standaardstatussen die Linear zelf aanmaakte
workflowStateCreate (x N)          -> eigen statussen, in positievolgorde, met de juiste types
workflowStateArchive (x N)         -> standaardstatussen opruimen (alleen als er geen issues in staan)
workflowStates(team)               -> controle: volgorde en types gelijk aan hoofdstuk 2
issueLabelCreate (x 8)             -> groepen, isGroup true, zonder teamId
issueLabelCreate (x ~45)           -> leden, met parentId
template(id) { templateData }      -> lees de vorm van een handmatig gemaakt template
templateCreate (x 13 + 2 + 5)      -> issue-, project- en documenttemplates
initiativeCreate (x 5)             -> vier klantrelaties plus de machine
projectCreate (x 9)                -> teamIds [KR, WV], leadId = mens
initiativeToProjectCreate (x 9)    -> projecten onder hun initiative hangen
projectMilestoneCreate (x ~30)     -> milestones per project
documentCreate (x 9)               -> playbooks onder P9
issueCreate / issueBatchCreate     -> de 60 startissues, met labelIds, estimate, stateId, projectId
attachmentLinkURL                  -> repo- en preview-links op de issues
issueUpdate                        -> KR-1 vastzetten als bedieningspaneel
webhookCreate                      -> niet doen; dit ontwerp pollt bewust
```
