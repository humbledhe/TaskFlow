from fastapi import FastAPI

from app.routes.todo import router as todo_router
from app.routes.user import router as user_router
from app.core.exceptions import NotFoundError
from app.core.exception_handlers import not_found_error

app = FastAPI()

app.add_exception_handler(NotFoundError, not_found_error)


app.include_router(todo_router, prefix="/api/v1/todos", tags=["Todo"])
app.include_router(user_router, prefix="/api/v1/users", tags=["User"])
