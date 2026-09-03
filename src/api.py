from fastapi import FastAPI, HTTPException, Depends
from src.schemas import ProductCreate, ProductResponse, ProductUpdate, LogCreate, LogResponse, DailyReport
from src.math_core import calculate_calories, calculate_portion
from src.database import get_db, create_product, load_products, load_products_by_id, search_products, update_product, delete_product,  create_log, load_log_by_id, load_log_by_date, sum_day, delete_log
from sqlalchemy.orm import Session
from datetime import date

# # # # # # # # # # # # # # # # # # # # # # # # FASTAPI # # # # # # # # # # # # # # # # # # # # # # # #

app = FastAPI(
    title="Kalkulator kalorii API",
    description="Backendowa aplikacja REST API"
)

@app.get("/healthcheck", tags=["Check"])
def healthcheck():
    return {"status": "ok", "message": "Server is running smoothly"}


# # # # # # # # # # # # # # # # # # # # # # # # PRODUCTS # # # # # # # # # # # # # # # # # # # # # # # #

@app.post("/products", tags=["Products"], response_model=ProductResponse)
def create_product_endpoint(
        product: ProductCreate,
        session: Session = Depends(get_db)
    ):
    calculated_calories = calculate_calories(
        protein = product.protein,
        fat = product.fat, 
        carbohydrates = product.carbs
        )
    created_product = create_product(
        session=session,
        name=product.name,
        protein=product.protein,
        fat=product.fat,
        carbs=product.carbs,
        calories=calculated_calories
    )
    return created_product
@app.get("/products", tags=["Products"], response_model=list[ProductResponse])
def get_products(session: Session = Depends(get_db)):
    products = load_products(session)
    return products

@app.get("/products/search", tags=["Products"], response_model=list[ProductResponse])
def get_products_by_phrase(
    phrase: str,
    session: Session = Depends(get_db)
    ):
    products = search_products(phrase, session)
    return products

@app.patch("/products/{product_id}", tags=["Products"], response_model=ProductResponse)
def update_product_endpoint(
    product_id: int,
    product_update: ProductUpdate,
    session: Session = Depends(get_db)
):
    updated_product = update_product(
        session,
        product_id,
        product_update
    )
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    return updated_product


@app.delete("/products/{product_id}", tags=["Products"])
def delete_products(
    product_id: int,
    session: Session = Depends(get_db),
    ):
    deleted = delete_product(session, product_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "ok", "message": "Product is deleted"}

# # # # # # # # # # # # # # # # # # # # # # # # LOGS # # # # # # # # # # # # # # # # # # # # # # # #

@app.post("/logs", tags=["Logs"], response_model=LogResponse)
def create_log_endpoint(
    dane: LogCreate,
    session: Session = Depends(get_db)
    ):
    product = load_products_by_id(session, dane.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    portion_data = calculate_portion(product, dane.weight)
    data = str(date.today())
    created_log = create_log(
        session=session,
        product_id = dane.product_id,
        weight=dane.weight,
        protein=portion_data["protein"],
        fat=portion_data["fat"],
        carbs=portion_data["carbs"],
        calories=portion_data["calories"],
        date=data
    )
    return created_log

@app.get("/logs/{entry_id}", response_model=LogResponse, tags=["Logs"])
def get_log_by_id(
    entry_id: int,
    session: Session = Depends(get_db),
    ):
    log = load_log_by_id(session, entry_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log 

@app.get("/logs", response_model=list[LogResponse], tags=["Logs"])
def get_logs_by_date(
    target_date: str,
    session: Session = Depends(get_db)
    ):
    logs = load_log_by_date(target_date, session)
    return logs

@app.delete("/logs/{entry_id}", tags=["Logs"])
def delete_logs_endpoint(
    entry_id: int,
    session: Session = Depends(get_db)

    ):
    deletedL = delete_log(session, entry_id)
    if not deletedL:
        raise HTTPException(status_code=404, detail="Log not found")
    return {"status": "ok", "message": "Log is deleted"}    

# # # # # # # # # # # # # # # # # # # # # # # # REPORTS # # # # # # # # # # # # # # # # # # # # # # # #

@app.get("/reports/daily-summary", response_model=DailyReport, tags=["Reports"])
def sum_day_endpoint(
    target_date: str,
    session: Session = Depends(get_db)
    ):
    raport = sum_day(target_date, session)
    return raport 
