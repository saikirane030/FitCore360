# FitCore 360

FitCore 360 is a Streamlit fitness and wellness analytics project. It combines personal BMI check-ins, calorie estimates, a food diary, a Bengaluru gym-directory dataset, and an uploadable CSV analysis page.

## What the project demonstrates

- BMI screening with a dated check-in history and basic data-quality filtering.
- Estimated daily energy needs using the Mifflin–St Jeor equation, with an explicit light-activity assumption.
- A nutrition diary and calorie-reference analysis that explains the limits of the bundled food data.
- Gym-directory filtering, mapping, and area/brand counts, with a clear note that the directory is not independently verified.
- CSV validation, missing-value checks, descriptive statistics, and chart interpretations that distinguish sample patterns from causal or population claims.
- A shared responsive interface using a 60/30/10 visual balance: warm neutral canvas, forest-green structure, and lime accent.

## Data notes

- Profile and nutrition entries are stored in local CSV files under `data/`.
- The bundled profile CSV contains five illustrative example rows, not real or representative population data. Replace it with a properly sourced dataset for a substantive group analysis.
- BMI is a screening measure, not a diagnosis. Historical values outside a broad plausibility range are excluded from trend charts but are not removed from the source files.
- The food reference lists calories per serving only; it does not include macronutrients or micronutrients.
- Gym names and coordinates are read from `data/gyms.csv`; they may be incomplete or unverified.
- Calorie estimates vary between people and are not medical or dietary advice.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## Project structure

- `app.py` — personal profile, BMI check-in, calorie estimate, and check-in trend
- `pages/1_Nutrition.py` — food reference and personal food log
- `pages/2_Location_Insights.py` — gym directory map and area/brand analysis
- `pages/3_CSV_Upload.py` — CSV upload, quality checks, descriptive charts, and row management
- `pages/4_Dashboard.py` — profile-sample and check-in analytics
- `utils/` — calculations, CSV persistence, and shared UI styling
- `data/` — reference data and local CSV history
