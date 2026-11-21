from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.api.users import user_create_endpoint, user_login_endpoint
from src.database.session import get_db
from src.schemas import UserCreate, UserLogin

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="users/register.html")


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="users/login.html")


@router.post("/logout")
def logout_submit():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response


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
            name="users/register.html",
            context={"error": "Konto z tym adresem e-mail juz istnieje."},
            status_code=409,
        )
    return RedirectResponse(url="/login", status_code=303)


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
            name="users/login.html",
            context={"error": "Nieprawidłowy e-mail lub hasło."},
            status_code=401,
        )

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=tokens["access_token"], httponly=True)
    return response
