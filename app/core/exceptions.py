class TaskFlowError(Exception):
    """Base-class for all application specific exceptions"""


# Not found exceptions
class NotFoundError(TaskFlowError):
    """Base exceptions for resource not found"""


class TodoNotFoundError(NotFoundError):
    """Raised when the requested todo cannot be found"""


class UserNotFoundError(NotFoundError):
    """Raised when the requested user cannot be found"""


# Conflict exceptions
class ConflictError(TaskFlowError):
    """Base exceptions for resource conflicts"""


class EmailAlreadyExistsError(ConflictError):
    """Raised when attempting to create a user with an email that already exists."""


class UserAlreadyVerifiedError(ConflictError):
    """Raised when attempting to verify an already verfied user"""


# Bad request exceptions
class BadRequestError(TaskFlowError):
    """Base exception for resource that contains invalid data"""


class InvalidOTPError(BadRequestError):
    """Raised when a verification code is invalid"""


class ExpiredOTPError(BadRequestError):
    """Raised when a verification code is expired"""


# Authorization exceptions
class AuthorizationError(Exception):
    """Base exception for authorization-related errors."""


class InvalidCredentialsError(AuthorizationError):
    """Raised when the provided login credentials are invalid."""


class InvalidAccessTokenError(AuthorizationError):
    """Raised when an access token is invalid."""


class InvalidRefreshTokenError(AuthorizationError):
    """Raised when an refresh token is invalid."""


class ExpiredAccessTokenError(AuthorizationError):
    """Raised when an access token has expired."""


class UserNotVerifiedError(AuthorizationError):
    """Raised when a user attempts an action before verifying their account."""
