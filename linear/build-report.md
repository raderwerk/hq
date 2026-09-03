# Linear-herbouw Fightclub Techhub — 3 september 2026

Werkruimte `fightclub-techhub` (id `496f9ed7-9270-4def-9591-617d73915cb1`) is leeggehaald en opnieuw opgebouwd uit `design/linear-spec.json`. De oude inhoud is verwijderd met expliciete toestemming; gebruikers zijn niet aangeraakt (7 gebruikers, ongewijzigd).

Eindstand: 2 teams, 72 labels, 5 initiatieven, 8 projecten, 29 mijlpalen, 16 sjablonen, 17 documenten, 69 issues. Drie dingen uit de spec konden niet gebouwd worden omdat Linear ze niet toestaat; die staan onderaan bij **Openstaand voor jou**.

## Back-up

`linear/backup-2026-09-03.json` (249 KB, volledig, geen mislukte secties). Inhoud: 132 issues (129 live + 3 gearchiveerd), 5 comments, 2 projecten, 1 initiatief, 4 issuelabels, 7 projectlabels, 2 teams, 7 gebruikers, 1 cyclus, 15 projectstatussen. Dit bestand is de enige weg terug en staat bewust niet in git.

## Wat is verwijderd

| Wat | Aantal | Details |
| --- | --- | --- |
| Issues | 129 | Permanent verwijderd (`permanentlyDelete: true`), in batches van 20 |
| Projecten | 2 | Luijtgaarden App \| Verzoeken, Fightclub Creative Briefing Platform |
| Initiatieven | 1 | Fightclub AI |
| Issuelabels | 4 | Bug, Improvement, Feature, Core |
| Projectlabels | 7 | Concrete CMS, Custom, Framer, Internal, VWO, Shopify, Projecttype |
| Teams | 1 | ZZA (ZZ Probe A), het gearchiveerde probeteam |

Team FC is **niet** verwijderd maar hernoemd naar WV (Werkvloer). Dat houdt de teamplek op het gratis plan bezit en omzeilt dat `teamDelete` zijn plek pas asynchroon vrijgeeft.

### organization.createdIssueCount rond de verwijdering

Voor het verwijderen van de 129 issues: **132**. Direct erna: **132**. De teller gaf de ruimte dus niet meteen terug.

Let op: dit veld is niet betrouwbaar. Achteraf gemeten geeft dezelfde query binnen dezelfde seconde **132** als je alleen `organization` opvraagt en **72** als je er `teams` bij vraagt. Het is een gecachet, afgeleid veld en geen bruikbare budgetmeter. De harde getallen zijn `team.issueCount`: KR 14 en WV 55, samen 69 live issues. Tegen de limiet van 250 blijft er dus minimaal 118 ruimte over, in de gunstigste lezing 178.

## Wat is gebouwd

### Teams

| Key | Naam | Issues | Triage | Cycli | URL |
| --- | --- | --- | --- | --- | --- |
| KR | Klantreis | 14 | aan | uit | https://linear.app/fightclub-techhub/team/KR |
| WV | Werkvloer | 55 | uit | aan (2 weken) | https://linear.app/fightclub-techhub/team/WV |

KR heeft 16 statussen uit de spec, WV 12. Beide hebben daarnaast Linears eigen `Duplicate`-status, die niet te verwijderen is.

### Labels

72 van de 74 labels, in 9 groepen: agent (6), dienst (7), facturatie (5), klant (6), poort (5), risico (3), run (6), schakelaar (3), soort (13), plus 9 ongegroepeerde labels. De twee ontbrekende labels staan onderaan bij **Openstaand voor jou**. Daarnaast 7 projectlabels: Shopify, Retainer, Site, Content, CMS, Merk, Intern.

### Initiatieven

| Naam | Projecten | URL |
| --- | --- | --- |
| Het raderwerk zelf | 1 | https://linear.app/fightclub-techhub/initiative/het-raderwerk-zelf-9437d8fe5f93 |
| Kantelbeer | 2 | https://linear.app/fightclub-techhub/initiative/kantelbeer-101f50d9e798 |
| Raderwerk | 2 | https://linear.app/fightclub-techhub/initiative/raderwerk-4566332bd235 |
| Spoorlinde | 1 | https://linear.app/fightclub-techhub/initiative/spoorlinde-a21da1c7ed94 |
| Zoutkaap | 2 | https://linear.app/fightclub-techhub/initiative/zoutkaap-9c1e0b741a71 |

