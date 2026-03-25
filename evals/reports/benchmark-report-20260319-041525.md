# wtchtwr Benchmark Report

- Benchmark file: `evals\benchmarks.local.json`
- Generated at: `2026-03-19T08:15:25.011204+00:00`
- Model label: `default`
- Main model: `env/default`
- Main fallback: `env/default`
- NL2SQL model: `env/default`
- NL2SQL fallback: `env/default`
- Cases: `6`
- Passed: `4`
- Failed: `2`
- Pass rate: `66.67%`

## Summary Metrics

- Assertion accuracy: `84.0%` (21/25)
- Average latency: `4.6867s`
- P50 latency: `3.25s`
- P95 latency: `11.4425s`
- Max latency: `13.68s`
- SQL cases passing: `2/2`
- RAG cases passing: `1/1`
- Hybrid cases passing: `0/2`

### Accuracy By Category

- `hybrid`: `0.0%` (0/2)
- `rag`: `100.0%` (1/1)
- `sql`: `100.0%` (2/2)
- `triage`: `100.0%` (1/1)

### Accuracy By Policy

- `PORTFOLIO_TRIAGE`: `100.0%` (1/1)
- `RAG_HYBRID`: `0.0%` (0/1)
- `RAG_MARKET`: `100.0%` (1/1)
- `SQL_COMPARE`: `100.0%` (2/2)
- `SQL_RAG_FUSED`: `0.0%` (0/1)

### Accuracy By Intent

- `FACT_SQL_COMPARE`: `100.0%` (2/2)
- `PORTFOLIO_TRIAGE_ADVANCED`: `100.0%` (1/1)
- `SENTIMENT_REVIEWS`: `33.33%` (1/3)

## sql-compare-midtown-prices [PASS]

- Query: `Compare our prices to the market in Midtown`
- Category: `sql`
- Tags: `compare, pricing, midtown`
- Intent: `FACT_SQL_COMPARE`
- Policy: `SQL_COMPARE`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `0`
- Latency: `3.57`
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
- Latency: `4.73`
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
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`
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
- Latency: `2.68`
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

## hybrid-midtown-price-and-reviews [FAIL]

- Query: `Compare our prices to the market in Midtown and summarize guest complaints`
- Category: `hybrid`
- Tags: `compare, pricing, reviews, midtown`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `RAG_HYBRID`
- Scope: `Hybrid`
- Row count: `0`
- RAG count: `4`
- Latency: `0.53`
- Manual checks:
  - Confirm both SQL comparison and review evidence are present.
- Assertions:
  - [FAIL] `policy`
    expected: `SQL_RAG_FUSED`
    actual: `RAG_HYBRID`
  - [PASS] `scope`
    expected: `Hybrid`
    actual: `Hybrid`
  - [FAIL] `require_sql`
    expected: `True`
    actual: `False`
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
- Row count: `0`
- RAG count: `0`
- Latency: `2.93`
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
  - [FAIL] `require_sql`
    expected: `True`
    actual: `False`
  - [FAIL] `min_rag_snippets`
    expected: `1`
    actual: `0`

## triage-manhattan [PASS]

- Query: `Be a portfolio triage agent and diagnose Highbury listings in Manhattan`
- Category: `triage`
- Tags: `triage, highbury, manhattan`
- Intent: `PORTFOLIO_TRIAGE_ADVANCED`
- Policy: `PORTFOLIO_TRIAGE`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `18`
- Latency: `13.68`
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
