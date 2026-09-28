from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.database import get_db, load_user_by_id
from src.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_db)
    ):

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    try:
        user_id = int(payload["sub"])
    except (ValueError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )
    current_user = load_user_by_id(session, user_id)
    if not current_user or not current_user.active:
        raise HTTPException(
            status_code=401,
            detail="Invalid user"
        )
    return current_user