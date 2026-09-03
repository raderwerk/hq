# Raderwerk — klantportfolio

Datum: 2026-09-02. Hoort bij `linear-workspace-spec.md` en `agent-roster.md`. De zaai-issues staan machineleesbaar in `linear-spec.json`.

Vier klanten. Drie zijn verzonnen bedrijven, de vierde is Raderwerk zelf. **De opdrachtgevers zijn fictief, het werk is echt**: echte repo's onder `github.com/raderwerk`, echte previewomgevingen, echte teksten, echte ontwerpen, echte campagne- en socialplannen. Niets is een mock-up. Er gaat geen enkel bericht naar een echt mens en er wordt geen euro advertentiebudget uitgegeven.

Elke publiek bereikbare pagina van een fictieve klant draagt in de voettekst één zin: *"Demonstratiebedrijf van Raderwerk. Dit bedrijf bestaat niet."*

---

## 0. Naamcontrole

De drie namen zijn op 2026-09-02 gecontroleerd op botsing, omdat er publieke casepagina's over deze bedrijven komen.

| Naam | GitHub-handle | `.nl` | `.com` | Oordeel |
|---|---|---|---|---|
| **Zoutkaap** | vrij (404) | niet geregistreerd | niet geregistreerd | schoon |
| **Kantelbeer** | vrij (404) | niet geregistreerd | niet geregistreerd | schoon |
| **Spoorlinde** | vrij (404) | niet geregistreerd | niet geregistreerd | schoon |

Methode: HTTP-status van `github.com/<naam>` (404 = vrij) en RDAP via rdap.org voor `.nl` (SIDN) en `.com` (Verisign); 404 = niet geregistreerd. Eerder overwogen namen zijn hierop afgevallen: *Vloedlijn* en *Trekvogel* hadden allebei een bezette GitHub-handle en geregistreerde `.nl` én `.com`.

**Wat nog niet gecontroleerd is en wél moet:** het KvK-handelsregister en het Benelux-merkenregister. Een vrij domein sluit een bestaande handelsnaam niet uit. Dat staat als blokkerend punt in de opstartlijst, vóór er publieke pagina's onder deze namen verschijnen.

---

## 1. Zoutkaap — DTC-webshop op Shopify met ERP-koppeling

**Merkregel.** Zoutkaap maakt zoutwaterbestendige buitenkleding voor mensen die het hele jaar aan het water zijn, en verkoopt uitsluitend direct via de eigen webshop.

**Toon.** Nuchter, materiaalgericht, geen avontuurromantiek. Praat over naden, ritsen en onderhoud, niet over "je grenzen verleggen". Nederlands, tutoyeren, geen uitroeptekens.

**Situatie.** De webshop draait, maar voorraad en orders worden met de hand overgetikt tussen de shop en het ERP. Twee keer per week staat er iets verkeerd op voorraad en wordt er verkocht wat er niet is. De eigenaar wil er vanaf voor het najaarsseizoen.

**Engagement (P1): fase 1, shop en ERP verbonden.** Omvang M, indicatie € 7.500 tot € 9.500, vaste prijs. Plus de productpagina zo bijwerken dat de nieuwe voorraadinformatie ook iets doet voor de bezoeker. Daarna een retainer (P2).

**Wat er echt gebouwd wordt.** Een Shopify development store met 24 echte producten; een echte, publiek bereikbare ERP-nabootsing als REST-service met OpenAPI-beschrijving en opwekbare foutscenario's; een voorraadsync en een orderdoorgifte met retry en idempotentie; een statuspagina; een productpagina-blok; teksten, een campagneplan en een socialkalender.

**Repositories.** `raderwerk/zoutkaap-shop` (Shopify-theme), `raderwerk/zoutkaap-erp-bridge` (middleware), `raderwerk/zoutkaap-erp-mock` (de ERP-nabootsing).

**Klantstem-persona.** Marije, eigenaar. Praktisch, weinig tijd, wil bewijs zien in plaats van beloften. Vraagt altijd door op "wat gebeurt er als het misgaat". Keurt niets goed wat ze niet zelf op de preview heeft kunnen aanklikken.

**Zaai-issues op de klantreis (KR).** Lead, engagement fase 1, account/retainer.

