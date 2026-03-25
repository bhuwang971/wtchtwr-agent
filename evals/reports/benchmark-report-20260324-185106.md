# wtchtwr Benchmark Report

- Benchmark file: `evals\benchmarks.holdout.json`
- Generated at: `2026-03-24T22:51:06.839216+00:00`
- Model label: `default`
- Main model: `env/default`
- Main fallback: `env/default`
- NL2SQL model: `env/default`
- NL2SQL fallback: `env/default`
- Cases: `13`
- Passed: `8`
- Failed: `5`
- Pass rate: `61.54%`

## Summary Metrics

- Assertion accuracy: `78.05%` (32/41)
- Average latency: `8.2338s`
- P50 latency: `2.81s`
- P95 latency: `34.09s`
- Max latency: `45.85s`
- SQL cases passing: `3/4`
- RAG cases passing: `2/3`
- Hybrid cases passing: `1/2`

### Accuracy By Category

- `expansion`: `50.0%` (1/2)
- `hybrid`: `50.0%` (1/2)
- `rag`: `66.67%` (2/3)
- `sql`: `75.0%` (3/4)
- `triage`: `50.0%` (1/2)

### Accuracy By Policy

- `EXPANSION_SCOUT`: `100.0%` (1/1)
- `PORTFOLIO_TRIAGE`: `100.0%` (1/1)
- `RAG_MARKET`: `100.0%` (2/2)
- `SQL_COMPARE`: `50.0%` (1/2)
- `SQL_HIGHBURY`: `50.0%` (1/2)
- `SQL_MARKET`: `50.0%` (1/2)
- `SQL_RAG_FUSED`: `33.33%` (1/3)

### Accuracy By Intent

- `EXPANSION_SCOUT`: `100.0%` (1/1)
- `FACT_SQL`: `60.0%` (3/5)
- `FACT_SQL_COMPARE`: `50.0%` (1/2)
- `FACT_SQL_RAG_HYBRID`: `33.33%` (1/3)
- `PORTFOLIO_TRIAGE_ADVANCED`: `100.0%` (1/1)
- `SENTIMENT_REVIEWS`: `100.0%` (1/1)

## holdout-sql-highbury-manhattan-nightly-rate [PASS]

- Query: `For Manhattan only, give me our Highbury units and the nightly price.`
- Category: `sql`
- Tags: `holdout, paraphrase, sql, highbury, manhattan`
- Intent: `FACT_SQL`
- Policy: `SQL_HIGHBURY`
- Scope: `Highbury`
- Row count: `5`
- RAG count: `0`
- Latency: `2.37`
- Manual checks:
  - Verify the result stays within Manhattan and only returns Highbury-managed units.
- Assertions:
  - [PASS] `policy`
    expected: `SQL_HIGHBURY`
    actual: `SQL_HIGHBURY`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Manhattan'], 'is_highbury': True}`
    actual: `{'borough': ['Manhattan'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rows`
    expected: `1`
    actual: `5`

## holdout-sql-market-queens-mean-price [PASS]

- Query: `Across Queens, what is the mean price per night for the market?`
- Category: `sql`
- Tags: `holdout, paraphrase, sql, market, queens`
- Intent: `FACT_SQL`
- Policy: `SQL_MARKET`
- Scope: `Market`
- Row count: `1`
- RAG count: `0`
- Latency: `1.46`
- Manual checks:
  - Check that the query is interpreted as market-wide pricing, not a single listing lookup.
- Assertions:
  - [PASS] `policy`
    expected: `SQL_MARKET`
    actual: `SQL_MARKET`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Queens'], 'is_highbury': False}`
    actual: `{'borough': ['Queens'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': None}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rows`
    expected: `1`
    actual: `1`

## holdout-sql-brooklyn-march-occupancy [FAIL]

- Query: `Pull occupancy for Brooklyn, but just for March.`
- Category: `sql`
- Tags: `holdout, sql, occupancy, brooklyn, month-filter`
- Intent: `FACT_SQL`
- Policy: `SQL_MARKET`
- Scope: `Market`
- Row count: `5`
- RAG count: `0`
- Latency: `2.81`
- Manual checks:
  - Confirm the generated SQL applies both the borough and month constraint.
- Assertions:
  - [FAIL] `filters_subset`
    expected: `{'borough': ['Brooklyn'], 'month': ['MAR']}`
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': None}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`

## holdout-sql-compare-midtown-rates [PASS]

- Query: `Against the market, how are our Midtown nightly rates stacked up?`
- Category: `sql`
- Tags: `holdout, sql, compare, midtown`
- Intent: `FACT_SQL_COMPARE`
- Policy: `SQL_COMPARE`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `0`
- Latency: `2.2`
- Manual checks:
  - Confirm the result is a true Highbury-vs-market comparison and not just one side.
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

## holdout-rag-brooklyn-negative-themes [PASS]

- Query: `Summarize the main negative themes guests raise in Brooklyn reviews.`
- Category: `rag`
- Tags: `holdout, rag, complaints, brooklyn, adversarial-wording`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `RAG_MARKET`
- Scope: `Market`
- Row count: `0`
- RAG count: `10`
- Latency: `5.35`
- Manual checks:
  - Check that the retrieved snippets are genuinely negative and Brooklyn-scoped.
