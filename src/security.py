from pwdlib import PasswordHash

def hash_password(password: str) -> str:
    password_hash = PasswordHash.recommended()
    hashed_password = password_hash.hash(password)
    return hashed_password

def verify_password(password: str, hashed_password: str) -> bool:
    password_hash = PasswordHash.recommended()
    verified_password = password_hash.verify(password, hashed_password)
    return verified_password