# wtchtwr Interview Metrics

- Benchmark file: `evals\benchmarks.holdout.json`
- Generated at: `2026-03-25T00:33:18.539368+00:00`
- Model label: `default`
- Main model: `env/default`
- Main fallback: `env/default`
- NL2SQL model: `env/default`
- NL2SQL fallback: `env/default`

## Headline Metrics

- Case pass rate: `100.0%` (13/13)
- Assertion pass rate: `100.0%` (41/41)

## Performance Metrics

- Average latency: `20.2985s`
- P50 latency: `5.82s`
- P95 latency: `79.992s`
- Max latency: `95.1s`

## Pipeline Breakdown

- Overall pass rate: `100.0%` (13/13)
- SQL pass rate: `100.0%` (4/4)
- RAG pass rate: `100.0%` (3/3)
- Hybrid pass rate: `100.0%` (2/2)

## Strongest Categories

- `sql`: `100.0%` (4/4)
- `rag`: `100.0%` (3/3)
- `triage`: `100.0%` (2/2)

## Weakest Categories

- `expansion`: `100.0%` (2/2)
- `hybrid`: `100.0%` (2/2)
- `triage`: `100.0%` (2/2)

## Trend Vs Previous Run

- Case pass rate delta: `38.46 pts`
- Assertion pass rate delta: `21.95 pts`
- P50 latency delta: `3.01s`
- P95 latency delta: `45.902s`

## Slowest Cases

- `holdout-expansion-brooklyn-only` (expansion, EXPANSION_SCOUT): `95.1s`
- `holdout-expansion-nyc-submarkets-next-year` (expansion, EXPANSION_SCOUT): `69.92s`
- `holdout-triage-queens-portfolio-lead` (triage, PORTFOLIO_TRIAGE): `37.38s`
- `holdout-triage-revenue-kpi-low-performers` (triage, PORTFOLIO_TRIAGE): `30.17s`
- `holdout-hybrid-manhattan-occupancy-review-themes` (hybrid, SQL_RAG_FUSED): `8.38s`

## Interview Talking Points

- Overall benchmark pass rate is 100.0% across 13 curated product questions.
- Assertion-level accuracy is 100.0%, which gives a more granular view than whole-case pass/fail.
- Median latency is 5.82s, while p95 latency is 79.992s, so long-tail cases are visible and measurable.
- SQL flows are the most stable at 100.0% pass rate, while weaker categories identify where the roadmap still is.
