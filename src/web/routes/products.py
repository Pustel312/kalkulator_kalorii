from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.api.products import (
    change_product_visibility_endpoint,
    create_product_endpoint,
    delete_products_endpoint,
    get_products,
    search_products_endpoint,
    update_product_endpoint,
)
from src.auth import get_current_user
from src.database.products import load_owned_product_by_id
from src.database.session import get_db
from src.models import User
from src.schemas import ProductCreate, ProductUpdate

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/add_product_page")
def add_product_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="products/add_product_page.html"
    )


@router.get("/products_page")
def products_page(
    request: Request,
    phrase: str = "",
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    if phrase:
        products = search_products_endpoint(
            phrase=phrase, session=session, current_user=current_user
        )
    else:
        products = get_products(session=session, current_user=current_user)
    return templates.TemplateResponse(
        request=request,
        name="products/products_page.html",
        context={"products": products},
    )


@router.post("/add_product_page")
def add_product_on_page(
    request: Request,
    product: ProductCreate = Form(),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    try:
        create_product_endpoint(
            product=product,
            session=session,
            current_user=current_user,
        )
    except HTTPException as exc:
        if exc.status_code != 409:
            raise
        return templates.TemplateResponse(
            request=request,
            name="products/add_product_page.html",
            context={"error": "Produkt o tej nazwie już istnieje!", "product": product},
            status_code=409,
        )
    return RedirectResponse(url="/products_page", status_code=303)


@router.get("/edit_product_page/{product_id}")
def edit_product_page(
    request: Request,
    product_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    product = load_owned_product_by_id(
        session=session, product_id=product_id, owner_id=current_user.id
    )
    if product is None:
        return templates.TemplateResponse(
            request=request,
            name="products/edit_product_page.html",
            context={
                "error": "Produkt nie istnieje albo nie jest dostępny dla użytkownika"
            },
            status_code=404,
        )
    return templates.TemplateResponse(
        request=request,
        name="products/edit_product_page.html",
        context={"product": product, "current_user": current_user},
    )


@router.post("/edit_product_page/{product_id}")
def edit_product_on_page(
    request: Request,
    product_id: int,
    product_update: ProductUpdate = Form(),
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        update_product_endpoint(
            session=session,
            product_id=product_id,
            product_update=product_update,
            current_user=current_user,
        )
    except HTTPException as exc:
        if exc.status_code == 409:
            return templates.TemplateResponse(
                request=request,
                name="products/edit_product_page.html",
                context={
                    "error": "Produkt o tej nazwie już istnieje!",
                    "product": product_update,
                    "current_user": current_user,
                },
                status_code=409,
            )
        elif exc.status_code == 404:
            return templates.TemplateResponse(
                request=request,
                name="products/edit_product_page.html",
                context={
                    "error": "Produkt nie istnieje albo nie jest dostępny dla użytkownika"
                },
                status_code=404,
            )
        else:
            raise
    return RedirectResponse(url="/products_page", status_code=303)


@router.post("/edit_product_visibility/{product_id}")
def change_product_visibility_on_page(
    request: Request,
    product_id: int,
    is_global: bool = Form(),
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        change_product_visibility_endpoint(
            product_id=product_id,
            is_global=is_global,
            session=session,
            current_user=current_user,
        )
    except HTTPException as exc:
        if exc.status_code == 409:
            if exc.detail == "Global product with this name already exists":
                error = "Produkt globalny o tej nazwie już istnieje!"
            else:
                error = (
                    "Nie można udostępnić produktu, który posiada prywatne składniki!"
                )

            return templates.TemplateResponse(
                request=request,
                name="products/edit_product_page.html",
                context={"error": error},
                status_code=409,
            )
        elif exc.status_code == 404:
            return templates.TemplateResponse(
                request=request,
                name="products/edit_product_page.html",
                context={
                    "error": "Produkt nie istnieje albo nie jest dostępny dla użytkownika"
                },
                status_code=404,
            )
        else:
            raise
    return RedirectResponse(url="/products_page", status_code=303)


@router.post("/edit_product_page/delete/{product_id}")
def delete_product_on_page(
    request: Request,
    product_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        delete_products_endpoint(
            product_id=product_id, session=session, current_user=current_user
        )
    except HTTPException as exc:
        if exc.status_code != 404:
            raise
        return templates.TemplateResponse(
            request=request,
            name="products/edit_product_page.html",
            context={
                "error": "Produkt nie istnieje albo nie jest dostępny dla użytkownika"
            },
            status_code=404,
        )
    return RedirectResponse(url="/products_page", status_code=303)
