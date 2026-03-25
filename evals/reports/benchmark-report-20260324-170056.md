# wtchtwr Benchmark Report

- Benchmark file: `evals\benchmarks.local.json`
- Generated at: `2026-03-24T21:00:56.452806+00:00`
- Model label: `default`
- Main model: `env/default`
- Main fallback: `env/default`
- NL2SQL model: `env/default`
- NL2SQL fallback: `env/default`
- Cases: `22`
- Passed: `13`
- Failed: `9`
- Pass rate: `59.09%`

## Summary Metrics

- Assertion accuracy: `88.46%` (69/78)
- Average latency: `39.8205s`
- P50 latency: `4.155s`
- P95 latency: `210.251s`
- Max latency: `210.78s`
- SQL cases passing: `8/8`
- RAG cases passing: `0/5`
- Hybrid cases passing: `0/2`

### Accuracy By Category

- `conversation`: `100.0%` (2/2)
- `expansion`: `0.0%` (0/2)
- `hybrid`: `0.0%` (0/2)
- `rag`: `0.0%` (0/5)
- `sql`: `100.0%` (8/8)
- `triage`: `100.0%` (3/3)

### Accuracy By Policy

- `CONVERSATION`: `100.0%` (2/2)
- `PORTFOLIO_TRIAGE`: `100.0%` (3/3)
- `RAG_HIGHBURY`: `0.0%` (0/1)
- `RAG_MARKET`: `0.0%` (0/4)
- `SQL_COMPARE`: `100.0%` (2/2)
- `SQL_HIGHBURY`: `100.0%` (2/2)
- `SQL_MARKET`: `100.0%` (4/4)
- `SQL_RAG_FUSED`: `0.0%` (0/2)
- `unknown`: `0.0%` (0/2)

### Accuracy By Intent

- `EXPANSION_SCOUT`: `0.0%` (0/2)
- `FACT_SQL`: `75.0%` (6/8)
- `FACT_SQL_COMPARE`: `100.0%` (2/2)
- `GREETING`: `100.0%` (1/1)
- `PORTFOLIO_TRIAGE_ADVANCED`: `100.0%` (3/3)
- `SENTIMENT_REVIEWS`: `0.0%` (0/5)
- `THANKS`: `100.0%` (1/1)

## greeting-hi [PASS]

- Query: `Hi`
- Category: `conversation`
- Tags: `greeting, baseline`
- Intent: `GREETING`
- Policy: `CONVERSATION`
- Scope: `General`
- Row count: `0`
- RAG count: `0`
- Latency: `0.01`
- Manual checks:
  - Greeting should stay concise and not include fabricated metrics.
- Assertions:
  - [PASS] `intent`
    expected: `GREETING`
    actual: `GREETING`
  - [PASS] `policy`
    expected: `CONVERSATION`
    actual: `CONVERSATION`
  - [PASS] `require_sql`
    expected: `False`
    actual: `False`
  - [PASS] `max_rows`
    expected: `0`
    actual: `0`

## greeting-thanks [PASS]

- Query: `Thank you`
- Category: `conversation`
- Tags: `thanks, baseline`
- Intent: `THANKS`
- Policy: `CONVERSATION`
- Scope: `General`
- Row count: `0`
- RAG count: `0`
- Latency: `0.01`
- Manual checks:
  - Reply should acknowledge thanks without unrelated portfolio content.
- Assertions:
  - [PASS] `intent`
    expected: `THANKS`
    actual: `THANKS`
  - [PASS] `policy`
    expected: `CONVERSATION`
    actual: `CONVERSATION`
  - [PASS] `require_sql`
    expected: `False`
    actual: `False`
  - [PASS] `max_rows`
    expected: `0`
    actual: `0`

## sql-highbury-manhattan-prices [PASS]

- Query: `List our Highbury listings in Manhattan with prices`
- Category: `sql`
- Tags: `highbury, pricing, manhattan`
- Intent: `FACT_SQL`
- Policy: `SQL_HIGHBURY`
- Scope: `Highbury`
- Row count: `5`
- RAG count: `0`
- Latency: `2.95`
- Manual checks:
  - Spot-check one listing and price directly in DuckDB.
  - Confirm all rows are genuinely Highbury-managed.
