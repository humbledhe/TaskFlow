import jwt
from pwdlib import PasswordHash

from typing import Annotated
import hashlib
import hmac

from .config import settings

password_hash = PasswordHash.recommended()


def hash(password: str) -> str:
    return password_hash.hash(password)


def verify(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_jwt_token(user_data: dict) -> str:
    secret_key = settings.JWT_SECRET_KEY
    algorithm = settings.JWT_ALGORITHM

    encoded_jwt = jwt.encode(payload=user_data, key=secret_key, algorithm=algorithm)

    return encoded_jwt


def decode_token(token: str) -> dict | None:
    try:
        token_data = jwt.decode(
            jwt=token, key=settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        return token_data
    except jwt.PyJWTError:
        return None


def hash_otp(otp: str, purpose: str, user_id: str):
    message = f"{purpose}:{user_id}:{otp}"

    return hmac.new(
        settings.OTP_SECRET_KEY.encode(), message.encode(), hashlib.sha256
    ).hexdigest()
