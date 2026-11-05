from datetime import date as Date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.auth import get_current_user
from src.core.math_core import (
    calculate_bmr,
    calculate_days,
    calculate_macro,
    calculate_tdee,
    calories_comparision,
    daily_calories,
    weightgoalratecalc,
)
from src.core.periods import calculate_period
from src.database.reports import (
    report_average_weight_of_log,
    report_top_eaten_products,
    sum_day,
)
from src.database.session import get_db
from src.database.users import load_userprofile_by_user_id
from src.enums import PeriodType
from src.models import User
from src.schemas import AvgWeightReport, PeriodReport, Top3Report

router = APIRouter(tags=["Reports"])

# # # # # # # # # # # # # # # # # # # # # # # # REPORTS # # # # # # # # # # # # # # # # # # # # # # # #


@router.get("/reports/period-summary", response_model=PeriodReport)
def sum_period_endpoint(
    target_date: Date,
    period: PeriodType,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    date_from, date_to = calculate_period(period, target_date)
    days = calculate_days(date_from, date_to)
    report = sum_day(session, date_from, date_to, current_user.id)
    days_without_logs = days - report["days_with_logs"]
    if report["days_with_logs"] > 0:
        avg_calories_per_logged_day = int(report["calories"] / report["days_with_logs"])
    else:
        avg_calories_per_logged_day = 0
    userprofile = load_userprofile_by_user_id(session=session, user_id=current_user.id)
    if not userprofile:
        raise HTTPException(status_code=404, detail="UserProfile not found.")
    bmr = calculate_bmr(
        userprofile.sex, userprofile.weight, userprofile.height, userprofile.birth_date
    )
    tdee = calculate_tdee(bmr, userprofile.activity_level)
    daily_change = weightgoalratecalc(userprofile.goal)
    target_calories = daily_calories(tdee, daily_change)
    macros = calculate_macro(target_calories)
    calories = calories_comparision(target_calories * days, report["calories"])
    return {
        "period": period,
        "date_from": date_from,
        "date_to": date_to,
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_calories * days,
        "remaining_calories": calories["remaining_calories"],
        "exceeded_calories": calories["exceeded_calories"],
        "protein_min": macros["protein_min"] * days,
        "protein_max": macros["protein_max"] * days,
        "protein_eaten": report["protein"],
        "fat_min": macros["fat_min"] * days,
        "fat_max": macros["fat_max"] * days,
        "fat_eaten": report["fat"],
        "carbs_min": macros["carbs_min"] * days,
        "carbs_max": macros["carbs_max"] * days,
        "carbs_eaten": report["carbs"],
        "log_count": report["log_count"],
        "days_with_logs": report["days_with_logs"],
        "days_without_logs": days_without_logs,
        "avg_calories_per_logged_day": avg_calories_per_logged_day,
    }


@router.get("/reports/top", response_model=list[Top3Report])
def report_top_eaten_products_endpoint(
    session: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    report = report_top_eaten_products(session, current_user.id)
    return report


@router.get("/reports/avg", response_model=list[AvgWeightReport])
def report_average_weight_of_log_endpoint(
    session: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    report = report_average_weight_of_log(session, current_user.id)
    return report
