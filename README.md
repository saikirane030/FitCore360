# FitCore360

FitCore360 is a modern fitness analytics web app built with Python and Streamlit. It helps users track their profile, calculate BMI, estimate daily calorie goals, explore nutrition and gym-related insights, and export a personal health report.

This project is designed to showcase practical Python development, data handling, dashboard building, and clean UI design in a portfolio-friendly format.

## Highlights

- BMI calculation based on user input
- Height input in feet for a simple user experience
- Daily calorie goal recommendations for different fitness goals
- Nutrition, gym finder, CSV upload, and dashboard pages
- CSV-based data persistence for simple record keeping
- Downloadable personal health report

## Tech Stack

- Python
- Streamlit
- Pandas
- Folium
- Streamlit-Folium
- FPDF

## Project Structure

- app.py — main Streamlit application entry point
- pages/ — multi-page experience for nutrition, gym finder, CSV upload, and dashboard views
- utils/ — reusable logic for calculations, CSV storage, and data handling
- data/ — sample datasets used by the app

## Features

### 1. Profile & BMI Analysis
Users can enter their name, age, weight, and height to calculate BMI and receive a health category suggestion.

### 2. Calorie Goal Planning
The app recommends an approximate daily calorie target based on user goals such as gain, maintain, or lose weight.

### 3. Multi-Page Fitness Experience
The app includes additional pages for nutrition planning, gym discovery, CSV upload, and a dashboard view.

### 4. Report Export
Users can download a personal health summary report for their profile.

## Installation

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run the App

```bash
streamlit run app.py
```

Then open the local URL shown in the terminal.

## How It Works

1. The user enters personal details in the main form.
2. The app converts the entered height and calculates BMI.
3. The app estimates calorie needs based on the selected fitness goal.
4. The results are displayed and saved for future review.

## Future Enhancements

- Add user authentication
- Store data in a database instead of CSV files
- Create charts and trend analysis
- Add machine learning-based diet recommendations
- Deploy the app to a cloud platform

## Author

Built by Sai Kiran E.

