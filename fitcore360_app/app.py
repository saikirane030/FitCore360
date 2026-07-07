from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from utils.calculations import calculate_bmi, get_bmi_category, get_health_suggestion
from utils.storage import append_to_csv

# --- WE MOVED THE MATH HERE TO FIX THE IMPORT ERROR ---
def calculate_calories(weight, height, age, goal):
    bmr = (10 * weight) + (6.25 * height) - (5 * age) - 78
    maintenance = bmr * 1.375
    if goal == "Lose Weight":
        return int(maintenance - 500) 
    elif goal == "Gain Weight":
        return int(maintenance + 500) 
    else:
        return int(maintenance) 
# ------------------------------------------------------

st.set_page_config(page_title="FitCore360", layout="centered")

st.title("🏋️ FitCore360 - Fitness Analytics")
st.subheader("Profile & BMI Check")

# --- 1. The Input Form ---
with st.form("profile_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=1, max_value=120, step=1)

    height_feet = st.number_input("Height (feet)", min_value=1.0, max_value=9.0, step=0.1, format="%.1f")
    height = round(height_feet * 30.48, 1)
    height_display = f"{height_feet:.1f} ft"

    weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, step=0.5, format="%.1f")
    submitted = st.form_submit_button("Calculate BMI & Save")

    if submitted:
        st.session_state['user_data'] = {
            "name": name,
            "age": age,
            "height": height,
            "height_display": height_display,
            "height_unit": "ft",
            "weight": weight
        }
        
        bmi = calculate_bmi(weight, height)
        category = get_bmi_category(bmi)
        suggestion = get_health_suggestion(category)
        
        st.session_state['bmi'] = bmi
        st.session_state['category'] = category
        st.session_state['suggestion'] = suggestion
        
        append_to_csv("data/profile_history.csv", st.session_state['user_data'])
        append_to_csv("data/bmi_history.csv", {"bmi": bmi, "category": category})

# --- 2. The Interactive Results Section ---
if 'bmi' in st.session_state:
    st.success("Profile saved successfully!")
    st.metric("Your BMI", st.session_state['bmi'])
    st.info(f"Category: {st.session_state['category']}")
    st.warning(f"Suggestion: {st.session_state['suggestion']}")
    
    st.divider()
    
    st.subheader("🎯 Daily Calorie Goal")
    goal = st.radio("Select your goal:", ["Gain Weight", "Stay Fit", "Lose Weight"], horizontal=True)
    
    ud = st.session_state['user_data']
    target_cals = calculate_calories(ud['weight'], ud['height'], ud['age'], goal)
    
    st.success(f"To **{goal.lower()}**, you should consume approximately **{target_cals} calories** per day.")
    st.markdown(f"**Height entered:** {ud['height_display']}")
    # --- 3. Download Report Feature ---
    st.divider()
    st.subheader("📄 Export Your Plan")
    
    # Format a clean, human-readable text report
    report_text = f"""
    =========================================
           FITCORE360 - HEALTH REPORT
    =========================================
    Name: {ud['name']}
    Age: {ud['age']} years
    Height: {ud['height_display']}
    Weight: {ud['weight']} kg
    
    -----------------------------------------
    YOUR RESULTS:
    BMI: {st.session_state['bmi']} ({st.session_state['category']})
    Goal Selected: {goal}
    Daily Calorie Target: {target_cals} kcal
    
    Recommendation: {st.session_state['suggestion']}
    =========================================
    """
    
    # Streamlit's native download button
    st.download_button(
        label="⬇️ Download Personal Health Report",
        data=report_text,
        file_name=f"{ud['name']}_FitCore_Report.txt",
        mime="text/plain"
    )