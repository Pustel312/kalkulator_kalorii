from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.auth import get_current_user, get_refresh_user
from src.database.session import get_db
from src.database.users import (
    create_user,
    create_userprofile,
    load_user_by_email,
    load_userprofile_by_user_id,
    update_userprofile,
)
from src.models import User
from src.schemas import (
    UserCreate,
    UserLogin,
    UserProfileCreate,
    UserProfileResponse,
    UserProfileUpdate,
    UserResponse,
)
from src.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

router = APIRouter(tags=["Users"])


# # # # # # # # # # # # # # # # # # # # # # # # USERS # # # # # # # # # # # # # # # # # # # # # # # #
@router.post("/users/register", response_model=UserResponse)
def user_create_endpoint(user: UserCreate, session: Session = Depends(get_db)):
    check_user = load_user_by_email(session=session, email=user.email)
    if check_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    hashed_password = hash_password(user.password)
    try:
        new_user = create_user(
            session=session, email=user.email, password_hash=hashed_password
        )
        session.commit()
        return new_user
    except Exception:
        session.rollback()
        raise


@router.post("/users/login")
def user_login_endpoint(user: UserLogin, session: Session = Depends(get_db)):
    check_user = load_user_by_email(session=session, email=user.email)
    if not check_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    password_valid = verify_password(user.password, check_user.password_hash)
    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access = create_access_token(check_user.id)
    refresh = create_refresh_token(check_user.id)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


@router.get("/users/me", response_model=UserResponse)
def get_current_user_endpoint(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/users/token/access")
def access_token_endpoint(
    form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)
):
    check_user = load_user_by_email(session=session, email=form_data.username)
    if not check_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    password_valid = verify_password(form_data.password, check_user.password_hash)
    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(check_user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users/token/refresh")
def refresh_token_endpoint(
    refresh_user: User = Depends(get_refresh_user),
):
    access_token = create_access_token(refresh_user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users/me/profile", response_model=UserProfileResponse)
def create_userprofile_endpoint(
    userprofile: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
):
    check_userprofile = load_userprofile_by_user_id(
        session=session, user_id=current_user.id
    )
    if check_userprofile:
        raise HTTPException(status_code=409, detail="UserProfile already exist.")
    try:
        new_userprofile = create_userprofile(
            session,
            userprofile.sex,
            userprofile.height,
            userprofile.weight,
            userprofile.birth_date,
            userprofile.activity_level,
            userprofile.goal,
            current_user.id,
        )
        session.commit()
        return new_userprofile
    except Exception:
        session.rollback()
        raise


@router.get("/users/me/profile", response_model=UserProfileResponse)
def get_userprofile(
    session: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    userprofile = load_userprofile_by_user_id(session=session, user_id=current_user.id)
    if not userprofile:
        raise HTTPException(status_code=404, detail="UserProfile not found.")
    return userprofile


@router.patch("/users/me/profile", response_model=UserProfileResponse)
def update_userprofile_endpoint(
    userprofile_update: UserProfileUpdate,
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated_userprofile = update_userprofile(
            session=session,
            user_id=current_user.id,
            userprofile_update=userprofile_update,
        )
        if not updated_userprofile:
            raise HTTPException(status_code=404, detail="UserProfile not found")
        session.commit()
        return updated_userprofile
    except Exception:
        session.rollback()
        raise
