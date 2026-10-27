from pathlib import Path

import pandas as pd
import streamlit as st

from utils.storage import append_to_csv
from utils.ui import apply_app_style, insight, page_header

ROOT = Path(__file__).resolve().parent.parent
FOOD_FILE = ROOT / "data" / "food_data.csv"
LOG_FILE = ROOT / "data" / "nutrition_history.csv"

st.set_page_config(page_title="Nutrition | FitCore 360", page_icon="🥗", layout="wide")
apply_app_style()
page_header(
    "FITCORE 360  /  NUTRITION",
    "Make your food choices visible.",
    "Explore the project’s food reference, record portions you eat, and review your logged calorie totals over time.",
)

if not FOOD_FILE.exists():
    st.error("The food reference file is missing: data/food_data.csv.")
    st.stop()

foods = pd.read_csv(FOOD_FILE)
required = {"Food", "Quantity", "Unit", "Calories"}
if not required.issubset(foods.columns) or foods.empty:
    st.error("The food reference needs Food, Quantity, Unit, and Calories columns with at least one row.")
    st.stop()

foods["Calories"] = pd.to_numeric(foods["Calories"], errors="coerce")
foods = foods.dropna(subset=["Calories"])

entry_col, summary_col = st.columns([0.95, 1.05], gap="large")
with entry_col:
    st.subheader("Log a food portion")
    with st.container(border=True):
        selected_food = st.selectbox("Food", foods["Food"].tolist())
        food = foods.loc[foods["Food"] == selected_food].iloc[0]
        st.markdown(f"**Reference serving:** {food['Quantity']} {food['Unit']} · **{food['Calories']:.0f} kcal**")
        servings = st.number_input("Servings eaten", min_value=0.25, max_value=20.0, value=1.0, step=0.25)
        calories = round(float(food["Calories"]) * servings)
        st.caption(f"Estimated logged amount: {calories:,} kcal")
        if st.button("Add to food log", type="primary", use_container_width=True):
            append_to_csv(
                str(LOG_FILE),
                {"food": f"{selected_food} ({servings:g} serving{'s' if servings != 1 else ''})", "calories": calories},
            )
            st.success("Food entry saved.")
            st.rerun()

with summary_col:
    st.subheader("Food reference: calorie range")
    plot_foods = foods.sort_values("Calories", ascending=False).head(10).sort_values("Calories")
    st.bar_chart(plot_foods.set_index("Food")[["Calories"]], color="#668443", height=290)
    highest = foods.loc[foods["Calories"].idxmax()]
    lowest = foods.loc[foods["Calories"].idxmin()]
    insight(
        f"Among the listed portions, {highest['Food']} has the most reference calories "
        f"({highest['Calories']:.0f} kcal) and {lowest['Food']} the least ({lowest['Calories']:.0f} kcal). "
        "Portion units differ (for example, 100 g versus one piece), so this is not a like-for-like nutrient comparison."
    )

st.divider()
st.subheader("Your food log")
if LOG_FILE.exists():
    log = pd.read_csv(LOG_FILE)
else:
    log = pd.DataFrame(columns=["food", "calories", "timestamp"])

if not log.empty and not {"food", "calories", "timestamp"}.issubset(log.columns):
    st.error("The saved nutrition log is missing one or more required columns: food, calories, timestamp.")
elif not log.empty:
    log["calories"] = pd.to_numeric(log["calories"], errors="coerce")
    log["timestamp"] = pd.to_datetime(log["timestamp"], errors="coerce")
    log = log.dropna(subset=["calories", "timestamp"]).copy()
    log["day"] = log["timestamp"].dt.date
    daily_totals = log.groupby("day")["calories"].sum().sort_index()
    metric1, metric2, metric3 = st.columns(3)
    metric1.metric("Logged food entries", len(log))
    metric2.metric("Days tracked", len(daily_totals))
    metric3.metric("Most recent day total", f"{daily_totals.iloc[-1]:,.0f} kcal" if not daily_totals.empty else "—")

    if len(daily_totals) > 1:
        st.markdown("**Calories logged per day**")
        st.bar_chart(daily_totals.rename_axis("Date").to_frame("Calories"), color="#668443", height=250)
        insight(
            f"Daily totals range from {daily_totals.min():,.0f} to {daily_totals.max():,.0f} kcal across "
            f"{len(daily_totals)} logged days. These are only foods entered in this tracker—not a complete dietary record."
        )
    elif len(daily_totals) == 1:
        insight("Only one day has been logged so far. Add entries on multiple days to compare trends; unlogged meals are not included.")
    else:
        st.info("No dated food entries are available yet. Add a food above to start your log.")

    if not log.empty:
        st.markdown("**Recent entries**")
        st.dataframe(
            log.sort_values("timestamp", ascending=False)[["timestamp", "food", "calories"]].rename(
                columns={"timestamp": "Logged at", "food": "Food / portion", "calories": "Calories (kcal)"}
            ),
            hide_index=True,
            use_container_width=True,
        )
else:
    st.info("Your food log is empty. The reference chart above uses the bundled food_data.csv values.")
    insight("The reference file contains calories per listed serving only; it has no protein, carbohydrate, fat, or micronutrient data. Calorie totals alone cannot describe diet quality.")
