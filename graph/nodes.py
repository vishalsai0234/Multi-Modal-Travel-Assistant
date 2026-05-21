"""
graph/nodes.py

Each function here is a LangGraph node.
Nodes receive the full state dict and return a PARTIAL dict
with only the keys they are updating. LangGraph merges these
back into the shared state automatically.
"""

import re
import concurrent.futures

from tools.vector_store import query_city
from tools.web_search import mock_web_search
from tools.weather import get_weather_forecast
from tools.images import get_city_images
from graph.state import TravelState


# ---------------------------------------------------------------------------
# Node 1: Extract city name from user query
# ---------------------------------------------------------------------------

def extract_city_node(state: TravelState) -> dict:
    """
    Parses the user's free-text query to extract a clean city name.
    Handles inputs like:
      - "Tell me about Tokyo"
      - "What's Kyoto like?"
      - "kyoto"
      - "I want to visit New York"
    """
    query = state["user_query"].strip()

    # Common trigger phrases to strip out
    patterns = [
        r"tell me about\s+",
        r"what(?:'s| is) .{0,15} like\??",
        r"what(?:'s| is)\s+",
        r"i want to (?:visit|know about|explore)\s+",
        r"show me\s+",
        r"search for\s+",
        r"information (?:about|on)\s+",
        r"about\s+",
    ]

    cleaned = query.lower()
    for pattern in patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()

    # Remove trailing punctuation
    cleaned = cleaned.rstrip("?.!,")

    # Title-case the result (e.g., "new york" → "New York")
    city = cleaned.title() if cleaned else query.title()

    return {"city": city, "error": ""}


# ---------------------------------------------------------------------------
# Node 2: Router — checks vector store, sets source
# ---------------------------------------------------------------------------

def router_node(state: TravelState) -> dict:
    """
    Queries the local vector store for the city.
    Sets state["source"] to either "vector_store" or "web_search".
    If found in vector store, also sets city_summary directly.
    """
    city = state["city"]

    try:
        summary, found = query_city(city)
        if found:
            return {
                "source": "vector_store",
                "city_summary": summary,
            }
        else:
            return {
                "source": "web_search",
                "city_summary": "",
            }
    except Exception as e:
        # If vector store fails, fall back to web search gracefully
        return {
            "source": "web_search",
            "city_summary": "",
            "error": f"Vector store error (falling back to web): {str(e)}",
        }


# ---------------------------------------------------------------------------
# Node 3a: Vector retrieval (city IS in local store)
# — This node is a no-op because router already set city_summary.
#   We include it explicitly so the graph topology is clear.
# ---------------------------------------------------------------------------

def vector_retrieve_node(state: TravelState) -> dict:
    """
    City was found in the vector store.
    city_summary is already set by router_node.
    This node is a checkpoint — useful for logging or post-processing.
    """
    return {}  # nothing to add; router already populated city_summary


# ---------------------------------------------------------------------------
# Node 3b: Web search (city is NOT in local store)
# ---------------------------------------------------------------------------

def web_search_node(state: TravelState) -> dict:
    """
    City was NOT found in the local vector store.
    Calls the web search tool (mock) to generate a summary.
    """
    city = state["city"]
    try:
        summary = mock_web_search(city)
        return {"city_summary": summary}
    except Exception as e:
        return {
            "city_summary": f"Could not retrieve information for {city}.",
            "error": f"Web search failed: {str(e)}",
        }


# ---------------------------------------------------------------------------
# Node 4: Parallel Fan-Out — weather AND images fetched simultaneously
# ---------------------------------------------------------------------------

def parallel_fetch_node(state: TravelState) -> dict:
    """
    DISTINCTION CHALLENGE: Parallel Fan-Out

    Weather and image fetching are completely independent operations.
    We use ThreadPoolExecutor to run both simultaneously, cutting
    total wait time roughly in half.

    Sequential would be: 0.8s (weather) + 0.6s (images) = ~1.4s
    Parallel gives us:   max(0.8s, 0.6s) = ~0.8s
    """
    city = state["city"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both tasks at the same time
        weather_future = executor.submit(get_weather_forecast, city)
        images_future = executor.submit(get_city_images, city)

        # Wait for both to complete
        try:
            weather_data = weather_future.result(timeout=10)
        except Exception as e:
            weather_data = []
            # We don't crash the whole graph for a weather failure

        try:
            image_data = images_future.result(timeout=10)
        except Exception as e:
            image_data = []

    return {
        "weather_forecast": weather_data,
        "image_urls": image_data,
    }


# ---------------------------------------------------------------------------
# Node 5: Synthesizer — assembles final structured output
# ---------------------------------------------------------------------------

def synthesizer_node(state: TravelState) -> dict:
    """
    DISTINCTION CHALLENGE: Structured Output

    Assembles all fetched data into a clean JSON-serializable dict.
    The Streamlit app reads ONLY from this final_output dict —
    it never parses raw state fields directly.

    Also generates a brief AI-style intro using the city name and source.
    """
    city = state["city"]
    source = state["source"]
    summary = state["city_summary"]
    forecast = state["weather_forecast"]
    images = state["image_urls"]

    # Determine data source label for UI transparency
    source_label = "Local Knowledge Base" if source == "vector_store" else "Web Search"

    final_output = {
        "city": city,
        "data_source": source_label,
        "city_summary": summary,
        "weather_forecast": forecast,   # List[dict] with day/date/temp_high/temp_low/condition
        "image_urls": images,           # List[str]
        "error": state.get("error", ""),
    }

    return {"final_output": final_output}
