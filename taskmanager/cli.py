"""
Main CLI interface for Task Manager.
"""

import click
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.rule import Rule
from .manager import TaskManager, TaskNotFoundError, TaskValidationError
from .models import TaskStatus, TaskPriority
from .display import create_task_table, display_task_detail, display_stats
from .utils import (
    show_spinner, prompt_date, prompt_tags, show_success, show_error,
    show_warning, show_info, create_header, confirm_action,
    select_from_list, format_task_summary
)

console = Console()

# Global task manager instance (will be replaced with persistence in TEA-13)
task_manager = TaskManager()


@click.group()
@click.version_option(version="0.2.0", prog_name="Task Manager CLI")
@click.pass_context
def cli(ctx):
    """
    Task Manager CLI - A powerful command-line task management tool.
    
    Manage your tasks efficiently with a beautiful terminal interface.
    """
    # Ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)


@cli.command()
@click.option("--quick", "-q", is_flag=True, help="Quick add with just title")
def add(quick):
    """Create a new task interactively."""
    create_header("Create New Task", "Add a new task to your list")
    
    try:
        # Get task details interactively
        title = Prompt.ask("[bold]Title[/bold]")
        
        if quick:
            # Quick mode - just create with defaults
            task = show_spinner(
                "Creating task...",
                lambda: task_manager.create_task(title=title)
            )
            show_success(f"Task created successfully! ID: {task.short_id}")
            return
        
        description = Prompt.ask("[bold]Description[/bold] (optional)", default="")
        
        # Priority selection with better display
        console.print("\n[bold]Priority levels:[/bold]")
        console.print("  🟢 low - Low priority tasks")
        console.print("  🟡 medium - Normal priority (default)")
        console.print("  🟠 high - Important tasks")
        console.print("  🔴 urgent - Critical tasks\n")
        
        priority_choices = [p.value for p in TaskPriority]
        priority = Prompt.ask(
            "[bold]Priority[/bold]",
            choices=priority_choices,
            default=TaskPriority.MEDIUM.value
        )
        
        # Enhanced due date input
        console.print("\n[dim]Due date formats: YYYY-MM-DD, today, tomorrow, +7 (days)[/dim]")
        due_date = prompt_date("[bold]Due date[/bold] (optional)")
        
        # Tags with validation
        tags = prompt_tags("[bold]Tags[/bold] (comma-separated, optional)")
        
        # Show summary before creating
        console.print("\n[bold cyan]Task Summary:[/bold cyan]")
        console.print(f"  Title: {title}")
        if description:
            console.print(f"  Description: {description}")
        console.print(f"  Priority: {priority}")
        if due_date:
            console.print(f"  Due date: {due_date.strftime('%Y-%m-%d')}")
        if tags:
            console.print(f"  Tags: {', '.join(tags)}")
        
        if not confirm_action("\nCreate this task?", default=True):
            show_warning("Task creation cancelled")
            return
        
        # Create the task with spinner
        task = show_spinner(
            "Creating task...",
            lambda: task_manager.create_task(
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                tags=tags
            )
        )
        
        show_success(f"Task created successfully! ID: {task.short_id}")
        
    except TaskValidationError as e:
        show_error(f"Validation error: {e}")
    except KeyboardInterrupt:
        console.print("\n")
        show_warning("Task creation cancelled")


