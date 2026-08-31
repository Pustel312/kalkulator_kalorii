import pytest
from src.models import Product
from src.math_core import calculate_calories, calculate_portion

@pytest.mark.parametrize(
    "protein, fat, carbs, expected",
    [
        (10, 5, 20, 165),
        (0, 0, 0, 0),
        (10.11, 5.23, 20.236, 168.45),
    ]
)
def test_calculate_calories(protein, fat, carbs, expected):
    result = calculate_calories(protein, fat, carbs)
    assert result == expected

def test_calculate_portion_default():
    product = Product(
        name="Makaron",
        protein=7,
        fat=2,
        carbs=70,
        calories=350,
        active=True
    )
    result = calculate_portion(product, weight=50)
    assert result["protein"] == 3.5
    assert result["fat"] == 1.0
    assert result["carbs"] == 35.0
    assert result["calories"] == 175.0
    assert result["weight"] == 50

def test_calculate_portion_zero_values():
    product = Product(
        name="Makaron",
        protein=0,
        fat=0,
        carbs=0,
        calories=0,
        active=True
    )
    result = calculate_portion(product, weight=0)
    assert result["protein"] == 0
    assert result["fat"] == 0
    assert result["carbs"] == 0
    assert result["calories"] == 0
    assert result["weight"] == 0