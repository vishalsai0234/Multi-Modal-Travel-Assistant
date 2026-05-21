"""
graph/edges.py

Conditional edge functions for LangGraph.
These functions read the current state and return a string key
that LangGraph uses to decide which node to go to next.
"""

from graph.state import TravelState


def route_by_source(state: TravelState) -> str:
    """
    CORE REQUIREMENT: The Intelligent "Switch"

    After the router_node runs, this function reads state["source"]
    and returns either "vector_store" or "web_search".

    LangGraph maps these strings to actual node names via the
    conditional_edges mapping in builder.py.
    """
    source = state.get("source", "web_search")
    return source
