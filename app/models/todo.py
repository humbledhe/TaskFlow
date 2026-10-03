from sqlalchemy import Uuid, String, Boolean, Enum, DateTime, func, ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column

from uuid import UUID, uuid7
from datetime import datetime

from .base import Base
from app.enums.todo import TodoPriority


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)

    public_id: Mapped[UUID] = mapped_column("publicId", Uuid, default=uuid7, index=True)

    title: Mapped[str] = mapped_column(String(50), index=True)

    description: Mapped[str] = mapped_column(nullable=True)

    is_completed: Mapped[bool] = mapped_column("isCompleted", Boolean, default=False)

    priority: Mapped[TodoPriority] = mapped_column(
        Enum(TodoPriority), default=TodoPriority.LOW
    )

    user_id: Mapped[int] = mapped_column("userId", ForeignKey("users.id"), index=True)

    due_date: Mapped[datetime] = mapped_column("dueDate", DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime(timezone=True), server_default=func.now()
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        "updated_at", DateTime(timezone=True), onupdate=func.now()
    )
