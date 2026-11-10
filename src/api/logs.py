from datetime import date as Date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.auth import get_current_user
from src.core.math_core import calculate_portion
from src.database.logs import create_log, delete_log, load_log_by_date, load_log_by_id
from src.database.products import load_products_by_id
from src.database.session import get_db
from src.models import User
from src.schemas import LogCreate, LogResponse

router = APIRouter(tags=["Logs"])


@router.post("/logs", response_model=LogResponse)
def create_log_endpoint(
    log_data: LogCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = load_products_by_id(session, log_data.product_id, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    portion_data = calculate_portion(product, log_data.weight)
    current_date = Date.today()
    try:
        created_log = create_log(
            session=session,
            user_id=current_user.id,
            product_id=log_data.product_id,
            product_type=product.type,
            weight=log_data.weight,
            protein=portion_data["protein"],
            fat=portion_data["fat"],
            carbs=portion_data["carbs"],
            calories=portion_data["calories"],
            date=current_date,
        )
        session.commit()
        return created_log
    except Exception:
        session.rollback()
        raise


@router.get("/logs/{entry_id}", response_model=LogResponse)
def get_log_by_id(
    entry_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = load_log_by_id(session, entry_id, current_user.id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log


@router.get("/logs", response_model=list[LogResponse])
def get_logs_by_date(
    target_date: Date,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logs = load_log_by_date(session, target_date, current_user.id)
    return logs


@router.delete("/logs/{entry_id}")
def delete_logs_endpoint(
    entry_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        deleted_log = delete_log(session, entry_id, current_user.id)
        if not deleted_log:
            raise HTTPException(status_code=404, detail="Log not found")
        session.commit()
        return {"status": "ok", "message": "Log is deleted"}
    except Exception:
        session.rollback()
        raise
