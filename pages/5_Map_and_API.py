from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from utils.api import fetch_weather

st.set_page_config(page_title="Map & API Insights", layout="wide")
st.title("🗺️ Bangalore Gym Finder")

st.sidebar.header("Bangalore Areas")
st.sidebar.markdown("Select an area in Bangalore to view gyms in that area.")

# Load gyms data
gyms_path = ROOT / "data" / "gyms.csv"
df_gyms = pd.read_csv(gyms_path)

# Derive area name heuristically: prefer last two words if repeated, else last word
def derive_area(name, candidates_count):
    parts = name.split()
    tail2 = " ".join(parts[-2:]) if len(parts) >= 2 else parts[-1]
    tail1 = parts[-1]
    if candidates_count.get(tail2, 0) >= 3:
        return tail2
    return tail1

# Count tail2 occurrences
tails = [" ".join(n.split()[-2:]) if len(n.split())>=2 else n.split()[-1] for n in df_gyms["Gym"]]
from collections import Counter
tails_count = Counter(tails)

areas = []
areas_map = {}
for name in df_gyms["Gym"]:
    area = derive_area(name, tails_count)
    areas_map.setdefault(area, []).append(name)

areas = sorted(areas_map.keys())

# Keep only Bangalore areas (they are all in the CSV). Provide dropdown.
selected_area = st.sidebar.selectbox("Select area (Bangalore)", options=areas)

# Optional filter for gym name/address within area
search_term = st.sidebar.text_input("Filter gyms (name/address)", value="")

st.write(f"Showing gyms for **{selected_area}**, filtered by: '{search_term}'")

# Filter gyms by derived area
filtered_names = areas_map.get(selected_area, [])
df_area = df_gyms[df_gyms["Gym"].isin(filtered_names)].copy()
if search_term:
    df_area = df_area[df_area["Gym"].str.contains(search_term, case=False, na=False)]

if df_area.empty:
    st.warning("No gyms found for selected area / filter.")
else:
    # Center map on the average location of gyms in area
    center = [df_area["Latitude"].mean(), df_area["Longitude"].mean()]
    m = folium.Map(location=center, zoom_start=13)
    for _, r in df_area.iterrows():
        folium.Marker([r["Latitude"], r["Longitude"]], popup=r["Gym"]).add_to(m)

    st_folium(m, width=900, height=600)
    st.dataframe(df_area)
    csv = df_area.to_csv(index=False).encode("utf-8")
    st.download_button("Download gyms (CSV)", data=csv, file_name=f"gyms_{selected_area}.csv", mime="text/csv")
