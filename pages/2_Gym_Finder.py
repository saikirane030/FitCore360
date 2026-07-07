import re
import streamlit as st
import pandas as pd
import folium
import requests
import streamlit.components.v1 as components


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


# --- Helper function: turn a gym name/address into a simple sub-area label ---
def infer_sub_area(name, address, city_name=""):
    """Create a simple sub-area label from the gym name or address."""
    text = f"{name} {address}".lower()

# Preferred sub-areas for Bangalore (top 15)
    known_areas = [
        "koramangala", "indiranagar", "whitefield", "electronic city", "itpl",
        "jayanagar", "hsr layout", "marathahalli", "btm layout", "malleshwaram",
        "rajajinagar", "yelahanka", "hebbal", "banashankari", "jp nagar"
    ]

    for area in known_areas:
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
def get_nearby_gyms(lat, lon, radius=5000):
    """Search for gyms near a location using the Overpass API."""
    overpass_url = "https://overpass-api.de/api/interpreter"
    fallback_gyms = [
        {
            "name": "Sample Gym",
            "address": "Live data unavailable. Please try again shortly.",
            "latitude": lat,
            "longitude": lon,
            "sub_area": "Fallback"
        }
    ]

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
        # Overpass works more reliably when the query is sent as a POST body.
        response = requests.post(
            overpass_url,
            data={"data": query},
            headers={"User-Agent": "FitCore360/1.0", "Accept": "application/json"},
            timeout=15,
        )
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

    except requests.exceptions.Timeout:
        st.warning("The live gym search timed out. Showing a fallback location for now.")
        return fallback_gyms

    except requests.exceptions.RequestException as e:
        st.warning(f"The live gym search is currently unavailable: {e}")
        return fallback_gyms


# --- User input ---
# Restrict the app to Bangalore only with a curated list of sub-areas
st.subheader("City: Bangalore")
st.info("This page searches only within Bangalore. Select a sub-area after searching.")
city_name = "Bangalore"

if st.button("Search gyms"):
    coords = get_coordinates_from_city(city_name)
    if coords is None:
        st.stop()
    lat, lon = coords

    gyms = get_nearby_gyms(lat, lon)

    if not gyms:
        st.info("No gyms were found near this location. Try another city or try again shortly.")
        st.stop()

    # Add a simple sub-area label to each gym result.
    for gym in gyms:
        gym["sub_area"] = infer_sub_area(gym["name"], gym["address"], city_name)

    # --- Show filters for sub-area and gym selection ---
    st.subheader("📍 Choose a gym")

    sub_areas = sorted({gym["sub_area"] for gym in gyms})
    selected_sub_area = st.selectbox("Select Sub-Area", sub_areas)

    area_gyms = [gym for gym in gyms if gym["sub_area"] == selected_sub_area]
    gym_names = [gym["name"] for gym in area_gyms]
    selected_gym_name = st.selectbox("Select Gym", gym_names)
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