**Zaai-issues op de werkvloer (WV), 11 stuks.**

| # | Issue | Omvang | Route |
|---|---|---|---|
| Z01 | Development store met 24 producten en 3 collecties | S | Codex |
| Z02 | ERP-nabootsing als echte REST-service met OpenAPI | M | Codex |
| Z03 | Voorraadsync ERP naar shop, elk kwartier | M | Codex |
| Z04 | Orderdoorgifte shop naar ERP, met retry en idempotentie | L | Cursor · **geënsceneerd** |
| Z05 | Statuspagina en logging voor de koppeling | S | Opus |
| Z06 | Designtokens en componentbibliotheek | M | Opus |
| Z07 | Productpagina: voorraad- en maatadviesblok | M | Opus |
| Z08 | Zes productteksten en één categorietekst | S | Sonnet |
| Z09 | Zoekcampagneplan Q4 | S | Opus |
| Z10 | Socialkalender voor de lanceermaand | S | Sonnet |
| Z11 | QA-rapport fase 1 en acceptatiebewijs | M | Fable |

**De geënsceneerde stap.** Z04 wordt bewust in eerste instantie zonder idempotentiecontrole opgeleverd, zodat de reviewer of QA echt afkeurt, de dev herstelt en QA daarna goedkeurt. Dit is de **enige** geregisseerde stap in de hele werkplaats. Het issue draagt het label `geënsceneerd` en de eerste regel van de omschrijving zegt het letterlijk.

---

## 2. Kantelbeer — B2B-industrie met dealercatalogus

**Merkregel.** Kantelbeer bouwt hydraulische hef- en kantelsystemen voor werkplaatsen en verkoopt uitsluitend via een dealernetwerk in de Benelux en Duitsland.

**Toon.** Technisch, precies, geen superlatieven en geen uitroeptekens. Specificaties boven adjectieven. Een inkoper wil weten of het past, niet of het geweldig is. Tweetalig NL en EN, waarbij de Engelse versie een echte vertaling is en geen woord-voor-woordomzetting.

**Situatie.** De bestaande site is een pdf-folder in webvorm. Inkopers vinden niet welk systeem bij hun werkplaats past, en dealers klagen dat ze geen leads krijgen.

**Engagement (P3): merksite en dealercatalogus.** Omvang L, indicatie € 12.000 tot € 16.000, vaste prijs. Doel: een inkoper vindt in drie klikken het juiste systeem en de dichtstbijzijnde dealer. Daarnaast een zichtbaarheidsspoor (P4) met content, technische SEO en een LinkedIn-ritme.

**Wat er echt gebouwd wordt.** Een statische site met acht pagina's op preview, een productcatalogus van twaalf systemen met vergelijkbare specificaties en genereerbare datasheets, een dealercatalogus met veertig dealers en deelbare filters, een offerteaanvraagformulier met spamharding, gestructureerde data, tweetalige teksten en een campagne- en socialplan.

**Repository.** `raderwerk/kantelbeer-site`.

**Klantstem-persona.** Dirk, commercieel directeur. Denkt in dealers en in marges. Wil weten hoeveel aanvragen een pagina oplevert en wie ze krijgt. Ergert zich aan marketingtaal en aan alles wat de dealer omzeilt.

**Zaai-issues op de klantreis (KR).** Lead, engagement merksite, account/retainer.

**Zaai-issues op de werkvloer (WV), 10 stuks.**

| # | Issue | Omvang | Route | Project |
|---|---|---|---|---|
| KB01 | Merksysteem als designtokens en acht kerncomponenten | M | Opus | P3 |
| KB02 | Merksite: acht pagina's, live op preview | L | Codex | P3 |
| KB03 | Productcatalogus: 12 systemen met specificatietabel en datasheet | M | Codex | P3 |
| KB04 | Dealercatalogus met 40 dealers en filters | M | Cursor | P3 |
| KB05 | Offerteaanvraagformulier met spamharding | S | Opus | P3 |
| KB06 | Technische SEO-basis en gestructureerde data | S | Opus | P4 |
| KB07 | Acht pagina's copy in Nederlands en Engels | M | Sonnet | P4 |
| KB08 | LinkedIn-kalender van zes weken | S | Sonnet | P4 |
| KB09 | Zoekcampagneplan maakindustrie | S | Opus | P4 |
| KB10 | QA en toegankelijkheidscontrole WCAG 2.2 AA op acht pagina's | M | Fable | P3 |

