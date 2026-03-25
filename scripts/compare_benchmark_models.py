#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evals.runner import ModelConfig, run_benchmarks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare benchmark results across multiple model configurations.")
    parser.add_argument("--benchmark-file", default="evals/benchmarks.local.json", help="Path to the benchmark JSON file.")
    parser.add_argument("--output-dir", default="evals/reports", help="Directory for generated comparison reports.")
    parser.add_argument("--case-id", action="append", dest="case_ids", help="Optional benchmark case id to run. Repeat for multiple.")
    parser.add_argument(
        "--model",
        action="append",
        required=True,
        help="Model config in the form label:main_model[:nl2sql_model[:main_fallback[:nl2sql_fallback]]]",
    )
    return parser.parse_args()


def _parse_model(value: str) -> ModelConfig:
    parts = [part.strip() for part in value.split(":")]
    if len(parts) < 2:
        raise ValueError(f"Invalid --model value '{value}'. Expected label:main_model[:nl2sql_model[:main_fallback[:nl2sql_fallback]]]")
    label = parts[0]
    openai_model = parts[1] or None
    nl2sql_model = parts[2] if len(parts) > 2 and parts[2] else None
    openai_fallback_model = parts[3] if len(parts) > 3 and parts[3] else None
    nl2sql_fallback_model = parts[4] if len(parts) > 4 and parts[4] else None
    return ModelConfig(
        label=label,
        openai_model=openai_model,
        openai_fallback_model=openai_fallback_model,
        nl2sql_model=nl2sql_model,
        nl2sql_fallback_model=nl2sql_fallback_model,
    )


def _comparison_payload(reports: list[dict[str, Any]]) -> dict[str, Any]:
    winner = max(reports, key=lambda item: (item["pass_rate"], item["assertion_pass_rate"], -item["p50_latency_s"]))
    fastest = min(reports, key=lambda item: (item["p50_latency_s"], item["p95_latency_s"], -item["pass_rate"]))
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "models": reports,
        "winner_by_accuracy": winner["model_label"],
        "winner_by_speed": fastest["model_label"],
    }


def _comparison_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# wtchtwr Model Comparison",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Accuracy winner: `{payload['winner_by_accuracy']}`",
        f"- Speed winner: `{payload['winner_by_speed']}`",
        "",
        "| Label | Main Model | NL2SQL Model | Overall | SQL | RAG | Hybrid | Assertion | P50 (s) | P95 (s) |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in payload["models"]:
        lines.append(
            f"| {item['model_label']} | {item['openai_model'] or 'env/default'} | {item['nl2sql_model'] or 'env/default'} "
            f"| {item['pass_rate']}% | {item['sql_pass_rate']}% | {item['rag_pass_rate']}% | {item['hybrid_pass_rate']}% "
            f"| {item['assertion_pass_rate']}% | {item['p50_latency_s']} | {item['p95_latency_s']} |"
        )
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    args = parse_args()
    benchmark_file = Path(args.benchmark_file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    models = [_parse_model(item) for item in args.model]
    model_rows: list[dict[str, Any]] = []
    exit_code = 0

    for model in models:
        report = run_benchmarks(benchmark_file, case_ids=args.case_ids, model_config=model)
        if report.failed_cases > 0:
            exit_code = 1
        model_rows.append(
            {
                "model_label": report.model_label,
                "openai_model": report.openai_model,
                "openai_fallback_model": report.openai_fallback_model,
                "nl2sql_model": report.nl2sql_model,
                "nl2sql_fallback_model": report.nl2sql_fallback_model,
                "pass_rate": report.pass_rate,
                "assertion_pass_rate": report.summary.assertion_pass_rate,
                "sql_pass_rate": round((report.summary.sql_cases_passed / report.summary.sql_cases) * 100, 2) if report.summary.sql_cases else 0.0,
                "rag_pass_rate": round((report.summary.rag_cases_passed / report.summary.rag_cases) * 100, 2) if report.summary.rag_cases else 0.0,
                "hybrid_pass_rate": round((report.summary.hybrid_cases_passed / report.summary.hybrid_cases) * 100, 2) if report.summary.hybrid_cases else 0.0,
                "p50_latency_s": report.summary.latency.p50_s,
                "p95_latency_s": report.summary.latency.p95_s,
            }
        )

    payload = _comparison_payload(model_rows)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = output_dir / f"model-comparison-{timestamp}.json"
    md_path = output_dir / f"model-comparison-{timestamp}.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(_comparison_markdown(payload), encoding="utf-8")

    print(f"Comparison JSON: {json_path}")
    print(f"Comparison Markdown: {md_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
