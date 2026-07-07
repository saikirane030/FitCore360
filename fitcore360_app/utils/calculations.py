def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 2)

def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obese"

def get_health_suggestion(category):
    if category == "Underweight":
        return "Increase caloric intake with nutrient-dense foods."
    elif category == "Normal":
        return "Maintain your current healthy lifestyle."
    elif category == "Overweight":
        return "Focus on a balanced diet and regular exercise."
    else:
        return "Consult a healthcare provider for a structured plan."

def calculate_calories(weight, height, age, goal):
    # Standard BMR Calculation (Basal Metabolic Rate)
    bmr = (10 * weight) + (6.25 * height) - (5 * age) - 78
    
    # Maintenance calories (assuming light daily activity)
    maintenance = bmr * 1.375
    
    if goal == "Lose Weight":
        return int(maintenance - 500) # 500 calorie deficit
    elif goal == "Gain Weight":
        return int(maintenance + 500) # 500 calorie surplus
    else:
        return int(maintenance) # Stay Fit / Maintain