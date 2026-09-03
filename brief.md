# AI-agency op Linear: operator-first demo, toonbaar in 45 minuten

## Doel

Aantonen dat één operator de dagelijkse agency-loop van Fightclub kan draaien met AI-agents als uitvoerders en Linear als besturingssysteem, getoond in één live demo van 45 minuten. De demo slaagt als een ticket de hele loop doorloopt terwijl de mens alleen op expliciete gates klikt. "Hoe realistisch is dit" krijgt drie deliverables: de werkende loop, een tooling-tabel (welk model draagt welke stap, faalkans, kosten) en een slotslide met unit economics per ticketgrootte.

## De loop

1. Intake: ticket uit Orbit, Slack of mail landt in INTAKE met bron-id.
2. Scoping: agent leest de thread, stelt vragen bij ontbrekende spec, schrijft spec, Definition of Done, repo en basisbranch (production).
3. Schatting: urenbandbreedte plus risico; mens keurt scope en prijs (gate 1).
4. Uitvoering: worktree, feature-branch vanaf production, PR met bewijs.
5. Review: thermos-dubbelreview (Claude plus Codex); mens merget (gate 2).
6. Oplevering: concept-klantbericht in een Slack-kanaal dat de klant simuleert; deploy alleen naar preview of dev store.
7. Facturatie: agent stelt uren voor (Orbit-concept) en genereert een factuurdocument; mens keurt (gate 3).
8. Incidenten: triage, hypothese, concept-communicatie; mens beslist.

Sales (lead, concept-offerte) en growth (Semrush, SEO-issue) volgen dezelfde vorm met eigen gates.

## Menselijke gates

Merge, deploy, live writes in Shopify, Hyper of Semrush, elk klantcommitment (prijs, datum, "opgelost"), uren en facturen, incident-rollback. Agents krijgen geen productie-credentials; prod-data read-only.

## Linear-ontwerp

