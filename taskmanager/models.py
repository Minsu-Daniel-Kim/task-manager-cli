"""
Data models for Task Manager.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
import uuid


class TaskStatus(str, Enum):
    """Task status enumeration."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Task:
    """Task model representing a single task."""
    
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    linear_issue_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate and convert fields after initialization."""
        # Ensure status is a TaskStatus enum
        if isinstance(self.status, str):
            self.status = TaskStatus(self.status)
        
        # Ensure priority is a TaskPriority enum
        if isinstance(self.priority, str):
            self.priority = TaskPriority(self.priority)
        
        # Ensure dates are datetime objects
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
        
        if self.due_date and isinstance(self.due_date, str):
            self.due_date = datetime.fromisoformat(self.due_date)
    
    def update(self, **kwargs):
        """Update task fields and set updated_at timestamp."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """Convert task to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "tags": self.tags,
            "linear_issue_id": self.linear_issue_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create a Task instance from a dictionary."""
        return cls(**data)
    
    @property
    def short_id(self):
        """Return the first 6 characters of the ID for display."""
        return self.id[:6]
    
    def __str__(self):
        """String representation of the task."""
        return f"Task({self.short_id}: {self.title})"