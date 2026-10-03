from fastapi import Request, status
from fastapi.responses import JSONResponse

from .exceptions import TodoNotFoundError, ConflictError, BadRequestError


async def not_found_error(request: Request, exc: TodoNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )


async def conflict_error(request: Request, exc: ConflictError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)}
    )


async def bad_request_error(request: Request, exc: BadRequestError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
    )
