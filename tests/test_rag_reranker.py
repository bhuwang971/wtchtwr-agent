from agent.vector_qdrant import _rerank_hits


def test_reranker_prioritizes_overlap_and_sentiment_match() -> None:
    hits = [
        {
            "listing_id": "1",
            "snippet": "Guests loved the host communication and said check in was smooth.",
            "score": 0.72,
            "borough": "Brooklyn",
            "year": 2025,
            "sentiment_label": "positive",
        },
        {
            "listing_id": "2",
            "snippet": "The apartment was clean but there were some issues with noise.",
            "score": 0.79,
            "borough": "Brooklyn",
            "year": 2023,
            "sentiment_label": "negative",
        },
    ]

    reranked = _rerank_hits(
        "Show positive guest feedback about communication in Brooklyn",
        hits,
        top_k=2,
    )

    assert reranked[0]["listing_id"] == "1"
    assert reranked[0]["rerank_score"] >= reranked[1]["rerank_score"]
