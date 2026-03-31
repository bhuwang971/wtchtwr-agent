import json

from backend.ai_observability import build_confidence_payload, build_trace_payload, load_ai_metrics_payload


def test_build_confidence_payload_marks_hybrid_degraded_when_rag_fails() -> None:
    result = {
        "response_type": "hybrid",
        "sql": {"text": "select * from highbury_listings"},
    }
    bundle = {
        "sql": "select * from highbury_listings",
        "rows": [{"listing_id": 1}],
        "rag_snippets": [],
    }
    state_snapshot = {"rag": {"weak_evidence": True, "confidence": "weak"}}
    telemetry = {"rag_error": "connection refused"}

    confidence = build_confidence_payload(
        result=result,
        bundle=bundle,
        state_snapshot=state_snapshot,
        telemetry=telemetry,
    )

    assert confidence["degraded"] is True
    assert confidence["overall"]["band"] == "low"
    assert confidence["sql"]["band"] == "high"
    assert confidence["rag"]["band"] == "low"


def test_build_trace_payload_captures_filters_and_tokens() -> None:
    result = {"intent": "SENTIMENT_REVIEWS", "scope": "General", "policy": "RAG_ONLY"}
    bundle = {"policy": "RAG_ONLY", "rows": [], "rag_snippets": [{"listing_id": "1"}]}
    state_snapshot = {
        "filters": {"borough": ["Brooklyn"], "sentiment_label": "negative"},
        "rag": {"weak_evidence": False, "confidence": "negative", "summary": "Top review evidence from Brooklyn."},
    }
    telemetry = {"latency_ms": 1234, "llm_usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}
    confidence = {"degraded": False, "degraded_reasons": []}

    trace = build_trace_payload(
        result=result,
        bundle=bundle,
        state_snapshot=state_snapshot,
        telemetry=telemetry,
        confidence=confidence,
    )

    assert trace["intent"] == "SENTIMENT_REVIEWS"
    assert trace["filters"]["borough"] == ["Brooklyn"]
    assert trace["retrieval"]["hit_count"] == 1
    assert trace["performance"]["tokens"]["total_tokens"] == 15


def test_load_ai_metrics_payload_includes_case_details(tmp_path, monkeypatch) -> None:
    reports_dir = tmp_path / "evals" / "reports"
    reports_dir.mkdir(parents=True)

    report_payload = {
        "benchmark_file": "evals\\benchmarks.adversarial.json",
        "generated_at": "2026-03-31T12:55:36+00:00",
        "model_label": "default",
        "total_cases": 1,
        "passed_cases": 1,
        "failed_cases": 0,
        "pass_rate": 100.0,
        "summary": {
            "assertion_total": 1,
            "assertion_passed": 1,
            "assertion_failed": 0,
            "assertion_pass_rate": 100.0,
            "category_breakdown": {"sql": {"total": 1, "passed": 1, "failed": 0, "pass_rate": 100.0}},
            "intent_breakdown": {"FACT_SQL": {"total": 1, "passed": 1, "failed": 0, "pass_rate": 100.0}},
            "policy_breakdown": {"SQL_HIGHBURY": {"total": 1, "passed": 1, "failed": 0, "pass_rate": 100.0}},
            "latency": {"count": 1, "avg_s": 1.2, "p50_s": 1.2, "p95_s": 1.2, "max_s": 1.2},
            "sql_cases": 1,
            "sql_cases_passed": 1,
            "rag_cases": 0,
            "rag_cases_passed": 0,
            "hybrid_cases": 0,
            "hybrid_cases_passed": 0,
        },
        "results": [
            {
                "case_id": "sample-case",
                "query": "Average price in Brooklyn",
                "category": "sql",
                "passed": True,
                "tags": ["sql"],
                "assertions": [{"name": "require_sql", "passed": True, "expected": True, "actual": True, "detail": None}],
                "result": {
                    "intent": "FACT_SQL",
                    "scope": "Market",
                    "policy": "SQL_HIGHBURY",
                    "filters": {},
                    "sql_text": "SELECT 1;",
                    "answer_text": "Average price computed.",
                    "row_count": 1,
                    "rag_count": 0,
                    "latency": 1.2,
                    "abstained": False,
                    "manual_checks": [],
                    "notes": None,
                },
                "error": None,
            }
        ],
    }
    (reports_dir / "benchmark-report-20260331-125536.json").write_text(json.dumps(report_payload), encoding="utf-8")

    monkeypatch.setattr("backend.ai_observability.build_business_kpi_snapshot", lambda repo_root: {})
    monkeypatch.setattr("backend.ai_observability._load_data_quality_payload", lambda repo_root: {})

    payload = load_ai_metrics_payload(
        reports_dir,
        {"checked_at": "2026-03-31T12:55:36+00:00", "status": "ready", "components": {}},
    )

    pack = payload["packs"]["benchmarks.adversarial"]
    assert pack["case_details"][0]["case_id"] == "sample-case"
    assert pack["case_details"][0]["query"] == "Average price in Brooklyn"
    assert pack["case_details"][0]["answer_text"] == "Average price computed."