- Assertions:
  - [PASS] `policy`
    expected: `SQL_HIGHBURY`
    actual: `SQL_HIGHBURY`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Manhattan'], 'is_highbury': True}`
    actual: `{'borough': ['Manhattan'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`
  - [PASS] `sql_contains`
    expected: `['highbury_listings']`
    actual: `SELECT listings_id, host_id, host_name, neighbourhood, price_in_usd
FROM highbury_listings
WHERE lower(neighbourhood_group) = 'manhattan';`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rows`
    expected: `1`
    actual: `5`

## sql-market-queens-average-price [PASS]

- Query: `What is the average nightly rate in Queens?`
- Category: `sql`
- Tags: `market, pricing, queens`
- Intent: `FACT_SQL`
- Policy: `SQL_MARKET`
- Scope: `Market`
- Row count: `1`
- RAG count: `0`
- Latency: `1.09`
- Manual checks:
  - Verify the average price result with a direct SQL check.
- Assertions:
  - [PASS] `policy`
    expected: `SQL_MARKET`
    actual: `SQL_MARKET`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Queens'], 'is_highbury': False}`
    actual: `{'borough': ['Queens'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': None}`
  - [PASS] `sql_contains`
    expected: `['listings', 'queens']`
    actual: `SELECT ROUND(AVG(price_in_usd), 2) AS average_nightly_rate
FROM listings_cleaned
WHERE lower(neighbourhood_group) = 'queens';`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rows`
    expected: `1`
    actual: `1`

## sql-market-brooklyn-bedrooms [PASS]

- Query: `Show average bedrooms for listings in Brooklyn`
- Category: `sql`
- Tags: `market, inventory, brooklyn`
- Intent: `FACT_SQL`
- Policy: `SQL_MARKET`
- Scope: `Market`
- Row count: `1`
- RAG count: `0`
- Latency: `2.44`
- Manual checks:
  - Check that the result is based on listings data, not reviews.
- Assertions:
  - [PASS] `policy`
    expected: `SQL_MARKET`
    actual: `SQL_MARKET`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Brooklyn']}`
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': None}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rows`
    expected: `1`
    actual: `1`

## sql-listing-specific-price [PASS]

- Query: `Show the price for listing 2595`
- Category: `sql`
- Tags: `listing, pricing, lookup`
- Intent: `FACT_SQL`
- Policy: `SQL_MARKET`
- Scope: `Market`
- Row count: `1`
- RAG count: `0`
- Latency: `0.78`
- Manual checks:
  - Confirm the row maps to listing_id 2595 only.
- Assertions:
  - [PASS] `filters_subset`
    expected: `{'listing_id': 2595}`
    actual: `{'borough': [], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': 2595, 'is_highbury': False, 'sentiment_label': None}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rows`
    expected: `1`
    actual: `1`

## sql-occupancy-trend-highbury [PASS]

- Query: `Show occupancy for our Highbury listings in Brooklyn`
- Category: `sql`
- Tags: `highbury, occupancy, brooklyn`
- Intent: `FACT_SQL`
- Policy: `SQL_HIGHBURY`
- Scope: `Highbury`
- Row count: `1`
- RAG count: `0`
- Latency: `3.59`
- Manual checks:
  - Check occupancy fields in the returned rows or aggregates.
