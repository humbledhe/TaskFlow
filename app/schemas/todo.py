from pydantic import BaseModel, ConfigDict, Field, AwareDatetime

from app.enums.todo import TodoPriority


class TodoBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    title: str
    description: str | None
    priority: TodoPriority = TodoPriority.LOW
    due_date: AwareDatetime = Field(
        alias="dueDate",
        description="The date and time when the todo is due, including timezone information",
        examples=["2030-09-30T18:30:00+01:00"],
    )


class TodoCreateModel(TodoBase):
    pass


class TodoUpdateModel(TodoCreateModel):
    is_completed: bool = Field(alias="isCompleted", default=False)


class TodoResponseModel(TodoBase):
    is_completed: bool = Field(alias="isCompleted")
    due_date: AwareDatetime = Field(alias="dueDate")
    created_at: AwareDatetime = Field(alias="createdAt")
    updated_at: AwareDatetime = Field(alias="updateAt")
