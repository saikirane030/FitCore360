from pathlib import Path

import pandas as pd
import streamlit as st

from utils.calculations import calculate_bmi, calculate_calories, get_bmi_category, get_health_suggestion
from utils.storage import append_to_csv
from utils.ui import apply_app_style, insight, page_header

ROOT = Path(__file__).resolve().parent
BMI_HISTORY = ROOT / "data" / "bmi_history.csv"

st.set_page_config(page_title="FitCore 360 | Your wellness, in focus", page_icon="🌿", layout="wide")
apply_app_style()
page_header(
    "FITCORE 360  /  PERSONAL WELLNESS",
    "Build habits. Understand your health.",
    "A practical, data-informed snapshot of your BMI and daily energy needs. Your entries stay in this project’s local CSV files.",
)

left, right = st.columns([1.05, 0.95], gap="large")
with left:
    st.subheader("Your profile")
    st.caption("BMI and calorie estimates below are intended for adults and are not a medical assessment.")
    with st.form("profile_form"):
        name = st.text_input("First name (optional)", max_chars=60)
        age_col, sex_col = st.columns(2)
        with age_col:
            age = st.number_input("Age", min_value=18, max_value=100, value=25, step=1)
        with sex_col:
            sex = st.selectbox("Sex used for calorie estimate", ["Female", "Male"])
        h_col, w_col = st.columns(2)
        with h_col:
            height_feet = st.number_input("Height (feet)", min_value=3.0, max_value=8.0, value=5.7, step=0.1, format="%.1f")
        with w_col:
            weight = st.number_input("Weight (kg)", min_value=25.0, max_value=300.0, value=65.0, step=0.5)
        goal = st.selectbox("Current goal", ["Stay Fit", "Lose Weight", "Gain Weight"])
        submitted = st.form_submit_button("Calculate and save check-in", type="primary", use_container_width=True)

    if submitted:
        height_cm = round(height_feet * 30.48, 1)
        bmi = calculate_bmi(weight, height_cm)
        category = get_bmi_category(bmi)
        profile = {
            "name": name.strip(),
            "age": int(age),
            "sex": sex,
            "height": height_cm,
            "height_display": f"{height_feet:.1f} ft",
            "height_unit": "ft",
            "weight": weight,
        }
        append_to_csv(str(ROOT / "data" / "profile_history.csv"), profile)
        append_to_csv(str(BMI_HISTORY), {"bmi": bmi, "category": category})
        st.session_state["latest_checkin"] = {
            "bmi": bmi,
            "category": category,
            "suggestion": get_health_suggestion(category),
            "profile": profile,
            "goal": goal,
            "calories": calculate_calories(weight, height_cm, int(age), goal, sex),
        }

with right:
    st.subheader("Your latest check-in")
    checkin = st.session_state.get("latest_checkin")
    if checkin:
        st.metric("Body mass index (BMI)", f"{checkin['bmi']:.1f}", help="Weight in kilograms divided by height in metres squared.")
        st.markdown(f"**BMI screening category:** {checkin['category']}")
        st.write(checkin["suggestion"])
        st.metric("Estimated daily energy", f"{checkin['calories']:,} kcal", checkin["goal"])
        st.caption("Estimate assumes light activity (×1.375) and uses the Mifflin–St Jeor equation. Individual needs vary.")
        report = (
            "FITCORE 360 — PERSONAL WELLNESS CHECK-IN\n"
            f"Name: {checkin['profile']['name'] or 'Not provided'}\n"
            f"Age: {checkin['profile']['age']}\n"
            f"Height: {checkin['profile']['height_display']}\n"
            f"Weight: {checkin['profile']['weight']} kg\n"
            f"BMI: {checkin['bmi']:.1f} ({checkin['category']})\n"
            f"Goal: {checkin['goal']}\n"
            f"Estimated daily energy: {checkin['calories']:,} kcal\n\n"
            "Estimates are for general information only and are not medical advice.\n"
        )
        st.download_button("Download your check-in", report, "fitcore360_checkin.txt", mime="text/plain")
    else:
        st.info("Submit your profile to see a personal BMI screening result and an estimated energy target.")
        insight("BMI uses height and weight only; it cannot measure body composition or diagnose health. A qualified health professional can help interpret your results in context.")

st.divider()
st.subheader("Check-in history")
st.caption("A trend is more useful than a single reading. Implausible legacy BMI entries outside 12–60 are excluded from this chart, not deleted.")
if BMI_HISTORY.exists():
    history = pd.read_csv(BMI_HISTORY)
    if {"bmi", "timestamp"}.issubset(history.columns):
        history["bmi"] = pd.to_numeric(history["bmi"], errors="coerce")
        history["timestamp"] = pd.to_datetime(history["timestamp"], errors="coerce")
        valid = history.dropna(subset=["bmi", "timestamp"])
        valid = valid[valid["bmi"].between(12, 60)].sort_values("timestamp")
        excluded_count = len(history) - len(valid)
        if not valid.empty:
            latest = valid.iloc[-1]["bmi"]
            previous = valid.iloc[-2]["bmi"] if len(valid) > 1 else None
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Valid check-ins", len(valid))
            kpi2.metric("Most recent BMI", f"{latest:.1f}", f"{latest - previous:+.1f} vs previous" if previous is not None else None)
            kpi3.metric("Legacy rows excluded", excluded_count)
            chart_data = valid.set_index("timestamp")[["bmi"]]
            st.line_chart(chart_data, color="#517b46", height=280)
            insight(
                f"The chart contains {len(valid)} saved readings after basic plausibility checks. "
                + ("The latest reading is higher than the previous one; this is a change in BMI, not a diagnosis." if previous is not None and latest > previous else
                   "The latest reading is lower than the previous one; short-term changes can reflect measurement variation." if previous is not None and latest < previous else
                   "Only one plausible reading is available, so no direction of change can be inferred.")
                + (f" {excluded_count} older row(s) were omitted because the value or date was invalid." if excluded_count else "")
            )
        else:
            st.info("No plausible, dated BMI check-ins are available yet. Save a profile above to start a clean trend.")
    else:
        st.warning("The saved BMI history is missing the expected columns.")
else:
    st.info("No check-in history yet. Your first saved profile will start the trend.")
