from fastapi import APIRouter, HTTPException, Depends
from src.schemas import LogCreate, LogResponse
from src.math_core import calculate_portion
from src.database.session import get_db
from src.database.products import load_products_by_id
from src.database.logs import create_log, load_log_by_id, load_log_by_date, delete_log
from src.auth import get_current_user
from src.models import User
from sqlalchemy.orm import Session
from datetime import date as Date

router = APIRouter()

# # # # # # # # # # # # # # # # # # # # # # # # LOGS # # # # # # # # # # # # # # # # # # # # # # # #

@router.post("/logs", tags=["Logs"], response_model=LogResponse)
def create_log_endpoint(
    dane: LogCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    product = load_products_by_id(session, dane.product_id, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    portion_data = calculate_portion(product, dane.weight)
    data = Date.today()
    created_log = create_log(
        session=session,
        user_id=current_user.id,
        product_id = dane.product_id,
        product_type = product.type,
        weight=dane.weight,
        protein=portion_data["protein"],
        fat=portion_data["fat"],
        carbs=portion_data["carbs"],
        calories=portion_data["calories"],
        date=data
    )
    return created_log

@router.get("/logs/{entry_id}", response_model=LogResponse, tags=["Logs"])
def get_log_by_id(
    entry_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    log = load_log_by_id(session, entry_id, current_user.id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log 

@router.get("/logs", response_model=list[LogResponse], tags=["Logs"])
def get_logs_by_date(
    target_date: Date,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    logs = load_log_by_date(target_date, session, current_user.id)
    return logs

@router.delete("/logs/{entry_id}", tags=["Logs"])
def delete_logs_endpoint(
    entry_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    deletedL = delete_log(session, entry_id, current_user.id)
    if not deletedL:
        raise HTTPException(status_code=404, detail="Log not found")
    return {"status": "ok", "message": "Log is deleted"}    
