#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evals.interview_summary import build_interview_summary, load_report, summary_to_json, summary_to_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an interview-ready summary from benchmark reports.")
    parser.add_argument(
        "--report-file",
        help="Path to a benchmark JSON report. Defaults to the latest report in evals/reports.",
    )
    parser.add_argument(
        "--reports-dir",
        default="evals/reports",
        help="Directory containing benchmark report JSON files.",
    )
    parser.add_argument(
        "--output-prefix",
        default="interview-metrics",
        help="Filename prefix for generated summary artifacts.",
    )
    return parser.parse_args()


def _latest_json_reports(reports_dir: Path) -> list[Path]:
    return sorted(reports_dir.glob("benchmark-report-*.json"), key=lambda path: path.stat().st_mtime, reverse=True)


def main() -> int:
    args = parse_args()
    reports_dir = Path(args.reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    if args.report_file:
        report_path = Path(args.report_file)
        previous_path = None
    else:
        candidates = _latest_json_reports(reports_dir)
        if not candidates:
            raise SystemExit("No benchmark report JSON files found. Run scripts/run_benchmarks.py first.")
        report_path = candidates[0]
        previous_path = candidates[1] if len(candidates) > 1 else None

    report = load_report(report_path)
    previous_report = load_report(previous_path) if previous_path else None
    summary = build_interview_summary(report, previous_report=previous_report)

    json_path = reports_dir / f"{args.output_prefix}.json"
    md_path = reports_dir / f"{args.output_prefix}.md"
    json_path.write_text(summary_to_json(summary), encoding="utf-8")
    md_path.write_text(summary_to_markdown(summary), encoding="utf-8")

    print(f"Source report: {report_path}")
    if previous_path:
        print(f"Previous report: {previous_path}")
    print(f"Interview JSON: {json_path}")
    print(f"Interview Markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
