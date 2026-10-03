from pydantic import BaseModel, ConfigDict, Field, EmailStr

from typing import Generic, TypeVar

from .user import UserResponse

T = TypeVar("T")


class AuthBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    email: EmailStr
    password_hash: str = Field(alias="passwordHash")


class AuthUser(AuthBase):
    pass


class AuthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")
    user: UserResponse


class Response(BaseModel, Generic[T]):
    data: T