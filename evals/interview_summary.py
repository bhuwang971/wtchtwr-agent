from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional

from evals.runner import (
    AggregateBucket,
    AssertionResult,
    BenchmarkReport,
    BenchmarkSummary,
    CaseResult,
    LatencySummary,
)


def _rate(passed: int, total: int) -> float:
    return round((passed / total) * 100, 2) if total else 0.0


def _bucket_to_dict(bucket: AggregateBucket) -> Dict[str, Any]:
    return asdict(bucket)


def _category_bucket(results: list[CaseResult], category: str) -> AggregateBucket:
    matched = [result for result in results if result.category == category]
    total = len(matched)
    passed = sum(1 for result in matched if result.passed)
    failed = total - passed
    return AggregateBucket(total=total, passed=passed, failed=failed, pass_rate=_rate(passed, total))


def _top_bucket_items(buckets: Dict[str, AggregateBucket], *, reverse: bool) -> list[tuple[str, AggregateBucket]]:
    return sorted(
        buckets.items(),
        key=lambda item: (item[1].pass_rate, item[1].total, item[0]),
        reverse=reverse,
    )


def _token_metrics(report: BenchmarkReport) -> Dict[str, Any]:
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    cases_with_usage = 0
    for result in report.results:
        telemetry = result.result.get("telemetry") if isinstance(result.result, dict) else None
        usage = telemetry.get("llm_usage") if isinstance(telemetry, dict) and isinstance(telemetry.get("llm_usage"), dict) else {}
        prompt = int(usage.get("prompt_tokens") or 0)
        completion = int(usage.get("completion_tokens") or 0)
        total = int(usage.get("total_tokens") or (prompt + completion) or 0)
        if total:
            cases_with_usage += 1
        prompt_tokens += prompt
        completion_tokens += completion
        total_tokens += total

    input_rate = float(os.getenv("WTCHTWR_COST_INPUT_PER_1K") or 0.0)
    output_rate = float(os.getenv("WTCHTWR_COST_OUTPUT_PER_1K") or 0.0)
    estimated_cost = None
    if input_rate or output_rate:
        estimated_cost = round((prompt_tokens / 1000.0) * input_rate + (completion_tokens / 1000.0) * output_rate, 4)

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cases_with_usage": cases_with_usage,
        "estimated_cost_usd": estimated_cost,
    }