---

## 3. Spoorlinde — reizen en boekingen op een CMS met CRM-koppeling

**Merkregel.** Spoorlinde stelt langzame treinreizen door Europa samen voor mensen die de reis belangrijker vinden dan de bestemming.

**Toon.** Rustig, concreet, zintuiglijk zonder bloemig te worden. Noemt afstanden, overstaptijden en hoogtemeters. Belooft nooit weer, uitzicht of beschikbaarheid die niet vaststaat.

**Situatie.** De reizen staan in een spreadsheet, de site wordt met de hand bijgewerkt, en aanvragen komen als losse mails binnen waardoor niemand de status kent.

**Engagement (P5): boekingssite met CMS en CRM.** Omvang L, indicatie € 11.000 tot € 15.000, vaste prijs. Reizen komen uit een CMS, bezoekers kunnen zoeken en aanvragen, en elke aanvraag landt schoon in het CRM. Geen betalingen. De seizoenscampagne zit als mijlpaal in hetzelfde project.

**Wat er echt gebouwd wordt.** Een contentmodel met twaalf volledig ingevoerde reizen, een reisdetailpagina met dagindeling en prijstabel, zoeken en filteren, een aanvraagformulier met CRM-koppeling en dubbeldetectie, een seizoensthema, twaalf reisbeschrijvingen, vier artikelen, een nieuwsbriefopzet met dubbele opt-in en een campagneplan met echte landingspaginavarianten.

**Repository.** `raderwerk/spoorlinde-web`.

**Extra gevoeligheid.** Dit engagement draagt `risico/klantdata`. Er wordt uitsluitend met testgegevens gewerkt, er gaat geen mail naar een echt adres, en de verwerking van persoonsgegevens wordt in het discovery-verslag beschreven.

**Klantstem-persona.** Hanneke, mede-oprichter en reisleider. Kent elke route persoonlijk en corrigeert onmiddellijk elk feitelijk detail dat niet klopt. Vindt snelheid belangrijker dan mooi, en wil dat een redacteur zonder ontwikkelaar een reis kan toevoegen.

**Zaai-issues op de klantreis (KR).** Lead, engagement boekingssite, account/retainer.

**Zaai-issues op de werkvloer (WV), 10 stuks.**

| # | Issue | Omvang | Route |
|---|---|---|---|
| S01 | Contentmodel en CMS met twaalf reizen | L | Codex |
| S02 | Reisdetailpagina met dagindeling en prijstabel | M | Cursor |
| S03 | Zoeken en filteren op maand, duur en land | M | Codex |
| S04 | Aanvraagformulier met CRM-koppeling en dubbeldetectie | L | Cursor |
| S05 | Seizoensthema en fotografierichtlijn | M | Opus |
| S06 | Twaalf reisbeschrijvingen | M | Sonnet |
| S07 | Vier artikelen over langzaam reizen | S | Sonnet |
| S08 | Nieuwsbriefopzet met dubbele opt-in | S | Opus |
| S09 | Seizoenscampagneplan met landingspaginavarianten | M | Opus |
| S10 | QA, snelheid en formuliertest | M | Fable |

---

## 4. Raderwerk — het bureau als eigen klant

**Merkregel.** Raderwerk is een digitaal bureau dat door AI-agents wordt gerund; mensen staan alleen bij de poorten. *Every part turns the next.*

**Toon.** Nuchter en controleerbaar. Elke claim over snelheid, kosten of autonomie komt uit het kostenboek, met het getal erbij. Geen enkele bewering die het bureau groter maakt dan het is. Waar iets niet werkt, staat dat er.

**Waarom dit de vierde klant is.** Het bureau behandelt zichzelf als klant en laat zijn eigen engagement dezelfde drie poorten doorlopen. Doet het dat niet, dan bewijst de demo niets over de werkbaarheid van de eigen werkwijze. Bovendien is dit de etalage: raderwerk.github.io (GitHub Pages; voorlopig geen eigen domein) legt uit hoe het bureau werkt en toont vier cases, waarvan drie fictief en zichtbaar als zodanig gemarkeerd.

