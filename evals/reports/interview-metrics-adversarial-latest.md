# wtchtwr Interview Metrics

- Benchmark file: `C:\Users\bhuwa\wtchtwr\evals\benchmarks.adversarial.json`
- Generated at: `2026-03-31T17:31:03.375627+00:00`
- Model label: `default`
- Main model: `env/default`
- Main fallback: `env/default`
- NL2SQL model: `env/default`
- NL2SQL fallback: `env/default`

## Headline Metrics

- Case pass rate: `100.0%` (8/8)
- Assertion pass rate: `100.0%` (21/21)

## Performance Metrics

- Average latency: `13.66s`
- P50 latency: `5.12s`
- P95 latency: `50.311s`
- Max latency: `67.44s`

## Cost Metrics

- Prompt tokens: `0`
- Completion tokens: `0`
- Total tokens: `0`
- Estimated cost: `None`

## Pipeline Breakdown

- Overall pass rate: `100.0%` (8/8)
- SQL pass rate: `100.0%` (2/2)
- RAG pass rate: `100.0%` (2/2)
- Hybrid pass rate: `100.0%` (2/2)

## Strongest Categories

- `sql`: `100.0%` (2/2)
- `rag`: `100.0%` (2/2)
- `hybrid`: `100.0%` (2/2)

## Weakest Categories

- `expansion`: `100.0%` (1/1)
- `triage`: `100.0%` (1/1)
- `hybrid`: `100.0%` (2/2)

## Trend Vs Previous Run

- Case pass rate delta: `12.5 pts`
- Assertion pass rate delta: `4.76 pts`
- P50 latency delta: `-0.425s`
- P95 latency delta: `-21.3465s`

## Slowest Cases

- `adversarial-expansion-constraint-following` (expansion, EXPANSION_SCOUT): `67.44s`
- `adversarial-triage-noisy-prompt` (triage, PORTFOLIO_TRIAGE): `18.5s`
- `adversarial-sql-vague-top-performers` (sql, SQL_HIGHBURY): `7.8s`
- `adversarial-hybrid-contradictory-brooklyn-midtown` (hybrid, SQL_RAG_FUSED): `6.15s`
- `adversarial-hybrid-unsupported-missing-evidence` (hybrid, SQL_RAG_FUSED): `4.09s`

## Interview Talking Points

- Overall benchmark pass rate is 100.0% across 8 curated product questions.
- Assertion-level accuracy is 100.0%, which gives a more granular view than whole-case pass/fail.
- Median latency is 5.12s, while p95 latency is 50.311s, so long-tail cases are visible and measurable.
- SQL flows are the most stable at 100.0% pass rate, while weaker categories identify where the roadmap still is.
- Observed token volume is 0 total tokens across the run; set WTCHTWR_COST_INPUT_PER_1K and WTCHTWR_COST_OUTPUT_PER_1K to turn this into an estimated dollar cost.
