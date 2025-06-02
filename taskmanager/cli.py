"""
Main CLI interface for Task Manager.
"""

import click
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm
from .manager import TaskManager, TaskNotFoundError, TaskValidationError
from .models import TaskStatus, TaskPriority
from .display import create_task_table, display_task_detail, display_stats
from .storage import StorageError

console = Console()


def get_task_manager() -> TaskManager:
    """Get or create the task manager instance with persistence."""
    if not hasattr(get_task_manager, "_instance"):
        manager = TaskManager(auto_save=True)
        try:
            manager.load()
        except StorageError as e:
            console.print(f"[yellow]Warning: Could not load tasks: {e}[/yellow]")
        get_task_manager._instance = manager
    return get_task_manager._instance


# Initialize task manager on module load
task_manager = get_task_manager()


@click.group()
@click.version_option(version="0.1.0", prog_name="Task Manager CLI")
@click.pass_context
def cli(ctx):
    """
    Task Manager CLI - A powerful command-line task management tool.
    
    Manage your tasks efficiently with a beautiful terminal interface.
    """
    # Ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)


@cli.command()
def add():
    """Create a new task interactively."""
    console.print("[bold green]Create a new task[/bold green]\n")
    
    try:
        # Get task details interactively
        title = Prompt.ask("Title")
        description = Prompt.ask("Description (optional)", default="")
        
        # Priority selection
        priority_choices = [p.value for p in TaskPriority]
        priority = Prompt.ask(
            "Priority",
            choices=priority_choices,
            default=TaskPriority.MEDIUM.value
        )
        
        # Due date (optional)
        due_date_str = Prompt.ask("Due date (YYYY-MM-DD, optional)", default="")
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            except ValueError:
                console.print("[yellow]Invalid date format, skipping due date[/yellow]")
        
        # Tags
        tags_str = Prompt.ask("Tags (comma-separated, optional)", default="")
        tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
        
        # Create the task
        task = task_manager.create_task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            tags=tags
        )
        
        console.print(f"\n[green]✅ Task created successfully![/green]")
        console.print(f"[cyan]ID: {task.short_id}[/cyan]")
        
    except TaskValidationError as e:
        console.print(f"[red]Error: {e}[/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Task creation cancelled[/yellow]")


@cli.command()
@click.option("--status", help="Filter by status (comma-separated)")
@click.option("--priority", help="Filter by priority (comma-separated)")
@click.option("--tag", help="Filter by tag")
def list(status, priority, tag):
    """List all tasks with optional filters."""
    # For now, only support single status/priority filter (multi-filter in TEA-15)
    status_filter = status.split(",")[0] if status else None
    priority_filter = priority.split(",")[0] if priority else None
    
    try:
        tasks = task_manager.list_tasks(status=status_filter, priority=priority_filter)
        
        if not tasks:
            console.print("[yellow]No tasks found[/yellow]")
            console.print("\nUse 'task add' to create your first task!")
            return
        
        # Filter by tag if provided (basic implementation)
        if tag:
            tasks = [t for t in tasks if tag in t.tags]
        
        table = create_task_table(tasks)
        console.print(table)
        
        # Show stats
        stats = task_manager.get_stats()
        console.print(f"\n[dim]Total: {stats['total']} tasks[/dim]")
        
    except TaskValidationError as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument("task_id")
def show(task_id):
    """Display detailed information about a task."""
    try:
        task = task_manager.get_task(task_id)
        display_task_detail(task)
    except TaskNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument("task_id")
@click.option("--status", help="New status")
@click.option("--priority", help="New priority")
@click.option("--title", help="New title")
@click.option("--description", help="New description")
def update(task_id, status, priority, title, description):
    """Update task properties."""
    try:
        # Build update dict with only provided options
        updates = {}
        if status:
            updates['status'] = status
        if priority:
            updates['priority'] = priority
        if title:
            updates['title'] = title
        if description is not None:
            updates['description'] = description
        
        if not updates:
            console.print("[yellow]No updates provided[/yellow]")
            return
        
        task = task_manager.update_task(task_id, **updates)
        console.print(f"[green]✅ Task {task.short_id} updated successfully![/green]")
        
    except TaskNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
    except TaskValidationError as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument("task_id")
@click.confirmation_option(prompt="Are you sure you want to delete this task?")
def delete(task_id):
    """Delete a task."""
    try:
        task = task_manager.delete_task(task_id)
        console.print(f"[red]🗑️  Task '{task.title}' deleted[/red]")
    except TaskNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument("task_id")
def done(task_id):
    """Mark a task as complete."""
    try:
        task = task_manager.mark_done(task_id)
        console.print(f"[green]✅ Task '{task.title}' marked as done![/green]")
    except TaskNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")


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


# Storage commands
@cli.command()
@click.argument("export_file", type=click.Path())
def export(export_file):
    """Export tasks to a JSON file."""
    try:
        from pathlib import Path
        export_path = Path(export_file)
        task_manager.storage.export_tasks(task_manager, export_path)
        console.print(f"[green]✅ Exported {len(task_manager.tasks)} tasks to {export_file}[/green]")
    except StorageError as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.argument("import_file", type=click.Path(exists=True))
@click.option("--merge", is_flag=True, help="Merge with existing tasks instead of replacing")
def import_tasks(import_file, merge):
    """Import tasks from a JSON file."""
    try:
        from pathlib import Path
        import_path = Path(import_file)
        
        if not merge and task_manager.tasks:
            if not Confirm.ask(f"This will replace all {len(task_manager.tasks)} existing tasks. Continue?"):
                console.print("[yellow]Import cancelled[/yellow]")
                return
        
        count = task_manager.storage.import_tasks(task_manager, import_path, merge=merge)
        task_manager.save()  # Save after import
        
        action = "merged" if merge else "imported"
        console.print(f"[green]✅ Successfully {action} {count} tasks[/green]")
        
    except StorageError as e:
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
def storage_info():
    """Display storage information."""
    info = task_manager.storage.get_storage_info()
    
    console.print("\n[bold cyan]Storage Information[/bold cyan]")
    console.print(f"[bold]Data Directory:[/bold] {info['data_directory']}")
    console.print(f"[bold]Tasks File:[/bold] {info['tasks_file']}")
    console.print(f"[bold]File Exists:[/bold] {'Yes' if info['file_exists'] else 'No'}")
    console.print(f"[bold]Backup Exists:[/bold] {'Yes' if info['backup_exists'] else 'No'}")
    
    if info.get('file_size') is not None:
        size_kb = info['file_size'] / 1024
        console.print(f"[bold]File Size:[/bold] {size_kb:.2f} KB")
        console.print(f"[bold]Last Modified:[/bold] {info['last_modified']}")
    console.print()


if __name__ == "__main__":
    cli()