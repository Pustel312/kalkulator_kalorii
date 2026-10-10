from src.models import Product
from src.schemas import ProductComponentCreate
from decimal import Decimal
from datetime import date as Date
from src.enums import UserProfileSex, UserProfileActivityLevel, UserProfileWeightGoalRate

def calculate_calories(protein: float, fat: float, carbohydrates: float) -> float:
    calories = round((protein * 4) + (fat * 9) + (carbohydrates * 4), 2)
    return calories

def calculate_portion(product: Product, weight: float)->dict:
    conversion_factor = weight/100
    porcja = {
            "weight": weight,
            "protein": round(product.protein*conversion_factor, 2),
            "fat": round(product.fat*conversion_factor, 2),
            "carbs": round(product.carbs*conversion_factor, 2),
            "calories": round(product.calories*conversion_factor, 2)
        }
    return porcja

def calculate_components_macro(
        product_list: list[Product],
        components: list[ProductComponentCreate]
    ) -> dict[str, float]:
    portions = []

    for component in components:
        for db_product in product_list:
            if db_product.id == component.product_id:
                portion = calculate_portion(db_product, component.weight)
                portions.append(portion)

    total_protein = 0
    total_fat = 0
    total_carbs = 0
    total_calories = 0

    for portion in portions:
        total_protein += portion["protein"]
        total_fat += portion["fat"]
        total_carbs += portion["carbs"]
        total_calories += portion["calories"]

    total_weight = sum(component.weight for component in components)

    protein = round((total_protein / total_weight) * 100, 2)
    fat = round((total_fat / total_weight) * 100, 2)
    carbs = round((total_carbs / total_weight) * 100, 2)
    calories = round((total_calories / total_weight) * 100, 2)

    return {
        "protein": protein,
        "fat": fat,
        "carbs": carbs,
        "calories": calories
    }   

def calculate_bmr(sex: UserProfileSex, weight: Decimal, height: int, date_birth: Date) -> int:
    today = Date.today()
    age = today.year - date_birth.year
    if (today.month, today.day) < (date_birth.month, date_birth.day):
        age -= 1
    if sex == UserProfileSex.male:
        bmr = ((Decimal("10")*weight)+(Decimal("6.25")*height)-(Decimal("5")*age)+Decimal("5"))
    elif sex == UserProfileSex.female:
        bmr = ((Decimal("10")*weight)+(Decimal("6.25")*height)-(Decimal("5")*age)-Decimal("161"))
    else:
        raise ValueError("Unsupported sex value")
    return round(bmr)

def calculate_tdee(bmr: int, activity_level: UserProfileActivityLevel) -> int:
    activity_factors = {
        UserProfileActivityLevel.sedentary: Decimal("1.2"),
        UserProfileActivityLevel.light: Decimal("1.375"),
        UserProfileActivityLevel.moderate: Decimal("1.55"),
        UserProfileActivityLevel.high: Decimal("1.725"),
        UserProfileActivityLevel.very_high: Decimal("1.9")
    }
    factor = activity_factors[activity_level]
    tdee = bmr*factor
    return round(tdee)

def weightgoalratecalc(weightgoalrate: UserProfileWeightGoalRate) -> Decimal:
    weightgoal_factors = {
        UserProfileWeightGoalRate.loss_0_1: Decimal("-0.1"),
        UserProfileWeightGoalRate.loss_0_2: Decimal("-0.2"),
        UserProfileWeightGoalRate.loss_0_3: Decimal("-0.3"),
        UserProfileWeightGoalRate.maintenance: Decimal("0"),
        UserProfileWeightGoalRate.gain_0_1: Decimal("0.1"),
        UserProfileWeightGoalRate.gain_0_2: Decimal("0.2"),
        UserProfileWeightGoalRate.gain_0_3: Decimal("0.3")
    }
    factor = weightgoal_factors[weightgoalrate]
    if weightgoalrate.value.startswith("loss_") or weightgoalrate.value.startswith("gain_"):
        weekly_change = factor*7700
        daily_change = weekly_change/7
        return daily_change
    else:
        return Decimal("0")

def daily_calories(tdee: int, daily_change: Decimal) -> int:
    target_calories = tdee+daily_change
    return round(target_calories)

def calculate_macro(target_calories: int):
    protein_min = (target_calories*0.15)/4
    protein_max = (target_calories*0.25)/4
    fat_min = (target_calories*0.2)/9
    fat_max = (target_calories*0.3)/9
    carbs_min = (target_calories*0.45)/4
    carbs_max = (target_calories*0.60)/4

    return {
        "protein_min": round(protein_min),
        "protein_max": round(protein_max),
        "fat_min": round(fat_min),
        "fat_max": round(fat_max),
        "carbs_min": round(carbs_min),
        "carbs_max": round(carbs_max),
        
    }

def calories_comparision(target_calories: int, eaten_calories: int) -> int:
    remaining_calories = max(target_calories - eaten_calories, 0)
    exceeded_calories = max(eaten_calories - target_calories, 0)
    return {
        "remaining_calories": round(remaining_calories),
        "exceeded_calories": round(exceeded_calories)
    }