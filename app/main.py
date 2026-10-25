from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.todo import router as todo_router
from app.routes.user import router as user_router
from app.routes.email_verification import router as email_verification_router
from app.routes.auth import router as auth_router
from app.core.exceptions import (
    NotFoundError,
    ConflictError,
    BadRequestError,
    AuthorizationError,
    ForbiddenRequestError,
)
from app.core.exception_handlers import (
    not_found_error,
    conflict_error,
    bad_request_error,
    authorization_error,
    forbidden_request_error,
)
from app.database.redis import lifespan
from app.core.config import settings


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=["*"],
)

app.add_exception_handler(NotFoundError, not_found_error)
app.add_exception_handler(ConflictError, conflict_error)
app.add_exception_handler(BadRequestError, bad_request_error)
app.add_exception_handler(AuthorizationError, authorization_error)
app.add_exception_handler(ForbiddenRequestError, forbidden_request_error)


app.include_router(todo_router, prefix="/api/v1/todos", tags=["Todo"])

app.include_router(user_router, prefix="/api/v1/users", tags=["User"])

app.include_router(
    email_verification_router,
    prefix="/api/v1/email_verifications",
    tags=["Email Verification"],
)

app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

if __name__ == "__main__":
    import uvicorn
