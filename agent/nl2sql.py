"""Compatibility shim for older tests and scripts expecting `agent.nl2sql`."""
from __future__ import annotations

from .nl2sql_llm import plan_to_sql_llm
from .types import graph_to_state, state_to_graph


def plan_to_sql(state):
    """Mutate a legacy dict-like state with NL2SQL output."""
    graph_state = state_to_graph(state)
    updated_graph = plan_to_sql_llm(graph_state)
    updated_state = graph_to_state(updated_graph, base=state)
    state.clear()
    state.update(updated_state)
    return state


__all__ = ["plan_to_sql"]
