import streamlit as st
import pandas as pd
import os
import folium
from streamlit_folium import st_folium

st.title("🏋️ Gym Finder")

csv_path = "data/gyms.csv"

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)

    # --- 🧠 Smart Data Processing ---
    # The uploaded CSV doesn't have City/Area columns, so we create them dynamically!
    df['City'] = 'Bangalore' # Since all current data is Bangalore
    
    known_areas = [
        'Koramangala', 'Indiranagar', 'Whitefield', 'Electronic City',
        'ITPL', 'Jayanagar', 'HSR Layout', 'Marathahalli', 'BTM Layout',
        'Malleshwaram', 'Rajajinagar', 'Yelahanka', 'Hebbal',
        'Banashankari', 'JP Nagar'
    ]

    def get_area(gym_name):
        for area in known_areas:
            if area in gym_name:
                return area
        return 'Other Area'

    df['Sub_Area'] = df['Gym'].apply(get_area)

    # --- 🎛️ UI: Cascading Filters ---
    st.subheader("Search for a Gym")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        cities = df['City'].unique().tolist()
        selected_city = st.selectbox("1. Select City", cities)

    # Filter background data by selected City
    city_df = df[df['City'] == selected_city]

    with col2:
        areas = sorted(city_df['Sub_Area'].unique().tolist())
        selected_area = st.selectbox("2. Select Sub-Area", areas)

    # Filter background data by selected Sub Area
    area_df = city_df[city_df['Sub_Area'] == selected_area]

    with col3:
        gyms = sorted(area_df['Gym'].tolist())
        selected_gym = st.selectbox("3. Select Gym", gyms)

    # Get final exact gym record
    final_gym = area_df[area_df['Gym'] == selected_gym].iloc[0]

    st.divider()

    # --- 📍 Display Results ---
    st.subheader("📍 Gym Details")
    
    info_col, map_col = st.columns([1, 2])

    with info_col:
        st.info(f"**Gym Name:**\n{final_gym['Gym']}")
        st.success(f"**Location:**\n{final_gym['Sub_Area']}, {final_gym['City']}")
        st.warning(f"**Coordinates:**\nLat: {final_gym['Latitude']}\nLon: {final_gym['Longitude']}")

    with map_col:
        # Create map zoomed directly onto the selected gym
        m = folium.Map(location=[final_gym['Latitude'], final_gym['Longitude']], zoom_start=15)

        folium.Marker(
            [final_gym['Latitude'], final_gym['Longitude']],
            popup=final_gym['Gym'],
            tooltip="Click for details",
            icon=folium.Icon(color="blue", icon="dumbbell", prefix="fa")
        ).add_to(m)

        st_folium(m, width="100%", height=300)

else:
    st.error("Gym data file not found. Please place 'gyms.csv' inside the 'data/' folder.")