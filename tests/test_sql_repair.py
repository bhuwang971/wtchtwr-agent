from agent.nl2sql_llm import _repair_sql_rule_based


def test_rule_based_sql_repair_removes_lower_from_numeric_columns() -> None:
    sql = "SELECT * FROM listings_cleaned l WHERE lower(l.review_scores_rating) < 7;"
    repaired = _repair_sql_rule_based(sql, "Binder Error: No function matches lower(DOUBLE)")
    assert repaired is not None
    assert "lower(l.review_scores_rating)" not in repaired.lower()
    assert "review_scores_rating" in repaired
