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

class UserProfileWeightGoalRate(str, Enum):
    loss_0_1 = "loss_0_1"
    loss_0_2 = "loss_0_2"
    loss_0_3 = "loss_0_3"
    maintenance = "maintenance"
    gain_0_1 = "gain_0_1"
    gain_0_2 = "gain_0_2"
    gain_0_3 = "gain_0_3"