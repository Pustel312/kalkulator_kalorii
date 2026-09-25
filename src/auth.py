from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.database import get_db, load_user_by_id
from src.security import decode_access_token


bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_db)
):
    current_token = credentials.credentials

    payload = decode_access_token(current_token)
    user_id = int(payload["sub"])
    current_user = load_user_by_id(session, user_id)

    return current_user