# Evaluation And Accuracy Testing

This is one of the strongest parts of the repo and one of the easiest places to overclaim. The right interview posture is: the eval design is thoughtful and practical, but it is still a curated benchmark harness, not perfect proof of general intelligence.

Repo anchors:

- benchmark runner: [`evals/runner.py`](../../evals/runner.py)
- interview rollups: [`evals/interview_summary.py`](../../evals/interview_summary.py)
- eval docs: [`evals/README.md`](../../evals/README.md)
- benchmark dashboard surface: [`backend/ai_observability.py`](../../backend/ai_observability.py), [`frontend/src/pages/AiMetrics.tsx`](../../frontend/src/pages/AiMetrics.tsx)

## What Benchmark Packs Exist

| Pack | File | Purpose |
| --- | --- | --- |
| Tuned regression | [`evals/benchmarks.local.json`](../../evals/benchmarks.local.json) | Core supported product flows that the system is expected to pass reliably |
| Holdout | [`evals/benchmarks.holdout.json`](../../evals/benchmarks.holdout.json) | Paraphrases / untuned prompts to test generalization |
| Adversarial | [`evals/benchmarks.adversarial.json`](../../evals/benchmarks.adversarial.json) | Contradictory prompts, vague wording, weak-evidence situations |
| Blind starter | [`evals/benchmarks.blind.sample.json`](../../evals/benchmarks.blind.sample.json) | Template for a future untouched blind pack |

Important honesty note:

- the repo has a **blind starter**, not a mature full blind benchmark program

## How Cases Are Structured

The runner loads benchmarks with [`evals/runner.py::load_benchmarks`](../../evals/runner.py).

Cases are JSON objects with fields like:

- `id`
- `query`
- `tenant`
- `composer_enabled`
- `category`
- `expected`
- `manual_checks`
- `notes`

The `expected` block can assert:

- `intent`
- `policy`
- `scope`
- `filters_subset`
- `sql_contains`
- `answer_contains`
- `require_sql`
- `min_rows`
- `max_rows`
- `min_rag_snippets`
- `field_equals`
- `require_abstain`

Why this matters:

- the repo does not only grade final prose
- it checks internal pipeline behavior too

## How The Runner Works

The core execution path is [`evals/runner.py::evaluate_case`](../../evals/runner.py).

For each case it:

1. calls [`agent/graph.py::run`](../../agent/graph.py) directly
2. captures the result
3. computes assertion results
4. stores a compact case record

The compact result includes:

- intent
- scope
- policy
- filters
- SQL text
- answer text
- row count
- RAG count
- latency
- abstained flag
- manual checks
- notes
- assertion details

## Important Eval Design Choice: Graph-Level, Not Full Backend-Level

Benchmarks call the agent graph directly, not the full FastAPI conversation endpoint.

Implication:

- evaluation is focused on the reasoning/tool pipeline
- but it does not fully exercise every backend persistence/rendering behavior

That is a strength for speed and determinism, but it is also a limitation worth acknowledging.

## Case-Level Vs Assertion-Level Accuracy

The repo tracks both.

### Case-level accuracy

- whole benchmark case passes or fails

### Assertion-level accuracy

- each expectation inside the case is scored separately

This is implemented in [`evals/runner.py`](../../evals/runner.py) through `AssertionResult`, `CaseResult`, and `_build_summary(...)`.

Why this is smart:

- AI systems often partially succeed
- assertion-level accuracy shows where the failure actually is

Example:

- intent correct
- filters correct
- SQL present
- but answer wording misses one expected phrase

That should not be flattened into “the system is useless.”

## How SQL Accuracy Is Evaluated

SQL-oriented evaluation can use:

- `require_sql`
- `sql_contains`
- `min_rows`
- `max_rows`
- `field_equals`

The runner also uses helper logic like:

- `_has_sql_signal(...)`
- `_row_count(...)`

This makes SQL evaluation more about grounded execution than final prose alone.

## How RAG Accuracy Is Evaluated

RAG-oriented evaluation can use:

- `min_rag_snippets`
- `answer_contains`
- filter assertions
- `require_abstain` for weak-evidence cases

The runner counts retrieval support through helpers like:

- `_rag_count(...)`

This is not a full IR metric suite like precision@k, but it is enough to evaluate the end-to-end product behavior.

## How Hybrid Accuracy Is Evaluated

Hybrid cases are not graded as a special LLM abstraction; they are evaluated through the same compact case structure, but expected behavior usually includes evidence from both sides:

- SQL present or row count > 0
- enough RAG snippets
- correct policy / intent
- answer content checks

Pipeline rollups in [`evals/interview_summary.py`](../../evals/interview_summary.py) explicitly compute:

