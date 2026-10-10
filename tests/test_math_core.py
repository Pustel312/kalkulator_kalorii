import pytest
from src.models import Product
from src.enums import UserProfileSex, UserProfileActivityLevel, UserProfileWeightGoalRate
from src.math_core import calculate_calories, calculate_portion, calculate_bmr, calculate_tdee, weightgoalratecalc, calculate_macro, calories_comparision
from decimal import Decimal
from datetime import date as Date

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

def test_calculate_bmr_male():
    result = calculate_bmr(
        UserProfileSex.male,
        Decimal("90.0"),
        180,
        Date(2003, 6, 25)
    )

    assert result == 1915

def test_calculate_bmr_female():
    result = calculate_bmr(
        UserProfileSex.female,
        Decimal("90.0"),
        180,
        Date(2003, 6, 25)
    )

    assert result == 1749

def test_calculate_tdee():
    bmr = 2000
    result1 = calculate_tdee(bmr, UserProfileActivityLevel.sedentary)
    result2 = calculate_tdee(bmr, UserProfileActivityLevel.light)
    result3 = calculate_tdee(bmr, UserProfileActivityLevel.moderate)
    result4 = calculate_tdee(bmr, UserProfileActivityLevel.high)
    result5 = calculate_tdee(bmr, UserProfileActivityLevel.very_high)

    assert result1 == 2400
    assert result2 == 2750
    assert result3 == 3100
    assert result4 == 3450
    assert result5 == 3800


@pytest.mark.parametrize(
    "factor, expected",
    [
        (UserProfileWeightGoalRate.loss_0_1, Decimal("-110")),
        (UserProfileWeightGoalRate.loss_0_2, Decimal("-220")),
        (UserProfileWeightGoalRate.loss_0_3, Decimal("-330")),
        (UserProfileWeightGoalRate.maintenance, Decimal("0")),
        (UserProfileWeightGoalRate.gain_0_1, Decimal("110")),
        (UserProfileWeightGoalRate.gain_0_2, Decimal("220")),
        (UserProfileWeightGoalRate.gain_0_3, Decimal("330")),
    ]
)
def test_weightgoalratecalc(factor, expected):
    assert weightgoalratecalc(factor) == expected

def test_calculate_macro():
    target_calories = 3000

    calc = calculate_macro(target_calories)

    assert calc["protein_min"] == 112
    assert calc["protein_max"] == 188
    assert calc["fat_min"] == 67
    assert calc["fat_max"] == 100
    assert calc["carbs_min"] == 338
    assert calc["carbs_max"] == 450

@pytest.mark.parametrize(
    "target, eaten, expected",
    [
        (3000, 2500, {
            "remaining_calories": 500,
            "exceeded_calories": 0
        }),
        (3000, 3000, {
            "remaining_calories": 0,
            "exceeded_calories": 0
        }),
        (3000, 3500, {
            "remaining_calories": 0,
            "exceeded_calories": 500
        }),
    ]
)
def test_calories_comparision(target, eaten, expected):
    assert calories_comparision(target, eaten) == expected