# wtchtwr Benchmark Report

- Benchmark file: `evals\benchmarks.local.json`
- Generated at: `2026-03-19T08:18:58.066413+00:00`
- Model label: `default`
- Main model: `env/default`
- Main fallback: `env/default`
- NL2SQL model: `env/default`
- NL2SQL fallback: `env/default`
- Cases: `1`
- Passed: `0`
- Failed: `1`
- Pass rate: `0.0%`

## Summary Metrics

- Assertion accuracy: `80.0%` (4/5)
- Average latency: `4.4s`
- P50 latency: `4.4s`
- P95 latency: `4.4s`
- Max latency: `4.4s`
- SQL cases passing: `0/0`
- RAG cases passing: `0/0`
- Hybrid cases passing: `0/1`

### Accuracy By Category

- `hybrid`: `0.0%` (0/1)

### Accuracy By Policy

- `SQL_RAG_FUSED`: `0.0%` (0/1)

### Accuracy By Intent

- `SENTIMENT_REVIEWS`: `0.0%` (0/1)

## hybrid-brooklyn-revenue-and-reviews [FAIL]

- Query: `Compare our revenue to the market in Brooklyn and what guests complain about`
- Category: `hybrid`
- Tags: `compare, revenue, reviews, brooklyn`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `SQL_RAG_FUSED`
- Scope: `Hybrid`
- Row count: `0`
- RAG count: `10`
- Latency: `4.4`
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
  - [FAIL] `require_sql`
    expected: `True`
    actual: `False`
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`
