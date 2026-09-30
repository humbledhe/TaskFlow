from fastapi import Request, status
from fastapi.responses import JSONResponse

from .exceptions import TodoNotFoundError


async def not_found_error(request: Request, exc: TodoNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)}
    )
