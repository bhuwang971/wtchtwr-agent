#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evals.interview_summary import build_interview_summary, load_report, summary_to_json, summary_to_markdown
from evals.runner import ModelConfig, report_to_json, report_to_markdown, run_benchmarks


def _pack_slug(path: Path) -> str:
    stem = path.stem.lower()
    stem = re.sub(r"^benchmarks[._-]?", "", stem)
    slug = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return slug or "default"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run wtchtwr benchmark cases and write a report.")
    parser.add_argument(
        "--benchmark-file",
        default="evals/benchmarks.sample.json",
        help="Path to the benchmark JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        default="evals/reports",
        help="Directory for generated reports.",
    )
    parser.add_argument(
        "--case-id",
        action="append",
        dest="case_ids",
        help="Optional benchmark case id to run. Repeat to run multiple specific cases.",
    )
    parser.add_argument("--label", default="default", help="Optional label for this model run.")
    parser.add_argument("--model", help="Override main agent model for this benchmark run.")
    parser.add_argument("--fallback-model", help="Override main fallback model for this benchmark run.")
    parser.add_argument("--nl2sql-model", help="Override NL2SQL model for this benchmark run.")
    parser.add_argument("--nl2sql-fallback-model", help="Override NL2SQL fallback model for this benchmark run.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    benchmark_file = Path(args.benchmark_file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    pack_slug = _pack_slug(benchmark_file)

    model_config = None
    if any([args.model, args.fallback_model, args.nl2sql_model, args.nl2sql_fallback_model]):
        model_config = ModelConfig(
            label=args.label,
            openai_model=args.model,
            openai_fallback_model=args.fallback_model,
            nl2sql_model=args.nl2sql_model,
            nl2sql_fallback_model=args.nl2sql_fallback_model,
        )

    try:
        report = run_benchmarks(benchmark_file, case_ids=args.case_ids, model_config=model_config)
    except RuntimeError as exc:
        print(f"Benchmark preflight failed: {exc}")
        return 2
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = output_dir / f"benchmark-report-{timestamp}.json"
    md_path = output_dir / f"benchmark-report-{timestamp}.md"

    json_path.write_text(report_to_json(report), encoding="utf-8")
    md_path.write_text(report_to_markdown(report), encoding="utf-8")

    previous_reports = []
    for path in output_dir.glob("benchmark-report-*.json"):
        if path == json_path:
            continue
        try:
            candidate = load_report(path)
        except Exception:
            continue
        if str(candidate.benchmark_file) == str(benchmark_file):
            previous_reports.append(path)
    previous_reports = sorted(previous_reports, key=lambda path: path.stat().st_mtime, reverse=True)
    previous_report = None
    if previous_reports:
        previous_report = load_report(previous_reports[0])

    interview_summary = build_interview_summary(report, previous_report=previous_report)
    interview_json_path = output_dir / "interview-metrics-latest.json"
    interview_md_path = output_dir / "interview-metrics-latest.md"
    interview_pack_json_path = output_dir / f"interview-metrics-{pack_slug}-latest.json"
    interview_pack_md_path = output_dir / f"interview-metrics-{pack_slug}-latest.md"
    interview_json_path.write_text(summary_to_json(interview_summary), encoding="utf-8")
    interview_md_path.write_text(summary_to_markdown(interview_summary), encoding="utf-8")
    interview_pack_json_path.write_text(summary_to_json(interview_summary), encoding="utf-8")
    interview_pack_md_path.write_text(summary_to_markdown(interview_summary), encoding="utf-8")

    print(f"Benchmark file: {benchmark_file}")
    print(f"Model label: {report.model_label}")
    print(f"Cases: {report.total_cases}")
    print(f"Passed: {report.passed_cases}")
    print(f"Failed: {report.failed_cases}")
    print(f"Pass rate: {report.pass_rate}%")
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {md_path}")
    print(f"Interview JSON: {interview_json_path}")
    print(f"Interview Markdown: {interview_md_path}")
    print(f"Pack Interview JSON: {interview_pack_json_path}")
    print(f"Pack Interview Markdown: {interview_pack_md_path}")
    return 0 if report.failed_cases == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