### Projecten en mijlpalen

Alle 8 projecten zijn aan hun initiatief gekoppeld en hebben hun mijlpalen (29 in totaal).

| Project | Teams | Mijlpalen | URL |
| --- | --- | --- | --- |
| Het raderwerk — bureau-OS | WV | 4 | https://linear.app/fightclub-techhub/project/het-raderwerk-bureau-os-aa84fe8288a0 |
| Kantelbeer — Merksite en dealercatalogus | KR+WV | 4 | https://linear.app/fightclub-techhub/project/kantelbeer-merksite-en-dealercatalogus-3fe6fb51fa56 |
| Kantelbeer — Zichtbaarheid B2B | KR+WV | 3 | https://linear.app/fightclub-techhub/project/kantelbeer-zichtbaarheid-b2b-ea1104c938c4 |
| Raderwerk — Contentmotor en social | KR+WV | 3 | https://linear.app/fightclub-techhub/project/raderwerk-contentmotor-en-social-25991e179c67 |
| Raderwerk — Merk en site | KR+WV | 4 | https://linear.app/fightclub-techhub/project/raderwerk-merk-en-site-2b53667633c0 |
| Spoorlinde — Boekingssite met CMS en CRM | KR+WV | 4 | https://linear.app/fightclub-techhub/project/spoorlinde-boekingssite-met-cms-en-crm-b40b397d8dc4 |
| Zoutkaap — Fase 1: shop en ERP verbonden | KR+WV | 4 | https://linear.app/fightclub-techhub/project/zoutkaap-fase-1-shop-en-erp-verbonden-135b95915df0 |
| Zoutkaap — Retainer | KR+WV | 3 | https://linear.app/fightclub-techhub/project/zoutkaap-retainer-a355ae49a06c |

### Documenten

17 documenten. D01 tot en met D13 hangen onder *Het raderwerk — bureau-OS*, D14 onder *Raderwerk — Merk en site*, D15 tot en met D17 onder de drie klantprojecten.

| Document | URL |
| --- | --- |
| D01 — Zo werkt Raderwerk | https://linear.app/fightclub-techhub/document/d01-zo-werkt-raderwerk-14cf226908dd |
| D02 — Poortbeleid | https://linear.app/fightclub-techhub/document/d02-poortbeleid-d31ffbdf4c65 |
| D03 — Rolcontract, basis | https://linear.app/fightclub-techhub/document/d03-rolcontract-basis-fd2bfdb5a134 |
| D04 — Rolcontracten per rol | https://linear.app/fightclub-techhub/document/d04-rolcontracten-per-rol-24ef75040945 |
| D05 — Kostenboek | https://linear.app/fightclub-techhub/document/d05-kostenboek-1f19d9940f23 |
| D06 — Noodstop, hartslag en incidentprocedure | https://linear.app/fightclub-techhub/document/d06-noodstop-hartslag-en-incidentprocedure-73c65f6bad69 |
| D07 — Issuebudget en opruimbeleid | https://linear.app/fightclub-techhub/document/d07-issuebudget-en-opruimbeleid-0a99b309f8ed |
| D08 — Klantcommunicatiebeleid | https://linear.app/fightclub-techhub/document/d08-klantcommunicatiebeleid-16de5b6994cf |
| D09 — AI-inzet en transparantie | https://linear.app/fightclub-techhub/document/d09-ai-inzet-en-transparantie-f304f28cfd1a |
| D10 — Definition of Done per dienstlijn | https://linear.app/fightclub-techhub/document/d10-definition-of-done-per-dienstlijn-eb93ec396c0a |
| D11 — Bureau-inrichting in Linear | https://linear.app/fightclub-techhub/document/d11-bureau-inrichting-in-linear-c698e5904c26 |
| D12 — Eerlijkheidsdocument | https://linear.app/fightclub-techhub/document/d12-eerlijkheidsdocument-ee6833d1f01d |
| D13 — Demoscript | https://linear.app/fightclub-techhub/document/d13-demoscript-c0e245dbb34e |
| D14 — Merkgids Raderwerk | https://linear.app/fightclub-techhub/document/d14-merkgids-raderwerk-156278bea11e |
| D15 — Klantdossier Zoutkaap | https://linear.app/fightclub-techhub/document/d15-klantdossier-zoutkaap-13ea31b3aff9 |
| D16 — Klantdossier Kantelbeer | https://linear.app/fightclub-techhub/document/d16-klantdossier-kantelbeer-7f539d997464 |
| D17 — Klantdossier Spoorlinde | https://linear.app/fightclub-techhub/document/d17-klantdossier-spoorlinde-5d6be631690a |

