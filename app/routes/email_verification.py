from fastapi import APIRouter, Depends, status, BackgroundTasks, Body
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated
from uuid import UUID

from app.core.dependencies import DbDependency, RedisDependency
from app.schemas.email_verification import OTPVerify, OTPSend
from app.services.email_verification import EmailVerificationService

router = APIRouter()
email_verification_service = EmailVerificationService()


@router.get("/send-verification-code/{user_public_id}")
async def send_verification_code(
    user_public_id: UUID,
    session: DbDependency,
    bg_tasks: BackgroundTasks,
    redis: RedisDependency,
):
    bg_tasks.add_task(
        email_verification_service.send_otp, user_public_id, session, redis
    )


@router.patch("/verify-email-otp/{user_public_id}")
async def verify_email_OTP(
    user_public_id: UUID,
    code: Annotated[str, Body(embed=True)],
    session: DbDependency,
    redis: RedisDependency,
):
    verify_email = await email_verification_service.verify_otp(
        user_public_id=user_public_id, code=code, session=session, redis=redis
    )

    return verify_email
