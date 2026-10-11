from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import UserCreate, UserResponse, UserLogin, UserProfileCreate, UserProfileResponse, UserProfileUpdate
from src.database.session import get_db
from src.database.users import load_user_by_email, create_user, load_userprofile_by_user_id, create_userprofile, update_userprofile
from src.security import hash_password, verify_password, create_access_token, create_refresh_token
from src.auth import get_current_user, get_refresh_user
from src.models import User
from sqlalchemy.orm import Session

router = APIRouter()

# # # # # # # # # # # # # # # # # # # # # # # # USERS # # # # # # # # # # # # # # # # # # # # # # # #
@router.post("/users/register", tags=["Users"], response_model=UserResponse)
def user_create_endpoint(
    user: UserCreate,
    session: Session = Depends(get_db)
    ):
    check_user = load_user_by_email(
        session=session,
        email=user.email)
    if check_user:
        raise HTTPException(
                    status_code=409,
                    detail="Invalid email or password"
                ) 
    hashed_password = hash_password(user.password)
    new_user = create_user(
        session=session,
        email=user.email,
        password_hash=hashed_password
    )
    return new_user

@router.post("/users/login", tags=["Users"])
def user_login_endpoint(
    user: UserLogin,
    session: Session = Depends(get_db)
    ):
    check_user = load_user_by_email(
        session=session,
        email=user.email
    )
    if not check_user:
        raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                ) 
    verifying = verify_password(user.password, check_user.password_hash)
    if not verifying:
        raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )
    access = create_access_token(check_user.id)
    refresh = create_refresh_token(check_user.id)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer"
    }

@router.get("/users/me", tags=["Users"], response_model=UserResponse)
def get_current_user_endpoint(
    current_user: User = Depends(get_current_user)
    ):
    return current_user

@router.post("/users/token/access", tags=["Users"])
def access_token_endpoint(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_db)
    ):
    check_user = load_user_by_email(
        session=session,
        email=form_data.username
    )
    if not check_user:
        raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                ) 
    verifying = verify_password(form_data.password, check_user.password_hash)
    if not verifying:
        raise HTTPException(
                    status_code=401,
                    detail="Invalid email or password"
                )
    access_token = create_access_token(check_user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/users/token/refresh", tags=["Users"])
def refresh_token_endpoint(
        refresh_user: User = Depends(get_refresh_user),
    ):
    access_token = create_access_token(refresh_user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/users/me/profile", response_model=UserProfileResponse, tags=["Users"])
def create_userprofile_endpoint(
    userprofile: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
    ):
    check_userprofile = load_userprofile_by_user_id(session=session, user_id=current_user.id)
    if check_userprofile:
        raise HTTPException(
            status_code=409,
            detail="UserProfile already exist."
        )
    new_userprofile = create_userprofile(
        userprofile.sex,
        userprofile.height,
        userprofile.weight,
        userprofile.birth_date,
        userprofile.activity_level,
        userprofile.goal,
        session=session,
        user_id=current_user.id,
    )
    return new_userprofile

@router.get("/users/me/profile", response_model=UserProfileResponse, tags=["Users"])
def get_userprofile(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    userprofile = load_userprofile_by_user_id(session=session, user_id=current_user.id)
    if not userprofile:
        raise HTTPException(
            status_code=404,
            detail="UserProfile not found."
        )
    return userprofile

@router.patch("/users/me/profile", response_model=UserProfileResponse, tags=["Users"])
def update_userprofile_endpoint(
    userprofile_update: UserProfileUpdate,    
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ):
    updated_userprofile = update_userprofile(session=session, user_id=current_user.id, userprofile_update=userprofile_update)
    if not updated_userprofile:
        raise HTTPException(status_code=404, detail="UserProfile not found")
    return updated_userprofile

