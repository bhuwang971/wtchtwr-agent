from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.data_trust import build_data_quality_snapshot, default_paths


def to_markdown(snapshot: dict) -> str:
    summary = snapshot.get("summary") or {}
    checks = snapshot.get("checks") or {}
    issues = snapshot.get("issues") or []
    lines = [
        "# wtchtwr Data Quality Report",
        "",
        f"- Status: `{snapshot.get('status', 'unknown')}`",
        f"- Highbury listings: `{summary.get('highbury_listing_count', 'n/a')}`",
        f"- Market listings: `{summary.get('market_listing_count', 'n/a')}`",
        f"- Review rows: `{summary.get('review_row_count', 'n/a')}`",
        f"- Schema contracts ok: `{summary.get('contract_ok', False)}`",
        "",
        "## Key Checks",
        "",
        f"- Duplicate listing IDs: `{checks.get('duplicate_listing_ids')}`",
        f"- Invalid coordinates: `{checks.get('invalid_coordinates')}`",
        f"- Impossible prices: `{checks.get('impossible_prices')}`",
        f"- Inconsistent borough labels: `{checks.get('inconsistent_borough_labels')}`",
        f"- Listing null rates: `{checks.get('listing_null_rates')}`",
        f"- Review null rates: `{checks.get('review_null_rates')}`",
        f"- Duplicate reviews: `{checks.get('duplicate_reviews')}`",
        "",
        "## Open Issues",
        "",
    ]
    if issues:
        lines.extend([f"- {issue}" for issue in issues])
    else:
        lines.append("- No blocking data quality issues detected in the current snapshot.")
    return "\n".join(lines) + "\n"


def main() -> None:
    repo_root = REPO_ROOT
    report_dir = repo_root / "docs" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    snapshot = build_data_quality_snapshot(default_paths(repo_root))
    (report_dir / "data-quality-latest.json").write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    (report_dir / "data-quality-latest.md").write_text(to_markdown(snapshot), encoding="utf-8")
    print("Wrote data quality report to docs/reports/data-quality-latest.{json,md}")


if __name__ == "__main__":
    main()