**Engagements.** P6 merk en site, P7 contentmotor en social. Beide `facturatie/niet-factureerbaar`, dus niet declarabel, maar wél volledig door de reis inclusief factuurconcept — anders is het geen bewijs.

**Repositories.** `raderwerk/raderwerk-site`, `raderwerk/agency-os` (Spil, controlescripts, exports, kostenboek-verzamelaar).

**Domein.** raderwerk.github.io (GitHub Pages; voorlopig geen eigen domein) (en eventueel raderwerk.github.io (GitHub Pages; voorlopig geen eigen domein)). raderwerk.com is speculatief geregistreerd en raderwerk.nl is actief; die twee laten we los.

**Klantstem-persona.** De eigen mens, in de rol van opdrachtgever. Hier speelt de klantstem-agent bewust géén rol: het bureau moet zichzelf niet goedkeuren.

**Zaai-issues op de klantreis (KR).** Engagement merklancering, account.

**Zaai-issues op de werkvloer (WV), 10 stuks.**

| # | Issue | Omvang | Route | Project |
|---|---|---|---|---|
| R01 | Merk: logo, kleur, typografie en tokens | M | Opus | P6 |
| R02 | Raderwerk-site op GitHub Pages met vier cases | L | Codex | P6 |
| R03 | Pagina "Zo werken wij": de poorten uitgelegd | S | Fable | P6 |
| R04 | Transparantiepagina: welke AI, welke poorten, wie verantwoordelijk | S | Fable | P6 |
| R05 | Publieke kostenpagina, gevoed uit het kostenboek | M | Opus | P6 |
| R06 | Zes artikelen over hoe dit bureau werkt | M | Sonnet | P7 |
| R07 | Publiek bouwlogboek, wekelijks | S | Sonnet | P7 |
| R08 | Socialkalender vier weken, twaalf posts | S | Sonnet | P7 |
| R09 | Advertentieplan zoek en LinkedIn | S | Opus | P7 |
| R10 | Prijskaart en dienstenmatrix S/M/L | S | Fable | P7 |

---

## 5. Afwijsleads

Drie extra leads staan gezaaid die naar verwachting **niet** doorgaan. Ze bewijzen dat de trechter een uitgang heeft en dat de Account-rol echt afwijst in plaats van alles binnen te halen.

| # | Lead | Verwachte uitkomst |
|---|---|---|
| L01 | Fictieve meubelmaker wil "gewoon even een webshop" met een budget van € 1.500 | Afwijzen: onder de ondergrens, scorecard onder 12 |
| L02 | Fictieve fysiopraktijk wil een advertentiecampagne zonder site en zonder meting | Afwijzen of doorvragen: geen landingspagina, dus geen meetbaar resultaat mogelijk |
| L03 | Fictieve marktplaats vraagt om een volledig platform in zes weken | Afwijzen: omvang XL, valt buiten wat dit bureau aankan zonder opknippen |

---

## 6. Bureau-OS: de machinekamer (14 zaai-issues op WV, project P8)

Dit zijn de issues die het bureau zelf laten draaien. Ze hebben `klant/geen` of `klant/raderwerk`, `dienst/intern` en `soort/bureau`.

