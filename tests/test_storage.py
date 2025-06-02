"""
Tests for JSON storage backend.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from taskmanager.storage import JSONStorage, StorageError
from taskmanager.manager import TaskManager
from taskmanager.models import TaskPriority, TaskStatus


class TestJSONStorage:
    """Test cases for JSONStorage."""
    
    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for testing."""
        return tmp_path / "taskmanager_test"
    
    @pytest.fixture
    def storage(self, temp_dir):
        """Create a storage instance with temporary directory."""
        return JSONStorage(data_dir=temp_dir)
    
    @pytest.fixture
    def manager_with_tasks(self):
        """Create a TaskManager with sample tasks."""
        manager = TaskManager(auto_save=False)
        
        # Add some tasks
        task1 = manager.create_task(
            title="Task 1",
            description="First task",
            priority=TaskPriority.HIGH,
            tags=["test", "important"]
        )
        
        task2 = manager.create_task(
            title="Task 2",
            description="Second task",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.LOW
        )
        
        task3 = manager.create_task(
            title="Task 3",
            status=TaskStatus.DONE,
            tags=["completed"]
        )
        
        return manager
    
    def test_storage_initialization(self, storage, temp_dir):
        """Test storage initialization creates directory."""
        assert storage.data_dir == temp_dir
        assert storage.data_dir.exists()
        assert storage.tasks_file == temp_dir / "tasks.json"
        assert storage.backup_file == temp_dir / "tasks.json.backup"
    
    def test_save_and_load_tasks(self, storage, manager_with_tasks):
        """Test saving and loading tasks."""
        # Save tasks
        storage.save_tasks(manager_with_tasks)
        
        # Verify file was created
        assert storage.tasks_file.exists()
        
        # Load into new manager
        new_manager = TaskManager(auto_save=False)
        storage.load_tasks(new_manager)
        
        # Verify tasks were loaded correctly
        assert len(new_manager.tasks) == 3
        
        # Check specific task details
        tasks = list(new_manager.tasks.values())
        task1 = next(t for t in tasks if t.title == "Task 1")
        assert task1.description == "First task"
        assert task1.priority == TaskPriority.HIGH
        assert task1.tags == ["test", "important"]
        
        task2 = next(t for t in tasks if t.title == "Task 2")
        assert task2.status == TaskStatus.IN_PROGRESS
        assert task2.priority == TaskPriority.LOW
    
    def test_json_file_format(self, storage, manager_with_tasks):
        """Test the JSON file format is correct."""
        storage.save_tasks(manager_with_tasks)
        
        # Read and parse the JSON file
        with open(storage.tasks_file, 'r') as f:
            data = json.load(f)
        
        assert data["version"] == "1.0.0"
        assert len(data["tasks"]) == 3
        assert "metadata" in data
        assert data["metadata"]["task_count"] == 3
        assert "last_modified" in data["metadata"]
        
        # Check task structure
        task = data["tasks"][0]
        assert all(key in task for key in [
            "id", "title", "description", "status", "priority",
            "created_at", "updated_at", "due_date", "tags"
        ])
    
    def test_backup_creation(self, storage, manager_with_tasks):
        """Test backup file is created on save."""
        # First save
        storage.save_tasks(manager_with_tasks)
        assert not storage.backup_file.exists()
        
        # Second save should create backup
        manager_with_tasks.create_task("New Task")
        storage.save_tasks(manager_with_tasks)
        assert storage.backup_file.exists()
        
        # Backup should contain original 3 tasks
        backup_data = json.loads(storage.backup_file.read_text())
        assert len(backup_data["tasks"]) == 3
    
    def test_atomic_write(self, storage, manager_with_tasks, monkeypatch):
        """Test atomic write prevents corruption."""
        storage.save_tasks(manager_with_tasks)
        original_content = storage.tasks_file.read_text()
        
        # Simulate write failure by making the temp file fail
        original_open = open
        
        def mock_open_fail(path, *args, **kwargs):
            # Only fail on writing to .tmp files
            if str(path).endswith('.tmp') and 'w' in str(args):
                raise IOError("Simulated write failure")
            return original_open(path, *args, **kwargs)
        
        monkeypatch.setattr("builtins.open", mock_open_fail)
        
        # Try to save again (should fail but not corrupt existing file)
        manager_with_tasks.create_task("Another Task")
        
        with pytest.raises(StorageError):
            storage.save_tasks(manager_with_tasks)
        
        # Original file should still be intact
        monkeypatch.undo()  # Restore normal open
        assert storage.tasks_file.read_text() == original_content
        
        # Verify we can still load the original tasks
        new_manager = TaskManager(auto_save=False)
        storage.load_tasks(new_manager)
        assert len(new_manager.tasks) == 3  # Original count
    
    def test_load_nonexistent_file(self, storage):
        """Test loading when no file exists."""
        manager = TaskManager(auto_save=False)
        storage.load_tasks(manager)  # Should not raise
        assert len(manager.tasks) == 0
    
    def test_load_corrupted_json(self, storage):
        """Test loading corrupted JSON file."""
        # Write invalid JSON
        storage.tasks_file.write_text("{ invalid json }")
        
        manager = TaskManager(auto_save=False)
        with pytest.raises(StorageError, match="Invalid JSON"):
            storage.load_tasks(manager)
    
    def test_export_tasks(self, storage, manager_with_tasks, temp_dir):
        """Test exporting tasks to a file."""
        export_file = temp_dir / "export.json"
        storage.export_tasks(manager_with_tasks, export_file)
        
        # Verify export file
        assert export_file.exists()
        data = json.loads(export_file.read_text())
        
        assert data["version"] == "1.0.0"
        assert len(data["tasks"]) == 3
        assert "exported_at" in data
        assert data["metadata"]["task_count"] == 3
    
    def test_import_tasks_replace(self, storage, manager_with_tasks, temp_dir):
        """Test importing tasks (replace mode)."""
        # Export tasks first
        export_file = temp_dir / "export.json"
        storage.export_tasks(manager_with_tasks, export_file)
        
        # Create new manager with different tasks
        new_manager = TaskManager(auto_save=False)
        new_manager.create_task("Different Task")
        assert len(new_manager.tasks) == 1
        
        # Import (replace mode)
        count = storage.import_tasks(new_manager, export_file, merge=False)
        assert count == 3
        assert len(new_manager.tasks) == 3
        assert not any(t.title == "Different Task" for t in new_manager.tasks.values())
    
    def test_import_tasks_merge(self, storage, manager_with_tasks, temp_dir):
        """Test importing tasks (merge mode)."""
        # Export tasks first
        export_file = temp_dir / "export.json"
        storage.export_tasks(manager_with_tasks, export_file)
        
        # Create new manager with different task
        new_manager = TaskManager(auto_save=False)
        new_manager.create_task("Existing Task")
        original_count = len(new_manager.tasks)
        
        # Import (merge mode)
        count = storage.import_tasks(new_manager, export_file, merge=True)
        assert count == 3
        assert len(new_manager.tasks) == 4  # 1 existing + 3 imported
        assert any(t.title == "Existing Task" for t in new_manager.tasks.values())
    
    def test_storage_info(self, storage, manager_with_tasks):
        """Test getting storage information."""
        # Before saving
        info = storage.get_storage_info()
        assert info["file_exists"] is False
        assert "file_size" not in info
        
        # After saving
        storage.save_tasks(manager_with_tasks)
        info = storage.get_storage_info()
        
        assert info["file_exists"] is True
        assert info["file_size"] > 0
        assert "last_modified" in info
        assert info["data_directory"] == str(storage.data_dir)
    
    def test_environment_variable_override(self, temp_dir, monkeypatch):
        """Test TASKMANAGER_DATA_DIR environment variable."""
        custom_dir = temp_dir / "custom"
        monkeypatch.setenv("TASKMANAGER_DATA_DIR", str(custom_dir))
        
        storage = JSONStorage()
        assert storage.data_dir == custom_dir
        assert custom_dir.exists()
    
    def test_auto_save_integration(self, storage):
        """Test auto-save integration with TaskManager."""
        # Create manager with auto-save enabled
        manager = TaskManager(auto_save=True)
        manager._storage = storage
        
        # Create a task (should auto-save)
        task = manager.create_task("Auto-saved Task")
        
        # Load into new manager to verify
        new_manager = TaskManager(auto_save=False)
        storage.load_tasks(new_manager)
        
        assert len(new_manager.tasks) == 1
        loaded_task = list(new_manager.tasks.values())[0]
        assert loaded_task.title == "Auto-saved Task"