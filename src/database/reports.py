from src.models import Product, Log
from src.schemas import Top3Report, AvgWeightReport
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from datetime import date as Date

# # # # # # # # # # # # # # # # # # # # # # # # REPORTS # # # # # # # # # # # # # # # # # # # # # # # #

def sum_day(
        target_date: Date,
        session: Session,
        user_id: int
    ):
    result = select(
        func.coalesce(func.sum(Log.calories), 0),
        func.coalesce(func.sum(Log.protein), 0),
        func.coalesce(func.sum(Log.fat), 0),
        func.coalesce(func.sum(Log.carbs), 0),
        func.count(Log.id)
    ).where(Log.date == target_date, Log.user_id == user_id)
    calories, protein, fat, carbs, log_count = session.execute(result).one()
    return {
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs,
        "log_count": log_count
    }

def report_top_eaten_products(session: Session, user_id: int):
    stmt = select(
        Product.name,
        func.count(Log.product_id).label("liczba_logow"),
        func.sum(Log.weight).label("suma_wagi")
    ).join(Product, Log.product_id == Product.id).where(Log.user_id == user_id).group_by(Product.id, Product.name).order_by(func.count(Log.product_id).desc(), Product.id.asc()).limit(3)
    

    result = session.execute(stmt)
    rows = result.all()
    report = []
    for name, number_of_logs, weight_sum in rows:
        report.append(
            Top3Report(
                name = name,
                number_of_logs = number_of_logs,
                weight_sum = weight_sum
            )
        )
    return report

def report_average_weight_of_log(session: Session, user_id: int):
    stmt = select(
        Product.name,
        func.count(Log.id).label("liczba_logow"),
        func.avg(Log.weight).label("srednia_waga")
    ).join(Product, Log.product_id == Product.id).where(Log.user_id == user_id).group_by(Product.name).having(func.count(Log.id) >= 2).order_by(func.avg(Log.weight).desc())
    result = session.execute(stmt)
    rows = result.all()
    report = []
    for name, number_of_logs, weight_avg in rows:
        report.append(
            AvgWeightReport(
                name = name,
                number_of_logs = number_of_logs,
                weight_avg = round(weight_avg, 2)
            )
        )
    return report