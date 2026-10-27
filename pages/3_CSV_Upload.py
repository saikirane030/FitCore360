import pandas as pd
import streamlit as st
from pathlib import Path

from utils.csv_handler import delete_csv, delete_row_csv, get_uploaded_csv, save_uploaded_csv
from utils.ui import apply_app_style, insight, page_header

ROOT = Path(__file__).resolve().parent.parent
DATASET_FILE = str(ROOT / "data" / "upload_data.csv")

st.set_page_config(page_title="Dataset lab | FitCore 360", page_icon="📊", layout="wide")
apply_app_style()
page_header(
    "FITCORE 360  /  DATASET LAB",
    "Bring your own data. Find the signal.",
    "Upload a CSV, check its structure, and explore how numeric measures vary across records or groups.",
)

uploaded_file = st.file_uploader("Upload a dataset (CSV)", type=["csv"], help="The uploaded dataset is stored locally at data/upload_data.csv.")
if uploaded_file is not None:
    try:
        incoming = pd.read_csv(uploaded_file)
    except (UnicodeDecodeError, pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
        st.error(f"Could not read this file as a CSV: {exc}")
        st.stop()
    if incoming.empty or incoming.columns.empty:
        st.error("This CSV has headers but no data rows. Please upload a file with records.")
        st.stop()
    if incoming.columns.duplicated().any():
        st.error("This CSV has duplicate column names. Rename the repeated headers and upload it again.")
        st.stop()
    save_uploaded_csv(incoming, DATASET_FILE)
    st.session_state["csv_uploaded"] = True
    st.success(f"Loaded {len(incoming):,} records across {len(incoming.columns)} columns.")

df = get_uploaded_csv(DATASET_FILE)
if df is None or df.empty:
    st.info("Upload a CSV to start exploring. The dashboard can analyse numeric columns and their relationship to categories.")
    st.stop()

df = df.copy()
numeric_cols = df.select_dtypes(include="number").columns.tolist()
category_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
missing_cells = int(df.isna().sum().sum())
total_cells = int(df.shape[0] * df.shape[1])

k1, k2, k3, k4 = st.columns(4)
k1.metric("Records", f"{len(df):,}")
k2.metric("Columns", len(df.columns))
k3.metric("Numeric measures", len(numeric_cols))
k4.metric("Missing cells", f"{missing_cells:,}", f"{missing_cells / total_cells:.1%} of all cells" if total_cells else None)

if not numeric_cols:
    st.warning("No numeric columns were detected. Check that measurement columns contain numbers rather than formatted text.")
else:
    st.subheader("Compare a measure")
    measure_col, group_col, aggregate_col = st.columns([1, 1, 1])
    with measure_col:
        measure = st.selectbox("Numeric measure", numeric_cols)
    with group_col:
        grouping = st.selectbox("Break down by", ["No grouping"] + category_cols)
    with aggregate_col:
        aggregation = st.selectbox("Group statistic", ["Mean", "Median", "Sum"])

    series = pd.to_numeric(df[measure], errors="coerce").dropna()
    if series.empty:
        st.warning(f"The selected column '{measure}' has no usable numeric values.")
    else:
        if grouping == "No grouping":
            st.bar_chart(series.reset_index(drop=True).rename_axis("Record").to_frame(measure), color="#668443", height=330)
            insight(
                f"Across {len(series):,} non-empty records, {measure} averages {series.mean():,.2f} "
                f"(median {series.median():,.2f}), with a range of {series.min():,.2f}–{series.max():,.2f}. "
                "Each bar represents a row in the uploaded file."
            )
        else:
            grouped = df.assign(**{measure: pd.to_numeric(df[measure], errors="coerce")}).dropna(subset=[measure, grouping])
            operation = {"Mean": "mean", "Median": "median", "Sum": "sum"}[aggregation]
            grouped_values = grouped.groupby(grouping, observed=True)[measure].agg(operation).sort_values()
            if grouped_values.empty:
                st.warning("No complete numeric/category pairs are available for this comparison.")
            else:
                st.bar_chart(grouped_values.rename_axis(grouping).to_frame(f"{aggregation} {measure}"), color="#668443", height=330)
                highest_group, lowest_group = grouped_values.index[-1], grouped_values.index[0]
                insight(
                    f"For groups with both a category and a numeric value, {highest_group} has the highest "
                    f"{aggregation.lower()} {measure} ({grouped_values.iloc[-1]:,.2f}); "
                    f"{lowest_group} has the lowest ({grouped_values.iloc[0]:,.2f}). "
                    f"This is a descriptive comparison of {len(grouped):,} rows, not evidence that group membership caused the difference."
                )

st.divider()
st.subheader("Data quality & records")
quality_left, quality_right = st.columns([0.75, 1.25])
with quality_left:
    st.markdown("**Missing values by column**")
    missing_by_column = df.isna().sum().sort_values(ascending=False)
    st.dataframe(
        missing_by_column.rename_axis("Column").to_frame("Missing values"),
        hide_index=False,
        use_container_width=True,
    )
with quality_right:
    st.markdown("**Preview**")
    st.dataframe(df.head(100), hide_index=True, use_container_width=True)
    st.caption("Showing up to the first 100 rows for readability.")

with st.expander("Manage saved dataset"):
    delete_col, note_col = st.columns([1, 2])
    with delete_col:
        row_to_delete = st.number_input("Row number to delete (starting at 0)", min_value=0, max_value=max(len(df) - 1, 0), step=1)
        if st.button("Delete selected row", disabled=df.empty):
            delete_row_csv(int(row_to_delete), DATASET_FILE)
            st.rerun()
        if st.button("Delete entire dataset"):
            delete_csv(DATASET_FILE)
            st.session_state["csv_uploaded"] = False
            st.rerun()
    with note_col:
        st.caption("Deletion changes data/upload_data.csv immediately. Keep a separate copy if you need to restore it.")
