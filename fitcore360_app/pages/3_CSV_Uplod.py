from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from utils.csv_handler import save_uploaded_csv, get_uploaded_csv, delete_csv, delete_row_csv

st.title("📂 CSV Upload Module")

uploaded_file = st.file_uploader("Upload your data (CSV)", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    save_uploaded_csv(df)
    st.session_state['csv_uploaded'] = True
    st.success("File uploaded successfully!")

if st.session_state.get('csv_uploaded'):
    df = get_uploaded_csv()
    if df is not None and not df.empty:
        st.dataframe(df)

        col1, col2 = st.columns(2)
        with col1:
            row_to_delete = st.number_input("Row index to delete", min_value=0, max_value=len(df)-1, step=1)
            if st.button("Delete Row"):
                delete_row_csv(row_to_delete)
                st.rerun()
        with col2:
            if st.button("Delete Entire Dataset"):
                delete_csv()
                st.session_state['csv_uploaded'] = False
                st.rerun()