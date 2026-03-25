from evals.runner import evaluate_case


def test_evaluate_case_supports_require_abstain(monkeypatch) -> None:
    def fake_run_agent(*args, **kwargs):
        return {
            "intent": "SENTIMENT_REVIEWS",
            "scope": "Hybrid",
            "answer_text": "I do not have enough grounded evidence to answer this confidently.",
            "result_bundle": {"policy": "RAG_HYBRID"},
            "sql": {"text": ""},
            "latency": 1.2,
        }

    monkeypatch.setattr("evals.runner.run_agent", fake_run_agent)

    result = evaluate_case(
        {
            "id": "abstain-case",
            "category": "hybrid",
            "query": "unsupported question",
            "expected": {"require_abstain": True},
        }
    )

    assert result.passed is True
    assert result.result["abstained"] is True
