from pathlib import Path
from html import escape

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from utils.ui import apply_app_style, insight, page_header

ROOT = Path(__file__).resolve().parent.parent
GYMS_FILE = ROOT / "data" / "gyms.csv"
BRAND_PREFIXES = [
    "Fitness First", "Power World Gym", "Muscle Factory", "Anytime Fitness",
    "Stryv Fitness", "Snap Fitness", "Beast Mode Gym", "Ultimate Fitness",
    "Iron Paradise", "Spartan Fitness", "Gold's Gym", "Cult.fit", "Burn Fitness",
    "Fit Arena", "Elite Fitness",
]

st.set_page_config(page_title="Bengaluru gym directory | FitCore 360", page_icon="📍", layout="wide")
apply_app_style()
page_header(
    "FITCORE 360  /  LOCATION DATA",
    "Explore the Bengaluru gym directory.",
    "Compare the locations and brands included in the project dataset, then inspect the records on a map.",
)

if not GYMS_FILE.exists():
    st.error("The gym directory is missing: data/gyms.csv.")
    st.stop()

gyms = pd.read_csv(GYMS_FILE)
required = {"Gym", "Latitude", "Longitude"}
if not required.issubset(gyms.columns) or gyms.empty:
    st.error("The gym directory needs Gym, Latitude, and Longitude columns with at least one row.")
    st.stop()

gyms["Latitude"] = pd.to_numeric(gyms["Latitude"], errors="coerce")
gyms["Longitude"] = pd.to_numeric(gyms["Longitude"], errors="coerce")
gyms = gyms.dropna(subset=["Gym", "Latitude", "Longitude"]).copy()
gyms = gyms[gyms["Latitude"].between(-90, 90) & gyms["Longitude"].between(-180, 180)]


def split_listing(gym_name):
    normalized_name = str(gym_name).strip()
    for brand in BRAND_PREFIXES:
        if normalized_name.casefold().startswith(brand.casefold()):
            return brand, normalized_name[len(brand):].strip()
    parts = normalized_name.split(maxsplit=1)
    return (parts[0], parts[1] if len(parts) > 1 else "Unspecified")


gyms[["Brand", "Area"]] = pd.DataFrame(gyms["Gym"].apply(split_listing).tolist(), index=gyms.index)
gyms.loc[gyms["Area"].eq(""), "Area"] = "Unspecified"
areas = sorted(gyms["Area"].unique().tolist())

with st.sidebar:
    st.markdown("### Directory filters")
    selected_areas = st.multiselect("Areas", areas, default=areas)
    brands = sorted(gyms["Brand"].unique().tolist())
    selected_brands = st.multiselect("Brands", brands, default=brands)

filtered = gyms[gyms["Area"].isin(selected_areas) & gyms["Brand"].isin(selected_brands)]
directory_total = len(gyms)
top_area = gyms["Area"].value_counts()
top_brand = gyms["Brand"].value_counts()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Directory entries", f"{directory_total:,}")
k2.metric("Areas represented", gyms["Area"].nunique())
k3.metric("Brands represented", gyms["Brand"].nunique())
k4.metric("Shown with filters", len(filtered))
st.caption("Counts describe rows in the bundled CSV, not a complete or independently verified list of Bengaluru gyms.")

if filtered.empty:
    st.warning("No listings match the selected filters. Select at least one area and brand.")
else:
    map_col, chart_col = st.columns([1.2, 0.8], gap="large")
    with map_col:
        st.subheader("Directory locations")
        center = [filtered["Latitude"].mean(), filtered["Longitude"].mean()]
        map_view = folium.Map(location=center, zoom_start=11, tiles="CartoDB positron")
        for _, row in filtered.iterrows():
            folium.CircleMarker(
                location=[row["Latitude"], row["Longitude"]],
                radius=5,
                color="#183b32",
                fill=True,
                fill_color="#d3f36b",
                fill_opacity=0.9,
                popup=escape(f"{row['Gym']} · {row['Area']}"),
            ).add_to(map_view)
        st_folium(map_view, width=None, height=440, use_container_width=True, returned_objects=[])
    with chart_col:
        st.subheader("Listings by area")
        area_counts = filtered.groupby("Area").size().sort_values()
        st.bar_chart(area_counts.rename_axis("Area").to_frame("Listings"), color="#668443", height=330)
        brand_counts = filtered["Brand"].value_counts()
        if not brand_counts.empty:
            insight(
                f"The largest area in the full directory is {top_area.index[0]} "
                f"({top_area.iloc[0]} listings); the most represented brand is {top_brand.index[0]} "
                f"({top_brand.iloc[0]}). This describes directory coverage—not real-world market share."
            )

st.subheader("Dataset scope")
insight(
    "The CSV provides gym names and coordinates, but no prices, membership terms, ratings, facilities, or opening hours. "
    "Map points come directly from the file and have not been independently verified; use this view to explore the dataset, not as a live recommendation."
)

with st.expander("View filtered listing records"):
    st.dataframe(
        filtered[["Gym", "Area", "Brand", "Latitude", "Longitude"]],
        hide_index=True,
        use_container_width=True,
    )
    st.download_button(
        "Download filtered listings",
        filtered[["Gym", "Area", "Latitude", "Longitude"]].to_csv(index=False).encode("utf-8"),
        "fitcore360_gym_directory.csv",
        "text/csv",
    )
