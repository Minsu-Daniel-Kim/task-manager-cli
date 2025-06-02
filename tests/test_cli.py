"""
Tests for enhanced CLI interface.
"""

import pytest
from click.testing import CliRunner
from datetime import datetime, timedelta
from taskmanager.cli import cli
from taskmanager.manager import TaskManager
from taskmanager.models import TaskStatus, TaskPriority


class TestCLI:
    """Test cases for CLI commands."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def manager_with_tasks(self, monkeypatch):
        """Create a manager with test tasks."""
        manager = TaskManager()
        
        # Add test tasks
        manager.create_task(
            "Test Task 1",
            "Description 1",
            priority=TaskPriority.HIGH,
            tags=["test", "urgent"]
        )
        
        manager.create_task(
            "Test Task 2",
            "Description 2",
            status=TaskStatus.IN_PROGRESS,
            due_date=datetime.now() + timedelta(days=1)
        )
        
        manager.create_task(
            "Test Task 3",
            status=TaskStatus.DONE,
            priority=TaskPriority.LOW
        )
        
        # Patch the global task_manager
        monkeypatch.setattr("taskmanager.cli.task_manager", manager)
        return manager
    
    def test_cli_version(self, runner):
        """Test version option."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.2.0" in result.output
    
    def test_cli_help(self, runner):
        """Test help option."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Task Manager CLI" in result.output
        assert "Commands:" in result.output
    
    def test_add_quick(self, runner, monkeypatch):
        """Test quick add command."""
        # Mock the task manager
        manager = TaskManager()
        monkeypatch.setattr("taskmanager.cli.task_manager", manager)
        
        result = runner.invoke(cli, ["add", "--quick"], input="Quick test task\n")
        assert result.exit_code == 0
        assert "Task created successfully!" in result.output
        assert len(manager.tasks) == 1
    
    def test_list_empty(self, runner, monkeypatch):
        """Test list command with no tasks."""
        manager = TaskManager()
        monkeypatch.setattr("taskmanager.cli.task_manager", manager)
        
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "No tasks found" in result.output
    
    def test_list_with_tasks(self, runner, manager_with_tasks):
        """Test list command with tasks."""
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "Test Task 1" in result.output
        assert "Test Task 2" in result.output
        assert "Test Task 3" in result.output
    
    def test_list_with_filters(self, runner, manager_with_tasks):
        """Test list command with filters."""
        # Filter by status
        result = runner.invoke(cli, ["list", "--status", "todo"])
        assert result.exit_code == 0
        assert "Test Task 1" in result.output
        assert "Test Task 2" not in result.output
        
        # Filter by priority
        result = runner.invoke(cli, ["list", "--priority", "high"])
        assert result.exit_code == 0
        assert "Test Task 1" in result.output
        assert "Test Task 3" not in result.output
    
    def test_list_summary(self, runner, manager_with_tasks):
        """Test list command with summary."""
        result = runner.invoke(cli, ["list", "--summary"])
        assert result.exit_code == 0
        assert "By Status:" in result.output
        assert "By Priority:" in result.output
        assert "Total:" in result.output
    
    def test_show_task(self, runner, manager_with_tasks):
        """Test show command."""
        task_id = list(manager_with_tasks.tasks.keys())[0]
        short_id = task_id[:6]
        
        result = runner.invoke(cli, ["show", short_id])
        assert result.exit_code == 0
        assert "Test Task 1" in result.output
        assert "Description 1" in result.output
    
    def test_show_nonexistent(self, runner, manager_with_tasks):
        """Test show command with nonexistent task."""
        result = runner.invoke(cli, ["show", "nonexistent"])
        assert result.exit_code == 0
        assert "not found" in result.output
    
    def test_update_task(self, runner, manager_with_tasks):
        """Test update command."""
        task_id = list(manager_with_tasks.tasks.keys())[0]
        short_id = task_id[:6]
        
        result = runner.invoke(cli, [
            "update", short_id,
            "--title", "Updated Title",
            "--priority", "low"
        ])
        assert result.exit_code == 0
        assert "updated successfully" in result.output
        
        # Verify update
        task = manager_with_tasks.get_task(task_id)
        assert task.title == "Updated Title"
        assert task.priority == TaskPriority.LOW
    
    def test_done_command(self, runner, manager_with_tasks):
        """Test done command."""
        # Get a todo task
        todo_task = next(t for t in manager_with_tasks.tasks.values() 
                        if t.status == TaskStatus.TODO)
        
        result = runner.invoke(cli, ["done", todo_task.short_id])
        assert result.exit_code == 0
        assert "marked as done" in result.output
        
        # Verify status change
        assert todo_task.status == TaskStatus.DONE
    
    def test_done_undo(self, runner, manager_with_tasks):
        """Test done command with undo."""
        # Get a done task
        done_task = next(t for t in manager_with_tasks.tasks.values() 
                        if t.status == TaskStatus.DONE)
        
        result = runner.invoke(cli, ["done", done_task.short_id, "--undo"])
        assert result.exit_code == 0
        assert "marked as todo" in result.output
        
        # Verify status change
        assert done_task.status == TaskStatus.TODO
    
    def test_delete_with_confirmation(self, runner, manager_with_tasks):
        """Test delete command with confirmation."""
        task_id = list(manager_with_tasks.tasks.keys())[0]
        short_id = task_id[:6]
        
        # Confirm deletion
        result = runner.invoke(cli, ["delete", short_id], input="y\n")
        assert result.exit_code == 0
        assert "has been deleted" in result.output
        assert task_id not in manager_with_tasks.tasks
    
    def test_delete_cancelled(self, runner, manager_with_tasks):
        """Test delete command cancelled."""
        task_id = list(manager_with_tasks.tasks.keys())[0]
        short_id = task_id[:6]
        initial_count = len(manager_with_tasks.tasks)
        
        # Cancel deletion
        result = runner.invoke(cli, ["delete", short_id], input="n\n")
        assert result.exit_code == 0
        assert "Delete cancelled" in result.output
        assert len(manager_with_tasks.tasks) == initial_count
    
    def test_delete_force(self, runner, manager_with_tasks):
        """Test delete command with force flag."""
        task_id = list(manager_with_tasks.tasks.keys())[0]
        short_id = task_id[:6]
        
        result = runner.invoke(cli, ["delete", short_id, "--force"])
        assert result.exit_code == 0
        assert "has been deleted" in result.output
        assert task_id not in manager_with_tasks.tasks
    
    def test_today_command(self, runner, monkeypatch):
        """Test today command."""
        manager = TaskManager()
        
        # Add tasks with different due dates
        manager.create_task("Overdue", due_date=datetime.now() - timedelta(days=1))
        manager.create_task("Today", due_date=datetime.now())
        manager.create_task("Tomorrow", due_date=datetime.now() + timedelta(days=1))
        manager.create_task("No due date")
        
        monkeypatch.setattr("taskmanager.cli.task_manager", manager)
        
        result = runner.invoke(cli, ["today"])
        assert result.exit_code == 0
        assert "Overdue" in result.output
        assert "Today" in result.output
        assert "Tomorrow" not in result.output
        assert "No due date" not in result.output
    
    def test_clear_command(self, runner, manager_with_tasks):
        """Test clear command."""
        # Ensure we have done tasks
        done_count = len([t for t in manager_with_tasks.tasks.values() 
                         if t.status == TaskStatus.DONE])
        assert done_count > 0
        
        # Confirm clear
        result = runner.invoke(cli, ["clear"], input="y\n")
        assert result.exit_code == 0
        assert f"Cleared {done_count} completed tasks" in result.output
        
        # Verify done tasks are removed
        remaining_done = len([t for t in manager_with_tasks.tasks.values() 
                             if t.status == TaskStatus.DONE])
        assert remaining_done == 0
    
    def test_stats_command(self, runner, manager_with_tasks):
        """Test stats command."""
        result = runner.invoke(cli, ["stats"])
        assert result.exit_code == 0
        assert "Task Statistics" in result.output
        assert "By Status:" in result.output
        assert "By Priority:" in result.output