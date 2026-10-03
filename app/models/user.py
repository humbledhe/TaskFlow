from sqlalchemy import Uuid, String, DateTime, func, Boolean, Identity
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime
from uuid import UUID, uuid7

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)

    public_id: Mapped[UUID] = mapped_column("publicId", Uuid, default=uuid7, index=True)

    email: Mapped[str] = mapped_column(unique=True, index=True)

    password_hash: Mapped[str] = mapped_column("passwordHash")

    is_verified: Mapped[bool] = mapped_column("isVerified", default=False)

    created_at: Mapped[datetime] = mapped_column(
        "createdAt", DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        "updatedAt", DateTime(timezone=True), onupdate=func.now()
    )
