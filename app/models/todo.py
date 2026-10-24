from sqlalchemy import (
    Uuid,
    String,
    Boolean,
    Enum,
    Date,
    DateTime,
    func,
    ForeignKey,
    Identity,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from uuid import UUID, uuid7
from datetime import date, datetime

from .base import Base
from app.enums.todo import TodoPriority, TodoStatus


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)

    public_id: Mapped[UUID] = mapped_column("publicId", Uuid, default=uuid7, index=True)

    title: Mapped[str] = mapped_column(String(50), index=True)

    priority: Mapped[TodoPriority] = mapped_column(
        Enum(TodoPriority, name="todo_priority"), default=TodoPriority.LOW
    )

    status: Mapped[TodoStatus] = mapped_column(
        Enum(TodoStatus, name="todo_status"), default=TodoStatus.TODO
    )

    user_id: Mapped[int] = mapped_column("userId", ForeignKey("users.id"), index=True)

    due_date: Mapped[date | None] = mapped_column("dueDate", Date)

    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime(timezone=True), server_default=func.now()
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        "updated_at", DateTime(timezone=True), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="todos", lazy="raise")
