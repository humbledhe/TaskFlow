from pydantic import BaseModel, ConfigDict, Field, AwareDatetime

from uuid import UUID
from datetime import date
from typing import Generic, TypeVar

from app.enums.todo import TodoPriority, TodoStatus

T = TypeVar("T")


class TodoBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    title: str
    status: TodoStatus = TodoStatus.TODO
    priority: TodoPriority = TodoPriority.LOW
    due_date: date = Field(alias="dueDate")


class TodoCreateModel(TodoBase):
    pass


class TodoUpdateModel(TodoCreateModel):
    pass


class TodoResponseModel(TodoBase):
    public_id: UUID = Field(alias="publicId")
    created_at: AwareDatetime = Field(alias="createdAt")
    updated_at: AwareDatetime | None = Field(alias="updateAt")


class Response(BaseModel, Generic[T]):
    data: T


class FilterQuery(BaseModel):
    page_size: int = 6
    page: int = 1
    status: TodoStatus | None = None
