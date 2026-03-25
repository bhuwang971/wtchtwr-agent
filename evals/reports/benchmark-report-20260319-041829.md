# wtchtwr Benchmark Report

- Benchmark file: `evals\benchmarks.local.json`
- Generated at: `2026-03-19T08:18:29.248814+00:00`
- Model label: `default`
- Main model: `env/default`
- Main fallback: `env/default`
- NL2SQL model: `env/default`
- NL2SQL fallback: `env/default`
- Cases: `2`
- Passed: `1`
- Failed: `1`
- Pass rate: `50.0%`

## Summary Metrics

- Assertion accuracy: `88.89%` (8/9)
- Average latency: `7.555s`
- P50 latency: `7.555s`
- P95 latency: `8.8375s`
- Max latency: `8.98s`
- SQL cases passing: `0/0`
- RAG cases passing: `0/0`
- Hybrid cases passing: `1/2`

### Accuracy By Category

- `hybrid`: `50.0%` (1/2)

### Accuracy By Policy

- `SQL_RAG_FUSED`: `50.0%` (1/2)

### Accuracy By Intent

- `SENTIMENT_REVIEWS`: `50.0%` (1/2)

## hybrid-midtown-price-and-reviews [PASS]

- Query: `Compare our prices to the market in Midtown and summarize guest complaints`
- Category: `hybrid`
- Tags: `compare, pricing, reviews, midtown`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `SQL_RAG_FUSED`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `4`
- Latency: `8.98`
- Manual checks:
  - Confirm both SQL comparison and review evidence are present.
- Assertions:
  - [PASS] `policy`
    expected: `SQL_RAG_FUSED`
    actual: `SQL_RAG_FUSED`
  - [PASS] `scope`
    expected: `Hybrid`
    actual: `Hybrid`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `4`

## hybrid-brooklyn-revenue-and-reviews [FAIL]

- Query: `Compare our revenue to the market in Brooklyn and what guests complain about`
- Category: `hybrid`
- Tags: `compare, revenue, reviews, brooklyn`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `SQL_RAG_FUSED`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `0`
- Latency: `6.13`
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
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': 'negative'}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [FAIL] `min_rag_snippets`
    expected: `1`
    actual: `0`
