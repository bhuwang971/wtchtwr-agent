# Feature Deep Dives

This section explains the product feature-by-feature, with both user value and implementation path.

## 1. Chat

### What it does

Lets users ask natural-language questions about portfolio metrics, reviews, triage, and expansion.

### Why it exists

- main natural-language interface to the system
- unifies SQL, RAG, and hybrid workflows behind one entry point

### End-to-end path

- UI: [`frontend/src/pages/Chat.tsx`](../../frontend/src/pages/Chat.tsx)
- input: [`frontend/src/components/ChatInput.tsx`](../../frontend/src/components/ChatInput.tsx)
- rendering: [`frontend/src/components/Message.tsx`](../../frontend/src/components/Message.tsx)
- API: [`backend/main.py::post_message`](../../backend/main.py)
- orchestration: [`agent/graph.py`](../../agent/graph.py)

### Tradeoffs

- strongest UX surface
- also the most complex UX/state path because it handles streaming, errors, commands, summaries, and exports

## 2. Dashboard

### What it does

Shows KPI and map-based analytics for Highbury vs comparison cohorts.

### Why it exists

- some users want direct visual analytics, not only narrated answers

### End-to-end path

- UI: [`frontend/src/pages/Dashboard.tsx`](../../frontend/src/pages/Dashboard.tsx)
- API: [`backend/dashboard_router.py`](../../backend/dashboard_router.py)
- compute layer: [`backend/dashboard.py::build_dashboard_response`](../../backend/dashboard.py)

### Dependencies

- DuckDB
- cached parquet feature table
- Deck.gl
- Recharts

### Tradeoffs

- efficient for visual exploration
- separate from agent path, so some business logic is duplicated between dashboard and chat abstractions

## 3. Summarize Conversation

### What it does

Creates concise and detailed summaries of a conversation thread.

### Why it exists

- converts chat into a reusable artifact
- useful for email handoff and meeting prep

### End-to-end path

- UI action: [`frontend/src/pages/Chat.tsx::handleSummarize`](../../frontend/src/pages/Chat.tsx)
- API helper: [`frontend/src/lib/api.ts::summarizeConversation`](../../frontend/src/lib/api.ts)
- backend builder: [`backend/main.py::_build_conversation_summary`](../../backend/main.py)

### Technical note

The backend summary path uses both:

- trace-derived concise summaries
- message-derived detailed summaries

So it is not just “send entire chat transcript to an LLM.”

## 4. Email

### What it does

Emails summaries and exports.

### Why it exists

- makes findings shareable without leaving the product

### End-to-end path

- frontend summary email: [`frontend/src/lib/api.ts::sendSummaryEmail`](../../frontend/src/lib/api.ts)
- backend email endpoints: [`backend/main.py`](../../backend/main.py)
- mail transport: [`backend/emailer.py`](../../backend/emailer.py)

### Tradeoffs

- useful for operator workflows
- requires SMTP config, so it is environment-dependent

## 5. Export

### What it does

Exports table results from chat and Data Explorer.

### Why it exists

- users often want data, not just narrative

### End-to-end path

- chat export UI: [`frontend/src/pages/Chat.tsx`](../../frontend/src/pages/Chat.tsx)
- Data Explorer export UI: [`frontend/src/pages/DataExport.tsx`](../../frontend/src/pages/DataExport.tsx)
- backend export endpoints: [`backend/main.py`](../../backend/main.py)
- in-memory CSV staging: [`backend/exporter.py`](../../backend/exporter.py)
- optional large-file fallback: [`backend/gdrive.py`](../../backend/gdrive.py)

### Tradeoffs

- strong analyst usability
- export logic adds operational complexity and file-size branching

## 6. History

### What it does

Shows past conversations, supports reopen/rename/delete.

### Why it exists

- makes the app feel like a persistent workspace, not a disposable chatbot

### End-to-end path

- UI: [`frontend/src/pages/History.tsx`](../../frontend/src/pages/History.tsx)
- APIs: `listConversations`, `getConversation`, `updateConversationTitle`, `deleteConversation`
- backend persistence: [`backend/main.py`](../../backend/main.py)

## 7. Citations / Trace / Confidence