### Sjablonen en issues

16 sjablonen: 11 issue-sjablonen, 1 projectsjabloon, 4 documentsjablonen. Teruggelezen ter controle: *Bug* (type issue, team WV) heeft 3 standaardlabels, prioriteit 2, schatting 2 en een body van 3.706 tekens waarin de sectie *Reproductie* aanwezig is.

69 issues: 14 op KR, 55 op WV. 13 daarvan zijn gedelegeerd aan een app-gebruiker: 9 aan Codex, 4 aan Cursor (WV-159, WV-170 tot en met WV-173, WV-182 tot en met WV-184, WV-191 tot en met WV-194, WV-202). Alle 13 zijn geverifieerd als echte app-gebruikers (`user.app = true`). De 4 KR-issues die in triage horen, staan ook echt in de triagestatus.

## Probes

De probes schrijven wegwerprecords, lezen ze terug en verwijderen ze weer. Er is niets van blijven staan (gecontroleerd: geen `zz-probe`-issues of -sjablonen over).

| Probe | Uitkomst |
| --- | --- |
| `permanentDeleteWorks` | **true** — `issueDelete(permanentlyDelete: true)` verwijdert echt, dus de teardown mocht draaien |
| `counterFreedByDelete` | **false** — de teller daalde niet direct na verwijderen |
| `templateDataIsJsonString` | **true** — `templateData` gaat als object heen en komt als JSON-string terug |
| `templateDataServerKeys` | `descriptionData` — Linear rendert de markdown-body naar een eigen blok |
| `templateDataBodyDropped` | `description` — de sleutel die wij sturen verdwijnt |
| `templateDataDrift` | leeg — geen enkele andere sleutel wordt herschreven |
| `triageStateAccepted` | **true** — `issueCreate` houdt een issue in de triagestatus |
| `delegateAccepted` | **true** — `delegateId` blijft staan |
| `estimateRoundTrip` | 4 — de `linear`-schaal rondt niets af |
| `descriptionRoundTrip` | **true** |
| `sameGroupLabelsRejected` | **true** — twee labels uit één groep worden hard geweigerd, niet stilletjes teruggebracht |

## Verificatie

`build_linear.py --verify` en daarnaast een losse, read-only controle die niet door de buildcode loopt (eigen GraphQL-queries, eigen assertions): **61 controles geslaagd, 6 gezakt**. Alle 6 gaan terug op de drie punten hieronder; er is geen enkel onverklaard verschil.

Wat exact klopt: teams (precies KR en WV actief), alle statussen per team, 7 projectlabels, 5 initiatieven, 8 projecten, 29 mijlpalen, 8 initiatiefkoppelingen, 16 sjablonen, 17 documenten, 69 issues met de juiste verdeling per team, 13 gedelegeerde issues, en de resterende ruimte onder de limiet van 250.

Een tweede droge run plant nu nog maar 5 handelingen, en dat zijn precies de drie onopgeloste punten (het icoon, de twee onmogelijke labels, en de twee issues die het weggevallen label willen). Verder is de build een echte no-op geworden.

## Wat er misging tijdens de run

De build is vier keer halverwege gestopt. Elke keer is de oorzaak uitgezocht, het script aangepast en opnieuw gedraaid; de build is idempotent, dus hervatten was steeds veilig. Geen van de veiligheidsregels is versoepeld.

