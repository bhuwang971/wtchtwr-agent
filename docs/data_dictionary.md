# Data Dictionary

This document defines the key business fields that the `wtchtwr` assistant relies on for SQL, dashboard, KPI, and evaluation flows.

## Listing performance fields

- `occupancy_rate_30`, `occupancy_rate_60`, `occupancy_rate_90`, `occupancy_rate_365`
  - Percentage of nights booked in the trailing 30/60/90/365 day window.
  - Used for portfolio triage, dashboard cards, and market comparisons.
- `estimated_revenue_30`, `estimated_revenue_60`, `estimated_revenue_90`, `estimated_revenue_365`
  - Estimated gross revenue over the trailing 30/60/90/365 day window.
  - Used for revenue ranking, pricing opportunity analysis, and portfolio triage.
- `price_in_usd`
  - Nightly listing price in USD.
  - Used for ADR-style comparisons, dashboard range filters, and market benchmarks.
- `review_scores_rating`
  - Overall Airbnb review score.
  - Used in KPI rollups, dashboard metrics, and expansion candidate ranking.

## Portfolio segmentation fields

- `is_highbury`
  - Boolean flag indicating whether a listing/review belongs to the Highbury portfolio.
  - `highbury_listings` is already portfolio-only, but review and retrieval layers still use this flag.
- `neighbourhood`
  - Neighborhood label used for market and portfolio comparisons.
- `neighbourhood_group`
  - Borough-level grouping used for dashboard, retrieval filtering, and review rollups.
- `host_name`
  - Host identifier surfaced in dashboard host comparisons.

## Review sentiment fields

- `sentiment_label`
  - Final label from sentiment scoring: `positive`, `neutral`, or `negative`.
- `compound`
  - Aggregate sentiment polarity score.
- `positive`, `neutral`, `negative`
  - Component sentiment probabilities used in review diagnostics and retrieval display.
- `comments`
  - Raw review text used for retrieval, reranking, and complaint theme analysis.

## Trust and evaluation notes

- SQL answers should be grounded in the listing performance fields above.
- RAG answers should be grounded in `comments` plus the sentiment fields.
- Hybrid answers should combine both forms of evidence and surface lower confidence if either side is weak.
