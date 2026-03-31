# wtchtwr Benchmark Report

- Benchmark file: `C:\Users\bhuwa\wtchtwr\evals\benchmarks.adversarial.json`
- Generated at: `2026-03-31T17:26:58.817934+00:00`
- Model label: `default`
- Main model: `env/default`
- Main fallback: `env/default`
- NL2SQL model: `env/default`
- NL2SQL fallback: `env/default`
- Cases: `8`
- Passed: `7`
- Failed: `1`
- Pass rate: `87.5%`

## Summary Metrics

- Assertion accuracy: `95.24%` (20/21)
- Average latency: `17.7712s`
- P50 latency: `5.545s`
- P95 latency: `71.6575s`
- Max latency: `100.27s`
- SQL cases passing: `2/2`
- RAG cases passing: `2/2`
- Hybrid cases passing: `1/2`

### Accuracy By Category

- `expansion`: `100.0%` (1/1)
- `hybrid`: `50.0%` (1/2)
- `rag`: `100.0%` (2/2)
- `sql`: `100.0%` (2/2)
- `triage`: `100.0%` (1/1)

### Accuracy By Policy

- `EXPANSION_SCOUT`: `100.0%` (1/1)
- `PORTFOLIO_TRIAGE`: `100.0%` (1/1)
- `RAG_MARKET`: `100.0%` (2/2)
- `SQL_COMPARE`: `100.0%` (1/1)
- `SQL_HIGHBURY`: `100.0%` (1/1)
- `SQL_RAG_FUSED`: `50.0%` (1/2)

### Accuracy By Intent

- `EXPANSION_SCOUT`: `100.0%` (1/1)
- `FACT_SQL`: `100.0%` (1/1)
- `FACT_SQL_COMPARE`: `100.0%` (1/1)
- `FACT_SQL_RAG_HYBRID`: `50.0%` (1/2)
- `PORTFOLIO_TRIAGE_ADVANCED`: `100.0%` (1/1)
- `SENTIMENT_REVIEWS`: `100.0%` (2/2)

## adversarial-hybrid-contradictory-brooklyn-midtown [PASS]

- Query: `Compare our Midtown pricing versus the market, but keep the guest complaints focused on Brooklyn only.`
- Category: `hybrid`
- Tags: `adversarial, hybrid, contradictory-filters`
- Intent: `FACT_SQL_RAG_HYBRID`
- Policy: `SQL_RAG_FUSED`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `10`
- Latency: `6.74`
- Manual checks:
  - Confirm SQL stays on Midtown while retrieval evidence reflects the stated Brooklyn complaint constraint.
  - If the system cannot reconcile both clauses cleanly, it should surface partial confidence instead of bluffing.
- Assertions:
  - [PASS] `scope`
    expected: `Hybrid`
    actual: `Hybrid`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`

## adversarial-rag-indirect-cleanliness [PASS]

- Query: `What do reviews imply about hygiene issues without literally saying cleanliness?`
- Category: `rag`
- Tags: `adversarial, rag, indirect-wording, cleanliness`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `RAG_MARKET`
- Scope: `Market`
- Row count: `0`
- RAG count: `10`
- Latency: `0.87`
- Manual checks:
  - Retrieved snippets should actually mention dirty, unclean, or equivalent hygiene complaints.
- Assertions:
  - [PASS] `intent`
    expected: `SENTIMENT_REVIEWS`
    actual: `SENTIMENT_REVIEWS`
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`

## adversarial-sql-vague-top-performers [PASS]

- Query: `Which of our listings are quietly doing the heavy lifting on revenue?`
- Category: `sql`
- Tags: `adversarial, sql, vague-business-language`
- Intent: `FACT_SQL`
- Policy: `SQL_HIGHBURY`
- Scope: `Highbury`
- Row count: `3`
- RAG count: `0`
- Latency: `2.84`
- Manual checks:
  - Check whether the system interprets 'heavy lifting on revenue' as a revenue-ranked listing query.
- Assertions:
  - [PASS] `filters_subset`
    expected: `{'is_highbury': True}`
    actual: `{'borough': [], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rows`
    expected: `1`
    actual: `3`

## adversarial-hybrid-unsupported-missing-evidence [FAIL]

