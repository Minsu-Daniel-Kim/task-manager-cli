"""
JSON storage backend for task persistence.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from .models import Task
from .manager import TaskManager


class StorageError(Exception):
    """Raised when storage operations fail."""
    pass


class JSONStorage:
    """
    Handles JSON file storage for tasks with atomic writes and backups.
    """
    
    DEFAULT_DATA_DIR = Path.home() / ".taskmanager"
    TASKS_FILE = "tasks.json"
    BACKUP_EXTENSION = ".backup"
    CURRENT_VERSION = "1.0.0"
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize storage with data directory.
        
        Args:
            data_dir: Custom data directory path (defaults to ~/.taskmanager)
        """
        # Check environment variable for custom data directory
        env_data_dir = os.getenv("TASKMANAGER_DATA_DIR")
        if env_data_dir:
            self.data_dir = Path(env_data_dir)
        else:
            self.data_dir = data_dir or self.DEFAULT_DATA_DIR
        
        self.tasks_file = self.data_dir / self.TASKS_FILE
        self.backup_file = self.data_dir / f"{self.TASKS_FILE}{self.BACKUP_EXTENSION}"
        
        # Ensure data directory exists
        self._ensure_data_dir()
    
    def _ensure_data_dir(self) -> None:
        """Create data directory if it doesn't exist."""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise StorageError(f"Failed to create data directory: {e}")
    
    def _create_backup(self) -> None:
        """Create a backup of the current tasks file."""
        if self.tasks_file.exists():
            try:
                shutil.copy2(self.tasks_file, self.backup_file)
            except Exception as e:
                raise StorageError(f"Failed to create backup: {e}")
    
    def _restore_backup(self) -> None:
        """Restore tasks from backup file."""
        if self.backup_file.exists():
            try:
                shutil.copy2(self.backup_file, self.tasks_file)
            except Exception as e:
                raise StorageError(f"Failed to restore backup: {e}")
    
    def _serialize_task(self, task: Task) -> dict:
        """Convert a Task object to a JSON-serializable dict."""
        return task.to_dict()
    
    def _deserialize_task(self, data: dict) -> Task:
        """Convert a dict to a Task object."""
        return Task.from_dict(data)
    
    def save_tasks(self, task_manager: TaskManager) -> None:
        """
        Save all tasks to JSON file with atomic write.
        
        Args:
            task_manager: TaskManager instance containing tasks
        """
        # Create backup before saving
        self._create_backup()
        
        # Prepare data structure
        data = {
            "version": self.CURRENT_VERSION,
            "tasks": [self._serialize_task(task) for task in task_manager.tasks.values()],
            "metadata": {
                "last_modified": datetime.now().isoformat(),
                "task_count": len(task_manager.tasks)
            }
        }
        
        # Write to temporary file first (atomic write)
        temp_file = self.tasks_file.with_suffix('.tmp')
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_file.replace(self.tasks_file)
            
        except Exception as e:
            # Restore from backup on failure
            if temp_file.exists():
                temp_file.unlink()
            self._restore_backup()
            raise StorageError(f"Failed to save tasks: {e}")
    
    def load_tasks(self, task_manager: TaskManager) -> None:
        """
        Load tasks from JSON file into TaskManager.
        
        Args:
            task_manager: TaskManager instance to populate
        """
        if not self.tasks_file.exists():
            # No tasks file yet, start with empty manager
            return
        
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check version for future migration support
            version = data.get('version', '0.1.0')
            if version != self.CURRENT_VERSION:
                # In the future, handle migrations here
                pass
            
            # Clear existing tasks
            task_manager.tasks.clear()
            
            # Load tasks
            for task_data in data.get('tasks', []):
                task = self._deserialize_task(task_data)
                task_manager.tasks[task.id] = task
                
        except json.JSONDecodeError as e:
            raise StorageError(f"Invalid JSON in tasks file: {e}")
        except Exception as e:
            raise StorageError(f"Failed to load tasks: {e}")
    
    def export_tasks(self, task_manager: TaskManager, export_file: Path) -> None:
        """
        Export tasks to a specified file.
        
        Args:
            task_manager: TaskManager instance containing tasks
            export_file: Path to export file
        """
        data = {
            "version": self.CURRENT_VERSION,
            "exported_at": datetime.now().isoformat(),
            "tasks": [self._serialize_task(task) for task in task_manager.tasks.values()],
            "metadata": {
                "task_count": len(task_manager.tasks),
                "export_source": str(self.tasks_file)
            }
        }
        
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise StorageError(f"Failed to export tasks: {e}")
    
    def import_tasks(self, task_manager: TaskManager, import_file: Path, 
                     merge: bool = False) -> int:
        """
        Import tasks from a file.
        
        Args:
            task_manager: TaskManager instance to populate
            import_file: Path to import file
            merge: If True, merge with existing tasks; if False, replace
            
        Returns:
            Number of tasks imported
        """
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not merge:
                task_manager.tasks.clear()
            
            count = 0
            for task_data in data.get('tasks', []):
                task = self._deserialize_task(task_data)
                # Only add if not already present (when merging)
                if task.id not in task_manager.tasks:
                    task_manager.tasks[task.id] = task
                    count += 1
            
            return count
            
        except json.JSONDecodeError as e:
            raise StorageError(f"Invalid JSON in import file: {e}")
        except Exception as e:
            raise StorageError(f"Failed to import tasks: {e}")
    
    def get_storage_info(self) -> dict:
        """
        Get information about storage.
        
        Returns:
            Dictionary with storage information
        """
        info = {
            "data_directory": str(self.data_dir),
            "tasks_file": str(self.tasks_file),
            "file_exists": self.tasks_file.exists(),
            "backup_exists": self.backup_file.exists()
        }
        
        if self.tasks_file.exists():
            stat = self.tasks_file.stat()
            info.update({
                "file_size": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return info


# Global storage instance
storage = None


def get_storage() -> JSONStorage:
    """Get or create the global storage instance."""
    global storage
    if storage is None:
        storage = JSONStorage()
    return storage