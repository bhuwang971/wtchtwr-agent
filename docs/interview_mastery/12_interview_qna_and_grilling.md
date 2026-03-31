# Interview Q&A And Grilling Guide

This section is written to help you defend the repo under serious follow-up questioning.

## 1. How I’d Explain Each Major Subsystem In Plain English

| Subsystem | Plain-English explanation |
| --- | --- |
| Frontend | A React app that lets users chat with the system, inspect metrics, explore data, and see confidence/trace information |
| Backend API | The FastAPI shell that validates requests, persists conversation history, invokes the agent graph, and returns structured answers |
| Orchestrator | A LangGraph workflow that decides whether the question should go to SQL, review retrieval, hybrid fusion, triage, or expansion |
| NL-to-SQL | A schema-aware SQL generator with verification and repair before DuckDB execution |
| RAG | A review retrieval layer that embeds the query, searches Qdrant, filters results, reranks them, and summarizes the best evidence |
| Triage | A domain-specific workflow that turns portfolio data into ranked operational actions rather than only a metric |
| Expansion scout | A web-grounded workflow that looks for external signals and synthesizes neighborhood recommendations |
| Evaluation | A benchmark harness that scores routing, policy, SQL, retrieval, hybrid behavior, latency, and abstention |

## 2. How I’d Explain Each Major Subsystem Technically

| Subsystem | Technical explanation |
| --- | --- |
| Frontend | React + TypeScript + Vite SPA with Zustand state, typed API client, streaming chat handling, and metrics/case inspection pages |
| Backend API | FastAPI app in [`backend/main.py`](../../backend/main.py) with DuckDB-backed conversation storage and multiple workflow endpoints |
| Orchestrator | `GraphState`-based LangGraph in [`agent/graph.py`](../../agent/graph.py) with conditional edges into SQL, RAG, hybrid, triage, and expansion |
| NL-to-SQL | Prompted DuckDB SQL generation in [`agent/nl2sql_llm.py`](../../agent/nl2sql_llm.py) with `EXPLAIN` validation and repair loops |
| RAG | Query embedding + Qdrant vector search + metadata filter + lightweight reranker in [`agent/vector_qdrant.py`](../../agent/vector_qdrant.py) |
| Triage | SQL-heavy ranking plus market benchmarking plus review context in [`agent/portfolio_triage.py`](../../agent/portfolio_triage.py) |
| Expansion scout | Tavily + article fetch/parsing + LLM synthesis in [`agent/expansion_scout.py`](../../agent/expansion_scout.py) |
| Evaluation | JSON benchmark packs executed through [`evals/runner.py`](../../evals/runner.py) with interview rollups in [`evals/interview_summary.py`](../../evals/interview_summary.py) |

## 3. Likely Grilling Questions And Strong Answers

### Q1. “Why do you call this agentic?”

Strong answer:

Because it is not a single prompt-response call. The repo maintains explicit state, classifies intent, resolves entities, plans a route, invokes tools conditionally, can run SQL and RAG in parallel for hybrid questions, persists memory/history, and surfaces confidence and degraded behavior.

Repo anchors:

- [`agent/graph.py`](../../agent/graph.py)
- [`agent/types.py`](../../agent/types.py)

### Q2. “Why not just use one prompt with some tool instructions?”

Strong answer:

This system has multiple evidence sources and failure modes. Structured metrics, guest reviews, triage workflows, and expansion scouting are different tasks. The graph gives explicit control over routing and makes evaluation much easier.

### Q3. “How do you know your SQL path is reliable?”

Strong answer:

The repo does not just accept model SQL. It grounds the model in an explicit schema, cleans generated SQL, validates it with DuckDB `EXPLAIN`, applies deterministic repair, optionally retries with LLM repair, and only then executes.

Repo anchor:

- [`agent/nl2sql_llm.py`](../../agent/nl2sql_llm.py)

### Q4. “How do you reduce hallucinations?”

Strong answer:

Primarily through architecture, not just prompting:

- structured questions route to DuckDB
- review questions route to Qdrant
- hybrid answers combine both
- generated SQL is verified and repaired
- retrieval tracks weak evidence
- backend computes confidence and abstain recommendations
- final answer prompt is constrained to grounded context

