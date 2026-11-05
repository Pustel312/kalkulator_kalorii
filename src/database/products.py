from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.core.math_core import calculate_calories
from src.enums import ProductType
from src.models import Product, ProductComponent, ProductRecipe
from src.schemas import ProductRecipeUpdate, ProductUpdate


# # # # # # # # # # # # # # # # # # # # # # # # PRODUCTS # # # # # # # # # # # # # # # # # # # # # # # #
def create_product(
    session: Session,
    name: str,
    owner_id: int,
    product_type: ProductType,
    protein: float,
    fat: float,
    carbs: float,
    calories: float,
):
    stmt = select(Product).where(
        Product.active.is_(True), Product.name == name, Product.owner_id == owner_id
    )
    result = session.execute(stmt)
    existing_product = result.scalar_one_or_none()
    if existing_product:
        return None
    product = Product(
        name=name,
        owner_id=owner_id,
        type=product_type,
        protein=protein,
        fat=fat,
        carbs=carbs,
        calories=calories,
        active=True,
    )
    session.add(product)
    session.flush()
    return product


def load_products(session: Session, owner_id: int):
    stmt = select(Product).where(
        Product.active.is_(True),
        or_(Product.owner_id == owner_id, Product.is_global.is_(True)),
    )
    result = session.execute(stmt)
    products = result.scalars().all()
    return products


def load_products_by_id(session: Session, product_id: int, owner_id: int):
    stmt = select(Product).where(
        Product.id == product_id,
        Product.active.is_(True),
        or_(Product.owner_id == owner_id, Product.is_global.is_(True)),
    )
    result = session.execute(stmt)
    product = result.scalar_one_or_none()
    return product


def load_private_products_by_id(session: Session, product_id: int, owner_id: int):
    stmt = select(Product).where(
        Product.id == product_id,
        Product.active.is_(True),
        Product.owner_id == owner_id,
        Product.is_global.is_(False),
    )
    result = session.execute(stmt)
    product = result.scalar_one_or_none()
    return product


def load_owned_product_by_id(session: Session, product_id: int, owner_id: int):
    stmt = select(Product).where(
        Product.id == product_id, Product.active.is_(True), Product.owner_id == owner_id
    )
    result = session.execute(stmt)
    product = result.scalar_one_or_none()
    return product


def search_products(session: Session, phrase: str, owner_id: int):
    stmt = (
        select(Product)
        .where(Product.name.contains(phrase))
        .where(
            Product.active.is_(True),
            or_(Product.owner_id == owner_id, Product.is_global.is_(True)),
        )
    )
    result = session.execute(stmt)
    search_result = result.scalars().all()
    return search_result


def update_product(
    session: Session, product_id: int, product_update: ProductUpdate, owner_id: int
):
    product = load_private_products_by_id(session, product_id, owner_id)
    if not product:
        return False
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    if any(field in update_data for field in ["protein", "fat", "carbs"]):
        product.calories = calculate_calories(
            product.protein, product.fat, product.carbs
        )
    session.flush()
    return product


def delete_product(session: Session, product_id: int, owner_id: int):
    product = load_private_products_by_id(session, product_id, owner_id)
    if not product:
        return False
    product.active = False
    session.flush()

    return True


def change_product_visibility(
    session: Session, product_id: int, owner_id: int, is_global: bool
):
    product = load_owned_product_by_id(session, product_id, owner_id)
    if not product:
        return False
    if is_global:
        for component in product.components:
            if not component.component_product.is_global:
                return False
    product.is_global = is_global
    session.flush()

    return product


# # # # # # # # # # # # # # # # # # # # # # # # COMPONENTS # # # # # # # # # # # # # # # # # # # # # # # #
def load_components(session: Session, product_ids: list[int], owner_id: int):
    stmt = select(Product).where(
        Product.id.in_(product_ids),
        Product.active.is_(True),
        or_(Product.owner_id == owner_id, Product.is_global.is_(True)),
    )
    result = session.execute(stmt)
    components = result.scalars().all()
    loaded_ids = [product.id for product in components]
    if set(product_ids) != set(loaded_ids):
        return False
    return components


def create_component(
    session: Session, parent_product_id: int, component_product_id: int, weight: float
):
    component = ProductComponent(
        parent_product_id=parent_product_id,
        component_product_id=component_product_id,
        weight=weight,
    )
    session.add(component)
    session.flush()
    return component


# # # # # # # # # # # # # # # # # # # # # # # # RECIPES # # # # # # # # # # # # # # # # # # # # # # # #
def load_recipe_by_product_id(session: Session, owner_id: int, product_id: int):
    existing_product = load_owned_product_by_id(session, product_id, owner_id)
    if not existing_product:
        return None
    stmt = select(ProductRecipe).where(ProductRecipe.product_id == product_id)
    result = session.execute(stmt)
    existing_recipe = result.scalar_one_or_none()
    if not existing_recipe:
        return False
    return existing_recipe


def create_recipe(
    session: Session,
    owner_id: int,
    product_id: int,
    recipe: str,
    servings: int,
    preparation_time: int | None = None,
):
    existing_recipe = load_recipe_by_product_id(session, owner_id, product_id)
    if existing_recipe is None:
        return None
    if existing_recipe:
        return False
    new_recipe = ProductRecipe(
        product_id=product_id,
        recipe=recipe,
        servings=servings,
        preparation_time=preparation_time,
    )
    session.add(new_recipe)
    session.flush()
    return new_recipe


def update_recipe(
    session: Session, owner_id: int, recipe_update: ProductRecipeUpdate, product_id: int
):
    existing_recipe = load_recipe_by_product_id(session, owner_id, product_id)
    if existing_recipe is None:
        return None
    if not existing_recipe:
        return False
    update_data = recipe_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_recipe, field, value)
    session.flush()
    return existing_recipe


def delete_recipe(session: Session, owner_id: int, product_id: int):
    existing_recipe = load_recipe_by_product_id(session, owner_id, product_id)
    if existing_recipe is None:
        return None
    if not existing_recipe:
        return False
    session.delete(existing_recipe)
    session.flush()
    return True
