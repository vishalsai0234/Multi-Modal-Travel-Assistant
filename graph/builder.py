"""
graph/builder.py

Assembles the complete LangGraph workflow.
This is the single source of truth for the graph topology.

Graph topology:
    START
      ↓
    extract_city
      ↓
    router ──── [conditional edge: route_by_source] ──→ vector_retrieve
      |                                                        |
      └─────────────────────────────────────→ web_search      |
                                                  |            |
                                                  ↓            ↓
                                           parallel_fetch ←────┘
                                                  ↓
                                            synthesizer
                                                  ↓
                                                END
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import TravelState
from graph.nodes import (
    extract_city_node,
    router_node,
    vector_retrieve_node,
    web_search_node,
    parallel_fetch_node,
    synthesizer_node,
)
from graph.edges import route_by_source


def build_graph(use_memory: bool = True):
    """
    Builds and compiles the LangGraph StateGraph.

    Args:
        use_memory: If True, attaches MemorySaver checkpointer for
                    Human-in-the-Loop / conversation memory (Distinction 3).

    Returns:
        Compiled LangGraph app ready to invoke.
    """
    # Initialize graph with our typed state
    workflow = StateGraph(TravelState)

    # -----------------------------------------------------------------------
    # Register all nodes
    # -----------------------------------------------------------------------
    workflow.add_node("extract_city", extract_city_node)
    workflow.add_node("router", router_node)
    workflow.add_node("vector_retrieve", vector_retrieve_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("parallel_fetch", parallel_fetch_node)
    workflow.add_node("synthesizer", synthesizer_node)

    # -----------------------------------------------------------------------
    # Define edges (the flow)
    # -----------------------------------------------------------------------

    # Entry point
    workflow.set_entry_point("extract_city")

    # extract_city always goes to router
    workflow.add_edge("extract_city", "router")

    # CONDITIONAL EDGE: router decides the path based on state["source"]
    workflow.add_conditional_edges(
        "router",
        route_by_source,
        {
            "vector_store": "vector_retrieve",  # city found locally
            "web_search": "web_search",          # city needs external search
        },
    )

    # Both paths converge at parallel_fetch
    workflow.add_edge("vector_retrieve", "parallel_fetch")
    workflow.add_edge("web_search", "parallel_fetch")

    # parallel_fetch always goes to synthesizer
    workflow.add_edge("parallel_fetch", "synthesizer")

    # synthesizer is the terminal node
    workflow.add_edge("synthesizer", END)

    # -----------------------------------------------------------------------
    # Compile with optional memory checkpointer
    # -----------------------------------------------------------------------
    if use_memory:
        # DISTINCTION 3: MemorySaver enables conversation context persistence
        # This lets the agent remember "Tokyo" across follow-up messages like
        # "What about next week?" without re-fetching the city summary.
        checkpointer = MemorySaver()
        app = workflow.compile(checkpointer=checkpointer)
    else:
        app = workflow.compile()

    return app


def generate_graph_image(app, output_path: str = "graph.png"):
    """
    Saves a PNG visualization of the graph topology.
    Required by the assignment submission guidelines.
    """
    try:
        image_bytes = app.get_graph().draw_mermaid_png()
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        print(f"Graph saved to {output_path}")
    except Exception as e:
        print(f"Could not generate graph image: {e}")
        print("This requires 'pip install grandalf' or a working Mermaid renderer.")
