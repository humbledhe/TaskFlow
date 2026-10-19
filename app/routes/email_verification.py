from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.core.dependencies import DbDependency, RedisDependency
from app.schemas.email_verification import OTPVerify, OTPSend
from app.services.email_verification import EmailVerificationService

router = APIRouter()
email_verification_service = EmailVerificationService()


@router.post("/send-verification-code")
async def send_verification_code(
    otp_send: OTPSend,
    session: DbDependency,
    bg_tasks: BackgroundTasks,
    redis: RedisDependency,
):
    bg_tasks.add_task(email_verification_service.send_otp, otp_send, session, redis)


@router.patch("/verify")
async def verify_email_OTP(
    otp_verify: OTPVerify, session: DbDependency, redis: RedisDependency
):
    verify_email = await email_verification_service.verify_otp(
        otp_verify, session, redis
    )

    return verify_email
