from src.models import Product, Log, Base, ProductComponent, User
from src.schemas import ProductUpdate, Top3Report, AvgWeightReport
from src.enums import ProductType
from src.math_core import calculate_calories
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from datetime import date as Date

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)
# # # # # # # # # # # # # # # # # # # # # # # # DATABASE # # # # # # # # # # # # # # # # # # # # # # # #

def get_db():
    with Session(engine) as session:
        yield session

# # # # # # # # # # # # # # # # # # # # # # # # PRODUCTS # # # # # # # # # # # # # # # # # # # # # # # #
def create_product(
        session: Session,
        name: str,
        product_type: ProductType,
        protein: float,
        fat: float,
        carbs: float,
        calories: float,
):
    stmt = select(Product).where(Product.active.is_(True), Product.name == name)
    result = session.execute(stmt)
    existing_product = result.scalar_one_or_none()
    if existing_product:
        return None
    product = Product(
        name=name,
        type=product_type,
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
# # # # # # # # # # # # # # # # # # # # # # # # COMPONENTS # # # # # # # # # # # # # # # # # # # # # # # #
def load_components(session: Session, product_ids: list[int]):
    stmt = select(Product).where(Product.id.in_(product_ids))
    result = session.execute(stmt)
    component = result.scalars().all()
    return component

def create_component(
    session: Session,
    parent_product_id: int,
    component_product_id: int,
    weight: float
    ):
    component = ProductComponent(
        parent_product_id=parent_product_id,
        component_product_id=component_product_id,
        weight=weight
    )
    session.add(component)
    session.commit()
    session.refresh(component)
    return component

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
    date: Date
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
        date=date
        )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log

def load_log_by_id(
    session: Session,
    log_id: int,
    user_id: int
    ):
    stmt = select(Log).where(Log.id == log_id, Log.user_id == user_id)
    result = session.execute(stmt)
    log = result.scalar_one_or_none()
    return log
    

def load_log_by_date(
    date: Date,
    session: Session,
    user_id: int   
    ):
    smtm = select(Log).where(Log.date == date, Log.user_id == user_id)
    result = session.execute(smtm)
    logs = result.scalars().all()
    return logs
    
def delete_log(
    session: Session,
    log_id: int,
    user_id: int
    ):
    stmt = select(Log).where(Log.id == log_id, Log.user_id == user_id)
    result = session.execute(stmt)
    log = result.scalar_one_or_none()
    if not log:
        return False
    session.delete(log)
    session.commit()
    return True

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
    ).join(Product, Log.product_id == Product.id).where(Log.user_id == user_id).group_by(Product.name).order_by(func.count(Log.product_id).desc()).limit(3)
    

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

# # # # # # # # # # # # # # # # # # # # # # # # USERS # # # # # # # # # # # # # # # # # # # # # # # #

def load_user_by_email(session: Session, email: str):
    stmt = select(User).where(User.email == email)
    result = session.execute(stmt)
    user = result.scalar_one_or_none()
    return user

def create_user(session: Session,
    email: str,
    password_hash: str):
    user = User(
        email=email,
        password_hash=password_hash
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def load_user_by_id(session: Session, user_id: int):
    stmt = select(User).where(User.id == user_id)
    result = session.execute(stmt)
    user = result.scalar_one_or_none()
    return user