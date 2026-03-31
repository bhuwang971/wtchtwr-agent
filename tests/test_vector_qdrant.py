from agent.vector_qdrant import _should_prefer_portfolio_reviews


def test_portfolio_review_hint_prefers_highbury_reviews_for_owned_hybrid_requests() -> None:
    assert (
        _should_prefer_portfolio_reviews(
            "Hybrid",
            "Show me Staten Island revenue vs market and back it up with guest complaints for our portfolio there.",
            {},
        )
        is True
    )


def test_generic_hybrid_compare_does_not_force_portfolio_review_filter() -> None:
    assert (
        _should_prefer_portfolio_reviews(
            "Hybrid",
            "Compare our Midtown pricing versus the market, but keep the guest complaints focused on Brooklyn only.",
            {},
        )
        is False
    )
