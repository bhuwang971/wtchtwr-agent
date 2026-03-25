from scripts.compare_benchmark_models import _comparison_payload, _comparison_markdown, _parse_model


def test_parse_model_supports_main_and_nl2sql_models() -> None:
    config = _parse_model("baseline:gpt-5.1:gpt-4o-mini:gpt-4o:gpt-4o")

    assert config.label == "baseline"
    assert config.openai_model == "gpt-5.1"
    assert config.nl2sql_model == "gpt-4o-mini"
    assert config.openai_fallback_model == "gpt-4o"
    assert config.nl2sql_fallback_model == "gpt-4o"


def test_comparison_payload_picks_accuracy_and_speed_winners() -> None:
    payload = _comparison_payload(
        [
            {
                "model_label": "accurate",
                "openai_model": "gpt-5.1",
                "nl2sql_model": "gpt-4o-mini",
                "pass_rate": 70.0,
                "assertion_pass_rate": 85.0,
                "sql_pass_rate": 80.0,
                "rag_pass_rate": 60.0,
                "hybrid_pass_rate": 50.0,
                "p50_latency_s": 3.0,
                "p95_latency_s": 9.0,
            },
            {
                "model_label": "fast",
                "openai_model": "gpt-4o",
                "nl2sql_model": "gpt-4o-mini",
                "pass_rate": 65.0,
                "assertion_pass_rate": 80.0,
                "sql_pass_rate": 75.0,
                "rag_pass_rate": 55.0,
                "hybrid_pass_rate": 45.0,
                "p50_latency_s": 1.8,
                "p95_latency_s": 6.0,
            },
        ]
    )

    assert payload["winner_by_accuracy"] == "accurate"
    assert payload["winner_by_speed"] == "fast"
    markdown = _comparison_markdown(payload)
    assert "| Label | Main Model | NL2SQL Model | Overall | SQL | RAG | Hybrid | Assertion | P50 (s) | P95 (s) |" in markdown
