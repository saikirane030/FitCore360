import requests

def geocode_place(query, limit=10):
    """Use Nominatim (OpenStreetMap) to geocode a query string to places.
    Returns a list of dicts with 'lat', 'lon', 'display_name'."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "json", "limit": limit}
    headers = {"User-Agent": "FitCore360-app"}
    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_weather(lat, lon, daily="temperature_2m_max,temperature_2m_min,precipitation_sum", timezone="auto"):
    """Fetch daily forecast from Open-Meteo for given lat/lon.
    Returns parsed JSON response."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": daily,
        "timezone": timezone
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()
