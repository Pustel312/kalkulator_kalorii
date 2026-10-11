from fastapi import APIRouter, HTTPException, Depends
from src.schemas import DailyReport, Top3Report, AvgWeightReport
from src.math_core import calculate_bmr, calculate_tdee, weightgoalratecalc, daily_calories, calculate_macro, calories_comparision
from src.database.session import get_db
from src.database.reports import sum_day, report_top_eaten_products, report_average_weight_of_log
from src.database.users import load_userprofile_by_user_id
from src.auth import get_current_user
from src.models import User
from sqlalchemy.orm import Session
from datetime import date as Date


router = APIRouter()

# # # # # # # # # # # # # # # # # # # # # # # # REPORTS # # # # # # # # # # # # # # # # # # # # # # # #

@router.get("/reports/daily-summary", response_model=DailyReport, tags=["Reports"])
def sum_day_endpoint(
    target_date: Date,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    raport = sum_day(target_date, session, current_user.id)
    userprofile = load_userprofile_by_user_id(session=session, user_id=current_user.id)
    if not userprofile:
        raise HTTPException(
            status_code=404,
            detail="UserProfile not found."
        )
    bmr = calculate_bmr(userprofile.sex, userprofile.weight, userprofile.height, userprofile.birth_date)
    tdee = calculate_tdee(bmr, userprofile.activity_level)
    daily_change = weightgoalratecalc(userprofile.goal)
    target_calories = daily_calories(tdee, daily_change)
    macros = calculate_macro(target_calories)
    calories = calories_comparision(target_calories, raport["calories"])
    return {
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_calories,
        "remaining_calories": calories["remaining_calories"],
        "exceeded_calories": calories["exceeded_calories"],
        "protein_min": macros["protein_min"],
        "protein_max": macros["protein_max"],
        "protein_eaten": raport["protein"],
        "fat_min": macros["fat_min"],
        "fat_max": macros["fat_max"],
        "fat_eaten": raport["fat"],
        "carbs_min": macros["carbs_min"],
        "carbs_max": macros["carbs_max"],
        "carbs_eaten": raport["carbs"],
        "log_count": raport["log_count"]
    }

@router.get("/report/top", response_model=list[Top3Report], tags=["Reports"])
def report_top_eaten_products_endpoint(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    report = report_top_eaten_products(session, current_user.id)
    return report

@router.get("/report/avg", response_model=list[AvgWeightReport], tags=["Reports"])
def report_average_weight_of_log_endpoint(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    report = report_average_weight_of_log(session, current_user.id)
    return report