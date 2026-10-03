from fastapi import FastAPI

from app.routes.todo import router as todo_router
from app.routes.user import router as user_router
from app.routes.email_verification import router as email_verification_router
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError
from app.core.exception_handlers import (
    not_found_error,
    conflict_error,
    bad_request_error,
)


app = FastAPI()

app.add_exception_handler(NotFoundError, not_found_error)
app.add_exception_handler(ConflictError, conflict_error)
app.add_exception_handler(BadRequestError, bad_request_error)


app.include_router(todo_router, prefix="/api/v1/todos", tags=["Todo"])
app.include_router(user_router, prefix="/api/v1/users", tags=["User"])
app.include_router(
    email_verification_router,
    prefix="/api/v1/email_verifications",
    tags=["Email Verification"],
)
