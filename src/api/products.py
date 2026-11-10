from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.auth import get_current_user
from src.core.math_core import (
    calculate_calories,
    calculate_components_macro,
    calculate_standard_portion,
)
from src.database.products import (
    change_product_visibility,
    create_component,
    create_product,
    create_recipe,
    delete_product,
    delete_recipe,
    load_components,
    load_products,
    load_products_by_id,
    load_recipe_by_product_id,
    search_products,
    update_product,
    update_recipe,
)
from src.database.session import get_db
from src.models import User
from src.schemas import (
    ProductComponentResult,
    ProductCreate,
    ProductCreateComposed,
    ProductRecipeCreate,
    ProductRecipeResponse,
    ProductRecipeUpdate,
    ProductResponse,
    ProductUpdate,
)

router = APIRouter()

# # # # # # # # # # # # # # # # # # # # # # # # PRODUCTS # # # # # # # # # # # # # # # # # # # # # # # #


@router.post("/products", tags=["Products"], response_model=ProductResponse)
def create_product_endpoint(
    product: ProductCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    factor = calculate_standard_portion(product.weight)
    protein = product.protein * factor
    fat = product.fat * factor
    carbs = product.carbs * factor
    calculated_calories = calculate_calories(
        protein=protein, fat=fat, carbohydrates=carbs
    )
    try:
        created_product = create_product(
            session=session,
            name=product.name,
            owner_id=current_user.id,
            product_type=product.type,
            protein=protein,
            fat=fat,
            carbs=carbs,
            calories=calculated_calories,
        )
        if created_product is None:
            session.rollback()
            raise HTTPException(
                status_code=409, detail="Active product with this name already exists"
            )
        session.commit()
        return created_product
    except HTTPException:
        raise
    except Exception:
        session.rollback()
        raise


@router.get("/products", tags=["Products"], response_model=list[ProductResponse])
def get_products(
    session: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    products = load_products(session, current_user.id)
    return products


@router.get("/products/search", tags=["Products"], response_model=list[ProductResponse])
def search_products_endpoint(
    phrase: str,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    products = search_products(session, phrase, current_user.id)
    return products


@router.patch(
    "/products/{product_id}", tags=["Products"], response_model=ProductResponse
)
def update_product_endpoint(
    product_id: int,
    product_update: ProductUpdate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated_product = update_product(
            session, product_id, product_update, current_user.id
        )
        if updated_product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        if updated_product is False:
            raise HTTPException(
                status_code=409, detail="Active product with this name already exists"
            )
        session.commit()
        return updated_product
    except Exception:
        session.rollback()
        raise


@router.delete("/products/{product_id}", tags=["Products"])
def delete_products_endpoint(
    product_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        deleted = delete_product(session, product_id, current_user.id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Product not found")
        session.commit()
        return {"status": "ok", "message": "Product is deleted"}
    except Exception:
        session.rollback()
        raise


@router.patch("/products/{product_id}/visibility", tags=["Products"])
def change_product_visibility_endpoint(
    product_id: int,
    is_global: bool,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated_product = change_product_visibility(
            session=session,
            product_id=product_id,
            is_global=is_global,
            owner_id=current_user.id,
        )

        if updated_product is False:
            raise HTTPException(status_code=404, detail="Product not found")
        if updated_product is None:
            raise HTTPException(
                status_code=409, detail="Product contains private components"
            )

        session.commit()
        return updated_product
    except Exception:
        session.rollback()
        raise


# # # # # # # # # # # # # # # # # # # # # # # # COMPONENTS # # # # # # # # # # # # # # # # # # # # # # # #


@router.post("/components/composed", tags=["Components"])
def create_composed_product_endpoint(
    product: ProductCreateComposed,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product_ids = [component.product_id for component in product.components]
    product_list = load_components(session, product_ids, current_user.id)
    if not product_list:
        raise HTTPException(status_code=404, detail="One or more components not found")
    macros = calculate_components_macro(
        product_list=product_list, components=product.components
    )
    try:
        created_product = create_product(
            session=session,
            owner_id=current_user.id,
            name=product.name,
            product_type=product.type,
            protein=macros["protein"],
            fat=macros["fat"],
            carbs=macros["carbs"],
            calories=macros["calories"],
        )
        if not created_product:
            session.rollback()
            raise HTTPException(
                status_code=409, detail="Active product with this name already exists"
            )

        for component in product.components:
            create_component(
                session=session,
                parent_product_id=created_product.id,
                component_product_id=component.product_id,
                weight=component.weight,
            )
        session.commit()
        return created_product
    except HTTPException:
        raise
    except Exception:
        session.rollback()
        raise


@router.get(
    "/products/{product_id}/details",
    response_model=ProductComponentResult,
    tags=["Components"],
)
def get_composed_product_details(
    product_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
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
            "weight": weight,
        }
        component_list.append(component_data)
    return {"id": product.id, "name": product.name, "components": component_list}


# # # # # # # # # # # # # # # # # # # # # # # # RECIPES # # # # # # # # # # # # # # # # # # # # # # # #


@router.post("/recipes", response_model=ProductRecipeResponse, tags=["Recipes"])
def create_recipe_endpoint(
    recipe: ProductRecipeCreate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        created_recipe = create_recipe(
            session=session,
            owner_id=current_user.id,
            product_id=recipe.product_id,
            recipe=recipe.recipe,
            servings=recipe.servings,
            preparation_time=recipe.preparation_time,
        )
        if created_recipe is None:
            raise HTTPException(status_code=404, detail="Product not found")
        if not created_recipe:
            raise HTTPException(status_code=409, detail="Product already has recipe")
        session.commit()
        return created_recipe
    except Exception:
        session.rollback()
        raise


@router.get("/recipes", response_model=ProductRecipeResponse, tags=["Recipes"])
def get_recipe_endpoint(
    product_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_recipe = load_recipe_by_product_id(session, current_user.id, product_id)
    if existing_recipe is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if not existing_recipe:
        raise HTTPException(status_code=404, detail="Product has no recipe")
    return existing_recipe


@router.patch("/recipes", response_model=ProductRecipeResponse, tags=["Recipes"])
def update_recipe_endpoint(
    product_id: int,
    recipe_update: ProductRecipeUpdate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated_recipe = update_recipe(
            session, current_user.id, recipe_update, product_id
        )
        if updated_recipe is None:
            raise HTTPException(status_code=404, detail="Product not found")
        if not updated_recipe:
            raise HTTPException(status_code=404, detail="Product has no recipe")
        session.commit()
        return updated_recipe
    except Exception:
        session.rollback()
        raise


@router.delete("/recipes", tags=["Recipes"])
def delete_recipe_endpoint(
    product_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        deleted_recipe = delete_recipe(session, current_user.id, product_id)
        if deleted_recipe is None:
            raise HTTPException(status_code=404, detail="Product not found")
        if not deleted_recipe:
            raise HTTPException(status_code=404, detail="Product has no recipe")
        session.commit()
        return {"status": "ok", "message": "Recipe is deleted"}
    except Exception:
        session.rollback()
        raise
