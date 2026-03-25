# Data Lineage

This project uses a simple but explicit lineage from raw review/listing assets to the assistant, dashboard, and evaluation surfaces.

## Lineage flow

1. Raw or provided source files
   - Listing snapshots
   - Review exports
   - Review sentiment parquet assets
2. Cleaned parquet artifacts in `data/clean/`
   - `listings_cleaned.parquet`
   - `highbury_listings.parquet`
   - `reviews_enriched.parquet`
   - `review_sentiment_scores.parquet`
3. DuckDB analytics layer in `db/airbnb.duckdb`
   - `listings_cleaned`
   - `highbury_listings`
4. Vector layer in `vec/airbnb_reviews/` and Qdrant
   - `reviews_embeddings.npy`
   - `reviews_metadata.parquet`
   - Qdrant collection used for review retrieval
5. Product surfaces
   - chat assistant
   - dashboard
   - data explorer
   - AI metrics / benchmark dashboard

## How each surface uses the data

- Dashboard
  - reads structured listing metrics from DuckDB
- SQL and hybrid chat
  - reads listing metrics from DuckDB
- Review and hybrid chat
  - retrieves review evidence from Qdrant using the review metadata and embeddings
- KPI and business pages
  - use DuckDB and review sentiment parquet data
- Benchmark and eval reports
  - validate whether outputs stay grounded on the same underlying data

## Why this matters

The point of documenting lineage is to make one thing clear in interviews:

- model quality depends on data quality
- RAG quality depends on retrieval metadata quality
- dashboard trust depends on clean and consistent numeric fields
- agentic quality is only as good as the structured and unstructured sources it routes into