def build_interview_summary(
    report: BenchmarkReport,
    *,
    previous_report: Optional[BenchmarkReport] = None,
) -> Dict[str, Any]:
    summary = report.summary
    sql_bucket = _category_bucket(report.results, "sql")
    rag_bucket = _category_bucket(report.results, "rag")
    hybrid_bucket = _category_bucket(report.results, "hybrid")
    token_metrics = _token_metrics(report)

    strongest_categories = [
        {"name": name, **_bucket_to_dict(bucket)}
        for name, bucket in _top_bucket_items(summary.category_breakdown, reverse=True)[:3]
    ]
    weakest_categories = [
        {"name": name, **_bucket_to_dict(bucket)}
        for name, bucket in _top_bucket_items(summary.category_breakdown, reverse=False)[:3]
    ]

    failed_cases = [result for result in report.results if not result.passed]
    slowest_cases = sorted(
        [
            {
                "case_id": result.case_id,
                "category": result.category,
                "latency_s": float(result.result.get("latency") or 0.0),
                "policy": result.result.get("policy"),
            }
            for result in report.results
            if not result.error
        ],
        key=lambda item: item["latency_s"],
        reverse=True,
    )[:5]

    delta = None
    if previous_report is not None:
        delta = {
            "pass_rate_delta": round(report.pass_rate - previous_report.pass_rate, 2),
            "assertion_pass_rate_delta": round(
                summary.assertion_pass_rate - previous_report.summary.assertion_pass_rate,
                2,
            ),
            "p50_latency_delta_s": round(
                summary.latency.p50_s - previous_report.summary.latency.p50_s,
                4,
            ),
            "p95_latency_delta_s": round(
                summary.latency.p95_s - previous_report.summary.latency.p95_s,
                4,
            ),
        }

    return {
        "benchmark_file": report.benchmark_file,
        "generated_at": report.generated_at,
        "model_label": report.model_label,
        "openai_model": report.openai_model,
        "openai_fallback_model": report.openai_fallback_model,
        "nl2sql_model": report.nl2sql_model,
        "nl2sql_fallback_model": report.nl2sql_fallback_model,
        "headline_metrics": {
            "case_pass_rate": report.pass_rate,
            "case_passed": report.passed_cases,
            "case_total": report.total_cases,
            "assertion_pass_rate": summary.assertion_pass_rate,
            "assertion_passed": summary.assertion_passed,
            "assertion_total": summary.assertion_total,
        },
        "performance_metrics": {
            "avg_latency_s": summary.latency.avg_s,
            "p50_latency_s": summary.latency.p50_s,
            "p95_latency_s": summary.latency.p95_s,
            "max_latency_s": summary.latency.max_s,
        },
        "cost_metrics": token_metrics,
        "pipeline_metrics": {
            "overall_pass_rate": report.pass_rate,
            "overall_cases_passed": report.passed_cases,
            "overall_cases_total": report.total_cases,
            "sql_pass_rate": sql_bucket.pass_rate,
            "sql_cases_passed": sql_bucket.passed,
            "sql_cases_total": sql_bucket.total,
            "rag_pass_rate": rag_bucket.pass_rate,
            "rag_cases_passed": rag_bucket.passed,
            "rag_cases_total": rag_bucket.total,
            "hybrid_pass_rate": hybrid_bucket.pass_rate,
            "hybrid_cases_passed": hybrid_bucket.passed,
            "hybrid_cases_total": hybrid_bucket.total,
        },
        "strongest_categories": strongest_categories,
        "weakest_categories": weakest_categories,
        "failed_case_count": len(failed_cases),
        "failed_case_ids": [result.case_id for result in failed_cases[:10]],
        "slowest_cases": slowest_cases,
        "policy_breakdown": {name: _bucket_to_dict(bucket) for name, bucket in summary.policy_breakdown.items()},
        "intent_breakdown": {name: _bucket_to_dict(bucket) for name, bucket in summary.intent_breakdown.items()},
        "delta_vs_previous": delta,
        "interview_talking_points": [
            f"Overall benchmark pass rate is {report.pass_rate}% across {report.total_cases} curated product questions.",
            f"Assertion-level accuracy is {summary.assertion_pass_rate}%, which gives a more granular view than whole-case pass/fail.",
            f"Median latency is {summary.latency.p50_s}s, while p95 latency is {summary.latency.p95_s}s, so long-tail cases are visible and measurable.",
            f"SQL flows are the most stable at {sql_bucket.pass_rate}% pass rate, while weaker categories identify where the roadmap still is.",
            f"Observed token volume is {token_metrics['total_tokens']} total tokens across the run; set WTCHTWR_COST_INPUT_PER_1K and WTCHTWR_COST_OUTPUT_PER_1K to turn this into an estimated dollar cost.",
        ],
    }


def summary_to_json(summary: Dict[str, Any]) -> str:
    return json.dumps(summary, indent=2)