Teams per discipline: INTAKE, DEV, GROWTH, SALES, OPS. Initiatives = klant, projects = engagement, elk issue draagt een Orbit-id. Workflow DEV: Triage, Scoping, Wacht op scope-akkoord, Ready, In uitvoering, Agent-review, Wacht op merge, Staging/QA, Wacht op klant, Done, plus Canceled en Duplicate. Uit een "Wacht op"-state beweegt alleen een mens. Labelgroepen: client, type, risk (high dwingt een extra gate af), billing, source, blocked, agent/* voor routering, agents/pause als kill-switch. Templates: Bug, Feature, Incident, SEO-taak, Lead, Engagement. Velden: ticketgrootte S/M/L, schatting, runtime, tokens, supervisieminuten.

## Orchestratie

Eén Claude Code-dispatcher pollt Linear (geen webhooks) en start per issue één run met vast input-contract (Linear-velden) en output-contract (artefact, comment, voorgestelde state). Alleen de orchestrator schrijft naar Linear; subagents zien de MCP niet. Eén MCP-gebruiker; identiteit via agent/*-label en gesigneerde comments zoals "[QA-agent / Codex]". Elke run eindigt met een comment: wat gedaan, bewijs, kosten, volgende state. Modelinzet: Fable 5.1 voor scoping en review, Opus 5 of Sonnet 5 voor uitvoering, Codex GPT-5.6 als tweede reviewer, Cursor Grok 4.6 optioneel als tweede dev.

## Faalwijzen en afvang

Klaar zonder bewijs: DoD-checklist verplicht. Races: één assignee, state is het lock. Context-drift: repo en basisbranch verplicht, release-train-regels in de instructie. Kosten en loops: budget per issue en per dag, agents/pause stopt binnen één poll-interval. Stille Hyper- of Shopify-fouten: writes alleen op staging of test.

## Demoscript: twee sporen

Spoor A (echt): een S/M-ticket uit Orbit voor TowMotive, een uur eerder gestart, staat bij aanvang in Agent-review op een feature-branch. Spoor B (gecontroleerd, live vanaf minuut 3): mock-lead, Semrush-kansenrapport, offerte (gate 1), project met 5 tot 8 issues, uitvoering in demo-repo met één bewust dubbelzinnige eis, QA keurt af, dev herstelt, QA keurt goed, merge (gate 2), opleverbericht, factuur (gate 3). De presentator wisselt tussen sporen zodat LLM-latency (2 tot 8 minuten per fase) nooit een leeg scherm geeft. Incident-drill als extra scène. Slot: cijfers per run en eerlijkheidsslide.

## Echt versus mock

Echt: Linear-mutaties, dispatcher, code, PR en CI, thermos-review, Semrush-data, Slack-berichten, documenten, spoor A op een echte repo. Mock: lead, klant, verzending, betaling, productie-deploy, Orbit-urenboeking (concept).

## Meten en vervolg

Per issue: tokens tegen API-lijstprijs, supervisieminuten, schatting versus runtime, first-pass-acceptatie. Slotslide: kosten per run, doorlooptijd, interventies, unit economics per S/M/L voor de go/no-go. Compliance-checklist als bijlage, te toetsen door een jurist, geen blocker: sub-verwerkers Anthropic, OpenAI, xAI en Linear; Fable 5.1 vereist 30 dagen dataretentie (geen zero-data-retention), dus modelkeuze per klant; AI Act art. 50 bij AI-gegenereerde publieke content; IP-voorbehoud.

## Bouwvolgorde en workflow-inzet

Deze brief is workflow 1 (promptverfijning). Daarna: (1) workspace plus reset-script (workflow 3); (2) tooling-tabel (workflow 2); (3) dispatcher en rolcontracten (workflow 4); (4) demo-repo, dev store, spoor A-ticket; (5) drie droogloop-runs zonder handmatige reparatie, pas dan de demo plannen.

## Buiten scope

Orbit vervangen, autonome deploys of klantcontact, productie-writes, webhook-infra, aparte Linear-seats, pilot met betalende klanten (vervolgstap na go).

## Aannames

- De Linear MCP hangt aan de orchestrator-sessie; subagents zien geen Linear-tools. Alleen de orchestrator schrijft naar Linear, subagents leveren resultaten terug.
- De Linear MCP werkt onder één gebruikersaccount; er zijn geen aparte agent-seats. Agentrollen zijn zichtbaar via agent/*-labels en gesigneerde comments.
- Er is geen webhook-infrastructuur; orchestratie start vanuit Claude Code via polling of cron, niet vanuit Linear-events.
- Orbit/Teamleader blijft de bron van waarheid voor klanttickets en uren; Linear is het agent-besturingssysteem met een Orbit-id op elk issue. Geen tweerichtingssync in de demo.
- Bestaande Linear-inhoud mag weg (staat in de opdracht); default is archiveren in plaats van verwijderen tot de aanvrager anders zegt.
- Agents krijgen geen productie-credentials. Prod-data alleen read-only via bestaande analysepaden; writes alleen op staging, test of dev store.
- Spoor A vereist een geschikt S/M Orbit-ticket op een repo waar een feature-branch vanaf production veilig kan; is dat er niet, dan wordt spoor A een tweede, eerder gestarte run in de demo-repo.
- De demo-repo is een nieuwe GitHub-repo onder eigen account met GitHub Actions als CI; er is een Shopify development store, anders wordt de deploystap gemockt met een preview-URL.
- Er is geen boekhoudpakket gekoppeld; de factuur is een gegenereerd document. Externe communicatie wordt niet echt verzonden; een Slack-kanaal simuleert de klant.
- Het publiek is intern (Fightclub-team en management). Linear-inhoud en klantteksten zijn Nederlands; code, commits en PR's Engels.
- "Ultracode workflows" verwijst naar de Workflow multi-agent orchestration tool.
- Elke LLM-fase kost 2 tot 8 minuten wall-clock; de keten serieel 30 tot 40 minuten, vandaar twee sporen.
- Modelfeiten uit de lokale claude-api-referentie (cache 2026-06-24): Fable 5.1 $10/$50 per MTok, cache-read $0,25/MTok, 30 dagen dataretentie vereist en niet beschikbaar onder zero-data-retention zonder expliciete autorisatie. Opus 5 $5/$25, Sonnet 5 $2/$10.
- Juridische punten (AVG, AI Act, IP) zijn hypotheses ter toetsing door een jurist, geen advies; er is geen webonderzoek gedaan.
- Semrush wordt tijdens de demo read-only op een echt domein bevraagd; dat levert geen klantdata-risico op.
- Een kostenplafond per issue en per dag bestaat; het bedrag zet de aanvrager (open vraag 6).

## Open vragen (gesorteerd op impact)

1. Welke casus en data draait spoor A: een echt Orbit-ticket op een echte repo, of alles fictief?
   Waarom: bepaalt of de demo iets zegt over de dagelijkse praktijk of alleen over de mechaniek, en of open blokkades (geschikt ticket, repo-toegang) de bouw ophouden.
   Opties: (a) echt S/M TowMotive-ticket op echte repo, feature-branch vanaf production, nooit gemerged; (b) volledig fictieve klant en demo-repo; (c) beide als twee sporen.
   Default: (c), spoor A echt, spoor B gecontroleerd.

2. Wat is de rol van Linear ten opzichte van Orbit/Teamleader?
   Waarom: bepaalt of Fightclub het systeem na de demo kan gebruiken en of tickets en uren dubbel bijgehouden worden.
   Opties: Linear vervangt Orbit; Linear naast Orbit als agent-OS met Orbit-id op elk issue; Linear alleen voor de demo.
   Default: naast Orbit, Orbit blijft bron van waarheid voor klanttickets en uren.

3. Welke handelingen mogen agents zelfstandig afronden zonder menselijke klik?
   Waarom: bepaalt de gate-states in de workflow, de credentials die agents krijgen en het risicoprofiel van de demo.
   Opties: alleen lezen en concepten; ook PR openen, CI draaien, comments en statuswissels tot aan een gate; ook merge naar feature- of staging-branch; ook deploy naar staging.
   Default: alles tot aan de gates (PR, status, comments); nooit merge, deploy of verzenden.

4. Voor wie is de demo en hoe live moet hij zijn?
   Waarom: bepaalt polish, of een opname als backup nodig is en hoeveel demotijd sales en growth krijgen.
   Opties: intern team, live 45 minuten met twee sporen; management of klant, live met opgenomen backup; alleen walkthrough van een afgeronde run.
   Default: intern, live met twee sporen, geen opname; sales en growth samen maximaal 10 minuten.

5. Hoe krijgen agents een identiteit en een trigger in Linear?
   Waarom: bepaalt de dispatcher-architectuur (polling versus events) en of er seats gekocht moeten worden.
   Opties: één MCP-user plus agent/*-labels en gesigneerde comments, polling; aparte Linear-users per rol (seats); Linear Agents API of webhooks (extra bouwwerk).
   Default: één user plus labels, polling elke 2 minuten.

6. Welk kostenplafond en welke cadans krijgt de orchestrator?
   Waarom: kill-switch en budgetten zijn de eerste faalwijzen van een dispatcher-loop; zonder bedrag is de test niet uitvoerbaar.
   Opties: €10 per issue en €50 per dag; €25 per issue en €100 per dag; geen plafond in de demo.
   Default: €10 per issue, €50 per dag, richtwaarde onder €25 per volledige run.

7. Wat gebeurt er met de huidige Linear-inhoud en gebruikt iemand anders die nu?
   Waarom: verwijderen via MCP is onomkeerbaar en kan collega's raken.
   Opties: alles verwijderen; archiveren; nieuwe teams naast de bestaande.
   Default: archiveren, na bevestiging dat niemand anders de workspace gebruikt.

8. Mogen agents richting klanten communiceren, worden klanten geïnformeerd over AI-inzet, en welk productmodel (S/M/L-prijs) komt op de slotslide?
   Waarom: bepaalt of de opleverstap echt of mock is en of de unit economics tegen een prijs afgezet kunnen worden.
   Opties: geen klantcontact, alleen concepten, disclosure later; klant kijkt mee in Linear; agents mailen direct.
   Default: geen klantcontact, alleen concepten; disclosure en S/M/L-prijsmodel als voorstel op de slotslide, geen besluit.

## Succescriteria

1. Linear is opnieuw opgebouwd: 5 teams, DEV-workflow met minimaal 3 "Wacht op"-gates, 7 labelgroepen inclusief agent/* en agents/pause, minimaal 6 templates, een initiative per klant en de vijf issue-velden; beschreven in één Linear-document dat een collega zonder uitleg kan volgen.
2. Spoor B rondt live af binnen 45 minuten wall-clock met maximaal 3 menselijke handelingen (de gates) en 0 handmatige correcties in Linear door de presentator.
3. Spoor A: 1 echt Orbit-ticket doorloopt Triage tot Wacht op klant met in elke state een agent-comment met bewijs (PR-link, testoutput, screenshot); doorlooptijd en kosten per state gelogd.
4. Elke fase laat een vanuit Linear klikbaar artefact achter: offertedocument, project met minimaal 5 issues met acceptatiecriteria, PR-URL, QA-rapport als comment, opleverbericht in Slack, factuurdocument.
5. De QA-afkeurlus is minstens 1 keer live zichtbaar: afkeur-comment, herstel-commit, goedkeur-comment op hetzelfde issue en dezelfde PR.
6. 0 merges naar production of staging, 0 deploys en 0 verzonden klantberichten door agents zonder menselijke handeling, controleerbaar via Linear-history, git log en Slack.
7. 100% van de door agents aangeraakte issues heeft repo, basisbranch, ticketgrootte, schatting, werkelijke runtime, tokens, supervisieminuten en een afgevinkte DoD-checklist.
8. Kill-switch getest: het label agents/pause stopt alle runs binnen één poll-interval, gelogd.
9. 3 opeenvolgende droogloop-runs geslaagd zonder handmatige reparatie vóór de demodatum; een reset-script zet workspace, demo-repo en Slack-kanaal binnen 5 minuten terug naar de startstaat.
10. Kosten per volledige run gemeten (richtwaarde onder €25) en op de slotslide naast doorlooptijd, interventies en unit economics per S/M/L; first-pass-acceptatie over droogloop- en demo-issues minimaal 70% en mediane supervisietijd per issue gelogd.
11. Tooling-tabel opgeleverd: per loop-stap het gekozen model of gereedschap, de faalkans uit de droogloop-runs en de kosten.
12. Eerlijkheidsslide benoemt elk mock-onderdeel; elke agent-comment is herleidbaar naar rol en model; het management kan op basis van de cijfers een go/no-go nemen over een vervolgstap.
