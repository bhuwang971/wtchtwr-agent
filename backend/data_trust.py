from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import duckdb
import pandas as pd


REQUIRED_DUCKDB_SCHEMAS: Dict[str, List[str]] = {
    "highbury_listings": [
        "listings_id",
        "host_id",
        "host_name",
        "neighbourhood",
        "neighbourhood_group",
        "latitude",
        "longitude",
        "property_type",
        "room_type",
        "accommodates",
        "bathrooms",
        "bedrooms",
        "beds",
        "price_in_usd",
        "review_scores_rating",
        "occupancy_rate_90",
        "estimated_revenue_30",
    ],
    "listings_cleaned": [
        "listings_id",
        "host_id",
        "host_name",
        "neighbourhood",
        "neighbourhood_group",
        "latitude",
        "longitude",
        "property_type",
        "room_type",
        "price_in_usd",
        "review_scores_rating",
        "occupancy_rate_90",
        "estimated_revenue_30",
    ],
}

REQUIRED_PARQUET_SCHEMAS: Dict[str, List[str]] = {
    "review_sentiment_scores.parquet": [
        "listing_id",
        "comment_id",
        "comments",
        "year",
        "month",
        "neighbourhood",
        "neighbourhood_group",
        "is_highbury",
        "negative",
        "neutral",
        "positive",
        "compound",
        "sentiment_label",
    ],
    "reviews_enriched.parquet": [
        "listing_id",
        "comment_id",
        "comments",
        "year",
        "month",
        "neighbourhood",
        "neighbourhood_group",
        "is_highbury",
    ],
}

EXPECTED_BOROUGHS = {"Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"}


@dataclass
class DataTrustPaths:
    repo_root: Path
    db_path: Path
    clean_dir: Path


def default_paths(repo_root: Path) -> DataTrustPaths:
    return DataTrustPaths(
        repo_root=repo_root,
        db_path=repo_root / "db" / "airbnb.duckdb",
        clean_dir=repo_root / "data" / "clean",
    )


def _duckdb_schema(con: duckdb.DuckDBPyConnection, table: str) -> List[str]:
    rows = con.execute(f"describe {table}").fetchall()
    return [str(row[0]) for row in rows]


def validate_data_contracts(paths: DataTrustPaths) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    all_ok = True

    with duckdb.connect(str(paths.db_path), read_only=True) as con:
        for table, required_columns in REQUIRED_DUCKDB_SCHEMAS.items():
            actual_columns = _duckdb_schema(con, table)
            missing = [column for column in required_columns if column not in actual_columns]
            ok = not missing
            all_ok = all_ok and ok
            checks.append(
                {
                    "type": "duckdb_table",
                    "name": table,
                    "ok": ok,
                    "missing_columns": missing,
                    "column_count": len(actual_columns),
                }
            )

    for filename, required_columns in REQUIRED_PARQUET_SCHEMAS.items():
        frame = pd.read_parquet(paths.clean_dir / filename)
        actual_columns = [str(column) for column in frame.columns]
        missing = [column for column in required_columns if column not in actual_columns]
        ok = not missing
        all_ok = all_ok and ok
        checks.append(
            {
                "type": "parquet_file",
                "name": filename,
                "ok": ok,
                "missing_columns": missing,
                "column_count": len(actual_columns),
            }
        )

    return {"ok": all_ok, "checks": checks}