Repo anchors:

- [`agent/nl2sql_llm.py`](../../agent/nl2sql_llm.py)
- [`agent/vector_qdrant.py`](../../agent/vector_qdrant.py)
- [`backend/ai_observability.py`](../../backend/ai_observability.py)

### Q5. “What exactly is your RAG stack?”

Strong answer:

Reviews are embedded with `all-MiniLM-L6-v2`, stored in Qdrant, retrieved by semantic similarity with metadata filters, reranked using vector score + lexical overlap + sentiment + borough + recency, deduplicated, summarized, and then passed to the composer.

Repo anchors:

- [`scripts/rebuild_review_vectors.py`](../../scripts/rebuild_review_vectors.py)
- [`agent/vector_qdrant.py`](../../agent/vector_qdrant.py)

### Q6. “How do you evaluate accuracy?”

Strong answer:

The repo uses tuned, holdout, and adversarial benchmark packs. Each case can assert intent, policy, scope, filter subset, SQL presence, SQL shape, row counts, RAG counts, and abstention. The runner computes both case-level and assertion-level accuracy and also tracks latency and cost/token metrics when available.

Repo anchors:

- [`evals/runner.py`](../../evals/runner.py)
- [`evals/interview_summary.py`](../../evals/interview_summary.py)

### Q7. “Why should I trust your 100% numbers?”

Strong answer:

I would not overclaim them. A 100% number only means 100% on the current curated pack. The repo separates tuned, holdout, and adversarial packs specifically to avoid claiming that one perfect run means universal robustness.

### Q8. “Where is the biggest architectural weakness?”

Strong answer:

The hybrid/compose path in [`agent/graph.py::_compose_node`](../../agent/graph.py) shows visible iterative patching. It works, but it is also the part most likely to need refactoring if this became a longer-term production codebase.

### Q9. “What would you improve first?”

Strong answer:

1. better reranking, ideally cross-encoder based  
2. sentence-level grounding and contradiction checks  
3. stronger blind evaluation  
4. cleaner separation/refactor of hybrid composition logic  
5. more durable/shared memory if deployed multi-instance

### Q10. “Why use DuckDB?”

Strong answer:

Because this repo is a local-first analytics system over Parquet-scale data. DuckDB is very strong for embedded analytics, reproducibility, and laptop demos. If scale/concurrency increased, I would move the structured analytics layer to a managed SQL/Lakehouse option.

## 4. Weak Spots / What I’d Improve

### Code-level weak spots

- `backend/main.py` is very large
- `agent/graph.py::_compose_node` contains defensive patch logic
- `backend/storage.py` looks legacy relative to the active persistence path
- expansion depends on live web fetches and parsing

### Modeling / AI weak spots

- reranker is lightweight
- no sentence-level claim grounding
- no formal contradiction checker between SQL and review evidence
- benchmark blind set is only a starter template

### Infra / ops weak spots

- no full IaC
- thread memory is in-process only
- mostly local/docker runtime story rather than cloud-native deployment

## 5. What Not To Overclaim

Do **not** say:

- “The system is production-ready.”
- “100% on the benchmark means it always gives correct answers.”
- “It has a full blind evaluation program.”
- “It has calibrated confidence.”
- “The Slack bot is a separate intelligent agent.”
- “Expansion is as deterministic as SQL.”

Safer phrasing:

- “production-inspired”
- “100% on the current curated pack”
- “heuristic confidence and abstention”
- “strongest on structured SQL and review-grounded flows”

## 6. If Asked “Why Is This More Than A Chatbot?”

Strong answer:

Because the repo separates orchestration, tools, synthesis, persistence, observability, and evaluation. The model is one component inside a larger system, not the system itself.

## 7. If Asked “How Would You Productionize This?”

Strong answer:

- host the backend in a managed container platform
- move secrets to a vault/managed identity model
- replace process-local memory with shared persistence where needed
- add IR metrics and blind evals
- add claim-level grounding and contradiction checks
- move artifact rebuild/eval scripts into scheduled jobs

## 8. The Best Honest Positioning

The strongest way to present the project is:

- not “I built a perfect agent”
- but “I built a constrained, observable, benchmarked multi-tool AI system and I can explain exactly how it works and where it still needs improvement”

