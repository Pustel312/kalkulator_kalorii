from src.models import User, UserProfile
from src.schemas import UserProfileUpdate
from src.enums import UserProfileActivityLevel, UserProfileWeightGoalRate, UserProfileSex
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date as Date
from decimal import Decimal

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

def create_userprofile(
    sex: UserProfileSex,
    height: int,
    weight: Decimal,
    birth_date: Date,
    activity_level: UserProfileActivityLevel,
    goal: UserProfileWeightGoalRate,
    session: Session,
    user_id: int
    ):
    userprofile = UserProfile(
        user_id=user_id,
        sex=sex,
        height=height,
        weight=weight,
        birth_date=birth_date,
        activity_level=activity_level,
        goal=goal
    )
    session.add(userprofile)
    session.commit()
    session.refresh(userprofile)
    return userprofile

def load_userprofile_by_user_id(session: Session, user_id: int):
    stmt = select(UserProfile).where(UserProfile.user_id == user_id)
    result = session.execute(stmt)
    userprofile = result.scalar_one_or_none()
    return userprofile

def update_userprofile(session: Session, user_id: int, userprofile_update: UserProfileUpdate):
    userprofile = load_userprofile_by_user_id(session, user_id)
    if not userprofile:
        return False
    update_data = userprofile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(userprofile, field, value)
    session.commit()
    session.refresh(userprofile)
    return userprofile
