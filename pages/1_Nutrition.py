from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import os
from utils.storage import append_to_csv

st.title("🍎 Nutrition Tracker")

food_csv_path = "data/food_data.csv"
history_path = "data/nutrition_history.csv"

# --- Helper Function: Delete specific row ---
def delete_nutrition_entry(index_to_drop):
    if os.path.exists(history_path):
        df = pd.read_csv(history_path)
        if index_to_drop in df.index:
            df = df.drop(index_to_drop).reset_index(drop=True)
            df.to_csv(history_path, index=False)

# --- Top Section: Add Food ---
if os.path.exists(food_csv_path):
    food_df = pd.read_csv(food_csv_path)
    
    selected_food = st.selectbox("Select Food Item", food_df['Food'].tolist())
    food_info = food_df[food_df['Food'] == selected_food].iloc[0]
    
    st.info(f"**Portion Size:** {food_info['Quantity']} {food_info['Unit']} = {food_info['Calories']} kcal")
    
    servings = st.number_input("Number of Servings (X)", min_value=0.5, step=0.5, value=1.0)
    total_calories = int(food_info['Calories'] * servings)

    # Determine current user name: prefer session value if available
    current_user = None
    if st.session_state.get('user_data'):
        current_user = st.session_state['user_data'].get('name')

    # If we already have the user's name from the profile, show it and hide the input
    if current_user:
        st.markdown(f"**Name:** {current_user}")
        user_name = current_user
    else:
        user_name = st.text_input("Your name", value="")

    if st.button("Add to Tracker"):
        display_name = f"{selected_food}  |  {servings}X"
        record = {"food": display_name, "calories": total_calories, "name": user_name}
        append_to_csv(history_path, record)
        st.success("Added successfully!")
        st.rerun() # Instantly refreshes the page to show the new item below
else:
    st.error("Food database 'food_data.csv' not found in the 'data/' folder.")


st.divider()


# --- Bottom Section: Tracker Log & Memory ---
st.subheader("🍽️ Today's Log")

from datetime import datetime

today = datetime.now().date()

if os.path.exists(history_path):
    history_df = pd.read_csv(history_path)

    if not history_df.empty:
        # Parse timestamps if present
        if 'timestamp' in history_df.columns:
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'], errors='coerce')
            history_df['date'] = history_df['timestamp'].dt.date
        else:
            history_df['date'] = None

        # Filter entries for today
        mask = history_df['date'] == today

        # If user provided a name, filter by that name
        if 'name' in history_df.columns and user_name:
            mask = mask & (history_df['name'] == user_name)

        todays = history_df[mask]

        if not todays.empty:
            for index, row in todays.iterrows():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{row['food']}**")
                with col2:
                    st.write(f"{row['calories']} kcal")
                with col3:
                    if st.button("❌ Remove", key=f"del_{index}"):
                        delete_nutrition_entry(index)
                        st.rerun()

            st.divider()
            total_cals_today = todays['calories'].sum()
            st.metric("🔥 Total Calories Consumed (today, filtered)", f"{total_cals_today} kcal")
        else:
            st.write("No entries for today for this user. Add some food above!")
    else:
        st.write("Your tracker is empty. Add some food above!")
else:
    st.write("Your tracker is empty. Add some food above!")