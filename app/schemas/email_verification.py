from pydantic import BaseModel, ConfigDict, Field, AwareDatetime, EmailStr

from uuid import UUID


class OTPBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    token_hash: str = Field(alias="tokenHash")


class OTPCreate(OTPBase):
    user_id: int = Field(alias="userId")
    expires_at: AwareDatetime = Field(alias="expiresAt")
    created_at: AwareDatetime = Field(alias="createdAt")


class OTPVerify(BaseModel):
    otp: str
    email: EmailStr


class OTPSend(BaseModel):
    email: EmailStr
    subject: str = "Verify email"
