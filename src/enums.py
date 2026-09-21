from enum import Enum

class ProductType(str, Enum):
    ingredient = "ingredient"
    product = "product"
    dish = "dish"