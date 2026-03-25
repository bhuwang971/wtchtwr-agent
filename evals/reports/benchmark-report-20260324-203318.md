# wtchtwr Benchmark Report

- Benchmark file: `evals\benchmarks.holdout.json`
- Generated at: `2026-03-25T00:33:18.539368+00:00`
- Model label: `default`
- Main model: `env/default`
- Main fallback: `env/default`
- NL2SQL model: `env/default`
- NL2SQL fallback: `env/default`
- Cases: `13`
- Passed: `13`
- Failed: `0`
- Pass rate: `100.0%`

## Summary Metrics

- Assertion accuracy: `100.0%` (41/41)
- Average latency: `20.2985s`
- P50 latency: `5.82s`
- P95 latency: `79.992s`
- Max latency: `95.1s`
- SQL cases passing: `4/4`
- RAG cases passing: `3/3`
- Hybrid cases passing: `2/2`

### Accuracy By Category

- `expansion`: `100.0%` (2/2)
- `hybrid`: `100.0%` (2/2)
- `rag`: `100.0%` (3/3)
- `sql`: `100.0%` (4/4)
- `triage`: `100.0%` (2/2)

### Accuracy By Policy

- `EXPANSION_SCOUT`: `100.0%` (2/2)
- `PORTFOLIO_TRIAGE`: `100.0%` (2/2)
- `RAG_HIGHBURY`: `100.0%` (1/1)
- `RAG_MARKET`: `100.0%` (2/2)
- `SQL_COMPARE`: `100.0%` (1/1)
- `SQL_HIGHBURY`: `100.0%` (1/1)
- `SQL_MARKET`: `100.0%` (2/2)
- `SQL_RAG_FUSED`: `100.0%` (2/2)

### Accuracy By Intent

- `EXPANSION_SCOUT`: `100.0%` (2/2)
- `FACT_SQL`: `100.0%` (4/4)
- `FACT_SQL_COMPARE`: `100.0%` (1/1)
- `FACT_SQL_RAG_HYBRID`: `100.0%` (2/2)
- `PORTFOLIO_TRIAGE_ADVANCED`: `100.0%` (2/2)
- `SENTIMENT_REVIEWS`: `100.0%` (2/2)

## holdout-sql-highbury-manhattan-nightly-rate [PASS]

- Query: `For Manhattan only, give me our Highbury units and the nightly price.`
- Category: `sql`
- Tags: `holdout, paraphrase, sql, highbury, manhattan`
- Intent: `FACT_SQL`
- Policy: `SQL_HIGHBURY`
- Scope: `Highbury`
- Row count: `5`
- RAG count: `0`
- Latency: `2.23`
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
- Latency: `1.52`
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

## holdout-sql-brooklyn-march-occupancy [PASS]

- Query: `Pull occupancy for Brooklyn, but just for March.`
- Category: `sql`
- Tags: `holdout, sql, occupancy, brooklyn, month-filter`
- Intent: `FACT_SQL`
- Policy: `SQL_MARKET`
- Scope: `Market`
- Row count: `5`
- RAG count: `0`
- Latency: `0.95`
- Manual checks:
  - Confirm the generated SQL applies both the borough and month constraint.
- Assertions:
  - [PASS] `filters_subset`
    expected: `{'borough': ['Brooklyn'], 'month': ['MAR']}`
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': ['MAR'], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': None}`
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
- Latency: `2.66`
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
- Latency: `5.82`
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

## holdout-rag-highbury-positive-feedback [PASS]

- Query: `Any upbeat guest feedback on our Highbury homes?`
- Category: `rag`
- Tags: `holdout, rag, positive, highbury`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `RAG_HIGHBURY`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `10`
- Latency: `1.13`
- Manual checks:
  - Confirm snippets are positive and actually tied to Highbury properties.
- Assertions:
  - [PASS] `filters_subset`
    expected: `{'is_highbury': True, 'sentiment_label': 'positive'}`
    actual: `{'borough': [], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': 'positive'}`
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
- Latency: `1.22`
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
- Row count: `5`
- RAG count: `10`
- Latency: `7.4`
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

## holdout-hybrid-manhattan-occupancy-review-themes [PASS]

- Query: `For Manhattan, compare our occupancy to the market and back it up with guest review themes.`
- Category: `hybrid`
- Tags: `holdout, hybrid, occupancy, manhattan`
- Intent: `FACT_SQL_RAG_HYBRID`
- Policy: `SQL_RAG_FUSED`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `10`
- Latency: `8.38`
- Manual checks:
  - Check that occupancy comes from SQL and that the narrative cites review evidence.
- Assertions:
  - [PASS] `policy`
    expected: `SQL_RAG_FUSED`
    actual: `SQL_RAG_FUSED`
  - [PASS] `scope`
    expected: `Hybrid`
    actual: `Hybrid`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Manhattan']}`
    actual: `{'borough': ['Manhattan'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': None}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`

## holdout-triage-queens-portfolio-lead [PASS]

- Query: `Act as my portfolio triage lead for Highbury units in Queens.`
- Category: `triage`
- Tags: `holdout, triage, queens, highbury`
- Intent: `PORTFOLIO_TRIAGE_ADVANCED`
- Policy: `PORTFOLIO_TRIAGE`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `18`
- Latency: `37.38`
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

## holdout-triage-revenue-kpi-low-performers [PASS]

- Query: `Use revenue as the KPI and flag weak Highbury performers.`
- Category: `triage`
- Tags: `holdout, triage, revenue, kpi`
- Intent: `PORTFOLIO_TRIAGE_ADVANCED`
- Policy: `PORTFOLIO_TRIAGE`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `18`
- Latency: `30.17`
- Manual checks:
  - Check that the triage prioritization is revenue-led rather than occupancy-led.
- Assertions:
  - [PASS] `intent`
    expected: `PORTFOLIO_TRIAGE_ADVANCED`
    actual: `PORTFOLIO_TRIAGE_ADVANCED`
  - [PASS] `filters_subset`
    expected: `{'is_highbury': True, 'kpi': 'estimated_revenue_30'}`
    actual: `{'borough': [], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'kpi': 'estimated_revenue_30', 'sentiment_label': None}`

## holdout-expansion-nyc-submarkets-next-year [PASS]

- Query: `If Highbury adds supply next year, which NYC submarkets look strongest and why?`
- Category: `expansion`
- Tags: `holdout, expansion, nyc, submarkets`
- Intent: `EXPANSION_SCOUT`
- Policy: `EXPANSION_SCOUT`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `0`
- Latency: `69.92`
- Manual checks:
  - Check that the recommendation is grounded in recent external sources, not generic expansion language.
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

## holdout-expansion-brooklyn-only [PASS]

- Query: `Limit the expansion recommendation to Brooklyn neighborhoods, not citywide.`
- Category: `expansion`
- Tags: `holdout, expansion, brooklyn, constraint`
- Intent: `EXPANSION_SCOUT`
- Policy: `EXPANSION_SCOUT`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `0`
- Latency: `95.1`
- Manual checks:
  - Verify that the write-up stays Brooklyn-focused and does not drift back to generic NYC.
- Assertions:
  - [PASS] `intent`
    expected: `EXPANSION_SCOUT`
    actual: `EXPANSION_SCOUT`
  - [PASS] `policy`
    expected: `EXPANSION_SCOUT`
    actual: `EXPANSION_SCOUT`
