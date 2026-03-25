from evals.interview_summary import build_interview_summary, summary_to_markdown
from evals.runner import (
    AggregateBucket,
    BenchmarkReport,
    BenchmarkSummary,
    CaseResult,
    LatencySummary,
)


def _report(*, pass_rate: float, p50: float, p95: float) -> BenchmarkReport:
    return BenchmarkReport(
        benchmark_file="evals/benchmarks.local.json",
        generated_at="2026-03-19T00:00:00+00:00",
        model_label="test-model",
        openai_model="gpt-5.1",
        openai_fallback_model="gpt-4o",
        nl2sql_model="gpt-4o-mini",
        nl2sql_fallback_model="gpt-4o",
        total_cases=10,
        passed_cases=6,
        failed_cases=4,
        pass_rate=pass_rate,
        summary=BenchmarkSummary(
            assertion_total=20,
            assertion_passed=16,
            assertion_failed=4,
            assertion_pass_rate=80.0,
            category_breakdown={
                "sql": AggregateBucket(total=4, passed=4, failed=0, pass_rate=100.0),
                "rag": AggregateBucket(total=3, passed=1, failed=2, pass_rate=33.33),
                "expansion": AggregateBucket(total=3, passed=1, failed=2, pass_rate=33.33),
            },
            intent_breakdown={
                "FACT_SQL": AggregateBucket(total=4, passed=4, failed=0, pass_rate=100.0),
            },
            policy_breakdown={
                "SQL_MARKET": AggregateBucket(total=4, passed=4, failed=0, pass_rate=100.0),
            },
            latency=LatencySummary(count=10, avg_s=3.2, p50_s=p50, p95_s=p95, max_s=8.1),
            sql_cases=4,
            sql_cases_passed=4,
            rag_cases=3,
            rag_cases_passed=1,
            hybrid_cases=1,
            hybrid_cases_passed=0,
        ),
        results=[
            CaseResult(
                case_id="sql-fast",
                query="What is the average nightly rate in Queens?",
                category="sql",
                passed=True,
                tags=["sql"],
                result={"latency": 1.2, "policy": "SQL_MARKET"},
            ),
            CaseResult(
                case_id="rag-slow",
                query="What complaints do guests mention in Brooklyn?",
                category="rag",
                passed=False,
                tags=["rag"],
                result={"latency": 5.8, "policy": "RAG_MARKET"},
            ),
        ],
    )


def test_build_interview_summary_includes_pipeline_metrics_and_delta() -> None:
    current = _report(pass_rate=60.0, p50=2.1, p95=5.9)
    previous = _report(pass_rate=50.0, p50=2.5, p95=6.5)

    summary = build_interview_summary(current, previous_report=previous)

    assert summary["headline_metrics"]["case_pass_rate"] == 60.0
    assert summary["pipeline_metrics"]["overall_pass_rate"] == 60.0
    assert summary["pipeline_metrics"]["sql_pass_rate"] == 100.0
    assert summary["pipeline_metrics"]["rag_pass_rate"] == 0.0
    assert summary["pipeline_metrics"]["hybrid_pass_rate"] == 0.0
    assert summary["delta_vs_previous"]["pass_rate_delta"] == 10.0
    assert summary["slowest_cases"][0]["case_id"] == "rag-slow"


def test_summary_markdown_contains_interview_sections() -> None:
    summary = build_interview_summary(_report(pass_rate=60.0, p50=2.1, p95=5.9))
    markdown = summary_to_markdown(summary)

    assert "## Headline Metrics" in markdown
    assert "## Pipeline Breakdown" in markdown
    assert "## Interview Talking Points" in markdown
    assert "Overall pass rate" in markdown
