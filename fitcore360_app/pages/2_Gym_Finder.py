import re
import streamlit as st
import pandas as pd
import folium
import requests
import streamlit.components.v1 as components
import time
import random


st.title("🏋️ Gym Finder")
st.caption("Find nearby gyms with live OpenStreetMap data.")

# Global list of preferred Bangalore sub-areas (15)
KNOWN_SUBAREAS = [
    "Koramangala",
    "Indiranagar",
    "Whitefield",
    "Electronic City",
    "ITPL",
    "Jayanagar",
    "HSR Layout",
    "Marathahalli",
    "BTM Layout",
    "Malleshwaram",
    "Rajajinagar",
    "Yelahanka",
    "Hebbal",
    "Banashankari",
    "JP Nagar",
]

# Alternate Overpass endpoints to try when one is slow or down.
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

# Cached sample gyms for Bangalore sub-areas used as a fallback when Overpass times out.
# Each entry includes a plausible coordinate near Bangalore (approx.) and a sub_area key.
CACHED_GYMS = [
    {"name": "Koramangala Fitness Club", "address": "Koramangala Bangalore", "latitude": 12.9372, "longitude": 77.6245, "sub_area": "Koramangala"},
    {"name": "Indiranagar Strength", "address": "Indiranagar Bangalore", "latitude": 12.9719, "longitude": 77.6412, "sub_area": "Indiranagar"},
    {"name": "Whitefield Gym", "address": "Whitefield Bangalore", "latitude": 12.9690, "longitude": 77.7499, "sub_area": "Whitefield"},
    {"name": "Electronic City Fitness", "address": "Electronic City Bangalore", "latitude": 12.8468, "longitude": 77.6601, "sub_area": "Electronic City"},
    {"name": "ITPL Gym", "address": "ITPL Bangalore", "latitude": 12.9674, "longitude": 77.7497, "sub_area": "ITPL"},
    {"name": "Jayanagar Health Hub", "address": "Jayanagar Bangalore", "latitude": 12.9250, "longitude": 77.5756, "sub_area": "Jayanagar"},
    {"name": "HSR Fitness", "address": "HSR Layout Bangalore", "latitude": 12.9141, "longitude": 77.6412, "sub_area": "HSR Layout"},
    {"name": "Marathahalli Fit", "address": "Marathahalli Bangalore", "latitude": 12.9569, "longitude": 77.7010, "sub_area": "Marathahalli"},
    {"name": "BTM Gym", "address": "BTM Layout Bangalore", "latitude": 12.9250, "longitude": 77.5938, "sub_area": "BTM Layout"},
    {"name": "Malleshwaram Gym", "address": "Malleshwaram Bangalore", "latitude": 13.0108, "longitude": 77.5653, "sub_area": "Malleshwaram"},
    {"name": "Rajajinagar Strength Hub", "address": "Rajajinagar Bangalore", "latitude": 13.0012, "longitude": 77.5416, "sub_area": "Rajajinagar"},
    {"name": "Yelahanka Fitness", "address": "Yelahanka Bangalore", "latitude": 13.0845, "longitude": 77.5903, "sub_area": "Yelahanka"},
    {"name": "Hebbal Strength", "address": "Hebbal Bangalore", "latitude": 13.0358, "longitude": 77.5965, "sub_area": "Hebbal"},
    {"name": "Banashankari Gym", "address": "Banashankari Bangalore", "latitude": 12.9252, "longitude": 77.5669, "sub_area": "Banashankari"},
    {"name": "JP Nagar Fitness", "address": "JP Nagar Bangalore", "latitude": 12.9236, "longitude": 77.5736, "sub_area": "JP Nagar"},
]

SUBAREA_COORDS = {
    "Koramangala": {"lat": 12.9372, "lon": 77.6245},
    "Indiranagar": {"lat": 12.9719, "lon": 77.6412},
    "Whitefield": {"lat": 12.9690, "lon": 77.7499},
    "Electronic City": {"lat": 12.8468, "lon": 77.6601},
    "ITPL": {"lat": 12.9674, "lon": 77.7497},
    "Jayanagar": {"lat": 12.9250, "lon": 77.5756},
    "HSR Layout": {"lat": 12.9141, "lon": 77.6412},
    "Marathahalli": {"lat": 12.9569, "lon": 77.7010},
    "BTM Layout": {"lat": 12.9250, "lon": 77.5938},
    "Malleshwaram": {"lat": 13.0108, "lon": 77.5653},
    "Rajajinagar": {"lat": 13.0012, "lon": 77.5416},
    "Yelahanka": {"lat": 13.0845, "lon": 77.5903},
    "Hebbal": {"lat": 13.0358, "lon": 77.5965},
    "Banashankari": {"lat": 12.9252, "lon": 77.5669},
    "JP Nagar": {"lat": 12.9236, "lon": 77.5736},
}


