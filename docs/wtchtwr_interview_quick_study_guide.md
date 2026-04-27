# wtchtwr Interview Quick Study Guide

This is the quick pre-interview guide for the `wtchtwr` project. It explains what the system does, how the stack fits together, how a user query flows through the agent, how accuracy/hallucination handling works, and how to defend the resume bullets honestly.

## 1. One-Minute Project Pitch

`wtchtwr` is an AI-powered short-term-rental analytics copilot. It helps operators ask natural-language questions about portfolio performance, market benchmarks, pricing, occupancy, revenue, and guest reviews.

The system combines:

- Text-to-SQL over DuckDB for structured KPI questions.
- RAG over Qdrant for guest review and sentiment questions.
- Hybrid SQL + RAG answers when a user wants both metrics and review evidence.
- Dashboard, data explorer, export, summary email, Slack bot, history, and AI metrics views.
- Evaluation packs for regression, holdout, and adversarial accuracy testing.

Interview framing:

> I built this as a constrained agentic analytics system, not just a chatbot. The LLM is routed into deterministic tools like DuckDB and Qdrant, intermediate outputs are verified or scored, and the final answer includes confidence and trace information.

## 2. Repo Map: Where Things Live

| Area | Files |
|---|---|
| Backend/API | `backend/main.py`, `backend/models.py`, `backend/storage.py` |
| Agent graph | `agent/graph.py`, `agent/types.py` |
| Intent and policy | `agent/intents.py`, `agent/policy.py` |
| NL-to-SQL | `agent/nl2sql_llm.py`, `agent/nl2sql.py` |
| RAG/vector search | `agent/vector_qdrant.py`, `scripts/rebuild_review_vectors.py`, `scripts/reindex_qdrant_reviews.py` |
| Composition | `agent/compose.py` |
| Confidence/trace | `backend/ai_observability.py` |
| Dashboard/export | `backend/dashboard_router.py`, `backend/dashboard.py`, `backend/data_explorer.py`, `backend/exporter.py`, `backend/emailer.py` |
| Frontend | `frontend/src/App.tsx`, `frontend/src/pages/Chat.tsx`, `frontend/src/pages/Dashboard.tsx`, `frontend/src/pages/DataExport.tsx`, `frontend/src/pages/AiMetrics.tsx`, `frontend/src/lib/api.ts`, `frontend/src/store/useChat.ts` |
| Evaluation | `evals/runner.py`, `evals/interview_summary.py`, `scripts/run_benchmarks.py`, `evals/benchmarks.local.json`, `evals/benchmarks.holdout.json`, `evals/benchmarks.adversarial.json` |

## 3. Resume Bullets Explained

### Built STR analytics copilot using Text-to-SQL and RAG over DuckDB for instant KPI answers

What it means:

- Users ask business questions like "average price in Brooklyn" or "which Highbury listings are underperforming?"
- Structured metrics are answered from DuckDB.
- Review questions are answered from Qdrant retrieval.
- Hybrid questions combine SQL metrics and review evidence.

Implementation:

- Chat request starts in `frontend/src/pages/Chat.tsx`.
- API calls are defined in `frontend/src/lib/api.ts`.
- FastAPI receives chat messages in `backend/main.py` at `POST /api/conversations/{conversation_id}/messages`.
- The LangGraph workflow in `agent/graph.py` routes the query.
- SQL is handled by `agent/nl2sql_llm.py`.
- RAG is handled by `agent/vector_qdrant.py`.
- Final answer composition is handled by `agent/compose.py`.

How to say it:

> The copilot separates structured and unstructured reasoning. If the user asks for KPIs, it uses NL-to-SQL and DuckDB. If the user asks about guest feedback, it uses Qdrant retrieval. If the user asks for both, the graph runs a hybrid path and fuses the outputs.

### Embedded 660k+ reviews with MiniLM and Sentence-BERT into Qdrant for semantic retrieval with citations

What it means:

- Review text was converted into embeddings.
- Embeddings are numeric vectors representing meaning.
- Qdrant stores those vectors plus metadata.
- At query time, the user question is embedded and matched against review vectors.

