# wtchtwr Benchmark Report

- Benchmark file: `evals\benchmarks.local.json`
- Generated at: `2026-03-19T08:22:16.923133+00:00`
- Model label: `default`
- Main model: `env/default`
- Main fallback: `env/default`
- NL2SQL model: `env/default`
- NL2SQL fallback: `env/default`
- Cases: `6`
- Passed: `6`
- Failed: `0`
- Pass rate: `100.0%`

## Summary Metrics

- Assertion accuracy: `100.0%` (25/25)
- Average latency: `7.065s`
- P50 latency: `7.175s`
- P95 latency: `11.36s`
- Max latency: `11.93s`
- SQL cases passing: `2/2`
- RAG cases passing: `1/1`
- Hybrid cases passing: `2/2`

### Accuracy By Category

- `hybrid`: `100.0%` (2/2)
- `rag`: `100.0%` (1/1)
- `sql`: `100.0%` (2/2)
- `triage`: `100.0%` (1/1)

### Accuracy By Policy

- `PORTFOLIO_TRIAGE`: `100.0%` (1/1)
- `RAG_MARKET`: `100.0%` (1/1)
- `SQL_COMPARE`: `100.0%` (2/2)
- `SQL_RAG_FUSED`: `100.0%` (2/2)

### Accuracy By Intent

- `FACT_SQL_COMPARE`: `100.0%` (2/2)
- `PORTFOLIO_TRIAGE_ADVANCED`: `100.0%` (1/1)
- `SENTIMENT_REVIEWS`: `100.0%` (3/3)

## sql-compare-midtown-prices [PASS]

- Query: `Compare our prices to the market in Midtown`
- Category: `sql`
- Tags: `compare, pricing, midtown`
- Intent: `FACT_SQL_COMPARE`
- Policy: `SQL_COMPARE`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `0`
- Latency: `4.01`
- Manual checks:
  - Confirm the result compares Highbury and market rather than only one side.
- Assertions:
  - [PASS] `policy`
    expected: `SQL_COMPARE`
    actual: `SQL_COMPARE`
  - [PASS] `scope`
    expected: `Hybrid`
    actual: `Hybrid`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rows`
    expected: `1`
    actual: `1`

## sql-compare-brooklyn-occupancy [PASS]

- Query: `Compare our occupancy to the market in Brooklyn`
- Category: `sql`
- Tags: `compare, occupancy, brooklyn`
- Intent: `FACT_SQL_COMPARE`
- Policy: `SQL_COMPARE`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `0`
- Latency: `7.7`
- Manual checks:
  - Check that market and Highbury metrics are both represented.
- Assertions:
  - [PASS] `policy`
    expected: `SQL_COMPARE`
    actual: `SQL_COMPARE`
  - [PASS] `scope`
    expected: `Hybrid`
    actual: `Hybrid`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Brooklyn']}`
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': None}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rows`
    expected: `1`
    actual: `1`

## rag-cleanliness-question [PASS]

- Query: `Are guests complaining about how clean the place is?`
- Category: `rag`
- Tags: `reviews, cleanliness, sentiment`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `RAG_MARKET`
- Scope: `Market`
- Row count: `0`
- RAG count: `10`
- Latency: `2.45`
- Manual checks:
  - Confirm the snippets are really about cleanliness rather than general sentiment.
- Assertions:
  - [PASS] `intent`
    expected: `SENTIMENT_REVIEWS`
    actual: `SENTIMENT_REVIEWS`
  - [PASS] `max_rows`
    expected: `0`
    actual: `0`
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`

## hybrid-midtown-price-and-reviews [PASS]

- Query: `Compare our prices to the market in Midtown and summarize guest complaints`
- Category: `hybrid`
- Tags: `compare, pricing, reviews, midtown`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `SQL_RAG_FUSED`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `10`
- Latency: `6.65`
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
    actual: `10`

## hybrid-brooklyn-revenue-and-reviews [PASS]

- Query: `Compare our revenue to the market in Brooklyn and what guests complain about`
- Category: `hybrid`
- Tags: `compare, revenue, reviews, brooklyn`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `SQL_RAG_FUSED`
- Scope: `Hybrid`
- Row count: `0`
- RAG count: `10`
- Latency: `9.65`
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

## triage-manhattan [PASS]

- Query: `Be a portfolio triage agent and diagnose Highbury listings in Manhattan`
- Category: `triage`
- Tags: `triage, highbury, manhattan`
- Intent: `PORTFOLIO_TRIAGE_ADVANCED`
- Policy: `PORTFOLIO_TRIAGE`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `18`
- Latency: `11.93`
- Manual checks:
  - Review backlog recommendations for plausibility.
  - Check that cited review snippets support the triage summary.
- Assertions:
  - [PASS] `intent`
    expected: `PORTFOLIO_TRIAGE_ADVANCED`
    actual: `PORTFOLIO_TRIAGE_ADVANCED`
  - [PASS] `policy`
    expected: `PORTFOLIO_TRIAGE`
    actual: `PORTFOLIO_TRIAGE`
  - [PASS] `scope`
    expected: `Highbury`
    actual: `Highbury`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Manhattan'], 'is_highbury': True}`
    actual: `{'borough': ['Manhattan'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`
