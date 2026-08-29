from src.models import Product, Log, Base
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///kalkulator.db")
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
    stmt = select(Product)
    result = session.execute(stmt)
    products = result.scalars().all()
    return products


def load_products_by_id(session: Session, product_id: int):
    product = session.get(Product, product_id)
    return product

def search_products(
        phrase: str,
        session: Session
):
    stmt = select(Product).where(Product.name.contains(phrase))
    result = session.execute(stmt)
    search_result = result.scalars().all()
    return search_result

def delete_product(session: Session, product_id: int):
    product = session.get(Product, product_id)
    if not product:
        return False
    session.delete(product)
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
    

def delete_log(session: Session, log_id: int):
    log = session.get(Log, log_id)
    if not log:
        return False
    session.delete(log)
    session.commit()
    return True
