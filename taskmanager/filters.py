"""
Advanced filtering and search functionality for tasks.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any, Callable, Union
from enum import Enum
import re
from .models import Task, TaskStatus, TaskPriority


class SortField(Enum):
    """Available fields for sorting tasks."""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    DUE_DATE = "due_date"
    PRIORITY = "priority"
    STATUS = "status"
    TITLE = "title"


class SortOrder(Enum):
    """Sort order options."""
    ASC = "asc"
    DESC = "desc"


class FilterPreset(Enum):
    """Predefined filter combinations."""
    ACTIVE = "active"  # TODO or IN_PROGRESS
    OVERDUE = "overdue"  # Past due date
    HIGH_PRIORITY = "high_priority"  # HIGH or URGENT
    TODAY = "today"  # Due today
    THIS_WEEK = "this_week"  # Due this week
    UNTAGGED = "untagged"  # No tags
    RECENT = "recent"  # Created in last 7 days


class TaskFilter:
    """
    Advanced task filtering with multiple criteria support.
    """
    
    def __init__(self):
        self.criteria: Dict[str, Any] = {}
    
    def with_statuses(self, statuses: List[Union[str, TaskStatus]]) -> "TaskFilter":
        """Filter by multiple statuses."""
        if statuses:
            validated_statuses = []
            for status in statuses:
                if isinstance(status, str):
                    try:
                        validated_statuses.append(TaskStatus(status.lower()))
                    except ValueError:
                        continue  # Skip invalid statuses
                else:
                    validated_statuses.append(status)
            if validated_statuses:
                self.criteria['statuses'] = validated_statuses
        return self
    
    def with_priorities(self, priorities: List[Union[str, TaskPriority]]) -> "TaskFilter":
        """Filter by multiple priorities."""
        if priorities:
            validated_priorities = []
            for priority in priorities:
                if isinstance(priority, str):
                    try:
                        validated_priorities.append(TaskPriority(priority.lower()))
                    except ValueError:
                        continue  # Skip invalid priorities
                else:
                    validated_priorities.append(priority)
            if validated_priorities:
                self.criteria['priorities'] = validated_priorities
        return self
    
    def with_tags(self, tags: List[str], match_all: bool = False) -> "TaskFilter":
        """Filter by tags (match any or all)."""
        if tags:
            self.criteria['tags'] = tags
            self.criteria['tags_match_all'] = match_all
        return self
    
    def with_date_range(self, 
                       start_date: Optional[Union[datetime, date]] = None,
                       end_date: Optional[Union[datetime, date]] = None,
                       field: str = 'due_date') -> "TaskFilter":
        """Filter by date range on specified field."""
        if start_date or end_date:
            self.criteria['date_range'] = {
                'start': start_date,
                'end': end_date,
                'field': field
            }
        return self
    
    def with_search_query(self, query: str, fields: Optional[List[str]] = None) -> "TaskFilter":
        """Full-text search in specified fields (default: title, description)."""
        if query:
            self.criteria['search_query'] = query.lower()
            self.criteria['search_fields'] = fields or ['title', 'description']
        return self
    
    def with_preset(self, preset: Union[str, FilterPreset]) -> "TaskFilter":
        """Apply a predefined filter preset."""
        if isinstance(preset, str):
            try:
                preset = FilterPreset(preset.lower())
            except ValueError:
                return self
        
        if preset == FilterPreset.ACTIVE:
            self.with_statuses([TaskStatus.TODO, TaskStatus.IN_PROGRESS])
        elif preset == FilterPreset.OVERDUE:
            self.criteria['overdue'] = True
        elif preset == FilterPreset.HIGH_PRIORITY:
            self.with_priorities([TaskPriority.HIGH, TaskPriority.URGENT])
        elif preset == FilterPreset.TODAY:
            today = datetime.now().date()
            self.with_date_range(today, today)
        elif preset == FilterPreset.THIS_WEEK:
            today = datetime.now().date()
            week_end = today + (6 - today.weekday()) * (datetime.now().date() - today)
            self.with_date_range(today, week_end)
        elif preset == FilterPreset.UNTAGGED:
            self.criteria['untagged'] = True
        elif preset == FilterPreset.RECENT:
            week_ago = datetime.now().date() - (datetime.now().date() - datetime.now().date())
            self.criteria['recent_days'] = 7
        
        return self
    
    def apply(self, tasks: List[Task]) -> List[Task]:
        """Apply all filter criteria to a list of tasks."""
        filtered = tasks
        
        # Status filter
        if 'statuses' in self.criteria:
            filtered = [t for t in filtered if t.status in self.criteria['statuses']]
        
        # Priority filter
        if 'priorities' in self.criteria:
            filtered = [t for t in filtered if t.priority in self.criteria['priorities']]
        
        # Tags filter
        if 'tags' in self.criteria:
            tags = self.criteria['tags']
            if self.criteria.get('tags_match_all', False):
                # Match all tags
                filtered = [t for t in filtered if all(tag in t.tags for tag in tags)]
            else:
                # Match any tag
                filtered = [t for t in filtered if any(tag in t.tags for tag in tags)]
        
        # Untagged filter
        if self.criteria.get('untagged'):
            filtered = [t for t in filtered if not t.tags]
        
        # Date range filter
        if 'date_range' in self.criteria:
            dr = self.criteria['date_range']
            field = dr['field']
            start = dr.get('start')
            end = dr.get('end')
            
            def check_date(task: Task) -> bool:
                value = getattr(task, field, None)
                if not value:
                    return False
                
                # Convert to date if datetime
                if isinstance(value, datetime):
                    value = value.date()
                
                if start and value < start:
                    return False
                if end and value > end:
                    return False
                return True
            
            filtered = [t for t in filtered if check_date(t)]
        
        # Overdue filter
        if self.criteria.get('overdue'):
            today = datetime.now().date()
            filtered = [t for t in filtered 
                       if t.due_date and t.due_date.date() < today 
                       and t.status != TaskStatus.DONE]
        
        # Recent filter
        if 'recent_days' in self.criteria:
            days = self.criteria['recent_days']
            cutoff = datetime.now() - (datetime.now() - datetime.now())
            filtered = [t for t in filtered 
                       if (datetime.now() - t.created_at).days <= days]
        
        # Search query
        if 'search_query' in self.criteria:
            query = self.criteria['search_query']
            fields = self.criteria['search_fields']
            
            def matches_search(task: Task) -> bool:
                for field in fields:
                    value = getattr(task, field, '')
                    if value and query in str(value).lower():
                        return True
                # Also search in tags
                if 'tags' in fields or not fields:
                    if any(query in tag.lower() for tag in task.tags):
                        return True
                return False
            
            filtered = [t for t in filtered if matches_search(t)]
        
        return filtered


class TaskSorter:
    """
    Handles sorting of tasks by various fields.
    """
    
    @staticmethod
    def sort(tasks: List[Task], 
             field: Union[str, SortField],
             order: Union[str, SortOrder] = SortOrder.ASC) -> List[Task]:
        """
        Sort tasks by specified field and order.
        
        Args:
            tasks: List of tasks to sort
            field: Field to sort by
            order: Sort order (asc/desc)
            
        Returns:
            Sorted list of tasks
        """
        # Convert string to enum if needed
        if isinstance(field, str):
            try:
                field = SortField(field.lower())
            except ValueError:
                return tasks  # Invalid field, return unsorted
        
        if isinstance(order, str):
            try:
                order = SortOrder(order.lower())
            except ValueError:
                order = SortOrder.ASC
        
        # Define sort key functions
        key_funcs: Dict[SortField, Callable[[Task], Any]] = {
            SortField.CREATED_AT: lambda t: t.created_at,
            SortField.UPDATED_AT: lambda t: t.updated_at,
            SortField.DUE_DATE: lambda t: (t.due_date or datetime.max, t.created_at),
            SortField.PRIORITY: lambda t: (
                list(TaskPriority).index(t.priority),
                t.created_at
            ),
            SortField.STATUS: lambda t: (
                list(TaskStatus).index(t.status),
                t.created_at
            ),
            SortField.TITLE: lambda t: (t.title.lower(), t.created_at)
        }
        
        key_func = key_funcs.get(field, lambda t: t.created_at)
        reverse = (order == SortOrder.DESC)
        
        return sorted(tasks, key=key_func, reverse=reverse)


class SearchEngine:
    """
    Advanced search functionality with regex support.
    """
    
    @staticmethod
    def search(tasks: List[Task], 
               query: str,
               regex: bool = False,
               case_sensitive: bool = False) -> List[Task]:
        """
        Search tasks with optional regex support.
        
        Args:
            tasks: List of tasks to search
            query: Search query (string or regex pattern)
            regex: Whether to treat query as regex
            case_sensitive: Whether search is case-sensitive
            
        Returns:
            List of matching tasks
        """
        if not query:
            return tasks
        
        if regex:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(query, flags)
            except re.error:
                return []  # Invalid regex
            
            def matches(text: str) -> bool:
                return bool(pattern.search(text))
        else:
            if not case_sensitive:
                query = query.lower()
            
            def matches(text: str) -> bool:
                check_text = text if case_sensitive else text.lower()
                return query in check_text
        
        results = []
        for task in tasks:
            # Search in multiple fields
            searchable_texts = [
                task.title,
                task.description,
                task.id,
                task.short_id,
                *task.tags
            ]
            
            if any(matches(text) for text in searchable_texts if text):
                results.append(task)
        
        return results