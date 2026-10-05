from enum import Enum

class ProductType(str, Enum):
    ingredient = "ingredient"
    product = "product"
    dish = "dish"

class UserProfileSex(str, Enum):
    male = "male"
    female = "female"

class UserProfileActivityLevel(str, Enum):
    sedentary = "sedentary"
    light = "light"
    moderate = "moderate"
    high = "high"
    very_high = "very_high"

class UserProfileGoal(str, Enum):
    reduction = "reduction"
    maintenance = "maintenance"
    gain = "gain"