from enum import Enum


class TodoPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TodoStatus(str, Enum):
    TODO = "To do"
    INPROGRESS = "In progress"
    DONE = "Done"
