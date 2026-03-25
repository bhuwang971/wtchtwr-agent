from evals.runner import (
    _build_summary,
    _categories_requiring_qdrant,
    _contains_all,
    _has_sql_signal,
    _model_env,
    _subset_match,
    CaseResult,
    ModelConfig,
    ReadinessStatus,
    ensure_benchmark_readiness,
    validate_benchmark_readiness,
)


def test_subset_match_supports_nested_dicts_and_lists() -> None:
    actual = {
        "borough": ["Manhattan", "Brooklyn"],
        "sentiment_label": "negative",
        "nested": {"scope": "Market"},
    }
    expected = {
        "borough": ["Brooklyn"],
        "nested": {"scope": "Market"},
    }
    assert _subset_match(actual, expected)


def test_contains_all_is_case_insensitive() -> None:
    assert _contains_all("SELECT * FROM highbury_listings", ["select", "HIGHBURY_LISTINGS"])


def test_build_summary_uses_benchmark_category_for_pipeline_counts() -> None:
    results = [
        CaseResult(case_id="sql-1", query="q1", category="sql", passed=True, result={"sql_text": "", "rag_count": 0, "latency": 1.0}),
        CaseResult(case_id="rag-1", query="q2", category="rag", passed=False, result={"sql_text": "select 1", "rag_count": 2, "latency": 2.0}),
        CaseResult(case_id="hy-1", query="q3", category="hybrid", passed=False, result={"sql_text": "", "rag_count": 0, "latency": 3.0}),
    ]

    summary = _build_summary(results)

    assert summary.sql_cases == 1
    assert summary.sql_cases_passed == 1
    assert summary.rag_cases == 1
    assert summary.rag_cases_passed == 0
    assert summary.hybrid_cases == 1
    assert summary.hybrid_cases_passed == 0


def test_model_env_sets_and_restores_overrides() -> None:
    import os

    os.environ.pop("WTCHTWR_OPENAI_MODEL", None)
    os.environ.pop("WTCHTWR_NL2SQL_MODEL", None)

    with _model_env(ModelConfig(label="test", openai_model="gpt-5.1", nl2sql_model="gpt-4o-mini")):
        assert os.environ["WTCHTWR_OPENAI_MODEL"] == "gpt-5.1"
        assert os.environ["WTCHTWR_NL2SQL_MODEL"] == "gpt-4o-mini"

    assert "WTCHTWR_OPENAI_MODEL" not in os.environ
    assert "WTCHTWR_NL2SQL_MODEL" not in os.environ


def test_has_sql_signal_accepts_rows_when_sql_text_is_missing() -> None:
    result = {"result_bundle": {"rows": [{"metric": 1}]}}
    assert _has_sql_signal(result)


def test_categories_requiring_qdrant_detects_retrieval_backed_cases() -> None:
    cases = [
        {"id": "sql-1", "category": "sql"},
        {"id": "rag-1", "category": "rag"},
        {"id": "triage-1", "category": "triage"},
    ]
    assert _categories_requiring_qdrant(cases) == {"rag", "triage"}


def test_validate_benchmark_readiness_checks_qdrant_for_retrieval_cases(monkeypatch) -> None:
    monkeypatch.setattr(
        "evals.runner._check_qdrant_readiness",
        lambda: ReadinessStatus(service="qdrant", ok=True, detail="reachable"),
    )
    statuses = validate_benchmark_readiness([{"id": "rag-1", "category": "rag"}])
    assert statuses == [ReadinessStatus(service="qdrant", ok=True, detail="reachable")]


def test_ensure_benchmark_readiness_raises_on_qdrant_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "evals.runner._check_qdrant_readiness",
        lambda: ReadinessStatus(service="qdrant", ok=False, detail="offline"),
    )
    try:
        ensure_benchmark_readiness([{"id": "hy-1", "category": "hybrid"}])
    except RuntimeError as exc:
        assert "qdrant: offline" in str(exc)
    else:
        raise AssertionError("Expected readiness failure for offline qdrant.")
