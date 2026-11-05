from datetime import date as Date

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.enums import ProductType
from src.models import Log

# # # # # # # # # # # # # # # # # # # # # # # # LOGS # # # # # # # # # # # # # # # # # # # # # # # #


def create_log(
    session: Session,
    user_id: int,
    product_id: int,
    product_type: ProductType,
    weight: float,
    protein: float,
    fat: float,
    carbs: float,
    calories: float,
    date: Date,
):
    log = Log(
        user_id=user_id,
        product_id=product_id,
        product_type=product_type,
        weight=weight,
        protein=protein,
        fat=fat,
        carbs=carbs,
        calories=calories,
        date=date,
    )
    session.add(log)
    session.flush()
    return log


def load_log_by_id(session: Session, log_id: int, user_id: int):
    stmt = select(Log).where(Log.id == log_id, Log.user_id == user_id)
    result = session.execute(stmt)
    log = result.scalar_one_or_none()
    return log


def load_log_by_date(session: Session, date: Date, user_id: int):
    stmt = select(Log).where(Log.date == date, Log.user_id == user_id)
    result = session.execute(stmt)
    logs = result.scalars().all()
    return logs


def delete_log(session: Session, log_id: int, user_id: int):
    stmt = select(Log).where(Log.id == log_id, Log.user_id == user_id)
    result = session.execute(stmt)
    log = result.scalar_one_or_none()
    if not log:
        return False
    session.delete(log)
    session.flush()
    return True
