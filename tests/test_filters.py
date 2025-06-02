"""
Tests for advanced filtering and search functionality.
"""

import pytest
from datetime import datetime, date, timedelta
from taskmanager.models import Task, TaskStatus, TaskPriority
from taskmanager.filters import (
    TaskFilter, TaskSorter, SearchEngine, 
    SortField, SortOrder, FilterPreset
)


class TestTaskFilter:
    """Test the TaskFilter class."""
    
    def test_filter_by_single_status(self):
        """Test filtering by a single status."""
        tasks = [
            Task(title="Task 1", status=TaskStatus.TODO),
            Task(title="Task 2", status=TaskStatus.IN_PROGRESS),
            Task(title="Task 3", status=TaskStatus.DONE),
        ]
        
        filter_obj = TaskFilter().with_statuses([TaskStatus.TODO])
        result = filter_obj.apply(tasks)
        
        assert len(result) == 1
        assert result[0].title == "Task 1"
    
    def test_filter_by_multiple_statuses(self):
        """Test filtering by multiple statuses."""
        tasks = [
            Task(title="Task 1", status=TaskStatus.TODO),
            Task(title="Task 2", status=TaskStatus.IN_PROGRESS),
            Task(title="Task 3", status=TaskStatus.DONE),
        ]
        
        filter_obj = TaskFilter().with_statuses([TaskStatus.TODO, TaskStatus.IN_PROGRESS])
        result = filter_obj.apply(tasks)
        
        assert len(result) == 2
        assert {t.title for t in result} == {"Task 1", "Task 2"}
    
    def test_filter_by_priorities(self):
        """Test filtering by priorities."""
        tasks = [
            Task(title="Task 1", priority=TaskPriority.LOW),
            Task(title="Task 2", priority=TaskPriority.HIGH),
            Task(title="Task 3", priority=TaskPriority.URGENT),
        ]
        
        filter_obj = TaskFilter().with_priorities([TaskPriority.HIGH, TaskPriority.URGENT])
        result = filter_obj.apply(tasks)
        
        assert len(result) == 2
        assert {t.title for t in result} == {"Task 2", "Task 3"}
    
    def test_filter_by_tags_match_any(self):
        """Test filtering by tags (match any)."""
        tasks = [
            Task(title="Task 1", tags=["work", "urgent"]),
            Task(title="Task 2", tags=["personal"]),
            Task(title="Task 3", tags=["work", "meeting"]),
        ]
        
        filter_obj = TaskFilter().with_tags(["work"], match_all=False)
        result = filter_obj.apply(tasks)
        
        assert len(result) == 2
        assert {t.title for t in result} == {"Task 1", "Task 3"}
    
    def test_filter_by_tags_match_all(self):
        """Test filtering by tags (match all)."""
        tasks = [
            Task(title="Task 1", tags=["work", "urgent", "bug"]),
            Task(title="Task 2", tags=["work", "urgent"]),
            Task(title="Task 3", tags=["work"]),
        ]
        
        filter_obj = TaskFilter().with_tags(["work", "urgent"], match_all=True)
        result = filter_obj.apply(tasks)
        
        assert len(result) == 2
        assert {t.title for t in result} == {"Task 1", "Task 2"}
    
    def test_filter_by_date_range(self):
        """Test filtering by date range."""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        
        tasks = [
            Task(title="Task 1", due_date=yesterday),
            Task(title="Task 2", due_date=today),
            Task(title="Task 3", due_date=tomorrow),
            Task(title="Task 4", due_date=next_week),
        ]
        
        filter_obj = TaskFilter().with_date_range(
            start_date=today.date(),
            end_date=tomorrow.date()
        )
        result = filter_obj.apply(tasks)
        
        assert len(result) == 2
        assert {t.title for t in result} == {"Task 2", "Task 3"}
    
    def test_filter_with_search_query(self):
        """Test filtering with search query."""
        tasks = [
            Task(title="Fix bug in login", description="Critical issue"),
            Task(title="Add feature", description="New dashboard"),
            Task(title="Update docs", description="Fix typos"),
        ]
        
        filter_obj = TaskFilter().with_search_query("fix")
        result = filter_obj.apply(tasks)
        
        assert len(result) == 2
        assert {t.title for t in result} == {"Fix bug in login", "Update docs"}
    
    def test_filter_preset_active(self):
        """Test the ACTIVE preset."""
        tasks = [
            Task(title="Task 1", status=TaskStatus.TODO),
            Task(title="Task 2", status=TaskStatus.IN_PROGRESS),
            Task(title="Task 3", status=TaskStatus.DONE),
        ]
        
        filter_obj = TaskFilter().with_preset(FilterPreset.ACTIVE)
        result = filter_obj.apply(tasks)
        
        assert len(result) == 2
        assert {t.title for t in result} == {"Task 1", "Task 2"}
    
    def test_filter_preset_overdue(self):
        """Test the OVERDUE preset."""
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow = datetime.now() + timedelta(days=1)
        
        tasks = [
            Task(title="Task 1", due_date=yesterday, status=TaskStatus.TODO),
            Task(title="Task 2", due_date=yesterday, status=TaskStatus.DONE),
            Task(title="Task 3", due_date=tomorrow, status=TaskStatus.TODO),
        ]
        
        filter_obj = TaskFilter().with_preset(FilterPreset.OVERDUE)
        result = filter_obj.apply(tasks)
        
        assert len(result) == 1
        assert result[0].title == "Task 1"
    
    def test_filter_preset_high_priority(self):
        """Test the HIGH_PRIORITY preset."""
        tasks = [
            Task(title="Task 1", priority=TaskPriority.LOW),
            Task(title="Task 2", priority=TaskPriority.HIGH),
            Task(title="Task 3", priority=TaskPriority.URGENT),
        ]
        
        filter_obj = TaskFilter().with_preset(FilterPreset.HIGH_PRIORITY)
        result = filter_obj.apply(tasks)
        
        assert len(result) == 2
        assert {t.title for t in result} == {"Task 2", "Task 3"}
    
    def test_combined_filters(self):
        """Test combining multiple filters."""
        today = datetime.now()
        tasks = [
            Task(title="Task 1", status=TaskStatus.TODO, priority=TaskPriority.HIGH, tags=["work"]),
            Task(title="Task 2", status=TaskStatus.TODO, priority=TaskPriority.LOW, tags=["work"]),
            Task(title="Task 3", status=TaskStatus.DONE, priority=TaskPriority.HIGH, tags=["work"]),
            Task(title="Task 4", status=TaskStatus.TODO, priority=TaskPriority.HIGH, tags=["personal"]),
        ]
        
        filter_obj = (TaskFilter()
                     .with_statuses([TaskStatus.TODO])
                     .with_priorities([TaskPriority.HIGH])
                     .with_tags(["work"]))
        result = filter_obj.apply(tasks)
        
        assert len(result) == 1
        assert result[0].title == "Task 1"


