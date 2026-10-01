from email.message import EmailMessage
import aiosmtplib

from app.core.config import settings


async def send_email(*, to: str, body: str, subject: str) -> None:
    message = EmailMessage()

    message["from"] = settings.MAIL_FROM
    message["TO"] = to
    message["SUBJECT"] = subject

    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USERNAME,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )
