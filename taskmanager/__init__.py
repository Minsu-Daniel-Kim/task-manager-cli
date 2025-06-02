"""
Task Manager CLI - A powerful command-line task management tool.
"""

__version__ = "0.2.0"
__author__ = "Daniel Kim"
__email__ = "daniel@example.com"

from .models import Task, TaskStatus, TaskPriority
from .manager import TaskManager, TaskNotFoundError, TaskValidationError

__all__ = [
    "Task", 
    "TaskStatus", 
    "TaskPriority", 
    "TaskManager",
    "TaskNotFoundError",
    "TaskValidationError"
]