| # | Issue | Omvang | Waarom het bestaat |
|---|---|---|---|
| B01 | Bedieningspaneel en noodrem (WV-1, vastgezet) | XS | Eén blik vertelt of de machine draait en zich gedraagt |
| B02 | Spil: pollcyclus, claimprotocol en idempotentie | L | Zonder claim doet een poller van 60 seconden hetzelfde werk vijf keer |
| B03 | Spil: poortlogica en verboden-tokencontrole | M | Het hele bewijs hangt hieraan |
| B04 | Handelingenlogboek en poortcontrolescript | M | Maakt auditeerbaarheid een artefact in plaats van een belofte |
| B05 | Hartslag en onafhankelijke wachthond | S | Een dode dispatcher laat een gezonde werkplaats achter |
| B06 | Kostenboek-verzamelaar | M | Zonder dit zijn de twee kopgetallen niet te tonen |
| B07 | Issuebudget: meting en budgetwacht | S | Het enige echte go/no-go-moment |
| B08 | Rolcontracten en systeemprompt-skelet vastleggen | M | Eén wijziging hier wijzigt elk agentgedrag |
| B09 | Poortbeleid en goedkeurderslijst vastleggen | S | Zonder gebruikers-id's is de actorcontrole niet uitvoerbaar |
| B10 | Eigen OAuth-app met actor=app en tokenvernieuwing | M | Maakt het onderscheid mens-machine native; zonder vernieuwing sterft de run binnen een dag |
| B11 | GitHub-org, repo's, rulesets en agent-tokens | M | De enige plek waar een poort echt afgedwongen kan worden |
| B12 | Codex- en Cursor-delegatie per repo end-to-end proefdraaien | M | Anders degradeert de demo stil tot één leverancier |
| B13 | Drie droogloopruns met logboek | L | Pas hierna mag er een demo gepland worden |
| B14 | Eerlijkheidsdocument en demoscript | S | Zonder script is dit niet te tonen; zonder eerlijkheidsdocument niet te geloven |

---

## 7. Repo-overzicht onder github.com/raderwerk

Alle repo's zijn **publiek**, want op een GitHub-organisatie op het gratis plan zijn branch protection en rulesets alleen op publieke repo's beschikbaar, en zonder ruleset is de mergepoort een belofte in plaats van een slot. Elke repo krijgt: een README waarmee iemand in maximaal vijf commando's draait, een CI-workflow (lint, typecheck, build, test), een preview-deploy per pull request, en een ruleset op de hoofdbranch met pull request verplicht, minimaal één review, verplichte status checks en **geen bypass voor de agent-tokens**.

| Repo | Klant | Wat erin zit |
|---|---|---|
| `zoutkaap-shop` | Zoutkaap | Shopify-theme, componenten, productpagina-blokken |
| `zoutkaap-erp-bridge` | Zoutkaap | Middleware: voorraadsync, orderdoorgifte, retry, statuspagina |
| `zoutkaap-erp-mock` | Zoutkaap | Draaiende ERP-nabootsing met OpenAPI en opwekbare fouten |
| `kantelbeer-site` | Kantelbeer | Statische site, product- en dealercatalogus, formulieren, tweetaligheid |
| `spoorlinde-web` | Spoorlinde | CMS-gevoede reissite, zoeken en filteren, aanvraagflow, CRM-koppeling |
| `raderwerk-site` | Raderwerk | Eigen site, cases, transparantie- en kostenpagina |
| `raderwerk-content` | alle | Alle contentstukken en kalenders als markdown, per klant in een map |
| `agency-os` | — | Spil, rolcontracten, controlescripts, kostenboek-verzamelaar, exports van verwijderde issues |

---

## 8. Wat gesimuleerd is en wat niet

Dit is de kern van het eerlijkheidsdocument (D12) en hoort ook in de demo uitgesproken te worden.

**Echt.** De Linear-mutaties. De dispatcher. De repo's, de CI, de pull requests, de reviews. De code. De sites op preview. De ontwerpen. De teksten. De campagne- en socialplannen. De Shopify development store. De ERP-nabootsing als draaiende service. De QA-runs met bewijs per criterium. Het kostenboek. De poortpassages en wie ze deed.

**Gesimuleerd.** De opdrachtgevers: bedrijf, contactpersoon, briefing, akkoord en feedback leven in Linear-comments en -documenten. De klantstem is een model met een persona, en haar oordeel is niet gezaghebbend. Offertes en facturen zijn documenten, geen verzonden post. Er is geen betaling en geen advertentiebudget dat echt wordt uitgegeven. Er is geen deploy naar een klantdomein.

**Geregisseerd.** Precies één stap: de afkeurlus op Zoutkaap-issue Z04. Dat issue draagt het label `geënsceneerd` en zegt het in zijn eerste regel. Niets anders in de hele werkplaats mag dat label dragen.

**Structureel incompleet.** Het tokenverbruik van Codex en Cursor loopt buiten het kostenboek om, want zij rekenen af binnen een ChatGPT-plan respectievelijk usage-based bij Cursor. Zolang die twee lanes native zijn, is de unit economics onvolledig. Dat hoort op de slotdia, niet in een voetnoot.