def summary_to_markdown(summary: Dict[str, Any]) -> str:
    headline = summary["headline_metrics"]
    perf = summary["performance_metrics"]
    cost = summary.get("cost_metrics") or {}
    pipeline = summary["pipeline_metrics"]

    lines = [
        "# wtchtwr Interview Metrics",
        "",
        f"- Benchmark file: `{summary['benchmark_file']}`",
        f"- Generated at: `{summary['generated_at']}`",
        f"- Model label: `{summary.get('model_label') or 'default'}`",
        f"- Main model: `{summary.get('openai_model') or 'env/default'}`",
        f"- Main fallback: `{summary.get('openai_fallback_model') or 'env/default'}`",
        f"- NL2SQL model: `{summary.get('nl2sql_model') or 'env/default'}`",
        f"- NL2SQL fallback: `{summary.get('nl2sql_fallback_model') or 'env/default'}`",
        "",
        "## Headline Metrics",
        "",
        f"- Case pass rate: `{headline['case_pass_rate']}%` ({headline['case_passed']}/{headline['case_total']})",
        f"- Assertion pass rate: `{headline['assertion_pass_rate']}%` ({headline['assertion_passed']}/{headline['assertion_total']})",
        "",
        "## Performance Metrics",
        "",
        f"- Average latency: `{perf['avg_latency_s']}s`",
        f"- P50 latency: `{perf['p50_latency_s']}s`",
        f"- P95 latency: `{perf['p95_latency_s']}s`",
        f"- Max latency: `{perf['max_latency_s']}s`",
        "",
        "## Cost Metrics",
        "",
        f"- Prompt tokens: `{cost.get('prompt_tokens', 0)}`",
        f"- Completion tokens: `{cost.get('completion_tokens', 0)}`",
        f"- Total tokens: `{cost.get('total_tokens', 0)}`",
        f"- Estimated cost: `{cost.get('estimated_cost_usd', 'n/a')}`",
        "",
        "## Pipeline Breakdown",
        "",
        f"- Overall pass rate: `{pipeline['overall_pass_rate']}%` ({pipeline['overall_cases_passed']}/{pipeline['overall_cases_total']})",
        f"- SQL pass rate: `{pipeline['sql_pass_rate']}%` ({pipeline['sql_cases_passed']}/{pipeline['sql_cases_total']})",
        f"- RAG pass rate: `{pipeline['rag_pass_rate']}%` ({pipeline['rag_cases_passed']}/{pipeline['rag_cases_total']})",
        f"- Hybrid pass rate: `{pipeline['hybrid_pass_rate']}%` ({pipeline['hybrid_cases_passed']}/{pipeline['hybrid_cases_total']})",
        "",
        "## Strongest Categories",
        "",
    ]

    for item in summary["strongest_categories"]:
        lines.append(f"- `{item['name']}`: `{item['pass_rate']}%` ({item['passed']}/{item['total']})")

    lines.extend(["", "## Weakest Categories", ""])
    for item in summary["weakest_categories"]:
        lines.append(f"- `{item['name']}`: `{item['pass_rate']}%` ({item['passed']}/{item['total']})")

    if summary.get("delta_vs_previous"):
        delta = summary["delta_vs_previous"]
        lines.extend(
            [
                "",
                "## Trend Vs Previous Run",
                "",
                f"- Case pass rate delta: `{delta['pass_rate_delta']} pts`",
                f"- Assertion pass rate delta: `{delta['assertion_pass_rate_delta']} pts`",
                f"- P50 latency delta: `{delta['p50_latency_delta_s']}s`",
                f"- P95 latency delta: `{delta['p95_latency_delta_s']}s`",
            ]
        )

    lines.extend(["", "## Slowest Cases", ""])
    for item in summary["slowest_cases"]:
        lines.append(
            f"- `{item['case_id']}` ({item['category']}, {item['policy']}): `{item['latency_s']}s`"
        )

    lines.extend(["", "## Interview Talking Points", ""])
    for point in summary["interview_talking_points"]:
        lines.append(f"- {point}")

    return "\n".join(lines).strip() + "\n"


def load_report(path: Path) -> BenchmarkReport:
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary_payload = payload["summary"]
    return BenchmarkReport(
        benchmark_file=payload["benchmark_file"],
        generated_at=payload["generated_at"],
        model_label=payload.get("model_label") or "default",
        openai_model=payload.get("openai_model"),
        openai_fallback_model=payload.get("openai_fallback_model"),
        nl2sql_model=payload.get("nl2sql_model"),
        nl2sql_fallback_model=payload.get("nl2sql_fallback_model"),
        total_cases=payload["total_cases"],
        passed_cases=payload["passed_cases"],
        failed_cases=payload["failed_cases"],
        pass_rate=payload["pass_rate"],
        summary=BenchmarkSummary(
            assertion_total=summary_payload["assertion_total"],
            assertion_passed=summary_payload["assertion_passed"],
            assertion_failed=summary_payload["assertion_failed"],
            assertion_pass_rate=summary_payload["assertion_pass_rate"],
            category_breakdown={
                name: AggregateBucket(**bucket) for name, bucket in summary_payload["category_breakdown"].items()
            },
            intent_breakdown={
                name: AggregateBucket(**bucket) for name, bucket in summary_payload["intent_breakdown"].items()
            },
            policy_breakdown={
                name: AggregateBucket(**bucket) for name, bucket in summary_payload["policy_breakdown"].items()
            },
            latency=LatencySummary(**summary_payload["latency"]),
            sql_cases=summary_payload["sql_cases"],
            sql_cases_passed=summary_payload["sql_cases_passed"],
            rag_cases=summary_payload["rag_cases"],
            rag_cases_passed=summary_payload["rag_cases_passed"],
            hybrid_cases=summary_payload["hybrid_cases"],
            hybrid_cases_passed=summary_payload["hybrid_cases_passed"],
        ),
        results=[
            CaseResult(
                case_id=item["case_id"],
                query=item["query"],
                category=item["category"],
                passed=item["passed"],
                tags=item.get("tags") or [],
                assertions=[AssertionResult(**assertion) for assertion in item.get("assertions") or []],
                result=item.get("result") or {},
                error=item.get("error"),
            )
            for item in payload["results"]
        ],
    )
