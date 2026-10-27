from pathlib import Path

import pandas as pd
import streamlit as st

from utils.calculations import calculate_calories, get_bmi_category
from utils.ui import apply_app_style, insight, page_header

ROOT = Path(__file__).resolve().parent.parent
UPLOAD_FILE = ROOT / "data" / "upload_data.csv"
BMI_FILE = ROOT / "data" / "bmi_history.csv"

st.set_page_config(page_title="Insights dashboard | FitCore 360", page_icon="📈", layout="wide")
apply_app_style()
page_header(
    "FITCORE 360  /  INSIGHTS",
    "A clearer view of your fitness data.",
    "Explore BMI patterns in the saved profile dataset and your check-in history—with sample sizes and data limitations kept in view.",
)

if not UPLOAD_FILE.exists():
    st.info("No profile dataset is saved yet. Upload a CSV with height, weight, and age fields on the Dataset Lab page.")
    profiles = pd.DataFrame()
else:
    profiles = pd.read_csv(UPLOAD_FILE)

if not profiles.empty:
    normalized = {str(column).strip().casefold(): column for column in profiles.columns}
    height_col = normalized.get("height_cm", normalized.get("height"))
    weight_col = normalized.get("weight_kg", normalized.get("weight"))
    age_col = normalized.get("age")
    gender_col = normalized.get("gender", normalized.get("sex"))
    goal_col = normalized.get("goal")

    if height_col and weight_col:
        profiles["height_cm"] = pd.to_numeric(profiles[height_col], errors="coerce")
        profiles["weight_kg"] = pd.to_numeric(profiles[weight_col], errors="coerce")
        valid = profiles[
            profiles["height_cm"].between(100, 250)
            & profiles["weight_kg"].between(25, 300)
        ].copy()
        valid["BMI"] = valid["weight_kg"] / ((valid["height_cm"] / 100) ** 2)
        valid = valid[valid["BMI"].between(12, 60)].copy()

        if not valid.empty:
            valid["BMI category"] = valid["BMI"].map(get_bmi_category)
            count, avg_bmi = len(valid), valid["BMI"].mean()
            counts_by_category = valid["BMI category"].value_counts().reindex(
                ["Underweight", "Normal", "Overweight", "Obese"], fill_value=0
            )
            sample_label = (
                "The bundled CSV starts with five illustrative example profiles—not real or representative population data. "
                "Upload a properly sourced dataset to replace it. All summaries describe only the currently loaded rows and are not diagnoses."
            )

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Usable profiles", count)
            kpi2.metric("Average BMI", f"{avg_bmi:.1f}")
            kpi3.metric("Most common category", counts_by_category.idxmax())
            kpi4.metric("Rows excluded", len(profiles) - count)
            st.caption(sample_label)

            distribution_col, group_col = st.columns(2, gap="large")
            with distribution_col:
                st.subheader("BMI screening categories")
                st.bar_chart(counts_by_category.rename_axis("Category").to_frame("Profiles"), color="#668443", height=300)
                most_common = counts_by_category.idxmax()
                insight(
                    f"{most_common} is the most frequent category in these {count} usable profiles "
                    f"({counts_by_category[most_common]} records). BMI categories are broad screening ranges and do not account for individual body composition."
                )
            with group_col:
                st.subheader("Average BMI by stated goal")
                if goal_col:
                    grouped = valid.assign(_goal=profiles.loc[valid.index, goal_col]).groupby("_goal", dropna=True)["BMI"].agg(["mean", "count"]).sort_values("mean")
                    if not grouped.empty:
                        st.bar_chart(grouped["mean"].rename_axis("Goal").to_frame("Average BMI"), color="#668443", height=300)
                        low, high = grouped.iloc[0], grouped.iloc[-1]
                        insight(
                            f"The highest group average is {high['mean']:.1f} (n={int(high['count'])}); "
                            f"the lowest is {low['mean']:.1f} (n={int(low['count'])}). Differences describe this dataset only and cannot show that a goal caused a BMI difference."
                        )
                    else:
                        st.info("No usable goal labels are available for this comparison.")
                else:
                    st.info("Add a 'goal' column to compare average BMI across stated goals.")
                    insight("Group comparisons are only shown when the CSV includes a goal field and valid height and weight values.")

            if age_col and gender_col and goal_col:
                with st.expander("Estimated energy needs in this dataset"):
                    st.caption("Calculated per row from age, height, weight, and sex using the Mifflin–St Jeor equation with light activity. These are estimates, not measured intake.")
                    usable = valid.copy()
                    usable["age"] = pd.to_numeric(profiles.loc[usable.index, age_col], errors="coerce")
                    usable["sex"] = profiles.loc[usable.index, gender_col].astype(str)
                    usable["goal"] = profiles.loc[usable.index, goal_col].astype(str)
                    usable = usable[usable["age"].between(18, 100) & usable["sex"].str.casefold().isin(["male", "female"])]
                    if not usable.empty:
                        usable["Estimated kcal/day"] = usable.apply(
                            lambda row: calculate_calories(
                                row["weight_kg"], row["height_cm"], int(row["age"]),
                                "Gain Weight" if "gain" in row["goal"].casefold() else
                                "Lose Weight" if "lose" in row["goal"].casefold() else "Stay Fit",
                                "Male" if row["sex"].casefold() == "male" else "Female",
                            ),
                            axis=1,
                        )
                        st.metric("Average estimated target", f"{usable['Estimated kcal/day'].mean():,.0f} kcal/day")
                    else:
                        st.info("The dataset has no rows with a valid adult age and Male/Female sex value for this estimate.")
        else:
            st.warning("No profiles have plausible height and weight values (height 100–250 cm, weight 25–300 kg, BMI 12–60).")
    else:
        st.info("The saved profile dataset needs 'height' and 'weight' columns (centimetres and kilograms) to calculate BMI.")
else:
    st.info("The profile dataset is empty. Add a CSV on the Dataset Lab page to unlock profile analysis.")

st.divider()
st.subheader("Saved BMI check-ins")
if BMI_FILE.exists():
    history = pd.read_csv(BMI_FILE)
    if {"bmi", "timestamp"}.issubset(history.columns):
        history["bmi"] = pd.to_numeric(history["bmi"], errors="coerce")
        history["timestamp"] = pd.to_datetime(history["timestamp"], errors="coerce")
        valid_history = history.dropna(subset=["bmi", "timestamp"])
        valid_history = valid_history[valid_history["bmi"].between(12, 60)].sort_values("timestamp")
        invalid_count = len(history) - len(valid_history)
        if not valid_history.empty:
            st.line_chart(valid_history.set_index("timestamp")[["bmi"]], color="#668443", height=280)
            latest = valid_history.iloc[-1]["bmi"]
            previous = valid_history.iloc[-2]["bmi"] if len(valid_history) > 1 else None
            direction = f" The most recent reading changed by {latest - previous:+.1f} from the previous one." if previous is not None else " Only one reading is available."
            insight(
                f"This trend shows {len(valid_history)} plausible dated check-ins; {invalid_count} malformed or implausible legacy record(s) were omitted without changing the saved file."
                + direction
            )
        else:
            st.info("No plausible, dated BMI check-ins are available yet.")
    else:
        st.warning("The saved BMI history is missing the expected columns.")
else:
    st.info("No saved check-ins yet. Save a profile on the home page to start tracking.")