- Query: `Show me Staten Island revenue vs market and back it up with guest complaints for our portfolio there.`
- Category: `hybrid`
- Tags: `adversarial, hybrid, unsupported, abstention`
- Intent: `FACT_SQL_RAG_HYBRID`
- Policy: `SQL_RAG_FUSED`
- Scope: `Hybrid`
- Row count: `0`
- RAG count: `0`
- Latency: `7.77`
- Manual checks:
  - If the portfolio has sparse or no Staten Island evidence, the answer should degrade gracefully and say evidence is weak.
- Assertions:
  - [PASS] `scope`
    expected: `Hybrid`
    actual: `Hybrid`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [FAIL] `require_abstain`
    expected: `True`
    actual: `False`

## adversarial-triage-noisy-prompt [PASS]

- Query: `Give me the 'what is going wrong and what should I fix first' view for Highbury in Manhattan.`
- Category: `triage`
- Tags: `adversarial, triage, noisy-phrasing`
- Intent: `PORTFOLIO_TRIAGE_ADVANCED`
- Policy: `PORTFOLIO_TRIAGE`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `18`
- Latency: `18.52`
- Manual checks:
  - The triage should stay Manhattan-only and prioritize operational fixes rather than generic commentary.
- Assertions:
  - [PASS] `intent`
    expected: `PORTFOLIO_TRIAGE_ADVANCED`
    actual: `PORTFOLIO_TRIAGE_ADVANCED`
  - [PASS] `policy`
    expected: `PORTFOLIO_TRIAGE`
    actual: `PORTFOLIO_TRIAGE`
  - [PASS] `filters_subset`
    expected: `{'borough': ['Manhattan'], 'is_highbury': True}`
    actual: `{'borough': ['Manhattan'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': True, 'sentiment_label': None}`

## adversarial-expansion-constraint-following [PASS]

- Query: `Recommend where Highbury should expand next, but do not use Manhattan and do not drift outside New York City.`
- Category: `expansion`
- Tags: `adversarial, expansion, constraints`
- Intent: `EXPANSION_SCOUT`
- Policy: `EXPANSION_SCOUT`
- Scope: `Highbury`
- Row count: `0`
- RAG count: `0`
- Latency: `100.27`
- Manual checks:
  - Recommendations should honor both constraints: NYC only, Manhattan excluded.
- Assertions:
  - [PASS] `intent`
    expected: `EXPANSION_SCOUT`
    actual: `EXPANSION_SCOUT`
  - [PASS] `policy`
    expected: `EXPANSION_SCOUT`
    actual: `EXPANSION_SCOUT`

## adversarial-rag-negative-vs-positive-conflict [PASS]

- Query: `Guests seem split on Brooklyn. What are the strongest complaints, not the praise?`
- Category: `rag`
- Tags: `adversarial, rag, conflicting-sentiment`
- Intent: `SENTIMENT_REVIEWS`
- Policy: `RAG_MARKET`
- Scope: `Market`
- Row count: `0`
- RAG count: `10`
- Latency: `0.81`
- Manual checks:
  - The answer should bias toward negative evidence and avoid mixing in positive snippets unless it labels them explicitly.
- Assertions:
  - [PASS] `filters_subset`
    expected: `{'borough': ['Brooklyn'], 'sentiment_label': 'negative'}`
    actual: `{'borough': ['Brooklyn'], 'neighbourhood': [], 'month': [], 'year': [], 'listing_id': None, 'is_highbury': False, 'sentiment_label': 'negative'}`
  - [PASS] `min_rag_snippets`
    expected: `1`
    actual: `10`

## adversarial-sql-compare-implicit-market [PASS]

- Query: `Are our Upper West Side prices punching above the neighborhood around us?`
- Category: `sql`
- Tags: `adversarial, sql, compare, implicit-market`
- Intent: `FACT_SQL_COMPARE`
- Policy: `SQL_COMPARE`
- Scope: `Hybrid`
- Row count: `1`
- RAG count: `0`
- Latency: `4.35`
- Manual checks:
  - Check whether the system correctly interprets the neighborhood benchmark as a Highbury vs market comparison.
- Assertions:
  - [PASS] `policy`
    expected: `SQL_COMPARE`
    actual: `SQL_COMPARE`
  - [PASS] `require_sql`
    expected: `True`
    actual: `True`
  - [PASS] `min_rows`
    expected: `1`
    actual: `1`
