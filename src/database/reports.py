from datetime import date as Date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.models import Log, Product
from src.schemas import AvgWeightReport, Top3Report

# # # # # # # # # # # # # # # # # # # # # # # # REPORTS # # # # # # # # # # # # # # # # # # # # # # # #


def sum_day(session: Session, date_from: Date, date_to: Date, user_id: int):
    stmt = select(
        func.coalesce(func.sum(Log.calories), 0),
        func.coalesce(func.sum(Log.protein), 0),
        func.coalesce(func.sum(Log.fat), 0),
        func.coalesce(func.sum(Log.carbs), 0),
        func.count(Log.id),
        func.count(func.distinct(Log.date)),
    ).where(Log.date.between(date_from, date_to), Log.user_id == user_id)
    calories, protein, fat, carbs, log_count, days_with_logs = session.execute(
        stmt
    ).one()
    return {
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs,
        "log_count": log_count,
        "days_with_logs": days_with_logs,
    }


def report_top_eaten_products(session: Session, user_id: int):
    stmt = (
        select(
            Product.name,
            func.count(Log.product_id).label("number_of_logs"),
            func.sum(Log.weight).label("weight_sum"),
        )
        .join(Product, Log.product_id == Product.id)
        .where(Log.user_id == user_id)
        .group_by(Product.id, Product.name)
        .order_by(func.count(Log.product_id).desc(), Product.id.asc())
        .limit(3)
    )

    result = session.execute(stmt)
    rows = result.all()
    report = []
    for name, number_of_logs, weight_sum in rows:
        report.append(
            Top3Report(name=name, number_of_logs=number_of_logs, weight_sum=weight_sum)
        )
    return report


def report_average_weight_of_log(session: Session, user_id: int):
    stmt = (
        select(
            Product.name,
            func.count(Log.id).label("number_of_logs"),
            func.avg(Log.weight).label("weight_avg"),
        )
        .join(Product, Log.product_id == Product.id)
        .where(Log.user_id == user_id)
        .group_by(Product.id, Product.name)
        .having(func.count(Log.id) >= 2)
        .order_by(func.avg(Log.weight).desc())
    )
    result = session.execute(stmt)
    rows = result.all()
    report = []
    for name, number_of_logs, weight_avg in rows:
        report.append(
            AvgWeightReport(
                name=name,
                number_of_logs=number_of_logs,
                weight_avg=round(weight_avg, 2),
            )
        )
    return report
