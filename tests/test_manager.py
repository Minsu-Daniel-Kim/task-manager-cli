"""
Tests for TaskManager CRUD operations.
"""

import pytest
from datetime import datetime
from taskmanager.manager import TaskManager, TaskNotFoundError, TaskValidationError
from taskmanager.models import Task, TaskStatus, TaskPriority


class TestTaskManager:
    """Test cases for TaskManager."""
    
    @pytest.fixture
    def manager(self):
        """Create a fresh TaskManager for each test."""
        return TaskManager()
    
    @pytest.fixture
    def sample_task(self, manager):
        """Create a sample task."""
        return manager.create_task(
            title="Sample Task",
            description="Sample Description",
            priority=TaskPriority.MEDIUM,
            tags=["test", "sample"]
        )
    
    def test_create_task_basic(self, manager):
        """Test basic task creation."""
        task = manager.create_task(
            title="New Task",
            description="Task Description"
        )
        
        assert task.title == "New Task"
        assert task.description == "Task Description"
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.MEDIUM
        assert task.id in manager.tasks
        assert len(manager.tasks) == 1
    
    def test_create_task_with_all_fields(self, manager):
        """Test task creation with all fields."""
        due_date = datetime.now()
        task = manager.create_task(
            title="Complete Task",
            description="Full description",
            priority="high",  # Test string conversion
            status="in_progress",  # Test string conversion
            due_date=due_date,
            tags=["work", "urgent"]
        )
        
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.due_date == due_date
        assert task.tags == ["work", "urgent"]
    
    def test_create_task_validation(self, manager):
        """Test task creation validation."""
        # Empty title
        with pytest.raises(TaskValidationError, match="cannot be empty"):
            manager.create_task(title="")
        
        with pytest.raises(TaskValidationError, match="cannot be empty"):
            manager.create_task(title="   ")
        
        # Title too long
        with pytest.raises(TaskValidationError, match="cannot exceed 200"):
            manager.create_task(title="x" * 201)
        
        # Invalid priority
        with pytest.raises(TaskValidationError, match="Invalid priority"):
            manager.create_task(title="Task", priority="invalid")
        
        # Invalid status
        with pytest.raises(TaskValidationError, match="Invalid status"):
            manager.create_task(title="Task", status="invalid")
    
    def test_get_task(self, manager, sample_task):
        """Test getting a task by ID."""
        # Get by full ID
        retrieved = manager.get_task(sample_task.id)
        assert retrieved.id == sample_task.id
        assert retrieved.title == sample_task.title
        
        # Get by short ID
        short_id = sample_task.id[:6]
        retrieved = manager.get_task(short_id)
        assert retrieved.id == sample_task.id
    
    def test_get_task_not_found(self, manager):
        """Test getting non-existent task."""
        with pytest.raises(TaskNotFoundError):
            manager.get_task("nonexistent")
    
    def test_list_tasks(self, manager):
        """Test listing tasks."""
        # Empty list
        assert manager.list_tasks() == []
        
        # Create multiple tasks
        task1 = manager.create_task("Task 1", priority="high", status="todo")
        task2 = manager.create_task("Task 2", priority="low", status="done")
        task3 = manager.create_task("Task 3", priority="high", status="in_progress")
        
        # List all tasks (should be sorted by created date, newest first)
        all_tasks = manager.list_tasks()
        assert len(all_tasks) == 3
        assert all_tasks[0].title == "Task 3"  # Newest
        assert all_tasks[2].title == "Task 1"  # Oldest
    
    def test_list_tasks_filtered(self, manager):
        """Test listing tasks with filters."""
        # Create tasks with different statuses and priorities
        manager.create_task("Todo High", priority="high", status="todo")
        manager.create_task("Todo Low", priority="low", status="todo")
        manager.create_task("Done High", priority="high", status="done")
        manager.create_task("In Progress Medium", priority="medium", status="in_progress")
        
        # Filter by status
        todo_tasks = manager.list_tasks(status="todo")
        assert len(todo_tasks) == 2
        assert all(t.status == TaskStatus.TODO for t in todo_tasks)
        
        # Filter by priority
        high_tasks = manager.list_tasks(priority="high")
        assert len(high_tasks) == 2
        assert all(t.priority == TaskPriority.HIGH for t in high_tasks)
        
        # Filter by both
        todo_high_tasks = manager.list_tasks(status="todo", priority="high")
        assert len(todo_high_tasks) == 1
        assert todo_high_tasks[0].title == "Todo High"
    
    def test_update_task(self, manager, sample_task):
        """Test updating a task."""
        original_updated = sample_task.updated_at
        
        # Update multiple fields
        updated = manager.update_task(
            sample_task.id,
            title="Updated Title",
            description="Updated Description",
            status="done",
            priority="urgent",
            tags=["updated", "test"]
        )
        
        assert updated.title == "Updated Title"
        assert updated.description == "Updated Description"
        assert updated.status == TaskStatus.DONE
        assert updated.priority == TaskPriority.URGENT
        assert updated.tags == ["updated", "test"]
        assert updated.updated_at > original_updated
    
    def test_update_task_validation(self, manager, sample_task):
        """Test update validation."""
        # Empty title
        with pytest.raises(TaskValidationError, match="cannot be empty"):
            manager.update_task(sample_task.id, title="")
        
        # Invalid priority
        with pytest.raises(TaskValidationError, match="Invalid priority"):
            manager.update_task(sample_task.id, priority="invalid")
        
        # Task not found
        with pytest.raises(TaskNotFoundError):
            manager.update_task("nonexistent", title="New Title")
    
    def test_delete_task(self, manager, sample_task):
        """Test deleting a task."""
        task_id = sample_task.id
        
        # Delete the task
        deleted = manager.delete_task(task_id)
        assert deleted.id == task_id
        assert task_id not in manager.tasks
        assert len(manager.tasks) == 0
        
        # Try to get deleted task
        with pytest.raises(TaskNotFoundError):
            manager.get_task(task_id)
    
    def test_delete_task_not_found(self, manager):
        """Test deleting non-existent task."""
        with pytest.raises(TaskNotFoundError):
            manager.delete_task("nonexistent")
    
    def test_mark_done(self, manager, sample_task):
        """Test marking a task as done."""
        assert sample_task.status == TaskStatus.TODO
        
        # Mark as done
        updated = manager.mark_done(sample_task.id)
        assert updated.status == TaskStatus.DONE
        assert updated.id == sample_task.id
    
    def test_get_stats(self, manager):
        """Test getting task statistics."""
        # Empty stats
        stats = manager.get_stats()
        assert stats['total'] == 0
        
        # Create tasks with various statuses and priorities
        manager.create_task("Task 1", status="todo", priority="high")
        manager.create_task("Task 2", status="todo", priority="low")
        manager.create_task("Task 3", status="in_progress", priority="high")
        manager.create_task("Task 4", status="done", priority="medium")
        manager.create_task("Task 5", status="done", priority="urgent")
        
        stats = manager.get_stats()
        
        assert stats['total'] == 5
        assert stats['by_status']['todo'] == 2
        assert stats['by_status']['in_progress'] == 1
        assert stats['by_status']['done'] == 2
        assert stats['by_priority']['low'] == 1
        assert stats['by_priority']['medium'] == 1
        assert stats['by_priority']['high'] == 2
        assert stats['by_priority']['urgent'] == 1
    
    def test_short_id_matching(self, manager):
        """Test that short IDs work correctly."""
        # Create multiple tasks
        task1 = manager.create_task("Task 1")
        task2 = manager.create_task("Task 2")
        
        # Ensure we can get each by short ID
        assert manager.get_task(task1.id[:6]).id == task1.id
        assert manager.get_task(task2.id[:6]).id == task2.id
        
        # Test with even shorter IDs if unique
        assert manager.get_task(task1.id[:4]).id == task1.id