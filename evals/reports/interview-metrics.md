# wtchtwr Interview Metrics

- Benchmark file: `evals\benchmarks.local.json`
- Generated at: `2026-03-19T06:16:15.610206+00:00`

## Headline Metrics

- Case pass rate: `59.09%` (13/22)
- Assertion pass rate: `82.05%` (64/78)

## Performance Metrics

- Average latency: `25.5277s`
- P50 latency: `2.375s`
- P95 latency: `73.819s`
- Max latency: `385.44s`

## Pipeline Breakdown

- Overall pass rate: `59.09%` (13/22)
- SQL pass rate: `75.0%` (6/8)
- RAG pass rate: `80.0%` (4/5)
- Hybrid pass rate: `0.0%` (0/2)

## Strongest Categories

- `conversation`: `100.0%` (2/2)
- `rag`: `80.0%` (4/5)
- `sql`: `75.0%` (6/8)

## Weakest Categories

- `expansion`: `0.0%` (0/2)
- `hybrid`: `0.0%` (0/2)
- `triage`: `33.33%` (1/3)

## Slowest Cases

- `expansion-brooklyn-neighborhoods` (expansion, None): `385.44s`
- `expansion-where-next` (expansion, None): `76.11s`
- `triage-custom-kpi-revenue` (triage, PORTFOLIO_TRIAGE): `30.29s`
- `triage-brooklyn` (triage, PORTFOLIO_TRIAGE): `19.31s`
- `triage-manhattan` (triage, PORTFOLIO_TRIAGE): `16.91s`

## Interview Talking Points

- Overall benchmark pass rate is 59.09% across 22 curated product questions.
- Assertion-level accuracy is 82.05%, which gives a more granular view than whole-case pass/fail.
- Median latency is 2.375s, while p95 latency is 73.819s, so long-tail cases are visible and measurable.
- SQL flows are the most stable at 75.0% pass rate, while weaker categories identify where the roadmap still is.
