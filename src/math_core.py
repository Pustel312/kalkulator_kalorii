from src.models import Product
from src.schemas import ProductComponentCreate
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