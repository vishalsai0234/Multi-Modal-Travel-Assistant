"""
tools/vector_store.py - Strict city name matching only.
No TF-IDF on content — just clean city name lookup.
"""

import json
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "cities.json")

_cities = None

def _load():
    global _cities
    if _cities is None:
        with open(DATA_PATH, "r") as f:
            _cities = json.load(f)
    return _cities

def query_city(city_name: str) -> tuple:
    """
    Strict match: only returns True if the query IS one of our stored cities.
    No partial matching, no similarity — just clean name comparison.
    
    Stored: "paris", "tokyo", "new york"
    "japan"     → False (not a stored city name)
    "new delhi" → False (not a stored city name)
    "tokyo"     → True
    "new york"  → True
    "Tell me about Paris" → True (after cleaning)
    """
    cities = _load()
    
    # Clean the query — remove common filler words
    query = city_name.lower().strip()
    
    # Remove common trigger phrases that might be passed in
    filler = [
        "tell me about", "what is", "what's", "show me", "about",
        "i want to visit", "information on", "search for", "explore"
    ]
    for f in filler:
        if query.startswith(f):
            query = query[len(f):].strip()
    
    query = query.rstrip("?.!,").strip()
    
    # STRICT: only match if query exactly equals a stored city name
    # No substring, no similarity, no partial overlap
    if query in cities:
        return cities[query], True
    
    # Handle common aliases
    aliases = {
        "nyc": "new york",
        "ny": "new york",
        "new york city": "new york",
        "the big apple": "new york",
        "city of light": "paris",
        "city of lights": "paris",
    }
    if query in aliases and aliases[query] in cities:
        return cities[aliases[query]], True
    
    return "", False