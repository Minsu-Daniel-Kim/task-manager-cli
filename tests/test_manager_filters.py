"""
Tests for TaskManager with advanced filtering capabilities.
"""

import pytest
from datetime import datetime, timedelta
from taskmanager.manager import TaskManager
from taskmanager.models import TaskStatus, TaskPriority
from taskmanager.filters import TaskFilter, FilterPreset, SortField, SortOrder


class TestTaskManagerFiltering:
    """Test TaskManager filtering methods."""
    
    @pytest.fixture
    def manager_with_tasks(self):
        """Create a manager with sample tasks."""
        manager = TaskManager(auto_save=False)
        
        # Create various tasks
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow = datetime.now() + timedelta(days=1)
        next_week = datetime.now() + timedelta(days=7)
        
        manager.create_task(
            title="Urgent bug fix",
            description="Critical production issue",
            priority=TaskPriority.URGENT,
            status=TaskStatus.IN_PROGRESS,
            tags=["bug", "production"],
            due_date=yesterday
        )
        
        manager.create_task(
            title="New feature development",
            description="Implement user dashboard",
            priority=TaskPriority.HIGH,
            status=TaskStatus.TODO,
            tags=["feature", "dashboard"],
            due_date=next_week
        )
        
        manager.create_task(
            title="Update documentation",
            description="Fix typos in README",
            priority=TaskPriority.LOW,
            status=TaskStatus.TODO,
            tags=["docs"],
            due_date=tomorrow
        )
        
        manager.create_task(
            title="Code review",
            description="Review PR #123",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.DONE,
            tags=["review"]
        )
        
        manager.create_task(
            title="Fix login issue",
            description="Users cannot login with email",
            priority=TaskPriority.HIGH,
            status=TaskStatus.TODO,
            tags=["bug", "auth"],
            due_date=tomorrow
        )
        
        return manager
    
    def test_list_tasks_with_multiple_statuses(self, manager_with_tasks):
        """Test listing tasks with multiple status filters."""
        tasks = manager_with_tasks.list_tasks(
            statuses=[TaskStatus.TODO, TaskStatus.IN_PROGRESS]
        )
        
        assert len(tasks) == 4
        statuses = {t.status for t in tasks}
        assert statuses == {TaskStatus.TODO, TaskStatus.IN_PROGRESS}
    
    def test_list_tasks_with_multiple_priorities(self, manager_with_tasks):
        """Test listing tasks with multiple priority filters."""
        tasks = manager_with_tasks.list_tasks(
            priorities=[TaskPriority.HIGH, TaskPriority.URGENT]
        )
        
        assert len(tasks) == 3
        titles = {t.title for t in tasks}
        assert titles == {"Urgent bug fix", "New feature development", "Fix login issue"}
    
    def test_list_tasks_with_tags(self, manager_with_tasks):
        """Test listing tasks filtered by tags."""
        tasks = manager_with_tasks.list_tasks(tags=["bug"])
        
        assert len(tasks) == 2
        titles = {t.title for t in tasks}
        assert titles == {"Urgent bug fix", "Fix login issue"}
    
    def test_list_tasks_with_preset_active(self, manager_with_tasks):
        """Test listing tasks with ACTIVE preset."""
        tasks = manager_with_tasks.list_tasks(preset=FilterPreset.ACTIVE)
        
        assert len(tasks) == 4
        for task in tasks:
            assert task.status in [TaskStatus.TODO, TaskStatus.IN_PROGRESS]
    
    def test_list_tasks_with_preset_overdue(self, manager_with_tasks):
        """Test listing tasks with OVERDUE preset."""
        tasks = manager_with_tasks.list_tasks(preset=FilterPreset.OVERDUE)
        
        assert len(tasks) == 1
        assert tasks[0].title == "Urgent bug fix"
        assert tasks[0].status != TaskStatus.DONE
    
    def test_list_tasks_with_sorting(self, manager_with_tasks):
        """Test listing tasks with different sort options."""
        # Sort by priority ascending
        tasks = manager_with_tasks.list_tasks(
            sort_by=SortField.PRIORITY,
            sort_order=SortOrder.ASC
        )
        
        priorities = [t.priority for t in tasks]
        assert priorities[0] == TaskPriority.LOW
        assert priorities[-1] == TaskPriority.URGENT
        
        # Sort by title
        tasks = manager_with_tasks.list_tasks(
            sort_by=SortField.TITLE,
            sort_order=SortOrder.ASC
        )
        
        titles = [t.title for t in tasks]
        assert titles == sorted(titles)
    
    def test_search_tasks(self, manager_with_tasks):
        """Test searching tasks."""
        # Search for "fix"
        tasks = manager_with_tasks.search_tasks("fix")
        
        # Should find "Urgent bug fix", "Update documentation" (has "Fix" in description), and "Fix login issue"
        assert len(tasks) == 3
        titles = {t.title for t in tasks}
        # Check that all found tasks contain "fix" in title or description
        for task in tasks:
            assert "fix" in task.title.lower() or "fix" in task.description.lower()
        
        # Search for "bug" (should find in title, description, and tags)
        tasks = manager_with_tasks.search_tasks("bug")
        
        assert len(tasks) == 2
        titles = {t.title for t in tasks}
        assert titles == {"Urgent bug fix", "Fix login issue"}
    
    def test_search_tasks_case_sensitive(self, manager_with_tasks):
        """Test case-sensitive search."""
        # Case-insensitive search (default)
        tasks = manager_with_tasks.search_tasks("FIX")
        assert len(tasks) == 3
        
        # Case-sensitive search
        tasks = manager_with_tasks.search_tasks("FIX", case_sensitive=True)
        assert len(tasks) == 0  # No exact "FIX" in uppercase
    
    def test_search_tasks_with_regex(self, manager_with_tasks):
        """Test regex search."""
        # Search for tasks with "fix" or "Fix" at the beginning (in any field)
        tasks = manager_with_tasks.search_tasks(r"^(fix|Fix)", regex=True)
        
        # Should find "Fix login issue" (title starts with "Fix") and 
        # "Update documentation" (description starts with "Fix")
        assert len(tasks) == 2
        titles = {t.title for t in tasks}
        assert titles == {"Fix login issue", "Update documentation"}
    
    def test_filter_tasks_with_custom_filter(self, manager_with_tasks):
        """Test filtering with custom TaskFilter object."""
        # Create a complex filter
        task_filter = (TaskFilter()
                      .with_statuses([TaskStatus.TODO])
                      .with_priorities([TaskPriority.HIGH, TaskPriority.URGENT])
                      .with_tags(["bug"]))
        
        tasks = manager_with_tasks.filter_tasks(task_filter)
        
        assert len(tasks) == 1
        assert tasks[0].title == "Fix login issue"
    
    def test_get_overdue_tasks(self, manager_with_tasks):
        """Test getting overdue tasks."""
        tasks = manager_with_tasks.get_overdue_tasks()
        
        assert len(tasks) == 1
        assert tasks[0].title == "Urgent bug fix"
        assert tasks[0].due_date < datetime.now()
        assert tasks[0].status != TaskStatus.DONE
    
    def test_get_tasks_by_date_range(self, manager_with_tasks):
        """Test getting tasks by date range."""
        today = datetime.now().date()
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        
        tasks = manager_with_tasks.get_tasks_by_date_range(
            start_date=today,
            end_date=tomorrow
        )
        
        assert len(tasks) == 2
        titles = {t.title for t in tasks}
        assert titles == {"Update documentation", "Fix login issue"}
    
    def test_backward_compatibility(self, manager_with_tasks):
        """Test that old single filter methods still work."""
        # Single status filter
        tasks = manager_with_tasks.list_tasks(status=TaskStatus.TODO)
        assert all(t.status == TaskStatus.TODO for t in tasks)
        
        # Single priority filter
        tasks = manager_with_tasks.list_tasks(priority=TaskPriority.HIGH)
        assert all(t.priority == TaskPriority.HIGH for t in tasks)
    
    def test_combined_filters_and_sort(self, manager_with_tasks):
        """Test combining multiple filters with sorting."""
        tasks = manager_with_tasks.list_tasks(
            statuses=[TaskStatus.TODO, TaskStatus.IN_PROGRESS],
            priorities=[TaskPriority.HIGH, TaskPriority.URGENT],
            sort_by=SortField.DUE_DATE,
            sort_order=SortOrder.ASC
        )
        
        assert len(tasks) == 3
        
        # Check filters applied correctly
        for task in tasks:
            assert task.status in [TaskStatus.TODO, TaskStatus.IN_PROGRESS]
            assert task.priority in [TaskPriority.HIGH, TaskPriority.URGENT]
        
        # Check sorting (tasks with due dates should come first)
        due_dates = [t.due_date for t in tasks if t.due_date]
        assert len(due_dates) >= 2  # At least 2 tasks have due dates
        
        # Verify due dates are in ascending order
        for i in range(1, len(due_dates)):
            assert due_dates[i-1] <= due_dates[i]