Implementation:

- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`.
- Rebuild script: `scripts/rebuild_review_vectors.py`.
- Reindex script: `scripts/reindex_qdrant_reviews.py`.
- Runtime retrieval: `agent/vector_qdrant.py`.
- Artifacts: `vec/airbnb_reviews/reviews_embeddings.npy` and `vec/airbnb_reviews/reviews_metadata.parquet`.

Important nuance:

- Chunking is review-level. One review comment equals one retrieval unit.
- This is simple and traceable, but long reviews can mix multiple themes.

How to say it:

> I used review-level chunking because Airbnb reviews are usually short and each row has clean metadata like listing ID, borough, month, sentiment, and Highbury flag. That makes citations easy. A stronger version would add sentence-window chunks for long reviews.

### Validated Text-to-SQL outputs via manual checks; achieved about 95% accuracy on curated two-table schema

What it means:

- Accuracy was checked against expected behavior, not just whether the answer sounded good.
- The current repo has automated benchmark packs and assertion-level scoring.

Implementation:

- Runner: `evals/runner.py`.
- Summary builder: `evals/interview_summary.py`.
- CLI: `scripts/run_benchmarks.py`.
- Benchmark packs: `evals/benchmarks.local.json`, `evals/benchmarks.holdout.json`, `evals/benchmarks.adversarial.json`.

How to defend the number:

> The resume uses a conservative number from curated manual checks over the core schema. The repo also includes automated benchmark packs that measure SQL, RAG, hybrid, routing, filters, and latency. I would not claim universal 100% accuracy; I would say accuracy is measured per benchmark pack and category.

### Shipped Slack bot and email delivery for summaries and data extracts when services are running

Implementation:

- Slack bot code: `agent/slack/bot.py`.
- Slack runner: `scripts/run_slackbot.py`.
- Slack endpoints: `POST /api/slackbot/start` and `GET /api/slackbot/status` in `backend/main.py`.
- Email logic: `backend/emailer.py`.
- Export logic: `backend/exporter.py`.
- Summary email endpoint: `POST /api/conversations/{conversation_id}/summary/email`.
- Export endpoint: `POST /api/conversations/{conversation_id}/messages/{message_id}/export`.

Limitation:

- Slack and email depend on environment variables, credentials, SMTP config, and running services.

### Built FastAPI gateway with typed schemas and request validation for consistent agent execution

Implementation:

- FastAPI app: `backend/main.py`.
- Pydantic models: `backend/models.py`.
- Frontend API wrappers: `frontend/src/lib/api.ts`.

Important endpoints:

- `GET /api/conversations`
- `POST /api/conversations`
- `POST /api/conversations/{conversation_id}/messages`
- `POST /api/conversations/{conversation_id}/summary`
- `POST /api/conversations/{conversation_id}/summary/email`
- `POST /api/data-explorer/query`
- `POST /api/data-explorer/export`
- `GET /api/health/status`
- `GET /api/ai/metrics`

### Added sentiment scoring with VADER and NLTK to surface review themes behind KPI changes

Repo-grounded explanation:

- The repo uses sentiment-scored review fields: `sentiment_label`, `compound`, `positive`, `neutral`, and `negative`.
- `docs/data_dictionary.md` documents those fields.
- `scripts/inspect_review_sentiment_score.py` references VADER score stats.
- Runtime code consumes sentiment fields in `agent/intents.py`, `agent/policy.py`, `agent/vector_qdrant.py`, `agent/portfolio_triage.py`, and `agent/compose.py`.

Honest caveat:

- The repo clearly contains sentiment-scored artifacts and downstream use. The full original VADER/NLTK scoring pipeline is not deeply implemented as a repeatable ETL job in the current repo.

How to say it:

> The app consumes precomputed VADER-style sentiment labels and scores from the cleaned review data. Those labels drive sentiment filters, retrieval, triage, and sentiment summaries. In a production version I would make the sentiment scoring pipeline a documented scheduled ETL step.

## 4. Tech Stack: What Each Component Does

| Component | What it does here | Why it was a good fit |
|---|---|---|
| React + TypeScript | Frontend UI for chat, dashboard, export, history, metrics | Type-safe interactive UI |
| Vite | Frontend dev/build tool | Fast local iteration |
| Tailwind CSS | Styling through utility classes and `frontend/src/index.css` | Quick consistent UI |
| Zustand | Chat/conversation state in `frontend/src/store/useChat.ts` | Lightweight global state |
| FastAPI | Backend gateway in `backend/main.py` | Typed APIs, async support, easy local serving |
| Pydantic | Request/response validation in `backend/models.py` | Consistent payload contracts |
| LangGraph | Agent orchestration in `agent/graph.py` | Explicit state graph instead of one prompt |
| OpenAI API | SQL generation and answer composition | Natural language reasoning/synthesis |
| DuckDB | Structured analytics database | Fast local analytical SQL |
| Qdrant | Vector database for reviews | Semantic search plus metadata filtering |
| MiniLM / SentenceTransformers | Embedding model | Local, fast semantic embeddings |
| Docker | Runs Qdrant locally | Isolates vector DB service |
| Slack SDK/Bolt | Slack bot integration | Alternate interaction channel |
| SMTP/email | Sends summaries and extracts | Business workflow integration |

## 5. Main Capabilities

### Chat copilot

The chat surface answers natural-language questions, returns tables when useful, and shows confidence/trace metadata.

Files:

- `frontend/src/pages/Chat.tsx`
- `frontend/src/components/ChatInput.tsx`
- `frontend/src/components/Message.tsx`
- `backend/main.py`
- `agent/graph.py`

Example questions:

- "What is the average price in Brooklyn?"
- "Compare Highbury vs market occupancy in Manhattan."
- "What are guests complaining about in Midtown?"
- "Which listings are underperforming?"
- "Where should we expand next?"

### Dashboard

The dashboard is for visual exploration of portfolio and market performance.

Files:

- `frontend/src/pages/Dashboard.tsx`
- `backend/dashboard_router.py`
- `backend/dashboard.py`

It supports filtering and visual inspection of geographic/property slices, market comparisons, KPI cards, charts, and map-style views.

### Data explorer and export

The data export page lets users pick tables/columns, apply filters/sorts, preview results, download CSV, or email extracts.

Files:

- `frontend/src/pages/DataExport.tsx`
- `backend/data_explorer.py`
- `backend/exporter.py`
- `backend/emailer.py`

Flow:

1. Fetch schema from `/api/data-explorer/schema`.
2. User selects tables, columns, filters, sorts, and limit.
3. Preview runs through `/api/data-explorer/query`.
4. Download/email runs through `/api/data-explorer/export`.

### AI metrics page

The AI metrics page shows benchmark packs, pack rankings, accuracy, latency, failed cases, and case outputs.

Files:

- `frontend/src/pages/AiMetrics.tsx`
- `backend/ai_observability.py`
- `GET /api/ai/metrics` in `backend/main.py`
- `evals/reports/*`

### History

Conversation history is persisted and can be reopened.

Files:

- `frontend/src/pages/History.tsx`
- conversation endpoints in `backend/main.py`

## 6. End-to-End Flow When a User Inputs a Question

Plain English flow:

1. User types a question in the React chat UI.
2. Frontend sends it to the FastAPI backend.
3. Backend saves the user message and builds recent conversation history.
4. LangGraph agent receives query, history, filters, and thread state.
5. Intent classifier decides whether this is SQL, RAG, hybrid, triage, expansion, or conversation.
6. Entity resolver extracts filters like borough, month, year, listing ID, sentiment, and Highbury scope.
7. Planner chooses the execution path.
8. Tool path runs:
   - DuckDB for SQL.
   - Qdrant for RAG.
   - SQL + Qdrant for hybrid.
   - specialized workflows for triage/expansion.
9. Results are normalized into a result bundle.
10. Composer creates the final answer from the tool outputs.
11. Backend attaches confidence, trace, citations, tables, and telemetry.
12. Assistant message is persisted.
13. Frontend renders markdown, tables, confidence, and AI trace.

Technical flow:

| Step | What happens | Files/functions |
|---|---|---|
| Capture query | User submits message | `frontend/src/pages/Chat.tsx`, `handleSend` |
| API call | Request to backend | `frontend/src/lib/api.ts`, `sendMessage`; streaming fetch in `Chat.tsx` |
| Receive request | FastAPI endpoint handles message | `backend/main.py`, `POST /api/conversations/{conversation_id}/messages` |
| Persist user turn | Saves user message | `backend/main.py`, `_record_user_message`, `insert_message` |
| Build history | Trims recent chat history | `backend/main.py`, `trim_history` |
| Execute graph | Calls agent runtime | `backend/main.py`, `_execute_langgraph`; `agent/graph.py`, `run` |
| Ingress | Normalizes initial graph state | `agent/graph.py`, `_ingress_node` |
| Guardrails | Applies request guardrails | `agent/graph.py`, `_guardrails_node`; `agent/guards.py` |
| Intent | Classifies task and rough filters | `agent/graph.py`, `_classify_intent_node`; `agent/intents.py`, `classify_intent` |
| Resolve entities | Normalizes filters | `agent/policy.py`, `resolve_entities` |
| Plan route | Chooses mode and policy | `agent/policy.py`, `plan_steps`, `choose_path` |
| SQL path | Generate, verify, repair, execute SQL | `agent/nl2sql_llm.py` |
| RAG path | Embed, search, rerank, summarize reviews | `agent/vector_qdrant.py` |
| Hybrid path | Runs SQL and RAG, fuses outputs | `agent/graph.py`, `_hybrid_fusion_node` |
| Triage | Portfolio diagnostic workflow | `agent/portfolio_triage.py` |
| Expansion | Expansion scout workflow | `agent/expansion_scout.py` |
| Compose | Generates final answer from context | `agent/compose.py`, `compose_answer`, `fallback_text` |
| Payload | Builds tables/confidence/trace | `backend/main.py`, `build_assistant_payload`; `backend/ai_observability.py` |
| Persist answer | Saves assistant message | `backend/main.py`, `_finalize_assistant_message` |
| Render | Shows answer in UI | `frontend/src/components/Message.tsx` |

What can go wrong:

- OpenAI unavailable: SQL generation/composition may fail; fallback text is used where possible.
- Qdrant down: RAG/hybrid degrade; health endpoints show not ready.
- DuckDB unavailable: SQL/dashboard/export fail.
- Filters misclassified: wrong borough, sentiment, or Highbury/market scope.
- Weak retrieval evidence: confidence drops and abstention may be recommended.

## 7. Memory and Conversation State

There are three state layers.

### Browser-side thread state

- `frontend/src/pages/Chat.tsx` uses `THREAD_STORAGE_KEY = "wtchtwr.chat.thread_id"`.
- This stores a stable thread ID in browser localStorage.

### Backend conversation persistence

- `backend/main.py` creates DuckDB tables:
  - `conversations`
  - `messages`
  - `thread_map`
- User and assistant messages are stored with payloads.
- `trim_history` prepares recent turns for the agent.

### LangGraph memory/checkpointing

- `agent/graph.py` uses `MemorySaver`.
- Graph state carries fields like query, intent, scope, filters, plan, SQL, RAG, result bundle, telemetry, and memory.

Important limitation:

- `MemorySaver` is process-local. It is fine for local/demo use, but production would need Redis, Postgres, Cosmos DB, or another durable checkpoint store.

## 8. Orchestrator, Intent Classifier, Planner

### Orchestrator

The orchestrator is the LangGraph workflow in `agent/graph.py`.

Core nodes:

- `_ingress_node`
- `_guardrails_node`
- `_classify_intent_node`
- `_resolve_entities_node`
- `_plan_steps_node`
- `_plan_to_sql_node`
- `_exec_rag_node`
- `_hybrid_fusion_node`
- `_portfolio_triage_node`
- `_expansion_scout_node`
- `_compose_node`
- `_egress_node`

Why a graph exists:

- A single prompt would be harder to debug, evaluate, and constrain.
- A graph gives explicit routing and tool boundaries.
- Intermediate state can be inspected in the AI trace.

Tradeoff:

- More moving parts.
- Routing bugs are possible.
- State contracts must be kept consistent.

### Intent classifier

File:

- `agent/intents.py`

It detects:

- greeting/thanks
- SQL metric questions
- RAG/review questions
- hybrid questions
- portfolio triage
- expansion scout
- Highbury vs market vs hybrid scope
- filters like borough, neighborhood, month, year, listing ID, sentiment label

### Policy/planner

File:

- `agent/policy.py`

It converts intent/scope/filters into:

- `mode`: `sql`, `rag`, `hybrid`, `portfolio_triage`, `expansion_scout`, or `chat`
- `policy`: examples include `SQL_HIGHBURY`, `SQL_MARKET`, `SQL_COMPARE`, `RAG_MARKET`, `SQL_RAG_COMPARE`, `PORTFOLIO_TRIAGE`, `EXPANSION_SCOUT`
- retrieval `top_k`
- table target
- sentiment usage

Interview phrase:

> The planner is the control plane. It decides which deterministic tool path should handle the question before the LLM writes the final response.

## 9. NL-to-SQL: How It Works

File:

- `agent/nl2sql_llm.py`

Flow:

1. Planner routes to SQL.
2. `build_prompt` creates a schema-aware prompt using `SCHEMA_BLOCK`.
3. OpenAI generates DuckDB SQL.
4. SQL is cleaned.
5. `verify_sql` runs `EXPLAIN` against DuckDB.
6. `verify_and_repair_sql` attempts deterministic and optional LLM repair.
7. `execute_duckdb` runs the SQL.
8. Rows, columns, markdown table, and summaries are returned to graph state.

Why this design:

- Schema grounding reduces hallucinated tables/columns.
- `EXPLAIN` catches invalid SQL before execution.
- Repair loop reduces brittle failures.
- DuckDB is lightweight and fast for local analytical workloads.

Limitations:

- Verification catches syntax/planning errors, not every business-logic error.
- The LLM can generate semantically plausible but analytically wrong SQL.
- A stronger version would add golden SQL templates and logical-plan validation.

Strong answer:

> SQL verification prevents invalid queries, but it does not prove semantic correctness. That is why I also use benchmark assertions for expected filters, SQL fragments, row counts, and outputs.

## 10. RAG and Vector Search

Files:

- `scripts/rebuild_review_vectors.py`
- `scripts/reindex_qdrant_reviews.py`
- `agent/vector_qdrant.py`

Data:

- Source review sentiment parquet: `data/clean/review_sentiment_scores.parquet`
- Embeddings: `vec/airbnb_reviews/reviews_embeddings.npy`
- Metadata: `vec/airbnb_reviews/reviews_metadata.parquet`

Embedding model:

- `sentence-transformers/all-MiniLM-L6-v2`

What an embedding is:

- An embedding is a numeric vector representation of text meaning.
- Similar meanings should be near each other in vector space.
- Example: "dirty apartment", "unclean room", and "cleanliness issue" should be close even if the exact words differ.

What a vector database is:

- A vector database stores embeddings and searches for nearest vectors.
- Qdrant also stores metadata payloads, so retrieval can combine semantic search with structured filters.

Chunking strategy:

- Current strategy is review-level chunking.
- One review comment equals one retrieval chunk.
- No sentence-window chunking yet.

Metadata stored with review vectors:

- listing ID
- comment ID
- comments
- year/month
- borough/neighborhood
- sentiment label and scores
- Highbury flag

Runtime retrieval flow:

1. `exec_rag` loads Qdrant, metadata, and SentenceTransformer.
2. User query is embedded with `_encode_query`.
3. `_build_filter` creates Qdrant metadata filters.
4. Qdrant searches nearest vectors.
5. Filters may be relaxed if retrieval is too narrow.
6. `_rerank_hits` reranks candidate hits.
7. `summarize_hits` dedupes hits, creates citations, and marks confidence/weak evidence.

Why RAG:

- Review text is unstructured. SQL alone cannot answer "what are guests complaining about?"
- RAG lets the answer cite actual guest feedback instead of relying on model memory.

## 11. Ranking and Reranking

File:

- `agent/vector_qdrant.py`, especially `_rerank_hits`

Signals used:

- base vector similarity
- lexical overlap with query terms
- sentiment alignment
- borough alignment
- light recency weighting

Why:

- Raw semantic similarity can retrieve reviews that are related but not operationally best.
- Reranking improves business relevance by pushing location/sentiment/topic-aligned snippets higher.

Current limitation:

- This is a lightweight heuristic reranker, not a neural cross-encoder.

Best improvements:

- Add cross-encoder reranking.
- Add sentence-window chunking.
- Add retrieval metrics like precision@k and hit rate.
- Show raw hits vs reranked hits in the UI.

## 12. Hallucination Handling

The system reduces hallucination through architecture, not just prompting.

### Guard 1: Tool routing

- Metrics go to DuckDB.
- Review evidence goes to Qdrant.
- Hybrid answers combine both.

This avoids asking the LLM to answer from memory.

### Guard 2: SQL verification

- `agent/nl2sql_llm.py`
- `verify_sql` uses DuckDB `EXPLAIN`.
- Repair loop handles common SQL failures.

### Guard 3: Retrieval evidence checks

- `agent/vector_qdrant.py`
- `summarize_hits` marks weak evidence when hit count is low.

### Guard 4: Confidence and abstention

- `backend/ai_observability.py`
- `build_confidence_payload` computes SQL confidence, retrieval confidence, grounding coverage, degraded reasons, and `abstain_recommended`.
- `backend/main.py` can replace overconfident output with a safer insufficient-evidence response.

### Guard 5: Composer constraints

- `agent/compose.py`
- The prompt instructs the model not to invent columns, metrics, or filters and to use provided SQL/RAG context.

Missing/weak:

- No full sentence-level claim-to-citation checker.
- No contradiction detector between SQL and RAG.
- No human approval loop for high-stakes decisions.

Strong answer:

> I treat hallucination as a systems problem. The system reduces it by routing to tools, verifying SQL, retrieving evidence, scoring confidence, and recommending abstention when grounding is weak.

## 13. Evaluation and Accuracy Testing

Files:

- `evals/runner.py`
- `evals/interview_summary.py`
- `scripts/run_benchmarks.py`
- `evals/benchmarks.local.json`
- `evals/benchmarks.holdout.json`
- `evals/benchmarks.adversarial.json`
- `evals/error_taxonomy.md`
- `evals/review_sheet.template.csv`

Benchmark packs:

| Pack | Purpose |
|---|---|
| local | Tuned regression pack for core supported behavior |
| holdout | Paraphrased/generalization checks |
| adversarial | Contradictory, vague, unsupported, or noisy prompts |
| blind sample | Template for a future untouched eval |

What each case can check:

- expected intent
- expected policy
- expected scope
- expected filters subset
- required SQL
- SQL fragments
- min/max rows
- min RAG snippets
- answer contains expected text
- require abstention

Metrics:

- case pass rate
- assertion pass rate
- SQL pass rate
- RAG pass rate
- hybrid pass rate
- category/policy/intent breakdown
- latency average, P50, P95, max
- slowest cases
- token/cost rollups when usage is available

Readiness checks:

- `evals/runner.py` checks Qdrant readiness before retrieval-backed benchmark packs.
- This prevents misleading `0% RAG` results when Qdrant is offline.

Run commands:

```powershell
cd C:\Users\bhuwa\wtchtwr
.\.venv\Scripts\python scripts\run_benchmarks.py --benchmark-file evals\benchmarks.local.json
.\.venv\Scripts\python scripts\run_benchmarks.py --benchmark-file evals\benchmarks.holdout.json
.\.venv\Scripts\python scripts\run_benchmarks.py --benchmark-file evals\benchmarks.adversarial.json
```

What to say:

> I measured both case-level and assertion-level accuracy. Case-level says whether the full benchmark passed. Assertion-level shows partial correctness across routing, filters, SQL, RAG snippets, abstention, and output expectations.

What not to overclaim:

- Do not say "the model is universally 100% accurate."
- Say "the benchmark packs currently pass strongly, and accuracy is tracked by pack and category."

## 14. What Happens When You Move to Another Page

### Chat page

- Route renders `ChatPage`.
- Loads conversations through `useChatStore`.
- Sends messages to FastAPI.
- Renders answer, tables, confidence, trace, export/email actions.

Files:

- `frontend/src/pages/Chat.tsx`
- `frontend/src/store/useChat.ts`
- `frontend/src/components/Message.tsx`

### Dashboard page

- Route renders `Dashboard`.
- Fetches filter options and dashboard view data.
- Uses charts/maps to visualize portfolio/market slices.

Files:

- `frontend/src/pages/Dashboard.tsx`
- `backend/dashboard_router.py`
- `backend/dashboard.py`

### Data export page

- Route renders `DataExportPage`.
- Fetches schema.
- Lets user build a query through UI controls.
- Runs preview.
- Downloads CSV or emails export.

Files:

- `frontend/src/pages/DataExport.tsx`
- `backend/data_explorer.py`
- `backend/exporter.py`
- `backend/emailer.py`

### History page

- Shows saved conversations.
- Lets user reopen previous context.

Files:

- `frontend/src/pages/History.tsx`
- conversation endpoints in `backend/main.py`

### AI metrics page

- Fetches `/api/ai/metrics`.
- Shows benchmark pack rankings, latency, failed cases, and per-case outputs.

Files:

- `frontend/src/pages/AiMetrics.tsx`
- `backend/ai_observability.py`

## 15. Limitations to Be Honest About

Say these confidently. Interviewers like honest engineering judgment.

- This is not fully productionized. It is production-inspired and demo/interview ready.
- Qdrant must be running for RAG/hybrid reliability.
- Slack/email depend on external credentials and running services.
- Review chunking is review-level, not sentence/window-level.
- Reranking is heuristic, not cross-encoder based.
- SQL validation catches syntax/planning errors, not all semantic errors.
- Sentiment scoring is consumed from prepared data; the full scoring ETL is not deeply documented in the current repo.
- LangGraph `MemorySaver` is process-local, not a distributed memory/checkpoint store.
- Expansion scout depends on live external sources and is less deterministic than SQL/RAG.
- Some token usage metrics are currently zero in reports because usage collection is not fully wired for all paths.

## 16. How to Improve the Tool

Highest-impact improvements:

1. Add sentence-level claim grounding.
   - Map every final answer claim to SQL rows or review citations.

2. Add cross-encoder reranking.
   - Improve retrieval quality beyond heuristic reranking.

3. Add sentence-window chunking.
   - Split long reviews into smaller evidence spans.

4. Add golden SQL tests.
   - Compare generated SQL to expected templates for critical business questions.

5. Add contradiction detection.
   - If SQL says one thing and reviews imply another, surface the disagreement.

6. Add production memory/checkpointing.
   - Replace process-local memory with Redis/Postgres/Cosmos.

7. Add cost observability.
   - Capture token usage reliably across all LLM calls.

8. Add CI benchmark gates.
   - Run key tests and benchmark subsets on every push.

9. Make sentiment ETL repeatable.
   - Move VADER/NLTK scoring into a documented pipeline.

10. Add an Azure deployment path.
   - Azure OpenAI, Azure AI Search, Container Apps, Blob/ADLS, Key Vault, Application Insights.

## 17. Likely Interview Questions and Strong Answers

### Why is this agentic?

> Because it maintains structured state, classifies intent, resolves entities, plans a tool route, conditionally invokes SQL/RAG/hybrid/triage/expansion tools, fuses outputs, computes confidence, and persists conversation history. It is not a single prompt-response call.

### Why not just use one LLM prompt?

> One prompt would be simpler but less reliable. This project separates concerns: deterministic SQL for metrics, Qdrant retrieval for evidence, and LLM synthesis for explanation. That makes the system easier to debug, evaluate, and constrain.

### How do you handle hallucinations?

> I reduce hallucination by forcing answers through grounded tools. SQL is verified with DuckDB `EXPLAIN`, RAG evidence is retrieved from Qdrant and reranked, weak evidence lowers confidence, and the backend can recommend abstention.

### How did you measure accuracy?

> I used benchmark packs with structured assertions. Each case can check intent, policy, scope, filters, SQL presence, row counts, RAG snippets, answer text, and abstention. I track both whole-case pass rate and assertion-level accuracy.

### What is RAG doing here?

> RAG retrieves relevant review snippets from Qdrant before generation. The user query is embedded with MiniLM, Qdrant finds semantically similar reviews, metadata filters narrow the hits, reranking improves relevance, and the composer uses those snippets as evidence.

### What is Text-to-SQL doing here?

> Text-to-SQL converts natural-language KPI questions into DuckDB SQL using a schema-aware prompt. The SQL is cleaned, verified, repaired if needed, executed, and then summarized.

### How does memory work?

> Conversation history is persisted in DuckDB tables. The frontend also stores a thread ID in localStorage. LangGraph has process-local checkpoint memory for graph state. For production, I would move graph memory to a durable distributed store.

### What would you improve first?

> I would add sentence-level grounding, cross-encoder reranking, golden SQL tests, and production-grade memory/checkpointing. Those improve trustworthiness more than simply swapping models.

## 18. 60-Second Architecture Answer

> wtchtwr is an AI-powered short-term-rental analytics copilot. A user asks a question in the React frontend, which sends it to a FastAPI backend. The backend persists the message, prepares history, and invokes a LangGraph agent. The graph runs ingress, guardrails, intent classification, entity resolution, and planning. Based on the plan, it routes to DuckDB-backed Text-to-SQL, Qdrant-backed RAG, a hybrid SQL+RAG path, portfolio triage, or expansion scouting. SQL is verified and repaired before execution. RAG retrieves review evidence using MiniLM embeddings, metadata filters, and reranking. The result bundle is passed to a composer model, then the backend attaches confidence, grounding, trace, tables, and citations before returning the answer to the UI.

## 19. 2-Minute Deep Answer

> The project is designed as a constrained agentic analytics system. The frontend is React and TypeScript, and it sends chat, dashboard, export, and metrics requests to a FastAPI backend. The core chat endpoint persists the user message into DuckDB-backed conversation storage, trims recent history, and invokes a LangGraph workflow.
>
> The graph explicitly models the reasoning flow. It starts with ingress and guardrails, then classifies intent and extracts entities such as borough, month, year, listing ID, sentiment, and Highbury scope. The policy planner decides whether the query should be handled by SQL, RAG, hybrid, portfolio triage, expansion scout, or normal conversation.
>
> For structured KPI questions, the SQL path builds a schema-aware prompt, generates DuckDB SQL, validates it with `EXPLAIN`, repairs common failures, executes it, and returns normalized rows and tables. For review questions, the RAG path embeds the query using MiniLM, searches Qdrant over review embeddings, applies metadata filters, reranks hits using vector score plus lexical, sentiment, geography, and recency signals, then summarizes and cites the evidence. For hybrid questions, SQL and RAG results are fused so the final answer can include both numbers and review themes.
>
> The composer generates the final response from the result bundle rather than from memory alone. After that, the backend computes confidence, grounding coverage, weak-evidence signals, abstention recommendation, and trace metadata. The frontend renders the answer, tables, citations, confidence, and AI trace. Accuracy is evaluated through local, holdout, and adversarial benchmark packs with both case-level and assertion-level scoring.

## 20. What to Prioritize Tonight

Read in this order:

1. One-minute project pitch.
2. Resume bullets explained.
3. End-to-end query flow.
4. Orchestrator, intent classifier, planner.
5. NL-to-SQL.
6. RAG and vector search.
7. Hallucination handling.
8. Evaluation and accuracy.
9. Likely interview questions.

If you only remember one sentence:

> This is a grounded agentic analytics system: route first, use deterministic tools, verify intermediate outputs, retrieve evidence, compose from context, score confidence, and measure accuracy with benchmark packs.
