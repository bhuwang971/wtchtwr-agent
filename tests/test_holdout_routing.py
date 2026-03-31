from agent.guards import ingress
from agent.intents import classify_intent
from agent.policy import plan_steps, resolve_entities


def run_pipeline(query, tenant=None, user_filters=None):
    state = ingress(query, tenant, user_filters)
    state = classify_intent(state)
    state = resolve_entities(state)
    state = plan_steps(state)
    return state


def test_for_march_phrasing_extracts_month() -> None:
    state = run_pipeline("Pull occupancy for Brooklyn, but just for March.")
    assert "MAR" in state["filters"]["month"]


def test_upbeat_feedback_routes_to_positive_rag_without_default_borough() -> None:
    state = run_pipeline("Any upbeat guest feedback on our Highbury homes?", tenant="highbury")
    assert state["intent"] == "SENTIMENT_REVIEWS"
    assert state["policy"] == "RAG_HIGHBURY"
    assert state["filters"]["sentiment_label"] == "positive"
    assert state["filters"]["borough"] == []


def test_review_themes_prompt_routes_to_hybrid() -> None:
    state = run_pipeline(
        "For Manhattan, compare our occupancy to the market and back it up with guest review themes.",
        tenant="highbury",
    )
    assert state["intent"] == "FACT_SQL_RAG_HYBRID"
    assert state["policy"] == "SQL_RAG_COMPARE"
    assert state["scope"] == "Hybrid"


def test_revenue_low_performer_prompt_routes_to_triage() -> None:
    state = run_pipeline("Use revenue as the KPI and flag weak Highbury performers.", tenant="highbury")
    assert state["intent"] == "PORTFOLIO_TRIAGE_ADVANCED"
    assert state["policy"] == "PORTFOLIO_TRIAGE"
    assert state["filters"]["kpi"] == "estimated_revenue_30"


def test_submarket_supply_prompt_routes_to_expansion() -> None:
    state = run_pipeline(
        "If Highbury adds supply next year, which NYC submarkets look strongest and why?",
        tenant="highbury",
    )
    assert state["intent"] == "EXPANSION_SCOUT"
    assert state["policy"] == "EXPANSION_SCOUT"


def test_adversarial_contradictory_compare_stays_hybrid() -> None:
    state = run_pipeline(
        "Compare our Midtown pricing versus the market, but keep the guest complaints focused on Brooklyn only.",
        tenant="highbury",
    )
    assert state["scope"] == "Hybrid"
    assert state["intent"] in {"FACT_SQL_RAG_HYBRID", "FACT_SQL_RAG_HYBRID_COMPARE"}
    assert state["plan"]["mode"] == "hybrid"


def test_adversarial_noisy_triage_keeps_triage_policy() -> None:
    state = run_pipeline(
        "Give me the 'what is going wrong and what should I fix first' view for Highbury in Manhattan.",
        tenant="highbury",
    )
    assert state["intent"] == "PORTFOLIO_TRIAGE_ADVANCED"
    assert state["policy"] == "PORTFOLIO_TRIAGE"
    assert state["filters"]["borough"] == ["Manhattan"]


def test_adversarial_implicit_market_compare_routes_to_sql_compare() -> None:
    state = run_pipeline(
        "Are our Upper West Side prices punching above the neighborhood around us?",
        tenant="highbury",
    )
    assert state["intent"] == "FACT_SQL_COMPARE"
    assert state["policy"] == "SQL_COMPARE"
    assert state["scope"] == "Hybrid"


def test_staten_island_hybrid_prompt_extracts_borough() -> None:
    state = run_pipeline(
        "Show me Staten Island revenue vs market and back it up with guest complaints for our portfolio there.",
        tenant="highbury",
    )
    assert state["scope"] == "Hybrid"
    assert state["intent"] in {"FACT_SQL_RAG_HYBRID", "FACT_SQL_RAG_HYBRID_COMPARE"}
    assert state["filters"]["borough"] == ["Staten Island"]
