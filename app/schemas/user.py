from pydantic import BaseModel, ConfigDict, EmailStr, Field, AwareDatetime

from uuid import UUID
from typing import Generic, TypeVar

T = TypeVar("T")


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    email: EmailStr


class UserCreate(UserBase):
    password_hash: str = Field(alias="passwordHash")


class UserResponse(UserBase):
    public_id: UUID = Field(alias="publicId")
    is_verified: bool = Field(alias="isVerified")
    created_at: AwareDatetime = Field(alias="createdAt")
    updated_at: AwareDatetime | None = Field(alias="updatedAt")


class Response(BaseModel, Generic[T]):
    data: T
