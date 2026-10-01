from sqlalchemy import DateTime, func, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime
from uuid import UUID

from .base import Base


class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[UUID] = mapped_column("userId", ForeignKey("users.id"))

    token_hash: Mapped[str] = mapped_column("tokenHash", String(6))

    expires_at: Mapped[datetime] = mapped_column("expiresAt", DateTime(timezone=True))

    verified_at: Mapped[datetime | None] = mapped_column(
        "verfiedAt", DateTime(timezone=True)
    )

    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime(timezone=True))
