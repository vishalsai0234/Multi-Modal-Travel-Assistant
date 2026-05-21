from typing import TypedDict, Optional


class TravelState(TypedDict):
    """
    Shared state passed between all nodes in the LangGraph workflow.
    Each node reads from this and returns a partial update dict.
    """
    # Input from user
    user_query: str

    # Extracted city name (clean, title-cased)
    city: str

    # Routing decision: "vector_store" or "web_search"
    source: str

    # City description text (from vector store or web search)
    city_summary: str

    # 7-day weather forecast list of dicts
    weather_forecast: list

    # Image URLs list
    image_urls: list

    # Error message if something went wrong (empty string = no error)
    error: str

    # Final structured output assembled by synthesizer node
    final_output: Optional[dict]
