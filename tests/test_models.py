"""
Tests for task models.
"""

import pytest
from datetime import datetime
from taskmanager.models import Task, TaskStatus, TaskPriority


class TestTask:
    """Test cases for Task model."""
    
    def test_task_creation(self):
        """Test basic task creation."""
        task = Task(
            title="Test Task",
            description="Test Description"
        )
        
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.MEDIUM
        assert len(task.id) == 36  # UUID length
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
        assert task.due_date is None
        assert task.tags == []
        assert task.linear_issue_id is None
    
    def test_task_with_all_fields(self):
        """Test task creation with all fields."""
        due_date = datetime.now()
        task = Task(
            title="Complete Task",
            description="Full description",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            due_date=due_date,
            tags=["work", "urgent"],
            linear_issue_id="LIN-123"
        )
        
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.HIGH
        assert task.due_date == due_date
        assert task.tags == ["work", "urgent"]
        assert task.linear_issue_id == "LIN-123"
    
    def test_task_update(self):
        """Test task update method."""
        task = Task(title="Original Title")
        original_updated_at = task.updated_at
        
        # Update the task
        task.update(
            title="Updated Title",
            status=TaskStatus.DONE,
            priority=TaskPriority.URGENT
        )
        
        assert task.title == "Updated Title"
        assert task.status == TaskStatus.DONE
        assert task.priority == TaskPriority.URGENT
        assert task.updated_at > original_updated_at
    
    def test_task_to_dict(self):
        """Test task serialization to dictionary."""
        task = Task(
            title="Test Task",
            description="Test Description",
            tags=["test"]
        )
        
        data = task.to_dict()
        
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
        assert data["status"] == "todo"
        assert data["priority"] == "medium"
        assert data["tags"] == ["test"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_task_from_dict(self):
        """Test task creation from dictionary."""
        data = {
            "id": "test-id-123",
            "title": "From Dict Task",
            "description": "Created from dict",
            "status": "in_progress",
            "priority": "high",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "due_date": None,
            "tags": ["imported"],
            "linear_issue_id": "LIN-456"
        }
        
        task = Task.from_dict(data)
        
        assert task.id == "test-id-123"
        assert task.title == "From Dict Task"
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.HIGH
        assert task.tags == ["imported"]
        assert task.linear_issue_id == "LIN-456"
    
    def test_short_id(self):
        """Test short ID property."""
        task = Task(title="Test", id="abcdef123456")
        assert task.short_id == "abcdef"
    
    def test_string_representation(self):
        """Test string representation of task."""
        task = Task(title="Test Task", id="abcdef123456")
        assert str(task) == "Task(abcdef: Test Task)"