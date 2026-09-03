# Lane 05 — Multi-agent orchestration patterns and long-horizon reliability (as of 2026-09-02)

Research note for the "AI-run digital agency" feasibility study (Fightclub Agency, Linear as operating system). Method: 22 web searches, 40+ page fetches; primary sources preferred (vendor docs, changelogs, pricing pages, METR/OpenAI/Anthropic publications). Every claim below carries a URL, a source date and an honest confidence. Items that could not be verified are listed at the end.

## 0. The one question that matters: how long a task can a frontier agent finish unattended?

Short answer, with evidence in sections 1–2:

| Reliability target | Software-engineering task length (human-expert-equivalent) the best public models reach today | Source |
|---|---|---|
| 50 % success | ~12 h (Claude Opus 4.6: 11 h 59 min; GPT-5.6 Sol: 11 h 18 min). Claude Mythos Preview: "at least 16 h" (95 % CI 8.5–55 h), which is the ceiling of METR's task suite | METR via Wikipedia table + METR X post, Feb–Jun 2026 |
| 80 % success | 1–3 h (Opus 4.6: 1 h 10 min; Gemini 3.1 Pro: 1 h 30 min; Mythos Preview: 3 h 06 min; Opus 4.5 was only 27 min) | same |
| Consistency across repeats (pass^k) | Decays exponentially: pass^k = p^k. A 90 % single-run agent is ~57 % reliable across 8 runs. On knowledge-heavy customer-service tasks (τ³-banking) the best pass^1 is only 48–55 % | τ-bench paper (2024), taubench.com (Mar 2026) |
| Non-software domains | METR: horizons are "40–100x lower for visual computer-use tasks"; physical/other tasks ~minutes | METR limitations note, 22 Jan 2026 |
| Running a business for months | Project Vend phase 2: profitable, but only with "bureaucracy" (checklists, procedures) and continuous human intervention; the CEO agent approved lenient requests ~8x more often than it denied them; staff social-engineered it | Anthropic, 18 Dec 2025 |

Practical rule for the agency demo: an agent may run **unattended** on work units that a senior human would finish in **≤ 1–2 hours** and that have a **machine-checkable definition of done**. Work that is 4–12 h long lands at roughly coin-flip first-pass success and needs a verify/retry loop with a human gate. Anything longer must be decomposed by a planner and approved by a human before execution. Multi-day "run the client account" autonomy is not supported by any 2026 evidence.

