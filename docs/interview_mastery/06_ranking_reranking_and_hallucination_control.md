# Ranking, Reranking, And Hallucination Control

This section ties together three things interviewers often separate:

1. initial retrieval quality
2. reranking quality
3. hallucination control after retrieval / SQL execution

Repo anchors:

- retrieval and reranking: [`agent/vector_qdrant.py`](../../agent/vector_qdrant.py)
- SQL verification/repair: [`agent/nl2sql_llm.py`](../../agent/nl2sql_llm.py)
- confidence and abstention: [`backend/ai_observability.py`](../../backend/ai_observability.py)
- backend abstention rewrite: [`backend/main.py::build_assistant_payload`](../../backend/main.py)
- composer constraints: [`agent/compose.py`](../../agent/compose.py)

## Ranking In This Repo

“Ranking” here mainly means how retrieved review snippets are ordered after Qdrant search so the best evidence reaches the composer and the user.

## Stage 1: Initial Retrieval Ranking

Initial retrieval is driven by Qdrant nearest-neighbor search in [`agent/vector_qdrant.py::exec_rag`](../../agent/vector_qdrant.py).

The query is:

- embedded with the local SentenceTransformer model
- searched against stored review embeddings

This gives a first-pass ranked list based primarily on vector similarity.

Why this matters:

- vector similarity is fast
- it gets semantically related evidence into the candidate set
- but it is not always the best final ranking for business questions

## Stage 2: Metadata Filtering

Before trusting raw vector ranking, the repo applies metadata filters built by [`agent/vector_qdrant.py::_build_filter`](../../agent/vector_qdrant.py).

Supported filters include:

- borough
- neighbourhood
- month
- year
- listing ID
- sentiment label
- `is_highbury`

Why this matters:

- semantic similarity alone can return the right theme but the wrong slice
- analytics questions usually need semantic + structured alignment

## Stage 3: Post-Retrieval Reranking

The main reranker is [`agent/vector_qdrant.py::_rerank_hits`](../../agent/vector_qdrant.py).

Signals used:

| Signal | What it does |
| --- | --- |
| base vector score | keeps semantic closeness in the ranking |
| lexical overlap | rewards hits that share important query tokens |
| sentiment alignment | boosts positive or negative snippets based on query intent |
| borough alignment | boosts hits from the requested borough |
| recency weighting | gives a small lift to newer years |

The reranker also stores helper fields like:

- `rerank_score`
- `rerank_overlap`
- `retrieval_rank`

Telemetry later exposes:

- `rag_reranker = lexical_semantic_v1`

## Why These Signals Matter

Raw vector similarity can be “close enough” but still operationally weak. Examples:

- right theme, wrong borough
- right topic, wrong sentiment
- broad semantic match instead of the best evidence

So the reranker adds business-aware structure on top of embedding similarity.

## Deduplication

After retrieval/reranking, [`agent/vector_qdrant.py::summarize_hits`](../../agent/vector_qdrant.py) de-duplicates hits on:

- `(listing_id, comment_id)`

Why this matters:

- avoids repetitive evidence
- keeps citation count honest
- reduces redundant snippets in the final answer

## Weak-Evidence Handling

Weak evidence is explicitly tracked in [`agent/vector_qdrant.py::summarize_hits`](../../agent/vector_qdrant.py).

Weak evidence is set when:

- there are no hits
- evidence count is very low
- retrieval summary indicates sparse support

Outputs include:

- `weak_evidence`
- `evidence_count`
- retrieval-level `confidence`

This is important because the repo tries not to treat one weak snippet as strong proof.

## SQL-Side Hallucination Control

Hallucination control is not only about retrieval. The SQL path has its own safeguards in [`agent/nl2sql_llm.py`](../../agent/nl2sql_llm.py):

- schema-grounded prompt
- SQL cleaning
- `EXPLAIN` verification
- rule-based repair
- optional LLM repair

This prevents a major hallucination class:

- invented tables
- invented columns
- invalid SQL syntax

## Architecture-As-Hallucination-Control

One of the strongest anti-hallucination choices in the repo is architectural:

- structured questions route to DuckDB
- review questions route to Qdrant
- hybrid questions combine both
- expansion questions go down a separate workflow

This means the model is usually answering **from tools and evidence**, not from world knowledge or memory.

Repo evidence:

- routing: [`agent/policy.py::plan_steps`](../../agent/policy.py)
- graph branches: [`agent/graph.py::build_graph`](../../agent/graph.py)

## Confidence Scoring

Confidence is computed in [`backend/ai_observability.py::build_confidence_payload`](../../backend/ai_observability.py).

Important fields include:

- overall answer confidence
- SQL confidence
- retrieval confidence
- citation coverage
- degraded reasons
- weak evidence
- abstain recommendation

Examples of how the score is influenced:

- SQL rows returned -> stronger SQL confidence
- more review hits -> stronger retrieval confidence
- retrieval error or no evidence -> lower confidence

## Abstention Logic

The repo does have abstention behavior, though it is heuristic rather than formal proof-based abstention.

Two important layers:

1. [`backend/ai_observability.py::build_confidence_payload`](../../backend/ai_observability.py) decides when `abstain_recommended` should be true
2. [`backend/main.py::build_assistant_payload`](../../backend/main.py) rewrites the summary into a safer abstention-style answer when recommended

The graph also contains a targeted hybrid safeguard in:

- [`agent/graph.py::_should_abstain_for_missing_portfolio_evidence`](../../agent/graph.py)

That specifically protects against hybrid answers on an explicitly requested owned-portfolio slice when structured support is missing and review evidence is weak.

## Composer Constraints

The final composer in [`agent/compose.py`](../../agent/compose.py) uses a strong system prompt to constrain output. It tells the model to:

- avoid inventing metrics, filters, and columns
- use provided SQL/RAG context
- acknowledge empty results
- use operator-friendly grounded language

There is also fallback text generation in [`agent/compose.py::fallback_text`](../../agent/compose.py) when model composition is unavailable.

## What Is Missing

This repo reduces hallucination risk, but it does **not** implement:

- sentence-level claim verification
- formal contradiction detection between SQL and retrieval
- a second-pass answer critic that checks every claim against evidence
- minimum citation density thresholds for every answer sentence

Those are good “what I’d improve next” points for an interview.

## Strong Points To Highlight

- hallucination reduction is architectural, not only prompt-based
- SQL is validated before execution
- retrieval tracks weak evidence
- confidence and abstention are surfaced in both backend payloads and UI
- the system can fail safer when portfolio evidence is missing

## Weak Spots To Admit

- reranker is lightweight, not a neural cross-encoder
- no claim-by-claim grounding checker
- no robust contradiction resolution between SQL and review evidence
- confidence is heuristic, not calibrated

## What A More Advanced Production Version Would Use

| Current design | More advanced option |
| --- | --- |
| lexical-semantic reranker | cross-encoder reranker |
| heuristic confidence | calibrated confidence model |
| bundle-level grounding | sentence-level claim grounding |
| heuristic abstention | evidence-threshold + contradiction-aware abstention |
| review-level chunking | sentence/window chunking |

