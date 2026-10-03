from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.core.dependencies import get_async_db
from app.schemas.email import OTPVerify, OTPSend
from app.services.email import EmailService

router = APIRouter()

email_service = EmailService()

DbDependency = Annotated[AsyncSession, Depends(get_async_db)]


@router.post("/send-verification-code")
async def send_verification_code(otp_send: OTPSend, session: DbDependency):
    await email_service.send_otp(otp_send, session)


@router.patch("/verify")
async def verify_email_OTP(otp_verify: OTPVerify, session: DbDependency):
    verify_email = await email_service.verify_otp(otp_verify, session)

    return verify_email
