# wtchtwr Benchmark Report

- Benchmark file: `evals\benchmarks.local.json`
- Generated at: `2026-03-19T08:21:20.734269+00:00`
- Model label: `default`
- Main model: `env/default`
- Main fallback: `env/default`
- NL2SQL model: `env/default`
- NL2SQL fallback: `env/default`
- Cases: `1`
- Passed: `1`
- Failed: `0`
- Pass rate: `100.0%`

## Summary Metrics

- Assertion accuracy: `100.0%` (5/5)
- Average latency: `10.24s`
- P50 latency: `10.24s`
- P95 latency: `10.24s`
- Max latency: `10.24s`
- SQL cases passing: `0/0`
- RAG cases passing: `0/0`
- Hybrid cases passing: `1/1`

### Accuracy By Category

- `hybrid`: `100.0%` (1/1)

### Accuracy By Policy

- `SQL_RAG_FUSED`: `100.0%` (1/1)

### Accuracy By Intent

- `SENTIMENT_REVIEWS`: `100.0%` (1/1)

## hybrid-brooklyn-revenue-and-reviews [PASS]

- Query: `Compare our revenue to the market in Brooklyn and what guests complain about`
- Category: `hybrid`
- Tags: `compare, revenue, reviews, brooklyn`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `SQL_RAG_FUSED`
- Scope: `Hybrid`
- Row count: `0`
- RAG count: `10`
- Latency: `10.24`
- Manual checks:
  - Confirm revenue is from SQL and complaints are from review evidence.
- Assertions:
  - [PASS] `policy`
    expected: `SQL_RAG_FUSED`
    actual: `SQL_RAG_FUSED`
  - [PASS] `scope`
    expected: `Hybrid`
    actual: `Hybrid`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Brooklyn']}`
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': 'negative'}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`
