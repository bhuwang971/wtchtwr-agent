# wtchtwr Benchmark Report

- Benchmark file: `evals\benchmarks.local.json`
- Generated at: `2026-03-19T05:48:30.773752+00:00`
- Cases: `22`
- Passed: `11`
- Failed: `11`
- Pass rate: `50.0%`

## greeting-hi [PASS]

- Query: `Hi`
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
- Intent: `FACT_SQL`
- Policy: `SQL_HIGHBURY`
- Scope: `Highbury`
- Row count: `5`
- RAG count: `0`
- Latency: `3.25`
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
    actual: `SELECT listings_id, host_id, host_name, neighbourhood, neighbourhood_group, price_in_usd 
FROM highbury_listings 
WHERE lower(neighbourhood_group) = 'manhattan';`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rows`
    expected: `1`
    actual: `5`

## sql-market-queens-average-price [FAIL]

- Query: `What is the average nightly rate in Queens?`
- Intent: `FACT_SQL`
- Policy: `SQL_MARKET`
- Scope: `Market`
- Row count: `0`
- RAG count: `0`
- Latency: `1.07`
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
  - [FAIL] `min_rows`
    expected: `1`
    actual: `0`

## sql-market-brooklyn-bedrooms [PASS]

- Query: `Show average bedrooms for listings in Brooklyn`
- Intent: `FACT_SQL`
- Policy: `SQL_MARKET`
- Scope: `Market`
- Row count: `1`
- RAG count: `0`
- Latency: `1.2`
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
- Intent: `FACT_SQL`
- Policy: `SQL_MARKET`
- Scope: `Market`
- Row count: `1`
- RAG count: `0`
- Latency: `1.39`
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

## sql-occupancy-trend-highbury [FAIL]

- Query: `Show occupancy for our Highbury listings in Brooklyn`
- Intent: `FACT_SQL`
- Policy: `SQL_HIGHBURY`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `0`
- Latency: `2.83`
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
  - [FAIL] `min_rows`
    expected: `1`
    actual: `0`

## sql-compare-midtown-prices [FAIL]

- Query: `Compare our prices to the market in Midtown`
- Intent: `FACT_SQL_COMPARE`
- Policy: `SQL_RAG_COMPARE`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `10`
- Latency: `4.47`
- Manual checks:
  - Confirm the result compares Highbury and market rather than only one side.
- Assertions:
  - [FAIL] `policy`
    expected: `SQL_COMPARE`
    actual: `SQL_RAG_COMPARE`
  - [PASS] `scope`
    expected: `Hybrid`
    actual: `Hybrid`
  - [FAIL] `require_sql`
    expected: `True`
    actual: `False`
  - [PASS] `min_rows`
    expected: `1`
    actual: `1`

## sql-compare-brooklyn-occupancy [FAIL]

- Query: `Compare our occupancy to the market in Brooklyn`
- Intent: `FACT_SQL_COMPARE`
- Policy: `SQL_RAG_COMPARE`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `0`
- Latency: `6.22`
- Manual checks:
  - Check that market and Highbury metrics are both represented.
- Assertions:
  - [FAIL] `policy`
    expected: `SQL_COMPARE`
    actual: `SQL_RAG_COMPARE`
  - [PASS] `scope`
    expected: `Hybrid`
    actual: `Hybrid`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Brooklyn']}`
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`
  - [FAIL] `require_sql`
    expected: `True`
    actual: `False`
  - [PASS] `min_rows`
    expected: `1`
    actual: `1`

## sql-month-filter-march [PASS]

- Query: `Show occupancy in Queens in March`
- Intent: `FACT_SQL`
- Policy: `SQL_MARKET`
- Scope: `Market`
- Row count: `1`
- RAG count: `0`
- Latency: `2.19`
- Manual checks:
  - Confirm March filtering is reflected in the final SQL.
- Assertions:
  - [PASS] `filters_subset`
    expected: `{'borough': ['Queens'], 'month': ['MAR']}`
    actual: `{'borough': ['Queens'], 'neighbourhood': [], 'month': ['MAR'], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': None}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`

## rag-brooklyn-complaints [PASS]

- Query: `What complaints do guests mention in Brooklyn?`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `RAG_MARKET`
- Scope: `Market`
- Row count: `0`
- RAG count: `10`
- Latency: `1.6`
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
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`

## rag-cleanliness-question [FAIL]

- Query: `Are guests complaining about how clean the place is?`
- Intent: `REVIEWS_RAG`
- Policy: `RAG_MARKET`
- Scope: `Market`
- Row count: `0`
- RAG count: `10`
- Latency: `1.02`
- Manual checks:
  - Confirm the snippets are really about cleanliness rather than general sentiment.
- Assertions:
  - [FAIL] `intent`
    expected: `SENTIMENT_REVIEWS`
    actual: `REVIEWS_RAG`
  - [PASS] `max_rows`
    expected: `0`
    actual: `0`
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`

## rag-listing-specific-reviews [PASS]

- Query: `Show the latest 5 reviews for listing 2595`
- Intent: `FACT_SQL`
- Policy: `RAG_MARKET`
- Scope: `Market`
- Row count: `0`
- RAG count: `7`
- Latency: `0.87`
- Manual checks:
  - Confirm snippets belong to listing 2595.
- Assertions:
  - [PASS] `filters_subset`
    expected: `{'listing_id': 2595}`
    actual: `{'borough': [], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': 2595, 'is_highbury': False, 'sentiment_label': None}`
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `7`

## rag-parking-mentions-midtown [PASS]

- Query: `Show recent guest reviews mentioning parking in Midtown`
- Intent: `FACT_SQL`
- Policy: `RAG_MARKET`
- Scope: `Market`
- Row count: `0`
- RAG count: `10`
- Latency: `1.43`
- Manual checks:
  - Confirm parking is actually mentioned in the snippets.
  - Check Midtown alignment where possible.
- Assertions:
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`

## rag-positive-reviews-highbury [PASS]

- Query: `Show positive guest feedback for our Highbury listings`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `RAG_HIGHBURY`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `10`
- Latency: `1.07`
- Manual checks:
  - Confirm the snippets are actually positive and Highbury-specific.
- Assertions:
  - [PASS] `intent`
    expected: `SENTIMENT_REVIEWS`
    actual: `SENTIMENT_REVIEWS`
  - [PASS] `filters_subset`
    expected: `{'is_highbury': True, 'sentiment_label': 'positive'}`
    actual: `{'borough': ['Manhattan'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': 'positive'}`
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`

## hybrid-midtown-price-and-reviews [FAIL]

- Query: `Compare our prices to the market in Midtown and summarize guest complaints`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `SQL_RAG_COMPARE`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `4`
- Latency: `3.75`
- Manual checks:
  - Confirm both SQL comparison and review evidence are present.
- Assertions:
  - [FAIL] `policy`
    expected: `SQL_RAG_FUSED`
    actual: `SQL_RAG_COMPARE`
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
- Intent: `FACT_SQL_RAG_HYBRID`
- Policy: `SQL_RAG_COMPARE`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `0`
- Latency: `8.7`
- Manual checks:
  - Confirm revenue is from SQL and complaints are from review evidence.
- Assertions:
  - [FAIL] `policy`
    expected: `SQL_RAG_FUSED`
    actual: `SQL_RAG_COMPARE`
  - [PASS] `scope`
    expected: `Hybrid`
    actual: `Hybrid`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Brooklyn']}`
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`
  - [FAIL] `require_sql`
    expected: `True`
    actual: `False`
  - [FAIL] `min_rag_snippets`
    expected: `1`
    actual: `0`

## triage-manhattan [FAIL]

- Query: `Be a portfolio triage agent and diagnose Highbury listings in Manhattan`
- Intent: `PORTFOLIO_TRIAGE_ADVANCED`
- Policy: `PORTFOLIO_TRIAGE`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `18`
- Latency: `19.06`
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
  - [FAIL] `filters_subset`
    expected: `{'borough': ['Manhattan'], 'is_highbury': True}`
    actual: `{'borough': [], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`

## triage-brooklyn [FAIL]

- Query: `Diagnose my Highbury portfolio in Brooklyn`
- Intent: `PORTFOLIO_TRIAGE_ADVANCED`
- Policy: `PORTFOLIO_TRIAGE`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `18`
- Latency: `19.35`
- Manual checks:
  - Confirm the triage scope is limited to Brooklyn Highbury units.
- Assertions:
  - [PASS] `intent`
    expected: `PORTFOLIO_TRIAGE_ADVANCED`
    actual: `PORTFOLIO_TRIAGE_ADVANCED`
  - [PASS] `scope`
    expected: `Highbury`
    actual: `Highbury`
  - [FAIL] `filters_subset`
    expected: `{'borough': ['Brooklyn'], 'is_highbury': True}`
    actual: `{'borough': [], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`

## triage-custom-kpi-revenue [PASS]

- Query: `Rank my Highbury portfolio by revenue and diagnose low performers`
- Intent: `PORTFOLIO_TRIAGE_ADVANCED`
- Policy: `PORTFOLIO_TRIAGE`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `18`
- Latency: `20.61`
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
- Intent: `EXPANSION_SCOUT`
- Policy: `None`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `0`
- Latency: `167.46`
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
- Intent: `EXPANSION_SCOUT`
- Policy: `None`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `0`
- Latency: `85.61`
- Manual checks:
  - Confirm the response discusses Brooklyn neighborhoods rather than generic NYC.
- Assertions:
  - [PASS] `intent`
    expected: `EXPANSION_SCOUT`
    actual: `EXPANSION_SCOUT`
  - [FAIL] `policy`
    expected: `EXPANSION_SCOUT`
