from agent.graph import _should_abstain_for_missing_portfolio_evidence


def test_missing_portfolio_evidence_abstains_for_owned_hybrid_slice() -> None:
    assert (
        _should_abstain_for_missing_portfolio_evidence(
            "Show me Staten Island revenue vs market and back it up with guest complaints for our portfolio there.",
            "SQL_RAG_FUSED",
            [],
            [],
            {"weak_evidence": True},
        )
        is True
    )


def test_generic_hybrid_gap_does_not_force_abstention() -> None:
    assert (
        _should_abstain_for_missing_portfolio_evidence(
            "Compare our occupancy to the market in Manhattan and what guests complain about.",
            "SQL_RAG_FUSED",
            [],
            [{"snippet": "Noise issues."}, {"snippet": "Cleanliness complaints."}],
            {"weak_evidence": False},
        )
        is False
    )
