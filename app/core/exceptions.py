class TaskFlowError(Exception):
    """Base-class for all application specific exceptions"""


class NotFoundError(TaskFlowError):
    """Raised when the requested resource cannot be found"""


class TodoNotFoundError(NotFoundError):
    """Raised when the requested todo cannot be found"""


class UserNotFoundError(NotFoundError):
    """Raised when the requested user cannot be found"""
