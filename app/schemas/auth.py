from pydantic import BaseModel, ConfigDict, Field, EmailStr

from typing import Generic, TypeVar

from .user import UserResponse

T = TypeVar("T")


class AuthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken")
    user: UserResponse


class Response(BaseModel, Generic[T]):
    data: T
