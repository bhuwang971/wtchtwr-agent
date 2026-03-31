# Quick Revision Sheet

This is the pre-interview cram sheet.

## 1. 60-Second Architecture Version

`wtchtwr` is a constrained agentic analytics system for short-term rental operators. The frontend is a React + TypeScript app with chat, dashboard, data export, history, and AI metrics pages. The backend is FastAPI. When a user asks a question, the backend persists the message and sends it into a LangGraph orchestrator. The graph classifies intent, extracts filters, chooses whether the question should go to DuckDB-backed NL-to-SQL, Qdrant-backed review retrieval, hybrid SQL+RAG fusion, portfolio triage, or expansion scouting. SQL is validated and repaired before execution, retrieval is metadata-filtered and reranked, and both are normalized into a common result bundle. A composer then generates the grounded final answer, and the backend attaches confidence and AI trace data before persisting and returning the assistant message. The repo also includes benchmark packs for tuned, holdout, and adversarial evaluation so the system is measurable, not just demoable.

## 2. 2-Minute Architecture Version

The user interacts through a React/Vite frontend. The main chat page streams requests to a FastAPI backend endpoint at `/api/conversations/{id}/messages`. The backend stores the user message in DuckDB-backed conversation tables, loads recent history, and invokes a LangGraph workflow with structured state. The graph runs ingress, guardrails, intent classification, entity resolution, and planning. Based on the resulting plan, it routes into one of several execution branches: NL-to-SQL for structured metrics, Qdrant-based RAG for review evidence, a hybrid branch that runs SQL and retrieval in parallel, a portfolio triage workflow, or an expansion scout workflow that uses external web signals. The SQL path in `agent/nl2sql_llm.py` is schema-aware and uses DuckDB `EXPLAIN` plus repair loops before execution. The RAG path in `agent/vector_qdrant.py` embeds the query, applies metadata filters, retrieves review vectors from Qdrant, reranks them using semantic and lexical signals, and summarizes the evidence. All branches feed a normalized `result_bundle`, which is passed to the composer. The backend then computes confidence, grounding coverage, degraded reasons, and trace payloads, stores the assistant message, and returns the updated conversation. On top of that, the repo includes a benchmark harness with tuned, holdout, and adversarial packs plus an in-app AI metrics page so the system can be defended on routing, SQL, RAG, hybrid accuracy, latency, and failure cases.

## 3. Fast One-Liners For Major Subsystems

| Subsystem | One-liner |
| --- | --- |
| Frontend | React/Vite SPA that renders chat, dashboard, data export, history, and benchmark diagnostics |
| Backend | FastAPI shell that persists conversations and bridges requests into the graph |
| Orchestrator | LangGraph workflow that routes questions into the right tool path |
| NL-to-SQL | Schema-aware SQL generation with validation and repair before DuckDB execution |
| RAG | Qdrant review retrieval with metadata filters and reranking |
| Hybrid | Parallel SQL + RAG execution fused into one grounded answer |
| Triage | Portfolio ranking and action-backlog workflow |
| Expansion | Web-grounded scouting workflow using external signals |
| Evaluation | Benchmark harness with tuned, holdout, and adversarial packs |

## 4. Most Important File List

If you freeze in the interview, remember these:

- [`agent/graph.py`](../../agent/graph.py)
- [`backend/main.py`](../../backend/main.py)
- [`agent/nl2sql_llm.py`](../../agent/nl2sql_llm.py)
- [`agent/vector_qdrant.py`](../../agent/vector_qdrant.py)
- [`evals/runner.py`](../../evals/runner.py)
- [`frontend/src/pages/Chat.tsx`](../../frontend/src/pages/Chat.tsx)
- [`frontend/src/components/Message.tsx`](../../frontend/src/components/Message.tsx)

## 5. Strongest Things To Say

- “The system is not a single LLM prompt; it uses explicit routing and structured tool paths.”
- “SQL is validated and repaired before execution.”
- “RAG retrieval is not raw vector search only; it uses metadata filters and reranking.”
- “I evaluate routing and grounding behavior, not just final answer wording.”
- “Confidence and AI trace are surfaced to the user.”

## 6. Honest Caveats To Say

- “The benchmark packs are curated, so I would not treat 100% there as universal correctness.”
- “Hybrid composition works well but is also one of the messier parts of the codebase.”
- “Expansion is the least deterministic feature because it depends on external web sources.”
- “The repo is production-inspired, not a fully productionized cloud deployment.”

## 7. Most Likely Grilling Themes

Be ready on:

- why it is agentic
- how routing works
- how SQL hallucination is reduced
- how RAG retrieval works
- how reranking works
- how confidence and abstention work
- how benchmarks are structured
- why 100% on a pack is not the whole story

## 8. Best “What I’d Improve Next” Answer

If pressed for improvements:

1. add a stronger cross-encoder reranker  
2. add sentence-level grounding / contradiction checks  
3. add a real untouched blind evaluation set  
4. refactor hybrid compose/fusion logic  
5. replace process-local memory with shared durable memory if scaling out

## 9. What Not To Overclaim

Do not say:

- “It is production ready.”
- “The model always gives correct answers.”
- “Confidence is statistically calibrated.”
- “Expansion recommendations are deterministic.”

## 10. Best Closing Positioning

The strongest positioning is:

“I built a constrained, observable, benchmarked multi-tool AI system. I can explain exactly how each path works, what it is grounded on, how it fails, and how I would improve it.”

