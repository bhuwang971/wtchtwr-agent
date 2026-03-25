from backend.ai_observability import build_confidence_payload, build_trace_payload


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