def build_data_quality_snapshot(paths: DataTrustPaths) -> Dict[str, Any]:
    contract_report = validate_data_contracts(paths)
    with duckdb.connect(str(paths.db_path), read_only=True) as con:
        highbury_count = int(con.execute("select count(*) from highbury_listings").fetchone()[0])
        market_count = int(con.execute("select count(*) from listings_cleaned").fetchone()[0])
        duplicate_highbury = int(
            con.execute(
                """
                select count(*) from (
                    select listings_id
                    from highbury_listings
                    group by listings_id
                    having count(*) > 1
                )
                """
            ).fetchone()[0]
        )
        duplicate_market = int(
            con.execute(
                """
                select count(*) from (
                    select listings_id
                    from listings_cleaned
                    group by listings_id
                    having count(*) > 1
                )
                """
            ).fetchone()[0]
        )
        invalid_highbury_coords = int(
            con.execute(
                """
                select count(*)
                from highbury_listings
                where latitude is null
                   or longitude is null
                   or latitude not between -90 and 90
                   or longitude not between -180 and 180
                """
            ).fetchone()[0]
        )
        invalid_market_coords = int(
            con.execute(
                """
                select count(*)
                from listings_cleaned
                where latitude is null
                   or longitude is null
                   or latitude not between -90 and 90
                   or longitude not between -180 and 180
                """
            ).fetchone()[0]
        )
        impossible_highbury_prices = int(
            con.execute(
                "select count(*) from highbury_listings where price_in_usd is null or price_in_usd <= 0 or price_in_usd > 10000"
            ).fetchone()[0]
        )
        impossible_market_prices = int(
            con.execute(
                "select count(*) from listings_cleaned where price_in_usd is null or price_in_usd <= 0 or price_in_usd > 10000"
            ).fetchone()[0]
        )
        boroughs = [
            str(row[0])
            for row in con.execute(
                """
                select distinct neighbourhood_group
                from (
                    select neighbourhood_group from highbury_listings
                    union all
                    select neighbourhood_group from listings_cleaned
                )
                where neighbourhood_group is not null
                """
            ).fetchall()
        ]
        inconsistent_boroughs = sorted(value for value in boroughs if value not in EXPECTED_BOROUGHS)
        null_rates = con.execute(
            """
            select
                avg(case when price_in_usd is null then 1 else 0 end) as price_null_rate,
                avg(case when occupancy_rate_90 is null then 1 else 0 end) as occupancy_null_rate,
                avg(case when estimated_revenue_30 is null then 1 else 0 end) as revenue_null_rate,
                avg(case when review_scores_rating is null then 1 else 0 end) as rating_null_rate
            from highbury_listings
            """
        ).fetchdf().iloc[0].to_dict()

    sentiment = pd.read_parquet(paths.clean_dir / "review_sentiment_scores.parquet")
    review_null_rates = {
        "comments_null_rate": round(float(sentiment["comments"].isna().mean()), 4),
        "sentiment_label_null_rate": round(float(sentiment["sentiment_label"].isna().mean()), 4),
        "compound_null_rate": round(float(sentiment["compound"].isna().mean()), 4),
    }
    review_duplicates = int(sentiment.duplicated(subset=["listing_id", "comment_id"]).sum())

    issues: List[str] = []
    if duplicate_highbury or duplicate_market:
        issues.append("Duplicate listing IDs detected in DuckDB tables.")
    if invalid_highbury_coords or invalid_market_coords:
        issues.append("Invalid or missing coordinates found in listing tables.")
    if impossible_highbury_prices or impossible_market_prices:
        issues.append("Impossible or missing prices found in listing tables.")
    if inconsistent_boroughs:
        issues.append("Unexpected borough labels found in listing tables.")
    if review_duplicates:
        issues.append("Duplicate review IDs detected in sentiment parquet.")

    return {
        "status": "ok" if contract_report["ok"] and not issues else "attention",
        "summary": {
            "highbury_listing_count": highbury_count,
            "market_listing_count": market_count,
            "review_row_count": int(len(sentiment)),
            "contract_ok": contract_report["ok"],
        },
        "contracts": contract_report,
        "checks": {
            "duplicate_listing_ids": {
                "highbury": duplicate_highbury,
                "market": duplicate_market,
            },
            "invalid_coordinates": {
                "highbury": invalid_highbury_coords,
                "market": invalid_market_coords,
            },
            "impossible_prices": {
                "highbury": impossible_highbury_prices,
                "market": impossible_market_prices,
            },
            "inconsistent_borough_labels": inconsistent_boroughs,
            "listing_null_rates": {key: round(float(value), 4) for key, value in null_rates.items()},
            "review_null_rates": review_null_rates,
            "duplicate_reviews": review_duplicates,
        },
        "issues": issues,
    }