@cli.command(name="list")
@click.option("--status", "-s", help="Filter by status (todo/in_progress/done)")
@click.option("--priority", "-p", help="Filter by priority (low/medium/high/urgent)")
@click.option("--tag", "-t", help="Filter by tag")
@click.option("--summary", is_flag=True, help="Show summary statistics")
def list_tasks(status, priority, tag, summary):
    """List all tasks with optional filters."""
    # Build filter description
    filters = []
    if status:
        filters.append(f"status={status}")
    if priority:
        filters.append(f"priority={priority}")
    if tag:
        filters.append(f"tag={tag}")
    
    filter_desc = f" (filtered by {', '.join(filters)})" if filters else ""
    
    try:
        # Get tasks with filters
        tasks = show_spinner(
            "Loading tasks...",
            lambda: task_manager.list_tasks(
                status=status,
                priority=priority
            )
        )
        
        # Additional tag filtering
        if tag:
            tasks = [t for t in tasks if tag in t.tags]
        
        if not tasks:
            show_warning(f"No tasks found{filter_desc}")
            if filters:
                show_info("Try removing some filters or use 'task list' to see all tasks")
            else:
                show_info("Use 'task add' to create your first task!")
            return
        
        # Display tasks
        create_header(f"Task List{filter_desc}", f"Showing {len(tasks)} task(s)")
        table = create_task_table(tasks)
        console.print(table)
        
        # Show summary if requested or by default if many tasks
        if summary or len(tasks) > 10:
            console.print()
            console.rule("Summary", style="dim")
            stats = task_manager.get_stats()
            
            # Status breakdown
            console.print("\n[bold]By Status:[/bold]")
            for status_type, count in stats['by_status'].items():
                if count > 0:
                    emoji = {
                        'todo': '📋',
                        'in_progress': '🔄',
                        'done': '✅'
                    }.get(status_type, '')
                    console.print(f"  {emoji} {status_type}: {count}")
            
            # Priority breakdown
            console.print("\n[bold]By Priority:[/bold]")
            for priority_type, count in stats['by_priority'].items():
                if count > 0:
                    emoji = {
                        'low': '🟢',
                        'medium': '🟡',
                        'high': '🟠',
                        'urgent': '🔴'
                    }.get(priority_type, '')
                    console.print(f"  {emoji} {priority_type}: {count}")
            
            console.print(f"\n[dim]Total: {stats['total']} tasks[/dim]")
        
    except TaskValidationError as e:
        show_error(f"Invalid filter: {e}")


