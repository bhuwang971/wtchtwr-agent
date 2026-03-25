from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import duckdb
import pandas as pd


def _safe_round(value: Any, digits: int = 2) -> float | None:
    try:
        if value is None:
            return None
        return round(float(value), digits)
    except Exception:
        return None


def _keyword_theme(text: str) -> str:
    lowered = (text or "").lower()
    theme_map = {
        "cleanliness": ["dirty", "clean", "unclean", "dust", "smell"],
        "noise": ["noise", "noisy", "loud", "street"],
        "temperature": ["cold", "hot", "heat", "ac"],
        "wifi": ["wifi", "internet", "connection"],
        "bathroom": ["bathroom", "shower", "toilet"],
        "check_in": ["check in", "check-in", "access", "lock", "key"],
    }
    for theme, keywords in theme_map.items():
        if any(keyword in lowered for keyword in keywords):
            return theme
    return "general"


def build_business_kpi_snapshot(repo_root: Path) -> Dict[str, Any]:
    db_path = repo_root / "db" / "airbnb.duckdb"
    reviews_path = repo_root / "data" / "clean" / "review_sentiment_scores.parquet"

    with duckdb.connect(str(db_path), read_only=True) as con:
        portfolio = con.execute(
            """
            with portfolio_stats as (
                select
                    count(*) as listings,
                    median(occupancy_rate_90) as median_occ90,
                    avg(price_in_usd) as avg_price,
                    avg(estimated_revenue_30) as avg_revenue_30,
                    avg(review_scores_rating) as avg_rating
                from highbury_listings
            ),
            underperformers as (
                select count(*) as underperforming_count
                from highbury_listings, portfolio_stats
                where occupancy_rate_90 < portfolio_stats.median_occ90 - 10
            )
            select *
            from portfolio_stats, underperformers
            """
        ).fetchdf().iloc[0].to_dict()

        pricing_opportunities = int(
            con.execute(
                """
                with market_benchmarks as (
                    select neighbourhood, median(price_in_usd) as market_median_price
                    from listings_cleaned
                    group by neighbourhood
                )
                select count(*)
                from highbury_listings h
                join market_benchmarks m on h.neighbourhood = m.neighbourhood
                where h.price_in_usd < m.market_median_price * 0.85
                """
            ).fetchone()[0]
        )

        expansion_candidates = con.execute(
            """
            with neighborhood_rollup as (
                select
                    neighbourhood,
                    neighbourhood_group,
                    count(*) as listings,
                    avg(occupancy_rate_90) as avg_occ90,
                    avg(price_in_usd) as avg_price,
                    avg(estimated_revenue_30) as avg_rev30,
                    avg(review_scores_rating) as avg_rating
                from listings_cleaned
                where neighbourhood is not null
                group by neighbourhood, neighbourhood_group
                having count(*) >= 15
            )
            select
                neighbourhood,
                neighbourhood_group,
                listings,
                avg_occ90,
                avg_price,
                avg_rev30,
                avg_rating
            from neighborhood_rollup
            order by avg_occ90 desc, avg_rating desc, avg_rev30 desc
            limit 5
            """
        ).fetchdf().to_dict(orient="records")

    sentiment = pd.read_parquet(reviews_path)
    negative_reviews = sentiment[sentiment["sentiment_label"].astype(str).str.lower() == "negative"].copy()
    negative_reviews["theme"] = negative_reviews["comments"].astype(str).map(_keyword_theme)
    complaint_rollup = (
        negative_reviews.groupby(["neighbourhood_group", "theme"])
        .size()
        .reset_index(name="count")
        .sort_values(["count", "neighbourhood_group"], ascending=[False, True])
    )

    complaint_themes: List[Dict[str, Any]] = []
    for borough in complaint_rollup["neighbourhood_group"].dropna().unique()[:5]:
        borough_df = complaint_rollup[complaint_rollup["neighbourhood_group"] == borough].head(3)
        complaint_themes.append(
            {
                "borough": str(borough),
                "themes": [
                    {"theme": str(row["theme"]), "count": int(row["count"])}
                    for _, row in borough_df.iterrows()
                ],
            }
        )

    return {
        "headline": {
            "portfolio_listings": int(portfolio.get("listings") or 0),
            "pricing_opportunities_found": pricing_opportunities,
            "underperforming_listings_flagged": int(portfolio.get("underperforming_count") or 0),
            "portfolio_avg_price": _safe_round(portfolio.get("avg_price")),
            "portfolio_avg_revenue_30": _safe_round(portfolio.get("avg_revenue_30")),
            "portfolio_avg_rating": _safe_round(portfolio.get("avg_rating")),
            "portfolio_median_occupancy_90": _safe_round(portfolio.get("median_occ90")),
        },
        "complaint_themes_by_borough": complaint_themes,
        "expansion_candidates": [
            {
                "neighbourhood": str(item.get("neighbourhood")),
                "borough": str(item.get("neighbourhood_group")),
                "listings": int(item.get("listings") or 0),
                "avg_occupancy_90": _safe_round(item.get("avg_occ90")),
                "avg_price": _safe_round(item.get("avg_price")),
                "avg_revenue_30": _safe_round(item.get("avg_rev30")),
                "avg_rating": _safe_round(item.get("avg_rating")),
            }
            for item in expansion_candidates
        ],
        "decision_support_examples": [
            {
                "persona": "Operations manager",
                "before": "I need to inspect spreadsheets to figure out which listings are falling behind.",
                "after": "Show me underperforming Highbury listings in Manhattan and tell me the likely review themes behind the drop.",
            },
            {
                "persona": "Revenue manager",
                "before": "I manually compare our ADR against neighborhood medians in SQL.",
                "after": "Where are our Midtown prices below market and how much revenue upside is available?",
            },
            {
                "persona": "Expansion lead",
                "before": "I stitch together market stats and external reports by hand.",
                "after": "Recommend NYC neighborhoods with strong occupancy, strong ratings, and room for Highbury expansion.",
            },
        ],
    }