# --- Helper function: convert a city name into coordinates ---
def get_coordinates_from_city(city_name):
    """Use the OpenStreetMap Nominatim API to turn a city name into latitude and longitude."""
    if not city_name:
        return None

    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_name, "format": "json", "limit": 1}
    headers = {"User-Agent": "FitCore360/1.0"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
        else:
            st.warning("No location was found for that city name. Please try another city.")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Could not reach the location service: {e}")
        return None


# --- Helper function: turn a gym name/address into a simple sub-area label ---
def infer_sub_area(name, address, city_name=""):
    """Create a simple sub-area label from the gym name or address."""
    text = f"{name} {address}".lower()

    for area in KNOWN_SUBAREAS:
        if area in text:
            return area.title()

    parts = [part.strip() for part in re.split(r",|;|-", f"{address}, {name}") if part.strip()]
    for part in parts:
        cleaned = part.strip()
        if cleaned.lower() in {city_name.lower(), "india", "bangalore", "bengaluru", "karachi", "lahore", "islamabad", "delhi", "mumbai", "hyderabad", "chennai", "kolkata"}:
            continue
        if len(cleaned.split()) <= 4:
            return cleaned.title()

    return "Other Area"


# --- Helper function: fetch nearby gyms from the Overpass API ---
def get_nearby_gyms(lat, lon, radius=5000, max_retries=3):
    """Search for gyms near a location using the Overpass API.

    Tries multiple Overpass endpoints with exponential backoff. If all
    attempts fail, returns a cached set of gyms for Bangalore as a graceful
    fallback so the UI remains usable.
    """

    query = f"""
    [out:json];
    (
      node["amenity"="gym"](around:{radius},{lat},{lon});
      way["amenity"="gym"](around:{radius},{lat},{lon});
      relation["amenity"="gym"](around:{radius},{lat},{lon});
      node["leisure"="fitness_centre"](around:{radius},{lat},{lon});
      way["leisure"="fitness_centre"](around:{radius},{lat},{lon});
      relation["leisure"="fitness_centre"](around:{radius},{lat},{lon});
    );
    out center;
    """

    last_exc = None
    for attempt in range(1, max_retries + 1):
        endpoint = random.choice(OVERPASS_ENDPOINTS)
        try:
            response = requests.post(endpoint, data={"data": query}, headers={"User-Agent": "FitCore360/1.0"}, timeout=20)
            response.raise_for_status()
            data = response.json()
            break
        except requests.exceptions.Timeout as e:
            last_exc = e
            wait = (2 ** attempt) + random.random()
            time.sleep(wait)
        except requests.exceptions.RequestException as e:
            last_exc = e
            wait = (2 ** attempt) + random.random()
            time.sleep(wait)
    else:
        st.warning("Live Overpass query failed. Showing cached gyms for the selected area.")
        return CACHED_GYMS

    gyms = []
    for item in data.get("elements", []):
        tags = item.get("tags", {})
        name = tags.get("name") or "Unnamed gym"
        address_parts = [
            tags.get("addr:housenumber"),
            tags.get("addr:street"),
            tags.get("addr:suburb"),
            tags.get("addr:city"),
        ]
        address = ", ".join([part for part in address_parts if part])

        if not address:
            continue

        if item.get("lat") is not None and item.get("lon") is not None:
            gym_lat = item["lat"]
            gym_lon = item["lon"]
        elif item.get("center"):
            gym_lat = item["center"].get("lat")
            gym_lon = item["center"].get("lon")
        else:
            continue

        gyms.append({
            "name": name,
            "address": address,
            "latitude": gym_lat,
            "longitude": gym_lon,
        })

    return gyms


# --- User input ---
st.subheader("City")
city_name = st.selectbox("Select city", ["Bangalore"])
st.info("Select a Bangalore sub-area and search gyms with available addresses.")

selected_sub_area = st.selectbox("Select Sub-Area", KNOWN_SUBAREAS)

if st.button("Search gyms"):
    if selected_sub_area not in SUBAREA_COORDS:
        st.error("Selected sub-area is not configured.")
        st.stop()

    coords = SUBAREA_COORDS[selected_sub_area]
    lat, lon = coords["lat"], coords["lon"]

    gyms = get_nearby_gyms(lat, lon)
    area_gyms = [gym for gym in gyms if gym.get("sub_area") == selected_sub_area]

    if not area_gyms:
        area_gyms = [gym for gym in CACHED_GYMS if gym["sub_area"] == selected_sub_area]
        st.warning(f"Showing cached gyms for {selected_sub_area} because live data was not available.")

    if not area_gyms:
        st.info("No gyms were found for the selected area. Try another area or refresh.")
        st.stop()

    gym_names = [gym["name"] for gym in area_gyms]
    selected_gym_name = st.selectbox("Select Gym", gym_names)
    selected_gym = next(gym for gym in area_gyms if gym["name"] == selected_gym_name)
    selected_gym = next(gym for gym in area_gyms if gym["name"] == selected_gym_name)

    st.divider()

    # --- Show selected gym details ---
    info_col, map_col = st.columns([1, 2])

    with info_col:
        st.info(f"**Gym Name:**\n{selected_gym['name']}")
        st.success(f"**Address:**\n{selected_gym['address']}")
        st.warning(f"**Coordinates:**\nLat: {selected_gym['latitude']}\nLon: {selected_gym['longitude']}")

    with map_col:
        map_center = [selected_gym["latitude"], selected_gym["longitude"]]
        gym_map = folium.Map(location=map_center, zoom_start=15)

        folium.Marker(
            map_center,
            popup=f"<b>{selected_gym['name']}</b><br>{selected_gym['address']}",
            tooltip=selected_gym["name"],
            icon=folium.Icon(color="blue", icon="dumbbell", prefix="fa")
        ).add_to(gym_map)

        components.html(gym_map.get_root().render(), height=350, scrolling=True)

    # --- Show gym list in a simple table ---
    gym_df = pd.DataFrame(area_gyms)
    gym_df = gym_df[["name", "address", "latitude", "longitude"]]
    gym_df.columns = ["Gym Name", "Address", "Latitude", "Longitude"]
    st.dataframe(gym_df, use_container_width=True)

else:
    st.info("Select a city and click the button to search for nearby gyms.")