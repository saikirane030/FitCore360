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
    
    if st.button("Add to Tracker"):
        display_name = f"{selected_food}  |  {servings}X"
        record = {"food": display_name, "calories": total_calories}
        append_to_csv(history_path, record)
        st.success("Added successfully!")
        st.rerun() # Instantly refreshes the page to show the new item below
else:
    st.error("Food database 'food_data.csv' not found in the 'data/' folder.")


st.divider()


# --- Bottom Section: Tracker Log & Memory ---
st.subheader("🍽️ Today's Log")

if os.path.exists(history_path):
    history_df = pd.read_csv(history_path)
    
    if not history_df.empty:
        # Loop through the CSV and display each item cleanly
        for index, row in history_df.iterrows():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**{row['food']}**")
            with col2:
                st.write(f"{row['calories']} kcal")
            with col3:
                # Unique key for every button so Streamlit knows which one you clicked
                if st.button("❌ Remove", key=f"del_{index}"):
                    delete_nutrition_entry(index)
                    st.rerun()
        
        # Show the grand total at the bottom
        st.divider()
        total_cals_today = history_df['calories'].sum()
        st.metric("🔥 Total Calories Consumed", f"{total_cals_today} kcal")
        
    else:
        st.write("Your tracker is empty. Add some food above!")
else:
    st.write("Your tracker is empty. Add some food above!")