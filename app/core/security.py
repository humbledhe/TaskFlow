import jwt
from pwdlib import PasswordHash

from uuid import uuid7
from typing import Annotated

from .config import settings

password_hash = PasswordHash.recommended()

def hash(password: str) -> str:
    return password_hash.hash(password)


def verify(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)

def create_access_token(user_data: dict, expiry: int, refresh: bool = False) -> str:
    payload = {}
    secret_key = settings.JWT_SECRET_KEY
    algorithm = settings.JWT_ALGORITHM

    payload["user"] = user_data
    payload["exp"] = expiry
    payload["jti"] = str(uuid7())
    payload["refresh"] = refresh

    encoded_jwt = jwt.encode(payload=payload,key=secret_key, algorithm=algorithm)

    return encoded_jwt

def decode_token(token: str) -> dict | None:
    try:
        token_data = jwt.decode(jwt=token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        return token_data
    except jwt.PyJWTError:
        return None