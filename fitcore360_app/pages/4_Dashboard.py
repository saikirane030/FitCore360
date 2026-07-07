import streamlit as st
import pandas as pd
import os

st.title("📊 Analytics Dashboard")

# Path to the data saved by the CSV Upload page
csv_path = "data/upload_data.csv"

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)

    if not df.empty:
        # --- 1. AUTO-CALCULATION ENGINE ---
        # Automatically generate metrics if they are missing
        if 'Weight_kg' in df.columns and 'Height_cm' in df.columns and 'BMI' not in df.columns:
            df['BMI'] = round(df['Weight_kg'] / ((df['Height_cm'] / 100) ** 2), 2)
            
        if 'Weight_kg' in df.columns and 'Height_cm' in df.columns and 'Age' in df.columns and 'Daily_Calories' not in df.columns:
            bmr = (10 * df['Weight_kg']) + (6.25 * df['Height_cm']) - (5 * df['Age']) - 78
            df['Daily_Calories'] = (bmr * 1.375).astype(int)

        st.success(f"Dataset loaded ({len(df)} records). Analytics ready! 🚀")
        
        # --- 2. CHARTING SECTION ---
        numeric_cols = df.select_dtypes(include=['float64', 'int64', 'int32']).columns.tolist()
        all_cols = df.columns.tolist()

        if len(numeric_cols) > 0:
            st.subheader("📈 Custom Chart Explorer")
            col1, col2, col3 = st.columns(3)
            with col1:
                chart_type = st.selectbox("Chart Type", ["Scatter Plot", "Bar Chart", "Line Chart"])
            with col2:
                x_axis = st.selectbox("X-Axis", all_cols)
            with col3:
                y_axis = st.selectbox("Y-Axis", numeric_cols)

            # Render selected chart
            if chart_type == "Scatter Plot":
                st.scatter_chart(data=df, x=x_axis, y=y_axis)
            elif chart_type == "Bar Chart":
                st.bar_chart(data=df, x=x_axis, y=y_axis)
            elif chart_type == "Line Chart":
                st.line_chart(data=df, x=x_axis, y=y_axis)

            # --- 3. INSIGHTS SECTION ---
            st.divider()
            st.subheader("💡 Quick Insights")
            s1, s2, s3 = st.columns(3)
            with s1:
                st.metric(label=f"Avg {y_axis}", value=round(df[y_axis].mean(), 2))
            with s2:
                st.metric(label=f"Max {y_axis}", value=round(df[y_axis].max(), 2))
            with s3:
                st.metric(label=f"Min {y_axis}", value=round(df[y_axis].min(), 2))

            # --- 4. EXPORT REPORT SECTION ---
            st.divider()
            st.subheader("📄 Export Dataset Summary")
            
            # Safe calculation check
            avg_bmi = round(df['BMI'].mean(), 2) if 'BMI' in df.columns else "N/A"
            avg_cals = round(df['Daily_Calories'].mean(), 0) if 'Daily_Calories' in df.columns else "N/A"
            
            summary_text = f"""FITCORE360 DATASET SUMMARY
--------------------------
Total Users: {len(df)}
Average BMI: {avg_bmi}
Average Daily Calories: {avg_cals} kcal
--------------------------
Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d')}
"""
            st.download_button(
                label="⬇️ Download Dataset Summary", 
                data=summary_text, 
                file_name="FitCore_Summary.txt", 
                mime="text/plain"
            )

        else:
            st.warning("No numeric data found to visualize.")
    else:
        st.warning("The uploaded file is empty.")
else:
    st.info("No data found. Please go to the 'CSV Upload' page to upload your file first.")