@cli.command()
@click.argument("task_id")
@click.option("--format", "-f", type=click.Choice(["detail", "json", "markdown"]), default="detail", help="Output format")
def show(task_id, format):
    """Display detailed information about a task."""
    try:
        task = show_spinner(
            f"Loading task {task_id}...",
            lambda: task_manager.get_task(task_id)
        )
        
        if format == "detail":
            display_task_detail(task)
        elif format == "json":
            import json
            console.print_json(json.dumps(task.to_dict(), indent=2))
        elif format == "markdown":
            # Markdown format
            console.print(f"# {task.title}\n")
            if task.description:
                console.print(f"{task.description}\n")
            console.print(f"**Status**: {task.status.value}")
            console.print(f"**Priority**: {task.priority.value}")
            console.print(f"**Created**: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
            if task.due_date:
                console.print(f"**Due**: {task.due_date.strftime('%Y-%m-%d')}")
            if task.tags:
                console.print(f"**Tags**: {', '.join(task.tags)}")
            
    except TaskNotFoundError:
        show_error(f"Task with ID '{task_id}' not found")
        show_info("Use 'task list' to see available tasks")


@cli.command()
@click.argument("task_id", required=False)
@click.option("--status", "-s", help="New status")
@click.option("--priority", "-p", help="New priority")
@click.option("--title", "-t", help="New title")
@click.option("--description", "-d", help="New description")
@click.option("--due-date", help="New due date (YYYY-MM-DD or relative)")
@click.option("--add-tag", multiple=True, help="Add a tag (can be used multiple times)")
@click.option("--remove-tag", multiple=True, help="Remove a tag (can be used multiple times)")
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode")
def update(task_id, status, priority, title, description, due_date, add_tag, remove_tag, interactive):
    """Update task properties."""
    try:
        # If no task_id provided, show task selection
        if not task_id:
            tasks = task_manager.list_tasks()
            if not tasks:
                show_warning("No tasks available to update")
                return
            
            selected_task = select_from_list(
                tasks,
                "Select a task to update:",
                format_task_summary
            )
            
            if not selected_task:
                show_warning("Update cancelled")
                return
            
            task_id = selected_task.id
        
        # Get the task
        task = task_manager.get_task(task_id)
        
        # Interactive mode
        if interactive or (not any([status, priority, title, description, due_date, add_tag, remove_tag])):
            create_header(f"Update Task: {task.title}", f"ID: {task.short_id}")
            
            # Show current values
            console.print("[bold]Current values:[/bold]")
            console.print(f"  Title: {task.title}")
            console.print(f"  Status: {task.status.value}")
            console.print(f"  Priority: {task.priority.value}")
            console.print(f"  Description: {task.description or '[none]'}")
            console.print(f"  Due date: {task.due_date.strftime('%Y-%m-%d') if task.due_date else '[none]'}")
            console.print(f"  Tags: {', '.join(task.tags) if task.tags else '[none]'}")
            console.print()
            
            # Interactive prompts
            if confirm_action("Update title?"):
                title = Prompt.ask("[bold]New title[/bold]", default=task.title)
            
            if confirm_action("Update status?"):
                status_choices = [s.value for s in TaskStatus]
                status = Prompt.ask(
                    "[bold]New status[/bold]",
                    choices=status_choices,
                    default=task.status.value
                )
            
            if confirm_action("Update priority?"):
                priority_choices = [p.value for p in TaskPriority]
                priority = Prompt.ask(
                    "[bold]New priority[/bold]",
                    choices=priority_choices,
                    default=task.priority.value
                )
            
            if confirm_action("Update description?"):
                description = Prompt.ask(
                    "[bold]New description[/bold]",
                    default=task.description or ""
                )
            
            if confirm_action("Update due date?"):
                due_date = prompt_date("[bold]New due date[/bold] (leave empty to clear)")
                due_date = due_date.strftime("%Y-%m-%d") if due_date else ""
        
        # Build update dict
        updates = {}
        if status:
            updates['status'] = status
        if priority:
            updates['priority'] = priority
        if title:
            updates['title'] = title
        if description is not None:
            updates['description'] = description
        if due_date is not None:
            if due_date:
                updates['due_date'] = datetime.strptime(due_date, "%Y-%m-%d") if isinstance(due_date, str) else due_date
            else:
                updates['due_date'] = None
        
        # Handle tags
        if add_tag or remove_tag:
            current_tags = task.tags.copy()
            for tag in add_tag:
                if tag not in current_tags:
                    current_tags.append(tag)
            for tag in remove_tag:
                if tag in current_tags:
                    current_tags.remove(tag)
            updates['tags'] = current_tags
        
        if not updates:
            show_warning("No updates provided")
            return
        
        # Update with spinner
        task = show_spinner(
            "Updating task...",
            lambda: task_manager.update_task(task_id, **updates)
        )
        
        show_success(f"Task {task.short_id} updated successfully!")
        
        # Show what was updated
        console.print("\n[bold]Updated fields:[/bold]")
        for field, value in updates.items():
            if field == 'due_date':
                value = value.strftime('%Y-%m-%d') if value else 'cleared'
            elif field == 'tags':
                value = ', '.join(value) if value else 'none'
            console.print(f"  {field}: {value}")
        
    except TaskNotFoundError:
        show_error(f"Task with ID '{task_id}' not found")
    except TaskValidationError as e:
        show_error(f"Validation error: {e}")


@cli.command()
@click.argument("task_id", required=False)
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
def delete(task_id, force):
    """Delete a task."""
    try:
        # If no task_id provided, show task selection
        if not task_id:
            tasks = task_manager.list_tasks()
            if not tasks:
                show_warning("No tasks available to delete")
                return
            
            selected_task = select_from_list(
                tasks,
                "Select a task to delete:",
                format_task_summary
            )
            
            if not selected_task:
                show_warning("Delete cancelled")
                return
            
            task_id = selected_task.id
        
        # Get task details for confirmation
        task = task_manager.get_task(task_id)
        
        # Show task details before deletion
        console.print("\n[bold red]Task to be deleted:[/bold red]")
        console.print(f"  Title: {task.title}")
        console.print(f"  Status: {task.status.value}")
        console.print(f"  Created: {task.created_at.strftime('%Y-%m-%d')}")
        
        # Confirmation
        if not force:
            if not confirm_action("\nAre you sure you want to delete this task?"):
                show_warning("Delete cancelled")
                return
        
        # Delete with spinner
        task = show_spinner(
            "Deleting task...",
            lambda: task_manager.delete_task(task_id)
        )
        
        show_error(f"Task '{task.title}' has been deleted")
        
    except TaskNotFoundError:
        show_error(f"Task with ID '{task_id}' not found")


@cli.command()
@click.argument("task_id", required=False)
@click.option("--undo", is_flag=True, help="Mark as todo instead")
def done(task_id, undo):
    """Mark a task as complete (or undo completion)."""
    try:
        # If no task_id provided, show task selection
        if not task_id:
            # Filter based on undo flag
            status_filter = TaskStatus.DONE if undo else TaskStatus.TODO
            tasks = task_manager.list_tasks(status=status_filter)
            
            if not tasks:
                if undo:
                    show_warning("No completed tasks to undo")
                else:
                    show_warning("No todo tasks to complete")
                return
            
            action = "undo completion for" if undo else "mark as done"
            selected_task = select_from_list(
                tasks,
                f"Select a task to {action}:",
                format_task_summary
            )
            
            if not selected_task:
                show_warning("Action cancelled")
                return
            
            task_id = selected_task.id
        
        # Update task status
        new_status = TaskStatus.TODO if undo else TaskStatus.DONE
        task = show_spinner(
            "Updating task status...",
            lambda: task_manager.update_task(task_id, status=new_status)
        )
        
        if undo:
            show_info(f"Task '{task.title}' marked as todo")
        else:
            show_success(f"Task '{task.title}' marked as done!")
        
    except TaskNotFoundError:
        show_error(f"Task with ID '{task_id}' not found")


@cli.command()
def today():
    """Show tasks due today or overdue."""
    create_header("Today's Tasks", "Tasks due today or overdue")
    
    try:
        all_tasks = task_manager.list_tasks()
        today = datetime.now().date()
        
        # Filter tasks
        overdue_tasks = []
        today_tasks = []
        
        for task in all_tasks:
            if task.due_date and task.status != TaskStatus.DONE:
                task_date = task.due_date.date()
                if task_date < today:
                    overdue_tasks.append(task)
                elif task_date == today:
                    today_tasks.append(task)
        
        # Display overdue tasks
        if overdue_tasks:
            console.print("[bold red]⚠️  Overdue Tasks:[/bold red]")
            overdue_table = create_task_table(overdue_tasks, title=None)
            console.print(overdue_table)
            console.print()
        
        # Display today's tasks
        if today_tasks:
            console.print("[bold yellow]📅 Due Today:[/bold yellow]")
            today_table = create_task_table(today_tasks, title=None)
            console.print(today_table)
        
        if not overdue_tasks and not today_tasks:
            show_info("No tasks due today or overdue")
            
    except Exception as e:
        show_error(f"Error loading tasks: {e}")


@cli.command()
def clear():
    """Clear completed tasks (interactive)."""
    try:
        done_tasks = task_manager.list_tasks(status=TaskStatus.DONE)
        
        if not done_tasks:
            show_info("No completed tasks to clear")
            return
        
        create_header("Clear Completed Tasks", f"Found {len(done_tasks)} completed task(s)")
        
        # Show completed tasks
        table = create_task_table(done_tasks)
        console.print(table)
        
        if not confirm_action(f"\nDelete all {len(done_tasks)} completed tasks?"):
            show_warning("Clear cancelled")
            return
        
        # Delete tasks with progress
        deleted_count = 0
        with console.status("[bold green]Clearing completed tasks...") as status:
            for task in done_tasks:
                task_manager.delete_task(task.id)
                deleted_count += 1
                status.update(f"[bold green]Clearing completed tasks... {deleted_count}/{len(done_tasks)}")
        
        show_success(f"Cleared {deleted_count} completed tasks")
        
    except Exception as e:
        show_error(f"Error clearing tasks: {e}")


@cli.command()
@click.argument("query")
def search(query):
    """Search for tasks by keyword."""
    console.print(f"[bold]Searching for: {query}[/bold]")
    console.print("This feature will be implemented in TEA-15")


# Linear integration commands
@cli.group()
def linear():
    """Linear integration commands."""
    pass


@linear.command()
def pull():
    """Pull issues from Linear."""
    console.print("[blue]Pulling issues from Linear...[/blue]")
    console.print("This feature will be implemented in TEA-16")


@linear.command()
@click.argument("task_id")
def push(task_id):
    """Push a task to Linear."""
    console.print(f"[blue]Pushing task {task_id} to Linear...[/blue]")
    console.print("This feature will be implemented in TEA-16")


@linear.command()
def status():
    """Check Linear sync status."""
    console.print("[bold]Linear Sync Status[/bold]")
    console.print("This feature will be implemented in TEA-16")


# Stats command
@cli.command()
def stats():
    """Display task statistics."""
    stats = task_manager.get_stats()
    display_stats(stats)


# Configuration commands
@cli.group()
def config():
    """Configuration commands."""
    pass


@config.command()
def linear():
    """Configure Linear integration."""
    console.print("[bold]Linear Configuration[/bold]")
    console.print("This feature will be implemented in TEA-16")


if __name__ == "__main__":
    cli()