# Linear inventory (read-only) 2026-09-02

Workspace: Fightclub Techhub (id 496f9ed7-9270-4def-9591-617d73915cb1, https://linear.app/fightclub-techhub)

## Teams
- FC "Fightclub Techhub" (id ae7176f0-da44-48c8-b1cf-ecaf30240783) — only team

## Workflow states (FC)
Backlog (backlog) d7e2f333 · Blocked/Waiting (backlog) 1dd8e635 · Waiting for approval (backlog) 4ce1bd2c · Todo (unstarted) c3ba55f2 · In Progress (started) 42eb9356 · In Review (started) e0cba350 · Done (completed) 92321b66 · Canceled cc6cc652 · Duplicate 0d2d5049

## Projects
- Luijtgaarden App | Verzoeken (3437d539, Planned, no lead, no initiative)
- Fightclub Creative Briefing Platform (3b250cb1, Backlog, lead Youp, initiative "Fightclub AI") — ~139 issues bulk-imported 2025-10-20 (titles like "J12: Feature flags"), all Backlog, unassigned

## Initiatives
- Fightclub AI (3374153f, Planned, owner Youp) — "A set of Fightclub AI tools for internal and external use"

## Labels
Issue: Bug, Improvement, Feature (group Core). Project: Shopify, Concrete CMS, Framer, Custom, Internal, VWO.

## Users
Youp Verkooijen (admin), Marijn Stuyfzand (admin, last seen 2025-08), xander.vanveen (admin), Raf Schapendonk (admin), "Linear" app user. No agent app users installed.

## Documents / templates / cycles / milestones
None found (documents empty; templates, cycles, milestones not queried).

## MCP tool surface (mcp__linear-server, 61 tools)
CAN: save_issue, save_project, save_initiative, save_milestone, save_document, save_release(+notes), save_status_update, save_comment, create_issue_label / create_initiative_label, attachments, diffs/reviews, agent skills (list/get), search_documentation.
CANNOT: create/update teams, create workflow states, create templates, create cycles, create project labels, install agent/app users, delete issues (no delete_issue tool; archive only if save_issue supports it).
=> Full workspace rebuild (teams, custom workflows, templates) needs the GraphQL API with a personal API key, or manual UI work.

## Update 14:20 (via personal API key, GraphQL)
- Key works: viewer Youp Verkooijen (admin). Key file ~/.config/linear/api_key (chmod 600). Header: `Authorization: <key>` (no Bearer).
- organization.subscription = null => Free plan (no paid subscription). createdIssueCount 130, userCount 7.
- Feature flags: agentAutomationEnabled true, linearAgentEnabled true, codingAgentEnabled true, aiAddonEnabled false, customersEnabled false, releasesEnabled false, codeIntelligenceEnabled false.
- App/agent users installed: Cursor (afd5064f-8c2e-4f60-a91a-2b753321d325@oauthapp.linear.app), Codex (a4bc02c9-24f5-44c3-a1d1-03a2e3042a99@oauthapp.linear.app), Linear. Claude Code NOT installed as agent.
- Integrations: github only. Templates: none.
- Organization.templates is a TemplateConnection (use nodes); root `templates` query returns a plain list.
