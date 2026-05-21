import time
import random
import hashlib
from datetime import datetime, timedelta

# Known cities with specific climate data
CITY_TEMPS = {
    "paris":     {"base_high": 18, "base_low": 11, "conditions": ["Sunny", "Partly Cloudy", "Rainy", "Overcast"]},
    "tokyo":     {"base_high": 24, "base_low": 17, "conditions": ["Sunny", "Humid", "Partly Cloudy", "Rainy"]},
    "new york":  {"base_high": 20, "base_low": 13, "conditions": ["Sunny", "Windy", "Cloudy", "Rainy", "Clear"]},
    "kyoto":     {"base_high": 23, "base_low": 15, "conditions": ["Sunny", "Partly Cloudy", "Rainy", "Humid"]},
    "dubai":     {"base_high": 38, "base_low": 28, "conditions": ["Sunny", "Clear", "Hazy", "Hot & Sunny"]},
    "london":    {"base_high": 15, "base_low":  9, "conditions": ["Cloudy", "Rainy", "Overcast", "Partly Cloudy"]},
    "sydney":    {"base_high": 22, "base_low": 14, "conditions": ["Sunny", "Clear", "Partly Cloudy", "Breezy"]},
    "new delhi": {"base_high": 35, "base_low": 24, "conditions": ["Hot & Sunny", "Hazy", "Sunny", "Partly Cloudy"]},
    "japan":     {"base_high": 22, "base_low": 14, "conditions": ["Sunny", "Partly Cloudy", "Rainy", "Clear"]},
    "mumbai":    {"base_high": 32, "base_low": 25, "conditions": ["Humid", "Sunny", "Partly Cloudy", "Rainy"]},
    "bangkok":   {"base_high": 34, "base_low": 26, "conditions": ["Hot & Sunny", "Humid", "Rainy", "Partly Cloudy"]},
    "rome":      {"base_high": 25, "base_low": 16, "conditions": ["Sunny", "Clear", "Partly Cloudy", "Warm"]},
    "barcelona": {"base_high": 26, "base_low": 18, "conditions": ["Sunny", "Clear", "Breezy", "Partly Cloudy"]},
    "amsterdam": {"base_high": 16, "base_low": 10, "conditions": ["Cloudy", "Rainy", "Windy", "Partly Cloudy"]},
    "singapore": {"base_high": 31, "base_low": 24, "conditions": ["Humid", "Rainy", "Partly Cloudy", "Sunny"]},
    "cairo":     {"base_high": 36, "base_low": 22, "conditions": ["Sunny", "Hot & Sunny", "Clear", "Hazy"]},
    "moscow":    {"base_high":  8, "base_low":  2, "conditions": ["Cloudy", "Snowy", "Overcast", "Cold & Clear"]},
    "toronto":   {"base_high": 17, "base_low":  9, "conditions": ["Sunny", "Partly Cloudy", "Windy", "Cloudy"]},
    "beijing":   {"base_high": 26, "base_low": 16, "conditions": ["Hazy", "Sunny", "Cloudy", "Partly Cloudy"]},
    "snohomish": {"base_high": 16, "base_low":  8, "conditions": ["Cloudy", "Rainy", "Partly Cloudy", "Overcast"]},
}


def _derive_climate(city_name: str) -> dict:
    """
    For cities not in our known list, derive a unique but deterministic
    climate profile from the city name using a hash.
    This ensures the SAME city always gets the SAME climate — not random.
    """
    # Use city name hash as a stable seed
    h = int(hashlib.md5(city_name.lower().encode()).hexdigest(), 16)
    
    # Derive base temps from hash (range: 10°C to 36°C high)
    base_high = 10 + (h % 26)
    base_low  = base_high - 7 - (h % 5)
    
    all_conditions = [
        ["Sunny", "Partly Cloudy", "Clear", "Breezy"],
        ["Cloudy", "Rainy", "Overcast", "Windy"],
        ["Hot & Sunny", "Humid", "Hazy", "Sunny"],
        ["Sunny", "Clear", "Partly Cloudy", "Warm"],
    ]
    conditions = all_conditions[h % len(all_conditions)]
    
    return {"base_high": base_high, "base_low": base_low, "conditions": conditions}


def get_weather_forecast(city: str) -> list:
    """
    Returns a 7-day weather forecast for any city.
    Known cities → real climate profiles.
    Unknown cities → deterministic unique profile derived from city name.
    """
    time.sleep(0.8)

    city_lower = city.lower().strip()
    
    # Use known profile or derive one uniquely from the city name
    if city_lower in CITY_TEMPS:
        cfg = CITY_TEMPS[city_lower]
    else:
        cfg = _derive_climate(city_lower)

    base_high  = cfg["base_high"]
    base_low   = cfg["base_low"]
    conditions = cfg["conditions"]

    # Use city name as random seed so same city = same weather pattern
    seed = int(hashlib.md5(city_lower.encode()).hexdigest(), 16) % (2**32)
    rng  = random.Random(seed + datetime.now().day)  # changes daily but stable within a day

    forecast = []
    today = datetime.now()
    for i in range(7):
        d    = today + timedelta(days=i)
        v    = rng.randint(-4, 4)
        cond = rng.choice(conditions)
        mod  = -2 if "Rain" in cond else 0
        forecast.append({
            "day":       d.strftime("%A"),
            "date":      d.strftime("%b %d"),
            "temp_high": base_high + v + mod,
            "temp_low":  base_low  + v - 2 + mod,
            "condition": cond,
            "humidity":  rng.randint(45, 85),
            "wind_kmh":  rng.randint(5, 35),
        })
    return forecast