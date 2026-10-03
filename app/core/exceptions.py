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
