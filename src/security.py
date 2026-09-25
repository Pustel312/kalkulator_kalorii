from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_EXPIRE_TIME = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def hash_password(password: str) -> str:
    password_hash = PasswordHash.recommended()
    hashed_password = password_hash.hash(password)
    return hashed_password

def verify_password(password: str, hashed_password: str) -> bool:
    password_hash = PasswordHash.recommended()
    verified_password = password_hash.verify(password, hashed_password)
    return verified_password



def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_TIME)
    payload = {
        "sub": str(user_id),
        "exp": expires_at
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        ALGORITHM
    )
    return token

def decode_access_token(token: str):
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )
    return payload