from fastapi import APIRouter, HTTPException, Depends
from src.schemas import PeriodReport, Top3Report, AvgWeightReport
from src.core.math_core import calculate_bmr, calculate_tdee, weightgoalratecalc, daily_calories, calculate_macro, calories_comparision, calculate_days
from src.core.periods import calculate_period
from src.database.session import get_db
from src.database.reports import sum_day, report_top_eaten_products, report_average_weight_of_log
from src.database.users import load_userprofile_by_user_id
from src.auth import get_current_user
from src.models import User
from src.enums import PeriodType
from sqlalchemy.orm import Session
from datetime import date as Date


router = APIRouter()

# # # # # # # # # # # # # # # # # # # # # # # # REPORTS # # # # # # # # # # # # # # # # # # # # # # # #

@router.get("/reports/period-summary", response_model=PeriodReport, tags=["Reports"])
def sum_period_endpoint(
    target_date: Date,
    period: PeriodType,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    date_from, date_to = calculate_period(period, target_date)
    days = calculate_days(date_from, date_to)
    raport = sum_day(date_from, date_to, session, current_user.id)
    days_without_logs = days - raport["days_with_logs"]
    if raport["days_with_logs"] > 0:
        avg_calories_per_logged_day = int(raport["calories"] / raport["days_with_logs"])
    else:
        avg_calories_per_logged_day = 0
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
    calories = calories_comparision(target_calories * days, raport["calories"])
    return {
        "period": period,
        "date_from": date_from,
        "date_to": date_to,

        "bmr": bmr,
        "tdee": tdee,

        "target_calories": target_calories * days,
        "remaining_calories": calories["remaining_calories"],
        "exceeded_calories": calories["exceeded_calories"],

        "protein_min": macros["protein_min"]*days,
        "protein_max": macros["protein_max"] * days,
        "protein_eaten": raport["protein"],
        "fat_min": macros["fat_min"] * days,
        "fat_max": macros["fat_max"] * days,
        "fat_eaten": raport["fat"],
        "carbs_min": macros["carbs_min"] * days,
        "carbs_max": macros["carbs_max"] * days,
        "carbs_eaten": raport["carbs"],

        "log_count": raport["log_count"],
        "days_with_logs": raport["days_with_logs"],
        "days_without_logs": days_without_logs,
        "avg_calories_per_logged_day": avg_calories_per_logged_day
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