"""
Task management logic with full CRUD operations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union
from .models import Task, TaskStatus, TaskPriority


class TaskNotFoundError(Exception):
    """Raised when a task is not found."""
    pass


class TaskValidationError(Exception):
    """Raised when task validation fails."""
    pass


class TaskManager:
    """
    Manages task operations (CRUD) with validation and error handling.
    Now with persistent storage support.
    """
    
    def __init__(self, auto_save: bool = True):
        self.tasks: Dict[str, Task] = {}
        self.auto_save = auto_save
        self._storage = None
    
    def _validate_title(self, title: str) -> None:
        """Validate task title."""
        if not title or not title.strip():
            raise TaskValidationError("Task title cannot be empty")
        if len(title) > 200:
            raise TaskValidationError("Task title cannot exceed 200 characters")
    
    def _validate_priority(self, priority: Union[str, TaskPriority]) -> TaskPriority:
        """Validate and convert priority."""
        if isinstance(priority, str):
            try:
                return TaskPriority(priority.lower())
            except ValueError:
                valid_priorities = [p.value for p in TaskPriority]
                raise TaskValidationError(
                    f"Invalid priority '{priority}'. Must be one of: {', '.join(valid_priorities)}"
                )
        return priority
    
    def _validate_status(self, status: Union[str, TaskStatus]) -> TaskStatus:
        """Validate and convert status."""
        if isinstance(status, str):
            try:
                return TaskStatus(status.lower())
            except ValueError:
                valid_statuses = [s.value for s in TaskStatus]
                raise TaskValidationError(
                    f"Invalid status '{status}'. Must be one of: {', '.join(valid_statuses)}"
                )
        return status
    
    def _find_task(self, task_id: str) -> Task:
        """Find a task by ID or short ID."""
        # Try exact match first
        if task_id in self.tasks:
            return self.tasks[task_id]
        
        # Try short ID match
        for tid, task in self.tasks.items():
            if tid.startswith(task_id):
                return task
        
        raise TaskNotFoundError(f"Task with ID '{task_id}' not found")
    
    def create_task(self, 
                   title: str, 
                   description: str = "", 
                   priority: Union[str, TaskPriority] = TaskPriority.MEDIUM,
                   status: Union[str, TaskStatus] = TaskStatus.TODO,
                   due_date: Optional[datetime] = None,
                   tags: Optional[List[str]] = None) -> Task:
        """
        Create a new task with validation.
        
        Args:
            title: Task title (required)
            description: Task description
            priority: Task priority (low, medium, high, urgent)
            status: Task status (todo, in_progress, done)
            due_date: Optional due date
            tags: Optional list of tags
            
        Returns:
            Created Task object
            
        Raises:
            TaskValidationError: If validation fails
        """
        self._validate_title(title)
        priority = self._validate_priority(priority)
        status = self._validate_status(status)
        
        # Validate tags
        if tags:
            tags = [tag.strip() for tag in tags if tag.strip()]
        
        task = Task(
            title=title.strip(),
            description=description.strip(),
            priority=priority,
            status=status,
            due_date=due_date,
            tags=tags or []
        )
        
        self.tasks[task.id] = task
        self._auto_save()
        return task
    
    def get_task(self, task_id: str) -> Task:
        """
        Get a task by ID or short ID.
        
        Args:
            task_id: Full or short task ID
            
        Returns:
            Task object
            
        Raises:
            TaskNotFoundError: If task not found
        """
        return self._find_task(task_id)
    
    def list_tasks(self, 
                  status: Optional[Union[str, TaskStatus]] = None,
                  priority: Optional[Union[str, TaskPriority]] = None) -> List[Task]:
        """
        List tasks with optional filtering.
        
        Args:
            status: Filter by status
            priority: Filter by priority
            
        Returns:
            List of tasks matching criteria
        """
        tasks = list(self.tasks.values())
        
        # Apply filters
        if status is not None:
            status = self._validate_status(status)
            tasks = [t for t in tasks if t.status == status]
        
        if priority is not None:
            priority = self._validate_priority(priority)
            tasks = [t for t in tasks if t.priority == priority]
        
        # Sort by created date (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        return tasks
    
    def update_task(self, task_id: str, **kwargs) -> Task:
        """
        Update a task's properties.
        
        Args:
            task_id: Task ID to update
            **kwargs: Fields to update (title, description, status, priority, due_date, tags)
            
        Returns:
            Updated Task object
            
        Raises:
            TaskNotFoundError: If task not found
            TaskValidationError: If validation fails
        """
        task = self._find_task(task_id)
        
        # Validate updates
        if 'title' in kwargs:
            self._validate_title(kwargs['title'])
            kwargs['title'] = kwargs['title'].strip()
        
        if 'description' in kwargs:
            kwargs['description'] = kwargs['description'].strip()
        
        if 'priority' in kwargs:
            kwargs['priority'] = self._validate_priority(kwargs['priority'])
        
        if 'status' in kwargs:
            kwargs['status'] = self._validate_status(kwargs['status'])
        
        if 'tags' in kwargs and kwargs['tags']:
            kwargs['tags'] = [tag.strip() for tag in kwargs['tags'] if tag.strip()]
        
        # Apply updates
        task.update(**kwargs)
        self._auto_save()
        
        return task
    
    def delete_task(self, task_id: str) -> Task:
        """
        Delete a task.
        
        Args:
            task_id: Task ID to delete
            
        Returns:
            Deleted Task object
            
        Raises:
            TaskNotFoundError: If task not found
        """
        task = self._find_task(task_id)
        del self.tasks[task.id]
        self._auto_save()
        return task
    
    def mark_done(self, task_id: str) -> Task:
        """
        Convenience method to mark a task as done.
        
        Args:
            task_id: Task ID to mark as done
            
        Returns:
            Updated Task object
        """
        return self.update_task(task_id, status=TaskStatus.DONE)
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get task statistics.
        
        Returns:
            Dictionary with counts by status and priority
        """
        stats = {
            'total': len(self.tasks),
            'by_status': {},
            'by_priority': {}
        }
        
        # Count by status
        for status in TaskStatus:
            count = len([t for t in self.tasks.values() if t.status == status])
            stats['by_status'][status.value] = count
        
        # Count by priority
        for priority in TaskPriority:
            count = len([t for t in self.tasks.values() if t.priority == priority])
            stats['by_priority'][priority.value] = count
        
        return stats
    
    @property
    def storage(self):
        """Lazy-load storage instance."""
        if self._storage is None:
            from .storage import get_storage
            self._storage = get_storage()
        return self._storage
    
    def _auto_save(self) -> None:
        """Save tasks if auto-save is enabled."""
        if self.auto_save and self._storage:
            self.storage.save_tasks(self)
    
    def save(self) -> None:
        """Manually save tasks to storage."""
        self.storage.save_tasks(self)
    
    def load(self) -> None:
        """Load tasks from storage."""
        self.storage.load_tasks(self)