Two caveats on the METR numbers: error bars are "a factor of ~2 in each direction" (Opus 4.5's 50 % horizon CI runs 1 h 49 min to 20 h 25 min), and the suite is ~170 mostly-coding tasks that are cleaner than real client work ("messiness" lowers horizons).

## 1. Long-horizon reliability data

### 1.1 METR time horizons
- METR's live page (updated 8 May 2026) states "Measurements above 16 hrs are unreliable with our current task suite" and that several newer models (Opus 4.7, Grok 4.3, GPT-5.5) had no measurement yet. https://metr.org/time-horizons/
- Limitations note (22 Jan 2026): Opus 4.5 50 % horizon 4 h 49 min (CI 1 h 49 min–20 h 25 min), 80 % horizon 27 min; only ~170 tasks; "we lack longer, 2h+ tasks"; long-run trend "one doubling every 6–7 months" is what METR trusts, not individual points. https://metr.org/notes/2026-01-22-time-horizon-limitations/
- Per-model table (Wikipedia, citing METR Time Horizon 1.1): Opus 4.6 (Feb 2026) 11 h 59 min / 1 h 10 min; GPT-5.3-Codex high 6 h 30 min / 47 min; Gemini 3.1 Pro (Mar 2026) 5 h 50 min / 1 h 30 min; GPT-5.4 xhigh 5 h 42 min / 54 min; Claude Mythos Preview (Apr 2026) ≥16 h / 3 h 06 min; GPT-5.6 Sol (Jun 2026) 11 h 18 min. https://en.wikipedia.org/wiki/METR (secondary; medium confidence)
- METR on X: "We estimated a 50%-time-horizon of at least 16hrs (95% CI 8.5hrs to 55hrs) on our task suite, at the upper end of what we can measure without new tasks" for an early Mythos Preview, evaluated March 2026. https://x.com/METR_Evals/status/2052896621760004602
- AI Digest (updated March 2026): doubling every 7 months 2019–2025, every 4 months in 2024–2025; extrapolation gives one work-day (8 h) in 2027 and one work-week in 2028 — extrapolation, not measurement. https://theaidigest.org/time-horizons
- No METR figure for Claude Fable 5 / 5.1 or Opus 5 could be found (the Fable 5.1 system card PDF of 1 Sep 2026 was too large to fetch). Confidence: low that any public METR number exists for them yet.

### 1.2 Coding benchmarks
- SWE-bench Verified is saturated: top models cluster at 95–97 % (Opus 5 96.0 % launch figure, GPT-5.6 Sol 96.2 %, Fable 5 95.0 %) per aggregator write-ups; the official leaderboard page could not be parsed. https://codeant.ai/blogs/swe-bench-scores (secondary, medium confidence)
- SWE-bench Pro (BenchLM, updated 1 Sep 2026): Claude Fable 5.1 81.2 %, Mythos 5 80.3 %, Fable 5 80 %, Opus 5 79.2 %; rows are vendor-reported on differing scaffolds, so gaps are "directional". https://benchlm.ai/benchmarks/swe-bench-pro
- OpenAI retracted its recommendation of SWE-bench Pro on 8 Jul 2026 after an audit found 27.4 % (automated) to 34.1 % (five human engineers) of the 731-task public split broken; frontier pass rates had gone 23.3 % → 80.3 % in eight months. https://www.investing.com/news/stock-market-news/openai-retracts-swebench-pro-coding-benchmark-recommendation-93CH-4782526 (OpenAI's own post returned 403; press report, high confidence on the headline)
- Takeaway: public coding leaderboards no longer discriminate between frontier models and are partly broken; an agency must build its own evals on its own tickets.

### 1.3 Tool-use / customer-service agents (τ-bench family)
- pass^k defined in the τ-bench paper (17 Jun 2024): GPT-4o < 50 % overall, retail pass^8 < 25 %. https://arxiv.org/abs/2406.12045
- taubench.com leaderboard: τ²-bench text: Qwen3.5-397B 87.9 %, Gemini 3.0 Pro 85.4 %, Opus 4.5 85.3 % pass^1; τ³-banking (knowledge-intensive, Mar 2026): Qwen 3.8 Max 55.2 %, Opus 5 48.7 %; τ³-voice: 75.4 % top. https://taubench.com
- tau2-bench v1.0.1 (July 2026) re-graded banking tasks; results before/after are not comparable. https://github.com/sierra-research/tau2-bench

### 1.4 Economically valuable deliverables (GDPval)
- GDPval (OpenAI, 2 Oct 2025): 44 occupations, best model (Claude Opus 4.1) 47.6 % wins-or-ties vs human experts; automated grader agreed with humans only 66 %; tasks are one-shot deliverables (docs, slides, spreadsheets) with all context given, no multi-step or relationship work. https://www.transformernews.ai/p/openai-gdpval-ai-jobs-work (OpenAI page returned 403)
- GDPval-AA v2 (Artificial Analysis, Sep 2026): Elo vs a human baseline of 1,000; Claude Fable 5.1 (max effort) 1,853 ± 21, Opus 5 (max) 1,824 ± 18; graded pairwise by an LLM judge, agents run with shell + browser. https://artificialanalysis.ai/evaluations/gdpval-aa
- Meaning for an agency: on single, well-specified deliverables (a brief, a landing-page copy draft, an SEO audit doc) frontier models are at or above expert parity by these judges; the unmeasured part is exactly the account-management layer.

### 1.5 Business operation over months
- Project Vend phase 2 (Anthropic, 18 Dec 2025): Sonnet 4 → 4.5, three locations, negative-margin weeks "largely eliminated"; a CEO agent ("Seymour Cash") with OKRs approved lenient requests about eight times as often as it denied; Claudius nearly entered an illegal onion-futures contract, tried to hire below minimum wage, and was convinced an employee had been "elected CEO". Lesson: "bureaucracy matters" — procedures and checklists beat a supervising agent. https://www.anthropic.com/research/project-vend-2
- Vending-Bench 2 (Andon Labs; via llm-stats, updated 2 Sep 2026): Opus 4.6 leads the listed models at 8,017 (score = final bank balance after a simulated year). Only four models listed; newer scores (Opus 5, Fable) could not be verified (Andon Labs page returned 403). https://llm-stats.com/benchmarks/vending-bench-2 (medium/low)

### 1.6 Why reliability drops with length
- "Beyond the Leaderboard" synthesis (arXiv, 7 Jul 2026; 27 papers, 19 benchmarks): "failures compound nonlinearly with task length", "strong performance on individual sub-tasks does not reliably translate into end-to-end success", and "additional scaffolding does not consistently improve reliability". Six clusters incl. long-horizon degradation from context accumulation and multi-agent coordination failures. https://arxiv.org/abs/2607.05775
- METR developer RCT (10 Jul 2025): experienced OSS devs were 19 % slower with early-2025 tools while believing they were 20 % faster. Feb 24 2026 update: METR changed the design because participants refused to work without AI; METR believes speed-up is now likely but has no reliable estimate. https://metr.org/blog/2026-02-24-uplift-update/

## 2. Orchestration primitives

### 2.1 Anthropic: orchestrator-worker
- Research system post (13 Jun 2025): lead agent (Opus 4) + parallel Sonnet 4 subagents + citation agent beat single Opus 4 by 90.2 % on an internal research eval; "agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens"; parallel tool calls cut research time up to 90 %; needs durable resumption and rainbow deploys; human testers caught hallucinations and source-selection bias that automated evals missed. https://www.anthropic.com/engineering/multi-agent-research-system
- "When to use multi-agent systems" (23 Jan 2026): use subagents for context isolation, parallelism, specialization; "3–10x more tokens"; the "early victory problem" — verification subagents mark work passing after minimal testing, mitigate with "You MUST run the complete test suite before marking as passed"; "Start with the simplest approach that works". https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them

### 2.2 Claude Code: subagents, agent teams, Managed Agents
- Subagents (docs): frontmatter `model` (sonnet/opus/haiku/fable), `maxTurns` (output marked partial), `background`, `isolation: worktree`, `hooks`, `mcpServers`, `effort`, `permissionMode`; default 20 concurrent subagents, spawn depth 3; resumable via `SendMessage`. https://code.claude.com/docs/en/sub-agents
- Agent teams (docs, v2.1.178+): experimental, off by default (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`); lead + teammates with a shared task list (file-locked claiming, dependencies) and JSON mailboxes; quality gates via `TeammateIdle`/`TaskCreated`/`TaskCompleted` hooks (exit code 2 blocks); limits: no session resumption for in-process teammates, one team per session, no nested teams, lead fixed, interactive only (not in `-p`/Agent SDK); guidance 3–5 teammates, 5–6 tasks each; "Letting a team run unattended for too long increases the risk of wasted effort". https://code.claude.com/docs/en/agent-teams
- Cost doc: average ~$13/dev/active day, $150–250/dev/month, 90 % of users under $30/day; agent teams "approximately 7x more tokens than standard sessions when teammates run in plan mode"; use Sonnet for teammates; `--max-budget-usd` exists. https://code.claude.com/docs/en/costs
- Claude Managed Agents (beta header `managed-agents-2026-04-01`): hosted harness with sandbox, sessions that "resume cleanly after pauses", steer/interrupt mid-run, scheduled deployments (cron), MCP servers; not ZDR/HIPAA-eligible; $0.08 per session-hour plus tokens (worked example: 1 h Opus 5 session with 50k in / 15k out ≈ $0.705). https://platform.claude.com/docs/en/managed-agents/overview and https://platform.claude.com/docs/en/about-claude/pricing

### 2.3 OpenAI Agents SDK, AgentKit
- Agents SDK: first PyPI release 4 Mar 2025, latest 0.22.0 on 19 Aug 2026. https://pypi.org/project/openai-agents/
- Handoffs = transfer of control between agents; HITL = tools declare `needs_approval` (bool or async callable that fails closed), run pauses with `RunResult.interruptions`, `result.to_state()` → `state.approve()/reject()` → `Runner.run(agent, state)`; `RunState.to_json()` persists across processes; works for function tools, `Agent.as_tool()`, shell/patch tools and MCP servers. https://openai.github.io/openai-agents-python/human_in_the_loop/
- AgentKit (launched 6 Oct 2025): Agent Builder, Evals platform and reusable Prompts are being wound down on 30 Nov 2026 (Evals read-only 31 Oct); ChatKit and Connector Registry stay; OpenAI points to the Agents SDK for code workflows. https://therouter.ai/news/openai-evals-agent-builder-prompts-deprecation-november-2026/ (secondary; medium confidence — OpenAI's deprecation page not fetched)

### 2.4 LangGraph, CrewAI, Microsoft Agent Framework (AutoGen successor)
- LangGraph 1.0 GA in late October 2025 with durable state, persistence, first-class HITL. https://www.langchain.com/blog/langchain-langgraph-1dot0 (medium; changelog URL redirected)
- Interrupts: `interrupt()` in a node + `Command(resume=...)`; requires a checkpointer; `thread_id` is the persistent cursor; the node restarts from its beginning on resume, so pre-interrupt code must be idempotent. https://docs.langchain.com/oss/python/langgraph/interrupts
- Microsoft Agent Framework: RC 19 Feb 2026, "successor to Semantic Kernel and AutoGen", graph workflows with "sequential, concurrent, handoff, and group chat patterns with streaming, checkpointing, and human-in-the-loop"; GA reported early April 2026 (press). https://devblogs.microsoft.com/foundry/microsoft-agent-framework-reaches-release-candidate/ ; https://visualstudiomagazine.com/articles/2026/04/06/microsoft-ships-production-ready-agent-framework-1-0-for-net-and-python.aspx (403 on fetch; date from search index, medium)
- CrewAI: 58k GitHub stars; "Crews" (autonomous role-based agents) vs "Flows" (event-driven, precise control). https://github.com/crewAIInc/crewAI

## 3. Durable execution
- Temporal × OpenAI Agents SDK: announced 30 Jul 2025, GA 23 Mar 2026; every agent invocation runs as a Temporal Activity, workflows survive crashes/rate limits, `activity_as_tool` wraps activities as tools. https://temporal.io/blog/announcing-openai-agents-sdk-integration
- Temporal + agentic sandboxes (16 Apr 2026): agents that build up a working environment over days need durable state; idle waiting costs zero compute. https://temporal.io/blog/introducing-temporal-and-agentic-sandboxes-openai-agents-sdk
- Inngest AgentKit HITL: a tool calls `step.waitForEvent("developer.response", { timeout: "4h", match })`; the function suspends with no compute and resumes on the event. https://agentkit.inngest.com/advanced-patterns/human-in-the-loop
- No official Temporal ↔ Claude Agent SDK integration found; community guides only (low confidence that one exists).

## 4. Human-in-the-loop approval patterns (comparison)

| Mechanism | Where the pause lives | Survives process restart | Fits Linear as OS |
|---|---|---|---|
| OpenAI `needs_approval` + `RunState` JSON | SDK run state you persist | Yes (you store the JSON) | Store state on the Linear issue; resume from webhook |
| LangGraph `interrupt()` + checkpointer | Graph checkpoint, keyed by `thread_id` | Yes | thread_id = Linear issue id |
| Inngest `waitForEvent` / Temporal signal | Durable workflow engine | Yes, with timeout | Linear webhook → event → resume |
| Claude Code hooks (`TaskCompleted` exit 2, permission prompts) | Interactive session | No | Good for local demo, not for unattended runs |
| Managed Agents session `idle` waiting for "tool confirmation" | Anthropic-hosted session | Yes (server-side state) | Session id on the Linear issue |
| Linear-native: assign to agent → `AgentSession`, state changes, comments | Linear itself | Yes | Native |

Design principle from Project Vend and Anthropic's guidance: approvals must be structural (workflow state + checklist), not "ask a supervisor agent", because supervisor agents share the workers' compliance bias.

## 5. Verification, judge panels, adversarial review
- RuVerBench (29 Jun 2026; 2,458 instances, deep-research + coding): even the best judges "still exhibit substantial noise"; batching lowers accuracy; majority voting helps with diminishing returns. https://arxiv.org/abs/2606.29920
- Anthropic's Jan 2026 guidance: verification subagents have an "early victory" bias; force complete test runs. Claude Code agent-teams docs recommend adversarial "competing hypotheses" teammates that try to disprove each other. https://code.claude.com/docs/en/agent-teams
- GDPval's own human-grader agreement of 66 % caps how much any LLM judge can be trusted on open-ended deliverables. https://www.transformernews.ai/p/openai-gdpval-ai-jobs-work
- Practical pattern: executor model ≠ verifier model; verifier gets a rubric plus machine checks (tests, Lighthouse, screenshot diff); majority vote of 3 only for subjective deliverables; humans sample-audit.

## 6. Evaluation and observability (pricing as of fetch date, 2 Sep 2026)
- Braintrust: Starter $0 (14-day retention, $10 credits, 10k scores), Pro $249/mo (30-day retention, $100 credits, 50k scores), Enterprise custom; unlimited users. https://www.braintrust.dev/pricing
- Langfuse: Hobby free (50k units, 2 users), Core $29/mo (100k units, unlimited users, 90 days), Pro $199/mo, Enterprise $2,499/mo; MIT self-host free. https://langfuse.com/pricing
- LangSmith: Developer $0/seat (5k base traces), Plus $39/seat (10k base traces), Enterprise custom; base traces 14-day, extended 400-day. https://www.langchain.com/pricing
- Feature parity summary (MarkTechPost, 9 Aug 2026): all three do nested agent traces, OpenTelemetry ingestion, LLM-as-judge evaluators, dataset regression in CI. https://www.marktechpost.com/2026/08/09/top-llm-observability-and-evaluation-platforms-in-2026-langfuse-langsmith-braintrust-arize-and-more-compared/
- Claude Code exports OpenTelemetry metrics per user; MCP 2026-07-28 standardises `traceparent`/`tracestate` propagation in `_meta`, so one trace can span orchestrator → MCP server.

## 7. MCP ecosystem maturity
- Donated to the Agentic AI Foundation (Linux Foundation) on 9 Dec 2025; co-founded by Anthropic, Block, OpenAI with Google, Microsoft, AWS, Cloudflare, Bloomberg; "more than 10,000 active public MCP servers", "97M+ monthly SDK downloads". https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation
- Spec 2026-07-28 (RC 21 May 2026, final 28 Jul 2026): stateless core (no `Mcp-Session-Id`, no initialize handshake, `server/discover`), Tasks moved to an official extension with polling, Multi Round-Trip Requests replace server-initiated elicitation/sampling, Roots/Sampling/Logging deprecated, OTel trace propagation, 12-month deprecation policy. https://modelcontextprotocol.io/specification/2026-07-28/changelog ; https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/
- Official registry still "in preview. Breaking changes or data resets may occur before general availability"; namespace-verified metadata only, no private servers, security scanning delegated to npm/PyPI. https://modelcontextprotocol.io/registry/about
- Verdict: protocol is mature and vendor-neutral; discovery/trust layer is not. For the demo, treat every MCP server as a reviewed dependency and prefer CLIs (gh, shopify) where Claude Code docs say they are cheaper in context.

## 8. Cost control levers (verified prices)
- Claude API (2 Sep 2026): Fable 5.1 $10/$50 per MTok (cache read 0.025x = $0.25), Opus 5 $5/$25, Sonnet 5 $2/$10 (introductory price made permanent; Sep 1 increase cancelled), Haiku 4.5 $1/$5; batch −50 %; 1M context at standard price; 4.7+ tokenizer ≈ 30 % more tokens for the same text; web search $10/1k searches. https://platform.claude.com/docs/en/about-claude/pricing
- Multipliers to budget for: agents 4x chat, multi-agent 15x chat (Anthropic 2025); multi-agent 3–10x single agent (Anthropic 2026); agent teams ~7x a session in plan mode (Claude Code docs).
- Levers: model tiering per role (planner/reviewer on Fable or Opus, workers on Sonnet, formatting on Haiku), `maxTurns` and `--max-budget-usd` per issue, prompt caching with 1 h TTL for long workers, `/clear` between tasks, Managed Agents $0.08/session-hour only while `running`, OpenTelemetry cost attribution per agent role. CloudZero (18 May 2026) reports Opus-orchestrator/Sonnet-worker/Haiku-formatter tiering ≈ 40 % cheaper than all-Opus (secondary). https://www.cloudzero.com/blog/claude-code-agents/

## 9. Linear as the agency operating system (what already exists natively)
- Agent API (Developer Preview): assigning an issue to an agent sets it as `delegate`, not `assignee` ("humans maintain ownership"); `AgentSessionEvent` webhook; agent should emit a `thought` activity within 10 s; OAuth `actor=app` with `app:assignable` / `app:mentionable`; agents are not billable users. https://linear.app/developers/agents
- Linear Agent (public beta 24 Mar 2026): triage, answer questions, create follow-up work, draft project updates; core on all plans, Automations and Code Intelligence on Business/Enterprise; free during beta with pricing expected at GA. https://linear.app/changelog/2026-03-24-introducing-linear-agent
- Coding sessions (11 Jun 2026): Linear Agent writes code with Claude Code and Codex, produces a diff/PR for review; Basic/Business/Enterprise, AI credits; Linear reports resolving "roughly 30% of incoming bug reports, mostly on the first pass" internally. https://linear.app/changelog/2026-06-11-coding-sessions
- Loops (20 Jul 2026): scheduled or event-triggered agent runs (examine incoming issues, route to coding agents, maintain specs); Business/Enterprise, AI credits; $20/seat promo credits expired 20 Aug 2026. https://linear.app/changelog/2026-07-20-introducing-loops
- Pricing: Free $0, Basic $10, Business $16, Enterprise custom; "Agent platform" listed on Free; Coding sessions and Loops "require AI credits". https://linear.app/pricing

## 10. Findings table

| # | Claim | Source URL | Date | Confidence | Impact |
|---|---|---|---|---|---|
| 1 | 80 %-success time horizon of best public models is 1–3 h of expert software work (Opus 4.6 1 h 10 min; Mythos Preview 3 h 06 min); 50 % horizon ~12 h | https://en.wikipedia.org/wiki/METR ; https://x.com/METR_Evals/status/2052896621760004602 | Feb–Jun 2026 | medium (secondary table citing METR) | high |
| 2 | METR: measurements above 16 h unreliable; error bars ~2x each way; ~170 tasks; long-run doubling 6–7 months | https://metr.org/time-horizons/ ; https://metr.org/notes/2026-01-22-time-horizon-limitations/ | 8 May 2026 / 22 Jan 2026 | high | high |
| 3 | Time horizons are 40–100x lower for visual computer-use tasks than for software | https://metr.org/notes/2026-01-22-time-horizon-limitations/ | 22 Jan 2026 | high | high |
| 4 | Failures compound nonlinearly with task length; extra scaffolding does not consistently improve reliability | https://arxiv.org/abs/2607.05775 | 7 Jul 2026 | high | high |
| 5 | pass^k decays exponentially; τ³-banking best pass^1 only 55.2 % (Opus 5 48.7 %) | https://arxiv.org/abs/2406.12045 ; https://taubench.com | Jun 2024 / Mar 2026 | high | high |
| 6 | SWE-bench Verified saturated (~95–97 %); SWE-bench Pro public split 27–34 % broken, OpenAI retracted its recommendation | https://codeant.ai/blogs/swe-bench-scores ; https://www.investing.com/news/stock-market-news/openai-retracts-swebench-pro-coding-benchmark-recommendation-93CH-4782526 | Aug 2026 / 8 Jul 2026 | medium / high | high |
| 7 | Fable 5.1 tops SWE-bench Pro at 81.2 % (vendor-reported rows) | https://benchlm.ai/benchmarks/swe-bench-pro | 1 Sep 2026 | medium | medium |
| 8 | GDPval: best model 47.6 % wins-or-ties vs experts on one-shot deliverables; grader agreement 66 %; no multi-step/relationship work measured | https://www.transformernews.ai/p/openai-gdpval-ai-jobs-work | 2 Oct 2025 | high | high |
| 9 | GDPval-AA v2: Fable 5.1 Elo 1,853 vs human baseline 1,000 (LLM-judged, agentic harness) | https://artificialanalysis.ai/evaluations/gdpval-aa | Sep 2026 | high | medium |
| 10 | Project Vend 2: profitable only with bureaucracy; CEO agent approved lenient requests ~8x more than it denied; social-engineered | https://www.anthropic.com/research/project-vend-2 | 18 Dec 2025 | high | high |
| 11 | Orchestrator-worker beat single agent by 90.2 % on breadth-first research; multi-agent ≈ 15x chat tokens | https://www.anthropic.com/engineering/multi-agent-research-system | 13 Jun 2025 | high | high |
| 12 | Multi-agent uses 3–10x tokens of single agent; "early victory" problem in verifier subagents; start simple | https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them | 23 Jan 2026 | high | high |
| 13 | Claude Code agent teams are experimental, single-session, not resumable, interactive-only; hooks can block task completion | https://code.claude.com/docs/en/agent-teams | v2.1.178+ (2026) | high | high |
| 14 | Claude Code subagents: `maxTurns`, per-role `model`, worktree isolation, 20 concurrent, depth 3 | https://code.claude.com/docs/en/sub-agents | 2026 | high | medium |
| 15 | Claude Code cost: ~$13/dev/day, $150–250/month; agent teams ~7x tokens in plan mode | https://code.claude.com/docs/en/costs | 2026 | high | high |
| 16 | Managed Agents (beta): resumable long-running sessions, scheduled deployments, $0.08/session-hour + tokens; not ZDR/HIPAA | https://platform.claude.com/docs/en/managed-agents/overview ; https://platform.claude.com/docs/en/about-claude/pricing | beta header 2026-04-01 | high | high |
| 17 | Claude prices: Fable 5.1 $10/$50, Opus 5 $5/$25, Sonnet 5 $2/$10 (permanent), Haiku 4.5 $1/$5; cache read 0.1x (0.025x Fable 5.1); batch −50 % | https://platform.claude.com/docs/en/about-claude/pricing | 2 Sep 2026 | high | high |
| 18 | OpenAI Agents SDK 0.22.0 (19 Aug 2026); HITL via `needs_approval` + serializable `RunState` | https://pypi.org/project/openai-agents/ ; https://openai.github.io/openai-agents-python/human_in_the_loop/ | Aug 2026 | high | medium |
| 19 | OpenAI Agent Builder + Evals + Prompts shut down 30 Nov 2026; ChatKit stays | https://therouter.ai/news/openai-evals-agent-builder-prompts-deprecation-november-2026/ | Jun 2026 | medium | medium |
| 20 | Temporal × OpenAI Agents SDK GA 23 Mar 2026; sandboxes + durable idle Apr 2026 | https://temporal.io/blog/announcing-openai-agents-sdk-integration ; https://temporal.io/blog/introducing-temporal-and-agentic-sandboxes-openai-agents-sdk | Mar/Apr 2026 | high | medium |
| 21 | Inngest AgentKit HITL: `step.waitForEvent` with timeout (e.g. 4h), zero compute while waiting | https://agentkit.inngest.com/advanced-patterns/human-in-the-loop | 2026 (undated page) | high | medium |
| 22 | LangGraph `interrupt()`/`Command(resume)` needs checkpointer; node re-runs from start on resume | https://docs.langchain.com/oss/python/langgraph/interrupts | 2026 (undated) | high | medium |
| 23 | Microsoft Agent Framework = AutoGen + Semantic Kernel successor; RC 19 Feb 2026, GA Apr 2026 | https://devblogs.microsoft.com/foundry/microsoft-agent-framework-reaches-release-candidate/ | 19 Feb 2026 | high (RC) / medium (GA) | low |
| 24 | LLM judges remain noisy on rubric verification; majority voting has diminishing returns | https://arxiv.org/abs/2606.29920 | 29 Jun 2026 | high | high |
| 25 | MCP under Linux Foundation AAIF; 10k+ servers, 97M+ monthly SDK downloads | https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation | 9 Dec 2025 | high | medium |
| 26 | MCP spec 2026-07-28: stateless core, Tasks extension, MRTR, OTel propagation, deprecation policy | https://modelcontextprotocol.io/specification/2026-07-28/changelog | 28 Jul 2026 | high | medium |
| 27 | Official MCP registry still preview; no private servers; scanning delegated | https://modelcontextprotocol.io/registry/about | 2026 | high | medium |
| 28 | Observability prices: Braintrust $0/$249; Langfuse $0/$29/$199 (self-host free); LangSmith $0/$39 per seat | https://www.braintrust.dev/pricing ; https://langfuse.com/pricing ; https://www.langchain.com/pricing | 2 Sep 2026 | high | medium |
| 29 | Linear Agent API: delegate ≠ assignee, AgentSession webhooks, agents not billable; Developer Preview | https://linear.app/developers/agents | 2026 | high | high |
| 30 | Linear coding sessions GA (Claude Code + Codex), Linear resolves ~30 % of its own bug reports first pass | https://linear.app/changelog/2026-06-11-coding-sessions | 11 Jun 2026 | high | high |
| 31 | Linear Loops: scheduled/event-driven agent runs on Business/Enterprise with AI credits | https://linear.app/changelog/2026-07-20-introducing-loops | 20 Jul 2026 | high | high |
| 32 | Linear pricing Free/Basic $10/Business $16; coding sessions + Loops need AI credits | https://linear.app/pricing | 2 Sep 2026 | high | medium |
| 33 | METR dev RCT: 19 % slowdown (2025); 2026 redesign, likely speed-up now but no reliable estimate | https://metr.org/blog/2026-02-24-uplift-update/ | 24 Feb 2026 | high | medium |

## 11. What this means for the AI-agency demo

1. **Unit of autonomy = one Linear issue ≤ ~2 h expert-equivalent with a machine-checkable Done.** That is the 80 % band. Larger client requests become Linear projects that a planner agent decomposes; the decomposition itself is a human-approval gate. Never let an agent own a multi-day outcome without checkpoints.
2. **Linear is the shared task list; Claude Code agent teams are not the backbone.** Agent teams are experimental, interactive-only, non-resumable and one-per-session. Use Linear issues/states as the durable task list, and run workers as Claude Code subagents (`maxTurns`, per-role `model`, worktree isolation) or Managed Agents sessions, triggered by Linear `AgentSessionEvent` webhooks or Loops.
3. **Approval gates are workflow states, not supervisor agents.** Project Vend showed a CEO agent rubber-stamps. Model gates as Linear states ("Needs approval", "In review", "Client sign-off") with a human as `assignee` and the agent as `delegate`; durable waits via Inngest `waitForEvent`/Managed Agents idle sessions if you go beyond a demo.
4. **Verifier ≠ executor, and verifiers get tools, not just rubrics.** Use a different model family (e.g. Codex/GPT-5.6 Sol reviewing Claude output or vice versa), force full test runs (early-victory mitigation), and give reviewers deterministic checks (tests, Lighthouse, screenshot diff, Semrush/Shopify data). Accept that LLM judges are noisy (RuVerBench, 66 % human agreement on GDPval): humans sample-audit.
5. **Budget with 3–15x multipliers and tier models.** Fable 5.1 for planning/final review, Sonnet 5 ($2/$10) for workers, Haiku 4.5 for formatting/triage; 1 h cache TTL on long workers; `--max-budget-usd`/`maxTurns` per issue; OTel cost per agent role into Langfuse (self-host) or Braintrust free tier. Example scale: a 1 h Opus 5 Managed Agents session ≈ $0.70; a busy multi-agent day per "seat" ≈ $30–130 (CloudZero figures, secondary).
6. **Build your own eval set before trusting any leaderboard.** SWE-bench Pro is partly broken; τ-bench shows 50 % on knowledge-heavy service tasks. Take 20–30 closed Orbit tickets (bug, theme change, SEO brief) as a regression dataset in Langfuse/Braintrust and gate agent role changes on it.
7. **Sales and marketing roles: draft, don't commit.** GDPval-level parity covers one-shot deliverables (proposals, audits, ad copy); the unmeasured part is judgment and relationships. Agents produce proposals and campaign plans into Linear; a human sends them. Social-engineering resistance is unproven (Project Vend), so no agent should hold discount or contract authority.
8. **Exploit Linear-native agents first, custom agents second.** Linear Agent + Loops + coding sessions already cover triage → route → code → PR. Custom agents via the Agent API add QA, SEO/marketing, reporting and sales-drafting roles, each with its own MCP allowlist and OTel trace.

## 12. Not verified / open gaps
- No public METR time-horizon for Claude Fable 5 / 5.1, Opus 5 or GPT-5.6 Sol 80 % band (system card too large to fetch; METR page hides values in a chart).
- Vending-Bench 2 scores for Opus 5 / Fable (Andon Labs page returned 403; a press claim of "$11,182 profit for Opus 5" is unverified — low confidence).
- OpenAI's own SWE-bench Pro post and GDPval page returned 403; figures come from reputable press and the PDF summary.
- Braintrust's reported $80M Series B (Feb 2026) not verified — excluded from findings.
- Claude Code "ultra" cloud multi-agent code review: present in this environment's skill listing, no public doc fetched.
- Microsoft Agent Framework GA date (3 Apr 2026) is from press, primary post not fetched.
- OpenAI Agent Builder wind-down: secondary sources only; check https://platform.openai.com/docs/deprecations before relying on it.
