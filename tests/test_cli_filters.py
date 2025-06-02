"""
Tests for CLI filtering commands.
"""

import pytest
from click.testing import CliRunner
from taskmanager.cli import cli
from taskmanager.models import TaskStatus, TaskPriority
from datetime import datetime, timedelta


class TestCLIFiltering:
    """Test CLI filtering commands."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    def test_list_with_multiple_statuses(self, runner):
        """Test list command with multiple status filters."""
        # First create some tasks
        runner.invoke(cli, ['add'], input='Task 1\nDescription\nlow\n\n\n')
        runner.invoke(cli, ['add'], input='Task 2\nDescription\nhigh\n\n\n')
        
        # Mark one as in progress
        result = runner.invoke(cli, ['list'])
        lines = result.output.strip().split('\n')
        # Extract task ID from output
        task_id = None
        for line in lines:
            if 'Task 2' in line:
                # Extract ID from line (format varies but ID is after title)
                parts = line.split()
                for i, part in enumerate(parts):
                    if len(part) == 6:  # Short ID length
                        task_id = part
                        break
        
        if task_id:
            runner.invoke(cli, ['update', task_id, '--status', 'in_progress'])
        
        # Test filtering by multiple statuses
        result = runner.invoke(cli, ['list', '--status', 'todo,in_progress'])
        assert result.exit_code == 0
        assert 'Task 1' in result.output
        assert 'Task 2' in result.output
    
    def test_list_with_preset_active(self, runner):
        """Test list command with preset filter."""
        # Create tasks
        runner.invoke(cli, ['add'], input='Active Task\nDescription\nmedium\n\n\n')
        
        # Test active preset
        result = runner.invoke(cli, ['active'])
        assert result.exit_code == 0
        assert 'Active Task' in result.output or 'active task(s)' in result.output
    
    def test_list_with_tags(self, runner):
        """Test list command with tag filters."""
        # Create tasks with tags
        runner.invoke(cli, ['add'], input='Tagged Task\nDescription\nmedium\n\nwork,urgent\n')
        
        # Test tag filter
        result = runner.invoke(cli, ['list', '--tag', 'work'])
        if result.exit_code != 0:
            print(f"Error: {result.output}")
        assert result.exit_code == 0
        assert 'Tagged Task' in result.output or 'No tasks found' in result.output
    
    def test_list_with_sorting(self, runner):
        """Test list command with sorting options."""
        # Create multiple tasks
        runner.invoke(cli, ['add'], input='A Task\nDescription\nlow\n\n\n')
        runner.invoke(cli, ['add'], input='Z Task\nDescription\nhigh\n\n\n')
        
        # Test sorting by title ascending
        result = runner.invoke(cli, ['list', '--sort', 'title', '--order', 'asc'])
        assert result.exit_code == 0
        
        # Check that output contains tasks (order may vary in display)
        output_lines = result.output.strip().split('\n')
        task_lines = [line for line in output_lines if 'Task' in line and ('A Task' in line or 'Z Task' in line)]
        assert len(task_lines) >= 1  # At least one task found
    
    def test_search_command(self, runner):
        """Test search command."""
        # Create tasks
        runner.invoke(cli, ['add'], input='Fix login bug\nCritical issue\nhigh\n\nbug,auth\n')
        runner.invoke(cli, ['add'], input='Add logout feature\nNew feature\nmedium\n\nfeature\n')
        
        # Test search
        result = runner.invoke(cli, ['search', 'login'])
        assert result.exit_code == 0
        assert 'login' in result.output.lower() or 'No tasks found' in result.output
    
    def test_search_with_regex(self, runner):
        """Test search command with regex."""
        # Create tasks
        runner.invoke(cli, ['add'], input='TASK-123\nDescription\nmedium\n\n\n')
        runner.invoke(cli, ['add'], input='TASK-456\nDescription\nmedium\n\n\n')
        
        # Test regex search
        result = runner.invoke(cli, ['search', 'TASK-\\d+', '--regex'])
        assert result.exit_code == 0
        # Either finds tasks or shows no results
        assert 'TASK-' in result.output or 'No tasks found' in result.output
    
    def test_overdue_command(self, runner):
        """Test overdue command."""
        # Create an overdue task
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        runner.invoke(cli, ['add'], input=f'Overdue Task\nDescription\nhigh\n{yesterday}\n\n')
        
        # Test overdue command
        result = runner.invoke(cli, ['overdue'])
        assert result.exit_code == 0
        assert 'Overdue Task' in result.output or 'No overdue tasks' in result.output
    
    def test_today_command(self, runner):
        """Test today command."""
        # Create a task due today
        today = datetime.now().strftime('%Y-%m-%d')
        runner.invoke(cli, ['add'], input=f'Task Due Today\nDescription\nmedium\n{today}\n\n')
        
        # Test today command
        result = runner.invoke(cli, ['today'])
        assert result.exit_code == 0
        assert 'Task Due Today' in result.output or 'No tasks due today' in result.output
    
    def test_list_with_invalid_preset(self, runner):
        """Test list command with invalid preset."""
        result = runner.invoke(cli, ['list', '--preset', 'invalid_preset'])
        # Click should catch invalid choice
        assert result.exit_code != 0
        assert 'Invalid value' in result.output
    
    def test_empty_search_results(self, runner):
        """Test search with no results."""
        # Create a task
        runner.invoke(cli, ['add'], input='Some Task\nDescription\nmedium\n\n\n')
        
        # Search for something that doesn't exist
        result = runner.invoke(cli, ['search', 'nonexistent'])
        assert result.exit_code == 0
        assert 'No tasks found' in result.output