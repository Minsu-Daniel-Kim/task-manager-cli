"""
Task Manager CLI - A powerful command-line task management tool.
"""

__version__ = "0.3.0"
__author__ = "Daniel Kim"
__email__ = "daniel@example.com"

from .models import Task, TaskStatus, TaskPriority
from .manager import TaskManager, TaskNotFoundError, TaskValidationError
from .filters import TaskFilter, TaskSorter, SearchEngine, SortField, SortOrder, FilterPreset

__all__ = [
    "Task", 
    "TaskStatus", 
    "TaskPriority", 
    "TaskManager",
    "TaskNotFoundError",
    "TaskValidationError",
    "TaskFilter",
    "TaskSorter",
    "SearchEngine",
    "SortField",
    "SortOrder",
    "FilterPreset"
]