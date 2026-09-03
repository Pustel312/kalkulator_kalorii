from src.models import Product, Log, Base
from src.schemas import ProductUpdate
from src.math_core import calculate_calories
from sqlalchemy import create_engine, select, event, func
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///kalkulator.db")

@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):    
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()
    
Base.metadata.create_all(engine)
# # # # # # # # # # # # # # # # # # # # # # # # DATABASE # # # # # # # # # # # # # # # # # # # # # # # #

def get_db():
    with Session(engine) as session:
        yield session

# # # # # # # # # # # # # # # # # # # # # # # # PRODUCTS # # # # # # # # # # # # # # # # # # # # # # # #
def create_product(
        session: Session,
        name: str,
        protein: float,
        fat: float,
        carbs: float,
        calories: float,
):
    product = Product(
        name=name,
        protein=protein,
        fat=fat,
        carbs=carbs,
        calories=calories,
        active=True  
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

def load_products(session: Session):
    stmt = select(Product).where(Product.active.is_(True))
    result = session.execute(stmt)
    products = result.scalars().all()
    return products


def load_products_by_id(session: Session, product_id: int):
    stmt = select(Product).where(Product.id == product_id, Product.active.is_(True))
    result = session.execute(stmt)
    product = result.scalar_one_or_none()
    return product

def search_products(
        phrase: str,
        session: Session
):
    stmt = select(Product).where(Product.name.contains(phrase)).where(Product.active.is_(True))
    result = session.execute(stmt)
    search_result = result.scalars().all()
    return search_result

def update_product(session: Session, product_id: int, product_update: ProductUpdate):
    product = load_products_by_id(session, product_id)
    if not product:
        return False
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    if any(field in update_data for field in ["protein", "fat", "carbs"]):
        product.calories = calculate_calories(
        product.protein,
        product.fat,
        product.carbs
    )
    session.commit()
    return product

def delete_product(session: Session, product_id: int):
    product = load_products_by_id(session, product_id)
    if not product:
        return False
    product.active = False
    session.commit()

    return True

# # # # # # # # # # # # # # # # # # # # # # # # LOGS # # # # # # # # # # # # # # # # # # # # # # # #

def create_log(
        session: Session,
        product_id: int,
        weight: float,
        protein: float,
        fat: float,
        carbs: float,
        calories: float,
        date: str
    ):
    log = Log(
        product_id=product_id,
        weight=weight,
        protein=protein,
        fat=fat,
        carbs=carbs,
        calories=calories,
        date=date
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log

def load_log_by_id(session: Session, log_id: int):
    log = session.get(Log, log_id)
    return log
    

def load_log_by_date(
        date: str,
        session: Session
    ):
    smtm = select(Log).where(Log.date == date)
    result = session.execute(smtm)
    logs = result.scalars().all()
    return logs
    
def sum_day(
        target_date: str,
        session: Session
    ):
    result = select(
        func.coalesce(func.sum(Log.calories), 0),
        func.coalesce(func.sum(Log.protein), 0),
        func.coalesce(func.sum(Log.fat), 0),
        func.coalesce(func.sum(Log.carbs), 0),
        func.count(Log.id)
    ).where(Log.date == target_date)
    calories, protein, fat, carbs, log_count = session.execute(result).one()
    return {
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs,
        "log_count": log_count
    }
def delete_log(session: Session, log_id: int):
    log = session.get(Log, log_id)
    if not log:
        return False
    session.delete(log)
    session.commit()
    return True