- Assertions:
  - [PASS] `policy`
    expected: `SQL_HIGHBURY`
    actual: `SQL_HIGHBURY`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Brooklyn'], 'is_highbury': True}`
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rows`
    expected: `1`
    actual: `1`

## sql-compare-midtown-prices [PASS]

- Query: `Compare our prices to the market in Midtown`
- Category: `sql`
- Tags: `compare, pricing, midtown`
- Intent: `FACT_SQL_COMPARE`
- Policy: `SQL_COMPARE`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `0`
- Latency: `2.68`
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
- Latency: `4.94`
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

## sql-month-filter-march [PASS]

- Query: `Show occupancy in Queens in March`
- Category: `sql`
- Tags: `month-filter, queens, occupancy`
- Intent: `FACT_SQL`
- Policy: `SQL_MARKET`
- Scope: `Market`
- Row count: `1`
- RAG count: `0`
- Latency: `3.35`
- Manual checks:
  - Confirm March filtering is reflected in the final SQL.
- Assertions:
  - [PASS] `filters_subset`
    expected: `{'borough': ['Queens'], 'month': ['MAR']}`
    actual: `{'borough': ['Queens'], 'neighbourhood': [], 'month': ['MAR'], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': None}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`

## rag-brooklyn-complaints [FAIL]

- Query: `What complaints do guests mention in Brooklyn?`
- Category: `rag`
- Tags: `reviews, complaints, brooklyn`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `RAG_MARKET`
- Scope: `Market`
- Row count: `0`
- RAG count: `0`
- Latency: `24.02`
- Manual checks:
  - Confirm snippets are actually negative complaints.
  - Confirm snippets belong to Brooklyn listings.
- Assertions:
  - [PASS] `intent`
    expected: `SENTIMENT_REVIEWS`
    actual: `SENTIMENT_REVIEWS`
  - [PASS] `policy`
    expected: `RAG_MARKET`
    actual: `RAG_MARKET`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Brooklyn'], 'sentiment_label': 'negative', 'is_highbury': False}`
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': 'negative'}`
  - [PASS] `max_rows`
    expected: `0`
    actual: `0`
  - [FAIL] `min_rag_snippets`
    expected: `1`
    actual: `0`

## rag-cleanliness-question [FAIL]

- Query: `Are guests complaining about how clean the place is?`
- Category: `rag`
- Tags: `reviews, cleanliness, sentiment`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `RAG_MARKET`
- Scope: `Market`
- Row count: `0`
- RAG count: `0`
- Latency: `4.14`
- Manual checks:
  - Confirm the snippets are really about cleanliness rather than general sentiment.
- Assertions:
  - [PASS] `intent`
    expected: `SENTIMENT_REVIEWS`
    actual: `SENTIMENT_REVIEWS`
  - [PASS] `max_rows`
    expected: `0`
    actual: `0`
  - [FAIL] `min_rag_snippets`
    expected: `1`
    actual: `0`

## rag-listing-specific-reviews [FAIL]

- Query: `Show the latest 5 reviews for listing 2595`
- Category: `rag`
- Tags: `reviews, listing, lookup`
- Intent: `FACT_SQL`
- Policy: `RAG_MARKET`
- Scope: `Market`
- Row count: `0`
- RAG count: `0`
- Latency: `4.16`
- Manual checks:
  - Confirm snippets belong to listing 2595.
- Assertions:
  - [PASS] `filters_subset`
    expected: `{'listing_id': 2595}`
    actual: `{'borough': [], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': 2595, 'is_highbury': False, 'sentiment_label': None}`
  - [FAIL] `min_rag_snippets`
    expected: `1`
    actual: `0`

## rag-parking-mentions-midtown [FAIL]

- Query: `Show recent guest reviews mentioning parking in Midtown`
- Category: `rag`
- Tags: `reviews, parking, midtown`
- Intent: `FACT_SQL`
- Policy: `RAG_MARKET`
- Scope: `Market`
- Row count: `0`
- RAG count: `0`
- Latency: `4.16`
- Manual checks:
  - Confirm parking is actually mentioned in the snippets.
  - Check Midtown alignment where possible.
- Assertions:
  - [FAIL] `min_rag_snippets`
    expected: `1`
    actual: `0`

## rag-positive-reviews-highbury [FAIL]

- Query: `Show positive guest feedback for our Highbury listings`
- Category: `rag`
- Tags: `reviews, positive, highbury`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `RAG_HIGHBURY`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `0`
- Latency: `4.15`
- Manual checks:
  - Confirm the snippets are actually positive and Highbury-specific.
- Assertions:
  - [PASS] `intent`
    expected: `SENTIMENT_REVIEWS`
    actual: `SENTIMENT_REVIEWS`
  - [PASS] `filters_subset`
    expected: `{'is_highbury': True, 'sentiment_label': 'positive'}`
    actual: `{'borough': ['Manhattan'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': 'positive'}`
  - [FAIL] `min_rag_snippets`
    expected: `1`
    actual: `0`

## hybrid-midtown-price-and-reviews [FAIL]

- Query: `Compare our prices to the market in Midtown and summarize guest complaints`
- Category: `hybrid`
- Tags: `compare, pricing, reviews, midtown`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `SQL_RAG_FUSED`
- Scope: `Hybrid`
- Row count: `0`
- RAG count: `0`
- Latency: `7.11`
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
  - [FAIL] `min_rag_snippets`
    expected: `1`
    actual: `0`

## hybrid-brooklyn-revenue-and-reviews [FAIL]

- Query: `Compare our revenue to the market in Brooklyn and what guests complain about`
- Category: `hybrid`
- Tags: `compare, revenue, reviews, brooklyn`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `SQL_RAG_FUSED`
- Scope: `Hybrid`
- Row count: `0`
- RAG count: `0`
- Latency: `4.25`
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
- RAG count: `0`
- Latency: `207.42`
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

## triage-brooklyn [PASS]

- Query: `Diagnose my Highbury portfolio in Brooklyn`
- Category: `triage`
- Tags: `triage, highbury, brooklyn`
- Intent: `PORTFOLIO_TRIAGE_ADVANCED`
- Policy: `PORTFOLIO_TRIAGE`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `0`
- Latency: `210.4`
- Manual checks:
  - Confirm the triage scope is limited to Brooklyn Highbury units.
- Assertions:
  - [PASS] `intent`
    expected: `PORTFOLIO_TRIAGE_ADVANCED`
    actual: `PORTFOLIO_TRIAGE_ADVANCED`
  - [PASS] `scope`
    expected: `Highbury`
    actual: `Highbury`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Brooklyn'], 'is_highbury': True}`
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`

## triage-custom-kpi-revenue [PASS]

- Query: `Rank my Highbury portfolio by revenue and diagnose low performers`
- Category: `triage`
- Tags: `triage, revenue, kpi`
- Intent: `PORTFOLIO_TRIAGE_ADVANCED`
- Policy: `PORTFOLIO_TRIAGE`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `0`
- Latency: `210.78`
- Manual checks:
  - Check that revenue, not occupancy, is used as the triage KPI.
- Assertions:
  - [PASS] `intent`
    expected: `PORTFOLIO_TRIAGE_ADVANCED`
    actual: `PORTFOLIO_TRIAGE_ADVANCED`
  - [PASS] `filters_subset`
    expected: `{'is_highbury': True, 'kpi': 'estimated_revenue_30'}`
    actual: `{'borough': [], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'kpi': 'estimated_revenue_30', 'sentiment_label': None}`

## expansion-where-next [FAIL]

- Query: `Where should Highbury expand next in NYC?`
- Category: `expansion`
- Tags: `expansion, nyc, highbury`
- Intent: `EXPANSION_SCOUT`
- Policy: `None`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `0`
- Latency: `65.44`
- Manual checks:
  - Review the expansion recommendation for source grounding.
  - Check that cited web sources are relevant and recent.
- Assertions:
  - [PASS] `intent`
    expected: `EXPANSION_SCOUT`
    actual: `EXPANSION_SCOUT`
  - [FAIL] `policy`
    expected: `EXPANSION_SCOUT`
  - [PASS] `scope`
    expected: `Highbury`
    actual: `Highbury`
  - [PASS] `require_sql`
    expected: `False`
    actual: `False`

## expansion-brooklyn-neighborhoods [FAIL]

- Query: `Which Brooklyn neighborhoods should Highbury consider for expansion?`
- Category: `expansion`
- Tags: `expansion, brooklyn, neighborhoods`
- Intent: `EXPANSION_SCOUT`
- Policy: `None`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `0`
- Latency: `108.18`
- Manual checks:
  - Confirm the response discusses Brooklyn neighborhoods rather than generic NYC.
- Assertions:
  - [PASS] `intent`
    expected: `EXPANSION_SCOUT`
    actual: `EXPANSION_SCOUT`
  - [FAIL] `policy`
    expected: `EXPANSION_SCOUT`
