from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Location Insights", layout="wide")
st.title("Location Insights — Bengaluru Gyms")

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

areas_map = {}
for name in df_gyms["Gym"]:
    area = derive_area(name, tails_count)
    areas_map.setdefault(area, []).append(name)


# --- Sidebar filters (5 commonly used controls) ---
areas = sorted(areas_map.keys())
selected_area = st.sidebar.selectbox("Select area (Bengaluru)", options=areas)

# Derive brand (first token) for multiselect
def derive_brand(gym_name):
    return gym_name.split()[0]


# Budget tier filter: Budget, Mid-range, Premium
tier_options = ["Budget", "Mid-range", "Premium"]
selected_tiers = st.sidebar.multiselect("Filter by budget tier", options=tier_options, default=tier_options)

# Simple brand -> tier mapping (heuristic)
brand_tier_map = {
    "Gold's": "Premium",
    "Fitness": "Premium",
    "Elite": "Premium",
    "Cult.fit": "Mid-range",
    "Anytime": "Mid-range",
    "Stryv": "Mid-range",
    "Spartan": "Mid-range",
    "Power": "Mid-range",
    "Muscle": "Mid-range",
    "Iron": "Mid-range",
    "Snap": "Budget",
    "Beast": "Budget",
    "Burn": "Budget",
    "Fit": "Budget",
    "Ultimate": "Budget"
}

st.write(f"Showing gyms for **{selected_area}**")

# Filter gyms by derived area
selected_names = areas_map.get(selected_area, [])
df_area = df_gyms[df_gyms["Gym"].isin(selected_names)].copy()

# (previous brand/search filters removed; using budget tiers now)

# Apply budget tier filter using heuristic mapping
def derive_tier_from_brand(brand):
    return brand_tier_map.get(brand, "Mid-range")

if not df_area.empty:
    df_area = df_area[df_area["Gym"].apply(lambda x: derive_tier_from_brand(derive_brand(x)) in selected_tiers)]

if df_area.empty:
    st.warning("No gyms found for selected area.")
else:
    # KPI row
    total_in_area = len(df_gyms[df_gyms["Gym"].isin(areas_map.get(selected_area, []))])
    gyms_shown = len(df_area)
    brands_shown = df_area["Gym"].apply(derive_brand).nunique()
    top_brand = df_area["Gym"].apply(derive_brand).value_counts()
    top_brand_share = 0
    if gyms_shown > 0 and not top_brand.empty:
        top_brand_share = round((top_brand.iloc[0] / gyms_shown) * 100, 1)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Gyms Shown", gyms_shown)
    k2.metric("Total in Area", total_in_area)
    k3.metric("Unique Brands", brands_shown)
    k4.metric("Top Brand Share", f"{top_brand_share}%")

    # Center map on the average location of gyms in area
    center = [df_area["Latitude"].mean(), df_area["Longitude"].mean()]
    m = folium.Map(location=center, zoom_start=13)
    for _, r in df_area.iterrows():
        folium.Marker([r["Latitude"], r["Longitude"]], popup=r["Gym"]).add_to(m)

    st_folium(m, width=900, height=600)
    # Provide an Address column instead of raw latitude/longitude
    df_area = df_area.copy()
    df_area["Address"] = df_area["Gym"] + ", Bengaluru, Karnataka, India"
    st.dataframe(df_area[["Gym", "Address"]])
    csv = df_area[["Gym", "Address"]].to_csv(index=False).encode("utf-8")
    st.download_button("Download gyms (CSV)", data=csv, file_name=f"gyms_{selected_area}.csv", mime="text/csv")
