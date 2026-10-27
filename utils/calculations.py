def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 2)

def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
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

def calculate_calories(weight, height, age, goal, sex="Male"):
    sex_adjustment = 5 if sex == "Male" else -161
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + sex_adjustment
    maintenance = bmr * 1.375
    
    if goal == "Lose Weight":
        return int(maintenance - 500)
    elif goal == "Gain Weight":
        return int(maintenance + 500)
    else:
        return int(maintenance)