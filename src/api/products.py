from fastapi import APIRouter, HTTPException, Depends
from src.schemas import ProductCreate, ProductResponse, ProductUpdate, ProductCreateComposed, ProductComponentResult
from src.core.math_core import calculate_calories, calculate_components_macro
from src.database.session import get_db
from src.database.products import create_product, load_products, load_products_by_id, search_products, update_product, delete_product, load_components, create_component, change_product_visibility
from src.auth import get_current_user
from src.models import User
from sqlalchemy.orm import Session

router = APIRouter()

# # # # # # # # # # # # # # # # # # # # # # # # PRODUCTS # # # # # # # # # # # # # # # # # # # # # # # #

@router.post("/products", tags=["Products"], response_model=ProductResponse)
def create_product_endpoint(
        product: ProductCreate,
        session: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
    ):
    calculated_calories = calculate_calories(
        protein = product.protein,
        fat = product.fat, 
        carbohydrates = product.carbs
        )
    created_product = create_product(
        session=session,
        name=product.name,
        owner_id=current_user.id,
        product_type=product.type,
        protein=product.protein,
        fat=product.fat,
        carbs=product.carbs,
        calories=calculated_calories
    )
    if created_product is None:
        raise HTTPException(
            status_code=409,
            detail="Active product with this name already exists"
        )
    return created_product
@router.get("/products", tags=["Products"], response_model=list[ProductResponse])
def get_products(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    products = load_products(session, current_user.id)
    return products

@router.get("/products/search", tags=["Products"], response_model=list[ProductResponse])
def get_products_by_phrase(
    phrase: str,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    products = search_products(phrase, session, current_user.id)
    return products

@router.patch("/products/{product_id}", tags=["Products"], response_model=ProductResponse)
def update_product_endpoint(
    product_id: int,
    product_update: ProductUpdate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_product = update_product(
        session,
        product_id,
        product_update,
        current_user.id
    )
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product


@router.delete("/products/{product_id}", tags=["Products"])
def delete_products(
    product_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    deleted = delete_product(session, product_id, current_user.id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "ok", "message": "Product is deleted"}

@router.patch("/products/{product_id}/visibility", tags=["Products"])
def change_is_global(
    product_id: int,
    is_global: bool,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    global_or_private = change_product_visibility(
        session=session,
        product_id=product_id,
        is_global=is_global,
        owner_id=current_user.id
    )

    if not global_or_private:
        raise HTTPException(status_code=404, detail="Product not found")

    return global_or_private

# # # # # # # # # # # # # # # # # # # # # # # # COMPONENTS # # # # # # # # # # # # # # # # # # # # # # # #

@router.post("/components/composed", tags=["Components"])
def create_composed_product_endpoint(
    product: ProductCreateComposed,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    product_ids = []
    for component in product.components:
        product_id = component.product_id
        product_ids.append(product_id)
    product_list = load_components(session, product_ids, current_user.id)
    if not product_list:
        raise HTTPException(
            status_code=404,
            detail="One or more components not found"
        )
    macros = calculate_components_macro(product_list=product_list, product=product.components)
    created_product = create_product(
        session=session,
        owner_id=current_user.id,
        name=product.name,
        product_type=product.type,
        protein=macros["protein"],
        fat=macros["fat"],
        carbs=macros["carbs"],
        calories=macros["calories"]
    )

    for component in product.components:
        create_component(
            session=session,
            parent_product_id=created_product.id,
            component_product_id=component.product_id,
            weight=component.weight
        )
    return created_product

@router.get("/products/{product_id}/details", response_model=ProductComponentResult, tags=["Components"])
def get_composed_product_details(
    product_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    product = load_products_by_id(session, product_id, current_user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    components = product.components
    component_list = []
    for component in components:
        weight = component.weight
        component_product = component.component_product
        component_data = {
            "product_id": component_product.id,
            "name": component_product.name,
            "weight": weight
        }
        component_list.append(component_data)
    return {
        "id": product.id,
        "name": product.name,
        "components": component_list
    }