- Assertions:
  - [PASS] `intent`
    expected: `SENTIMENT_REVIEWS`
    actual: `SENTIMENT_REVIEWS`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Brooklyn'], 'sentiment_label': 'negative'}`
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': 'negative'}`
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`

## holdout-rag-highbury-positive-feedback [FAIL]

- Query: `Any upbeat guest feedback on our Highbury homes?`
- Category: `rag`
- Tags: `holdout, rag, positive, highbury`
- Intent: `FACT_SQL_RAG_HYBRID`
- Policy: `SQL_RAG_FUSED`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `10`
- Latency: `0.98`
- Manual checks:
  - Confirm snippets are positive and actually tied to Highbury properties.
- Assertions:
  - [FAIL] `filters_subset`
    expected: `{'is_highbury': True, 'sentiment_label': 'positive'}`
    actual: `{'borough': ['Manhattan'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`

## holdout-rag-midtown-parking-evidence [PASS]

- Query: `Show me review evidence about parking around Midtown.`
- Category: `rag`
- Tags: `holdout, rag, parking, midtown`
- Intent: `FACT_SQL`
- Policy: `RAG_MARKET`
- Scope: `Market`
- Row count: `0`
- RAG count: `10`
- Latency: `1.19`
- Manual checks:
  - Verify that parking is explicitly mentioned in the review snippets.
- Assertions:
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`

## holdout-hybrid-brooklyn-revenue-dislikes [PASS]

- Query: `Stack our Brooklyn revenue against the market, then tell me what guests dislike.`
- Category: `hybrid`
- Tags: `holdout, hybrid, revenue, brooklyn`
- Intent: `FACT_SQL_RAG_HYBRID`
- Policy: `SQL_RAG_FUSED`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `10`
- Latency: `6.09`
- Manual checks:
  - Confirm the answer includes both a revenue comparison and review-backed guest complaints.
- Assertions:
  - [PASS] `policy`
    expected: `SQL_RAG_FUSED`
    actual: `SQL_RAG_FUSED`
  - [PASS] `scope`
    expected: `Hybrid`
    actual: `Hybrid`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Brooklyn']}`
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': None}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`

## holdout-hybrid-manhattan-occupancy-review-themes [FAIL]

- Query: `For Manhattan, compare our occupancy to the market and back it up with guest review themes.`
- Category: `hybrid`
- Tags: `holdout, hybrid, occupancy, manhattan`
- Intent: `FACT_SQL_COMPARE`
- Policy: `SQL_COMPARE`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `0`
- Latency: `7.61`
- Manual checks:
  - Check that occupancy comes from SQL and that the narrative cites review evidence.
- Assertions:
  - [FAIL] `policy`
    expected: `SQL_RAG_FUSED`
    actual: `SQL_COMPARE`
  - [PASS] `scope`
    expected: `Hybrid`
    actual: `Hybrid`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Manhattan']}`
    actual: `{'borough': ['Manhattan'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': None}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [FAIL] `min_rag_snippets`
    expected: `1`
    actual: `0`

## holdout-triage-queens-portfolio-lead [PASS]

- Query: `Act as my portfolio triage lead for Highbury units in Queens.`
- Category: `triage`
- Tags: `holdout, triage, queens, highbury`
- Intent: `PORTFOLIO_TRIAGE_ADVANCED`
- Policy: `PORTFOLIO_TRIAGE`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `18`
- Latency: `26.25`
- Manual checks:
  - Review whether the triage summary stays constrained to Queens Highbury listings.
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
    expected: `{'borough': ['Queens'], 'is_highbury': True}`
    actual: `{'borough': ['Queens'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`

## holdout-triage-revenue-kpi-low-performers [FAIL]

- Query: `Use revenue as the KPI and flag weak Highbury performers.`
- Category: `triage`
- Tags: `holdout, triage, revenue, kpi`
- Intent: `FACT_SQL`
- Policy: `SQL_HIGHBURY`
- Scope: `Highbury`
- Row count: `5`
- RAG count: `0`
- Latency: `3.89`
- Manual checks:
  - Check that the triage prioritization is revenue-led rather than occupancy-led.
- Assertions:
  - [FAIL] `intent`
    expected: `PORTFOLIO_TRIAGE_ADVANCED`
    actual: `FACT_SQL`
  - [FAIL] `filters_subset`
    expected: `{'is_highbury': True, 'kpi': 'estimated_revenue_30'}`
    actual: `{'borough': [], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`

## holdout-expansion-nyc-submarkets-next-year [FAIL]

- Query: `If Highbury adds supply next year, which NYC submarkets look strongest and why?`
- Category: `expansion`
- Tags: `holdout, expansion, nyc, submarkets`
- Intent: `FACT_SQL_RAG_HYBRID`
- Policy: `SQL_RAG_FUSED`
- Scope: `Hybrid`
- Row count: `0`
- RAG count: `10`
- Latency: `0.99`
- Manual checks:
  - Check that the recommendation is grounded in recent external sources, not generic expansion language.
- Assertions:
  - [FAIL] `intent`
    expected: `EXPANSION_SCOUT`
    actual: `FACT_SQL_RAG_HYBRID`
  - [FAIL] `policy`
    expected: `EXPANSION_SCOUT`
    actual: `SQL_RAG_FUSED`
  - [FAIL] `scope`
    expected: `Highbury`
    actual: `Hybrid`

## holdout-expansion-brooklyn-only [PASS]

- Query: `Limit the expansion recommendation to Brooklyn neighborhoods, not citywide.`
- Category: `expansion`
- Tags: `holdout, expansion, brooklyn, constraint`
- Intent: `EXPANSION_SCOUT`
- Policy: `EXPANSION_SCOUT`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `0`
- Latency: `45.85`
- Manual checks:
  - Verify that the write-up stays Brooklyn-focused and does not drift back to generic NYC.
- Assertions:
  - [PASS] `intent`
    expected: `EXPANSION_SCOUT`
    actual: `EXPANSION_SCOUT`
  - [PASS] `policy`
    expected: `EXPANSION_SCOUT`
    actual: `EXPANSION_SCOUT`
