import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import st_folium

st.title("🏋️ Gym Finder")
st.caption("Find nearby gyms with live OpenStreetMap data.")


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


# --- Helper function: fetch nearby gyms from the Overpass API ---
def get_nearby_gyms(lat, lon, radius=5000):
    """Search for gyms near a location using the Overpass API."""
    overpass_url = "https://overpass-api.de/api/interpreter"

    # This query asks OpenStreetMap for nearby gym-like places.
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

    try:
        response = requests.get(overpass_url, params={"data": query}, timeout=15)
        response.raise_for_status()
        data = response.json()

        gyms = []
        for item in data.get("elements", []):
            tags = item.get("tags", {})
            name = tags.get("name") or "Unnamed gym"
            address = (
                tags.get("addr:street")
                or tags.get("addr:full")
                or tags.get("addr:city")
                or "Address not available"
            )

            # Some results are nodes, while others are ways/relations.
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

    except requests.exceptions.RequestException as e:
        st.error(f"The gym search service is unavailable right now: {e}")
        return []


# --- User input ---
search_type = st.radio("Choose search method", ["City name", "Latitude/Longitude"], horizontal=True)

if search_type == "City name":
    city_name = st.text_input("Enter a city name", placeholder="Example: Bangalore")
    location_ready = bool(city_name)
else:
    lat_input = st.text_input("Latitude", placeholder="12.9716")
    lon_input = st.text_input("Longitude", placeholder="77.5946")
    location_ready = bool(lat_input and lon_input)

radius = st.slider("Search radius (meters)", 1000, 10000, 5000, 1000)

if st.button("Search gyms"):
    if not location_ready:
        st.info("Please enter a city name or both latitude and longitude.")
    else:
        if search_type == "City name":
            coords = get_coordinates_from_city(city_name)
            if coords is None:
                st.stop()
            lat, lon = coords
        else:
            try:
                lat = float(lat_input)
                lon = float(lon_input)
            except ValueError:
                st.error("Please enter valid numeric coordinates.")
                st.stop()

        gyms = get_nearby_gyms(lat, lon, radius=radius)

        if not gyms:
            st.info("No gyms were found near this location. Try a bigger radius or another place.")
            st.stop()

        # --- Show results on a map ---
        st.subheader("📍 Nearby gyms")

        map_center = [lat, lon]
        gym_map = folium.Map(location=map_center, zoom_start=13)

        # Add a marker for the search location.
        folium.Marker(
            map_center,
            popup="Search location",
            tooltip="Search location",
            icon=folium.Icon(color="red", icon="home", prefix="fa")
        ).add_to(gym_map)

        # Add one marker for each gym found.
        for gym in gyms:
            folium.Marker(
                [gym["latitude"], gym["longitude"]],
                popup=f"<b>{gym['name']}</b><br>{gym['address']}",
                tooltip=gym["name"],
                icon=folium.Icon(color="blue", icon="dumbbell", prefix="fa")
            ).add_to(gym_map)

        st_folium(gym_map, width="100%", height=450)

        # --- Show gym details in a simple table ---
        gym_df = pd.DataFrame(gyms)
        gym_df = gym_df[["name", "address", "latitude", "longitude"]]
        gym_df.columns = ["Gym Name", "Address", "Latitude", "Longitude"]
        st.dataframe(gym_df, use_container_width=True)

else:
    st.info("Enter a location above and click the button to search for nearby gyms.")