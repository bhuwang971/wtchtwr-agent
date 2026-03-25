# wtchtwr Interview Metrics

- Benchmark file: `evals\benchmarks.adversarial.json`
- Generated at: `2026-03-25T03:38:36.038535+00:00`
- Model label: `default`
- Main model: `env/default`
- Main fallback: `env/default`
- NL2SQL model: `env/default`
- NL2SQL fallback: `env/default`

## Headline Metrics

- Case pass rate: `62.5%` (5/8)
- Assertion pass rate: `85.0%` (17/20)

## Performance Metrics

- Average latency: `13.8475s`
- P50 latency: `4.425s`
- P95 latency: `56.7085s`
- Max latency: `83.69s`

## Pipeline Breakdown

- Overall pass rate: `62.5%` (5/8)
- SQL pass rate: `50.0%` (1/2)
- RAG pass rate: `100.0%` (2/2)
- Hybrid pass rate: `50.0%` (1/2)

## Strongest Categories

- `rag`: `100.0%` (2/2)
- `expansion`: `100.0%` (1/1)
- `sql`: `50.0%` (1/2)

## Weakest Categories

- `triage`: `0.0%` (0/1)
- `hybrid`: `50.0%` (1/2)
- `sql`: `50.0%` (1/2)

## Trend Vs Previous Run

- Case pass rate delta: `0.0 pts`
- Assertion pass rate delta: `0.0 pts`
- P50 latency delta: `-0.12s`
- P95 latency delta: `2.4375s`

## Slowest Cases

- `adversarial-expansion-constraint-following` (expansion, EXPANSION_SCOUT): `83.69s`
- `adversarial-triage-noisy-prompt` (triage, SQL_RAG_FUSED): `6.6s`
- `adversarial-hybrid-contradictory-brooklyn-midtown` (hybrid, RAG_HYBRID): `5.95s`
- `adversarial-sql-vague-top-performers` (sql, SQL_HIGHBURY): `4.98s`
- `adversarial-sql-compare-implicit-market` (sql, SQL_HIGHBURY): `3.87s`

## Interview Talking Points

- Overall benchmark pass rate is 62.5% across 8 curated product questions.
- Assertion-level accuracy is 85.0%, which gives a more granular view than whole-case pass/fail.
- Median latency is 4.425s, while p95 latency is 56.7085s, so long-tail cases are visible and measurable.
- SQL flows are the most stable at 50.0% pass rate, while weaker categories identify where the roadmap still is.
