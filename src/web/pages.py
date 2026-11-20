from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.api.products import (
    create_product_endpoint,
    get_products,
    search_products_endpoint,
    update_product_endpoint,
    change_product_visibility_endpoint,
    delete_products_endpoint
)
from src.api.users import user_create_endpoint, user_login_endpoint
from src.auth import get_current_user
from src.database.products import load_owned_product_by_id
from src.database.session import get_db
from src.models import User
from src.schemas import ProductCreate, ProductUpdate, UserCreate, UserLogin

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@router.get("/")
def home_page(
    request: Request,
):
    return templates.TemplateResponse(request=request, name="home.html")


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/register")
def register_submit(
    request: Request,
    email: str = Form(),
    password: str = Form(),
    session: Session = Depends(get_db),
):
    credentials = UserCreate(email=email, password=password)
    try:
        user_create_endpoint(user=credentials, session=session)
    except HTTPException as exc:
        if exc.status_code != 409:
            raise
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Konto z tym adresem e-mail juz istnieje."},
            status_code=409,
        )
    return RedirectResponse(url="/login", status_code=303)


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(),
    password: str = Form(),
    session: Session = Depends(get_db),
):
    credentials = UserLogin(email=email, password=password)
    try:
        tokens = user_login_endpoint(user=credentials, session=session)
    except HTTPException as exc:
        if exc.status_code != 401:
            raise
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Nieprawidłowy e-mail lub hasło."},
            status_code=401,
        )

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=tokens["access_token"], httponly=True)
    return response


@router.post("/logout")
def logout_submit():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response


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
        name="products_page.html",
        context={"products": products},
    )


@router.get("/add_product_page")
def add_product_page(request: Request):
    return templates.TemplateResponse(request=request, name="add_product_page.html")


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
            name="add_product_page.html",
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
            name="edit_product_page.html",
            context={
                "error": "Produkt nie istnieje albo nie jest dostępny dla użytkownika"
            },
            status_code=404,
        )
    return templates.TemplateResponse(
        request=request,
        name="edit_product_page.html",
        context={
            "product": product,
            "current_user": current_user
            },
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
                name="edit_product_page.html",
                context={
                    "error": "Produkt o tej nazwie już istnieje!",
                    "product": product_update,
                    "current_user": current_user
                },
                status_code=409,
            )
        elif exc.status_code == 404:
            return templates.TemplateResponse(
                request=request,
                name="edit_product_page.html",
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
    product_id: int,
    is_global: bool = Form(),
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    change_product_visibility_endpoint(
        product_id=product_id,
        is_global=is_global,
        session=session,
        current_user=current_user
        )
    return RedirectResponse(url="/products_page", status_code=303)

@router.post("/edit_product_page/delete/{product_id}")
def delete_product_on_page(
    product_id: int,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    delete_products_endpoint(product_id=product_id, session=session, current_user=current_user)
    return RedirectResponse(url="/products_page", status_code=303)