### What it does

Shows how the answer was produced and how trustworthy it appears.

### Why it exists

- critical for AI trust and interview demos

### End-to-end path

- backend trace/confidence: [`backend/ai_observability.py`](../../backend/ai_observability.py)
- payload shaping: [`backend/main.py::build_assistant_payload`](../../backend/main.py)
- UI rendering: [`frontend/src/components/Message.tsx`](../../frontend/src/components/Message.tsx)

### Tradeoffs

- very strong trust/debug feature
- confidence is heuristic, not calibrated

## 8. Portfolio Triage

### What it does

Produces a ranking/backlog style analysis of portfolio performance instead of a simple SQL answer.

### Why it exists

- operators often need prioritized action plans, not only KPIs

### End-to-end path

- route selection: [`agent/policy.py::plan_steps`](../../agent/policy.py)
- execution: [`agent/portfolio_triage.py::run_portfolio_triage`](../../agent/portfolio_triage.py)
- graph node: [`agent/graph.py::_portfolio_triage_node`](../../agent/graph.py)
- final rendering: same chat payload path

### Dependencies

- SQL execution
- market benchmark lookups
- RAG snippets for root-cause context

### Tradeoffs

- high business value
- more domain-specific and therefore more custom logic than generic SQL/RAG paths

## 9. Expansion Scout

### What it does

Recommends neighborhoods for future expansion using web-grounded external signals.

### Why it exists

- growth strategy is an important business workflow not covered by portfolio-only SQL

### End-to-end path

- route selection: [`agent/intents.py`](../../agent/intents.py), [`agent/policy.py`](../../agent/policy.py)
- execution: [`agent/expansion_scout.py::exec_expansion_scout`](../../agent/expansion_scout.py)
- synthesis: `synthesize_expansion_report(...)`
- final rendering: same chat payload path

### Dependencies

- Tavily search
- HTTP article fetch/parsing
- optional PDF extraction
- OpenAI synthesis

### Tradeoffs

- strongest “agentic” demo feature
- also the least deterministic feature due to external sources

## 10. Data Explorer

### What it does

Lets users query approved tables/columns in a more structured self-serve mode.

### Why it exists

- bridges natural-language analytics and explicit analyst-style querying

### End-to-end path

- UI: [`frontend/src/pages/DataExport.tsx`](../../frontend/src/pages/DataExport.tsx)
- backend: [`backend/data_explorer.py`](../../backend/data_explorer.py)
- endpoints: [`backend/main.py`](../../backend/main.py)

### Tradeoffs

- safer than freeform SQL
- more rigid than natural-language chat

## 11. AI Metrics / Admin-Style Benchmark Dashboard

### What it does

Shows benchmark pack metrics and case-level diagnostics inside the app.

### Why it exists

- makes the evaluation story visible during demos and interviews

### End-to-end path

- backend aggregation: [`backend/ai_observability.py::load_ai_metrics_payload`](../../backend/ai_observability.py)
- API: `GET /api/ai/metrics`
- UI: [`frontend/src/pages/AiMetrics.tsx`](../../frontend/src/pages/AiMetrics.tsx)

### What it shows

- pack leaderboard
- selected pack stats
- trend history
- failed cases
- slowest cases
- exact benchmark question/output/assertions

## 12. Slack Integration

### What it does

Lets the same assistant be used from Slack.

### Why it exists

- extends the assistant into an operator collaboration channel

### End-to-end path

- frontend shortcuts/openers: [`frontend/src/App.tsx`](../../frontend/src/App.tsx), [`frontend/src/pages/Chat.tsx`](../../frontend/src/pages/Chat.tsx)
- backend lifecycle: [`backend/main.py::_start_slack_bot_thread`](../../backend/main.py)
- actual bot logic: [`agent/slack/bot.py`](../../agent/slack/bot.py)

### Important design choice

The Slack bot reuses the same backend conversation API rather than building a separate inference path.

## Strongest Features For Interviews

If you need to choose what to demo:

1. chat with trace/confidence
2. AI metrics page
3. one hybrid question
4. one triage question
5. one expansion question

That sequence shows architecture, grounding, observability, and business value in a compact way.