class TestTaskSorter:
    """Test the TaskSorter class."""
    
    def test_sort_by_created_at(self):
        """Test sorting by creation date."""
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")
        task3 = Task(title="Task 3")
        
        # Manually adjust created_at for testing
        task1.created_at = datetime.now() - timedelta(days=2)
        task2.created_at = datetime.now() - timedelta(days=1)
        task3.created_at = datetime.now()
        
        tasks = [task2, task3, task1]
        
        # Sort ascending
        result = TaskSorter.sort(tasks, SortField.CREATED_AT, SortOrder.ASC)
        assert [t.title for t in result] == ["Task 1", "Task 2", "Task 3"]
        
        # Sort descending
        result = TaskSorter.sort(tasks, SortField.CREATED_AT, SortOrder.DESC)
        assert [t.title for t in result] == ["Task 3", "Task 2", "Task 1"]
    
    def test_sort_by_priority(self):
        """Test sorting by priority."""
        tasks = [
            Task(title="Task 1", priority=TaskPriority.MEDIUM),
            Task(title="Task 2", priority=TaskPriority.URGENT),
            Task(title="Task 3", priority=TaskPriority.LOW),
        ]
        
        result = TaskSorter.sort(tasks, SortField.PRIORITY, SortOrder.ASC)
        priorities = [t.priority for t in result]
        assert priorities == [TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.URGENT]
    
    def test_sort_by_due_date(self):
        """Test sorting by due date."""
        today = datetime.now()
        tasks = [
            Task(title="Task 1", due_date=today + timedelta(days=2)),
            Task(title="Task 2"),  # No due date
            Task(title="Task 3", due_date=today + timedelta(days=1)),
        ]
        
        result = TaskSorter.sort(tasks, SortField.DUE_DATE, SortOrder.ASC)
        assert [t.title for t in result] == ["Task 3", "Task 1", "Task 2"]
    
    def test_sort_by_title(self):
        """Test sorting by title."""
        tasks = [
            Task(title="Zebra task"),
            Task(title="Alpha task"),
            Task(title="Beta task"),
        ]
        
        result = TaskSorter.sort(tasks, SortField.TITLE, SortOrder.ASC)
        assert [t.title for t in result] == ["Alpha task", "Beta task", "Zebra task"]


class TestSearchEngine:
    """Test the SearchEngine class."""
    
    def test_basic_search(self):
        """Test basic text search."""
        tasks = [
            Task(title="Fix login bug", description="User cannot log in"),
            Task(title="Add logout feature", description="Related to login system"),
            Task(title="Update user profile", description=""),
        ]
        
        result = SearchEngine.search(tasks, "login")
        assert len(result) == 2
        assert {t.title for t in result} == {"Fix login bug", "Add logout feature"}
    
    def test_case_sensitive_search(self):
        """Test case-sensitive search."""
        tasks = [
            Task(title="Fix LOGIN bug"),
            Task(title="Fix login bug"),
            Task(title="LOGIN feature"),
        ]
        
        # Case-insensitive (default)
        result = SearchEngine.search(tasks, "login", case_sensitive=False)
        assert len(result) == 3
        
        # Case-sensitive
        result = SearchEngine.search(tasks, "login", case_sensitive=True)
        assert len(result) == 1
        assert result[0].title == "Fix login bug"
    
    def test_regex_search(self):
        """Test regex pattern search."""
        tasks = [
            Task(title="Task-123", description=""),
            Task(title="Task-456", description=""),
            Task(title="Feature-789", description=""),
        ]
        
        result = SearchEngine.search(tasks, r"Task-\d+", regex=True)
        assert len(result) == 2
        assert {t.title for t in result} == {"Task-123", "Task-456"}
    
    def test_search_in_tags(self):
        """Test searching in tags."""
        tasks = [
            Task(title="Task 1", tags=["urgent", "bug"]),
            Task(title="Task 2", tags=["feature"]),
            Task(title="Task 3", tags=["bug", "low-priority"]),
        ]
        
        result = SearchEngine.search(tasks, "bug")
        assert len(result) == 2
        assert {t.title for t in result} == {"Task 1", "Task 3"}
    
    def test_invalid_regex(self):
        """Test invalid regex pattern handling."""
        tasks = [Task(title="Task 1")]
        
        # Invalid regex should return empty list
        result = SearchEngine.search(tasks, "[invalid(", regex=True)
        assert result == []