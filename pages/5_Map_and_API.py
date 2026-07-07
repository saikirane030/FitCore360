from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from utils.api import geocode_place, fetch_weather

st.set_page_config(page_title="Map & API Insights", layout="wide")
st.title("🗺️ Map & Live Data")

st.sidebar.header("Location Search & Filters")
query = st.sidebar.text_input("Search place (city, postcode, address)", "London")
limit = st.sidebar.slider("Max results", 1, 20, 8)
show_weather = st.sidebar.checkbox("Show weather KPIs for first result", value=True)

if st.sidebar.button("Search"):
    with st.spinner("Geocoding..."):
        try:
            places = geocode_place(query, limit=limit)
        except Exception as e:
            st.error(f"Geocoding failed: {e}")
            places = []

    if not places:
        st.warning("No places found for that query.")
    else:
        # Build a DataFrame of results
        df = pd.DataFrame([{"name": p.get("display_name", ""), "lat": float(p["lat"]), "lon": float(p["lon"])} for p in places])
        st.write(f"Found {len(df)} places for '{query}'")

        # Show map centered on first place
        center = [df.loc[0, "lat"], df.loc[0, "lon"]]
        m = folium.Map(location=center, zoom_start=12)
        for _, r in df.iterrows():
            folium.Marker([r["lat"], r["lon"]], popup=r["name"]).add_to(m)

        st_folium(m, width=900, height=600)

        # Show table and download
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download search results (CSV)", data=csv, file_name="places.csv", mime="text/csv")

        # Weather KPIs for first result
        if show_weather:
            lat = center[0]; lon = center[1]
            try:
                w = fetch_weather(lat, lon)
                daily = w.get("daily", {})
                temps_max = daily.get("temperature_2m_max", [])
                temps_min = daily.get("temperature_2m_min", [])
                prec = daily.get("precipitation_sum", [])

                col1, col2, col3 = st.columns(3)
                if temps_max:
                    col1.metric("Avg max temp (next days)", f"{sum(temps_max)/len(temps_max):.1f} °C")
                if temps_min:
                    col2.metric("Avg min temp (next days)", f"{sum(temps_min)/len(temps_min):.1f} °C")
                if prec:
                    col3.metric("Total precip (next days)", f"{sum(prec):.1f} mm")
            except Exception as e:
                st.warning(f"Unable to fetch weather: {e}")

else:
    st.info("Enter a place in the sidebar and click Search to geocode and display results.")