- overall pass rate
- SQL pass rate
- RAG pass rate
- hybrid pass rate

## How Routing / Policy / Filter Accuracy Is Evaluated

This is one of the better parts of the harness.

Cases can assert:

- exact intent
- exact policy
- exact scope
- `filters_subset`

This lets the repo catch failures that happen *before* answer generation.

Why that matters:

- many agent failures are routing errors, not language-generation errors

## Latency Tracking

Latency is tracked per case through helpers such as:

- `_latency_value(...)`

and summarized into:

- average latency
- p50 latency
- p95 latency
- max latency

The runner also highlights slowest cases in the interview summary payload.

## Cost / Token Tracking

[`evals/interview_summary.py::_token_metrics`](../../evals/interview_summary.py) extracts token usage from telemetry and can estimate cost if:

- `WTCHTWR_COST_INPUT_PER_1K`
- `WTCHTWR_COST_OUTPUT_PER_1K`

are configured

Important honesty note:

- if usage is not exposed by the model path, token counts can remain zero in reports
- you should not overclaim cost tracking if the current run did not record usage

## Readiness Checks Before Benchmarks

This is a strong practical feature.

[`evals/runner.py::validate_benchmark_readiness`](../../evals/runner.py) and `ensure_benchmark_readiness(...)` make sure that retrieval-backed categories do not run when Qdrant is unavailable.

Currently enforced for categories like:

- `rag`
- `hybrid`
- `triage`

Why this matters:

- without this, a dead Qdrant instance would look like a model-quality collapse rather than an infra issue

## Human Review Layer

The repo also includes a manual review artifact:

- [`evals/review_sheet.template.csv`](../../evals/review_sheet.template.csv)

It supports human judgment over dimensions such as:

- correctness
- completeness
- groundedness
- usefulness

This matters because some output quality dimensions are not easy to reduce to assertions.

## Error Taxonomy

The repo includes:

- [`evals/error_taxonomy.md`](../../evals/error_taxonomy.md)

That provides labels like:

- routing error
- filter extraction error
- SQL generation error
- retrieval miss
- synthesis / hallucination

Why it matters:

- failure analysis is more useful when categorized

## Output Formats

The benchmark system writes:

- timestamped raw benchmark JSON
- timestamped Markdown summaries
- interview summary JSON/Markdown
- pack-specific latest summaries

Repo evidence:

- [`evals/README.md`](../../evals/README.md)
- [`scripts/run_benchmarks.py`](../../scripts/run_benchmarks.py)

## How The Results Are Visualized

Results are surfaced through:

- [`backend/ai_observability.py::load_ai_metrics_payload`](../../backend/ai_observability.py)
- [`frontend/src/pages/AiMetrics.tsx`](../../frontend/src/pages/AiMetrics.tsx)

The AI Metrics page now shows:

- pack ranking
- selected pack metrics
- trend history
- failed cases
- slowest cases
- per-case details
- assertion details

So you do not have to read raw report files during a demo.

## Why The Chosen Benchmarks Make Sense

The pack design matches the product architecture:

- tuned regression for stable supported flows
- holdout for generalization
- adversarial for weak-evidence and noisy prompts

That is appropriate because the repo is evaluating a routed multi-tool system, not just a text generator.

## How The Benchmarks Were Likely Created

Based on the case structure and categories, the packs were likely assembled from:

- core product demo questions
- SQL compare questions
- review theme questions
- hybrid comparison questions
- triage prompts
- expansion prompts

This is a sensible starting point, but still curated.

## What A Critical Interviewer Might Challenge

### Challenge 1: “Are you overfitting to your benchmark wording?”

Strong answer:

- tuned pack is separate from holdout and adversarial packs
- the repo also includes a blind-pack starter precisely because overfitting risk is real

### Challenge 2: “Why should I trust 100% on a pack?”

Strong answer:

- 100% only means 100% on the current curated pack
- it is not a universal guarantee
- holdout/adversarial numbers matter more for generalization

### Challenge 3: “Why not retrieval precision@k?”

Strong answer:

- current evals are end-to-end product evals first
- IR-style metrics would be a meaningful next addition

## Where The Eval Design Is Strong

- evaluates routing/policy/filter behavior, not only output wording
- tracks case-level and assertion-level metrics
- includes holdout and adversarial packs
- includes readiness checks
- pushes results into product UI

## Where It Could Be Gamed Or Overfit

- tuned pack can be optimized against directly
- blind pack is only a sample starter
- graph-only benchmarking can miss some backend/persistence regressions
- assertion sets may not capture nuanced answer quality

## What I Would Improve Next

1. maintain a real untouched blind set
2. add IR metrics for retrieval quality
3. add sentence-level grounding review
4. add CI-based benchmark gating
5. store longer benchmark trend history

