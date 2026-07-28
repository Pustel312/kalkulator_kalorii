def calculate_bmr(weight: float, height: float, age: int, gender: str)->float:
    if gender.lower() == "m":
        bmr =  (10*weight)+(6.25*height)-(5*age)+5
    elif gender.lower() == "k":
        bmr =  (10*weight)+(6.25*height)-(5*age)-161
    else:
        raise ValueError("Niepoprawna płeć. Oczekiwano 'm' lub 'k'.") #Zwraca tekst w przypadku niepoprawnych danych wejsciowych
    return bmr

def calculate_tdee(bmr: float, activity_level: float)->float:
    tdee = bmr*activity_level
    return tdee

def calculate_macronutrients(weight: float, tdee: float)-> tuple[float, float, float]:
    proteins = 2*weight
    fat = 1.2*weight
    carbohydrates = (tdee-((proteins*4)+(fat*9)))/4

    return proteins, fat, carbohydrates

def adjust_calories_for_goal(goal: str, tdee: float)->float:
    if goal == "redukcja":
        return tdee - 300.0
    elif goal == "nadwyzka":
       return tdee + 400.0
    return tdee
