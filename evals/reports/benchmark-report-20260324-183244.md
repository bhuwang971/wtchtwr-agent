# wtchtwr Benchmark Report

- Benchmark file: `evals\benchmarks.local.json`
- Generated at: `2026-03-24T22:32:44.678800+00:00`
- Model label: `default`
- Main model: `env/default`
- Main fallback: `env/default`
- NL2SQL model: `env/default`
- NL2SQL fallback: `env/default`
- Cases: `2`
- Passed: `2`
- Failed: `0`
- Pass rate: `100.0%`

## Summary Metrics

- Assertion accuracy: `100.0%` (6/6)
- Average latency: `106.585s`
- P50 latency: `106.585s`
- P95 latency: `163.4965s`
- Max latency: `169.82s`
- SQL cases passing: `0/0`
- RAG cases passing: `0/0`
- Hybrid cases passing: `0/0`

### Accuracy By Category

- `expansion`: `100.0%` (2/2)

### Accuracy By Policy

- `EXPANSION_SCOUT`: `100.0%` (2/2)

### Accuracy By Intent

- `EXPANSION_SCOUT`: `100.0%` (2/2)

## expansion-where-next [PASS]

- Query: `Where should Highbury expand next in NYC?`
- Category: `expansion`
- Tags: `expansion, nyc, highbury`
- Intent: `EXPANSION_SCOUT`
- Policy: `EXPANSION_SCOUT`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `0`
- Latency: `169.82`
- Manual checks:
  - Review the expansion recommendation for source grounding.
  - Check that cited web sources are relevant and recent.
- Assertions:
  - [PASS] `intent`
    expected: `EXPANSION_SCOUT`
    actual: `EXPANSION_SCOUT`
  - [PASS] `policy`
    expected: `EXPANSION_SCOUT`
    actual: `EXPANSION_SCOUT`
  - [PASS] `scope`
    expected: `Highbury`
    actual: `Highbury`
  - [PASS] `require_sql`
    expected: `False`
    actual: `False`

## expansion-brooklyn-neighborhoods [PASS]

- Query: `Which Brooklyn neighborhoods should Highbury consider for expansion?`
- Category: `expansion`
- Tags: `expansion, brooklyn, neighborhoods`
- Intent: `EXPANSION_SCOUT`
- Policy: `EXPANSION_SCOUT`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `0`
- Latency: `43.35`
- Manual checks:
  - Confirm the response discusses Brooklyn neighborhoods rather than generic NYC.
- Assertions:
  - [PASS] `intent`
    expected: `EXPANSION_SCOUT`
    actual: `EXPANSION_SCOUT`
  - [PASS] `policy`
    expected: `EXPANSION_SCOUT`
    actual: `EXPANSION_SCOUT`
