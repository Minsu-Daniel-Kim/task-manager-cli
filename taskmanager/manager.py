"""
Task management logic with full CRUD operations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union
from .models import Task, TaskStatus, TaskPriority
from .filters import TaskFilter, TaskSorter, SearchEngine, SortField, SortOrder, FilterPreset


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
                  priority: Optional[Union[str, TaskPriority]] = None,
                  statuses: Optional[List[Union[str, TaskStatus]]] = None,
                  priorities: Optional[List[Union[str, TaskPriority]]] = None,
                  tags: Optional[List[str]] = None,
                  preset: Optional[Union[str, FilterPreset]] = None,
                  sort_by: Union[str, SortField] = SortField.CREATED_AT,
                  sort_order: Union[str, SortOrder] = SortOrder.DESC) -> List[Task]:
        """
        List tasks with advanced filtering and sorting.
        
        Args:
            status: Filter by single status (backward compatibility)
            priority: Filter by single priority (backward compatibility)
            statuses: Filter by multiple statuses
            priorities: Filter by multiple priorities
            tags: Filter by tags
            preset: Apply a filter preset
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            
        Returns:
            List of tasks matching criteria
        """
        tasks = list(self.tasks.values())
        
        # Build filter
        task_filter = TaskFilter()
        
        # Handle backward compatibility
        if status is not None:
            task_filter.with_statuses([status])
        elif statuses:
            task_filter.with_statuses(statuses)
        
        if priority is not None:
            task_filter.with_priorities([priority])
        elif priorities:
            task_filter.with_priorities(priorities)
        
        if tags:
            task_filter.with_tags(tags)
        
        if preset:
            task_filter.with_preset(preset)
        
        # Apply filters
        tasks = task_filter.apply(tasks)
        
        # Sort results
        tasks = TaskSorter.sort(tasks, sort_by, sort_order)
        
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
    
    def search_tasks(self, 
                    query: str,
                    regex: bool = False,
                    case_sensitive: bool = False,
                    sort_by: Union[str, SortField] = SortField.CREATED_AT,
                    sort_order: Union[str, SortOrder] = SortOrder.DESC) -> List[Task]:
        """
        Search tasks by query string.
        
        Args:
            query: Search query (searches in title, description, ID, and tags)
            regex: Whether to treat query as regex pattern
            case_sensitive: Whether search is case-sensitive
            sort_by: Field to sort results by
            sort_order: Sort order
            
        Returns:
            List of matching tasks
        """
        tasks = list(self.tasks.values())
        
        # Apply search
        tasks = SearchEngine.search(tasks, query, regex, case_sensitive)
        
        # Sort results
        tasks = TaskSorter.sort(tasks, sort_by, sort_order)
        
        return tasks
    
    def filter_tasks(self, filter_obj: TaskFilter,
                    sort_by: Union[str, SortField] = SortField.CREATED_AT,
                    sort_order: Union[str, SortOrder] = SortOrder.DESC) -> List[Task]:
        """
        Filter tasks using a TaskFilter object.
        
        Args:
            filter_obj: Pre-configured TaskFilter
            sort_by: Field to sort results by
            sort_order: Sort order
            
        Returns:
            List of matching tasks
        """
        tasks = list(self.tasks.values())
        
        # Apply filter
        tasks = filter_obj.apply(tasks)
        
        # Sort results
        tasks = TaskSorter.sort(tasks, sort_by, sort_order)
        
        return tasks
    
    def get_overdue_tasks(self) -> List[Task]:
        """
        Get all overdue tasks.
        
        Returns:
            List of overdue tasks (past due date and not done)
        """
        return self.list_tasks(preset=FilterPreset.OVERDUE)
    
    def get_tasks_by_date_range(self,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None,
                               field: str = 'due_date') -> List[Task]:
        """
        Get tasks within a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            field: Date field to filter on ('due_date', 'created_at', 'updated_at')
            
        Returns:
            List of tasks within date range
        """
        task_filter = TaskFilter().with_date_range(start_date, end_date, field)
        return self.filter_tasks(task_filter)
    
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