1. **`templateData` kwam terug als JSON-string, niet als object.** Het script deed `.get()` op een string. Bovendien vervangt Linear `description` door `descriptionData`, waardoor een naïeve vergelijking alle 16 sjablonen elke run zou herschrijven. Opgelost door de string te parsen en alleen de sleutels te vergelijken die Linear letterlijk teruggeeft.
2. **`unable to update reserved state`.** De triagestatus is volledig onveranderlijk: naam, kleur, omschrijving én positie worden allemaal geweigerd. Het script probeerde hem te hernoemen naar "Binnen". Opgelost door de status als alleen-lezen te behandelen en zijn id wel onder de spec-naam te registreren, zodat issues er correct in landen.
3. **`Argument Validation Error` op `icon: "Gear"`.** `teamCreate` slikt een onbekend icoon stilzwijgend, `teamUpdate` weigert de hele payload. Dezelfde waarde slaagde dus bij het aanmaken en brak bij de volgende run, inclusief alle andere instellingen in die payload. Opgelost: het icoon wordt losgelaten en gemeld, de rest gaat door.
4. **`labelIds not exclusive child labels`.** Dit was de probe die zijn werk deed: twee labels uit één groep worden hard geweigerd. De probe verwachtte een stille reductie en liet de fout doorslaan. Opgelost: de weigering is nu het antwoord op de vraag, waarna de probe met één label verdergaat.

Daarnaast zijn drie oorzaken van onnodige herschrijvingen weggenomen, zodat een herhaalde run echt niets meer doet: Linear bewaart markdown niet letterlijk (het herschrijft lege regels, maakt van `-` een `*` en linkt alles wat op een adres lijkt automatisch), en het negeert `position` bij het bijwerken van een status. Zonder die correcties plande elke volgende run 69 issue-updates, 8 project-updates en 8 status-updates die niets veranderden.

## Openstaand voor jou

1. **Het icoon van team KR.** De spec vraagt `Gear`, en dat kent Linear niet. KR staat nu op `Book` (wat Linear zelf koos), WV op `Shop`. Geverifieerd geldige waarden: Book, Shop, Compass, Phone, Heart, Chart, Briefcase, Calendar, Cloud, Cube, Folder, Home, Image, Link, Lock, Megaphone, Search, Shield, Wrench, Rocket, Users, Bolt. Kies er een en zet hem in de spec, of haal het veld weg.
2. **Twee labelnamen botsen.** Linear eist dat labelnamen uniek zijn over de hele werkruimte, ook over groepen heen. `intern` staat in de spec zowel onder `dienst` als onder `facturatie`, en `wacht-op-mens` zowel onder `poort` als onder `schakelaar`. Alleen de eerste van elk paar bestaat nu. Gevolg: `dienst/intern` en `poort/wacht-op-mens` zijn er wel, `facturatie/niet-factureerbaar` en `schakelaar/mens-vereist` niet, en de issues *Engagement: merklancering Raderwerk* en *Account: Raderwerk* missen daardoor hun facturatielabel. Hernoem één van elk paar in de spec, dan pakt een volgende run het vanzelf op.
3. **De triagestatus van KR heet "Triage" en niet "Binnen".** Linear reserveert die status en weigert elke wijziging. Issues komen er wel correct in terecht; alleen het bordlabel wijkt af. Als "Binnen" belangrijker is dan een echte triage-inbox, kun je overwegen triage op KR uit te zetten en "Binnen" als gewone status te maken, zoals WV het al heeft.
4. **De kolomvolgorde van WV klopt niet.** Linear beheert `position` zelf: de API accepteert een nieuwe waarde in het antwoord maar bewaart hem niet. KR is vers aangemaakt en staat daardoor wél in de goede volgorde. WV is de hernoemde FC en heeft de oude posities geërfd, met als resultaat: Binnen > In uitvoering > Ingepland > Klaar > Geannuleerd > Dubbel > Backlog > Wacht op input > Na-merge controle > Poort · Merge of publicatie > QA op preview > Agentreview. Dit is alleen met de hand te herstellen door de kolommen in de Linear-interface te verslepen.
5. **Sjabloonteksten worden niet meer bijgewerkt na het aanmaken.** Linear bewaart ze als gerenderd blok, waardoor vergelijken met de brontekst niet kan. Pas je een sjabloontekst aan in de spec, dan landt die pas als er ook een andere sleutel verandert (label, prioriteit, schatting). Anders: sjabloon met de hand weggooien en opnieuw laten bouwen.
6. **Team ZZA staat er nog.** `teamDelete` gaf `success: true`, maar ZZA blijft zichtbaar in `teams(includeArchived: true)`; Linear ruimt teamdata asynchroon op. Het heeft de bouw niet gehinderd (KR kon gewoon aangemaakt worden). Even in de gaten houden.
7. **`organization.createdIssueCount` is onbetrouwbaar.** Gebruik het niet als budgetmeter; `team.issueCount` is wel betrouwbaar (nu 14 + 55 = 69).
