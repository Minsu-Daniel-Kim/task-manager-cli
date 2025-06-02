"""
Display utilities for formatting task output.
"""

from rich.table import Table
from rich.console import Console
from rich.text import Text
from typing import List, Optional
from .models import Task, TaskStatus, TaskPriority


console = Console()


def get_status_display(status: TaskStatus) -> Text:
    """Get colored status display with emoji."""
    status_map = {
        TaskStatus.TODO: ("📋 todo", "yellow"),
        TaskStatus.IN_PROGRESS: ("🔄 in progress", "blue"),
        TaskStatus.DONE: ("✅ done", "green")
    }
    text, color = status_map[status]
    return Text(text, style=color)


def get_priority_display(priority: TaskPriority) -> Text:
    """Get colored priority display with emoji."""
    priority_map = {
        TaskPriority.LOW: ("🟢 low", "green"),
        TaskPriority.MEDIUM: ("🟡 medium", "yellow"),
        TaskPriority.HIGH: ("🟠 high", "orange1"),
        TaskPriority.URGENT: ("🔴 urgent", "red")
    }
    text, color = priority_map[priority]
    return Text(text, style=color)


def format_date(date) -> str:
    """Format date for display."""
    if date:
        return date.strftime("%Y-%m-%d")
    return "-"


def format_tags(tags: List[str]) -> str:
    """Format tags for display."""
    if tags:
        return ", ".join(tags)
    return "-"


def create_task_table(tasks: List[Task], title: Optional[str] = None) -> Table:
    """Create a rich table for displaying tasks."""
    table = Table(title=title or "Tasks", show_header=True, header_style="bold magenta")
    
    # Add columns
    table.add_column("ID", style="cyan", width=8)
    table.add_column("Title", style="white")
    table.add_column("Status", justify="center")
    table.add_column("Priority", justify="center")
    table.add_column("Due Date", style="green")
    table.add_column("Tags", style="dim")
    
    # Add rows
    for task in tasks:
        table.add_row(
            task.short_id,
            task.title,
            get_status_display(task.status),
            get_priority_display(task.priority),
            format_date(task.due_date),
            format_tags(task.tags)
        )
    
    return table


def display_task_detail(task: Task) -> None:
    """Display detailed information about a single task."""
    console.print(f"\n[bold cyan]Task Details[/bold cyan]")
    console.print(f"[bold]ID:[/bold] {task.short_id} ({task.id})")
    console.print(f"[bold]Title:[/bold] {task.title}")
    console.print(f"[bold]Description:[/bold] {task.description or '[dim]No description[/dim]'}")
    console.print(f"[bold]Status:[/bold] {get_status_display(task.status)}")
    console.print(f"[bold]Priority:[/bold] {get_priority_display(task.priority)}")
    console.print(f"[bold]Created:[/bold] {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    console.print(f"[bold]Updated:[/bold] {task.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    console.print(f"[bold]Due Date:[/bold] {format_date(task.due_date)}")
    console.print(f"[bold]Tags:[/bold] {format_tags(task.tags)}")
    if task.linear_issue_id:
        console.print(f"[bold]Linear Issue:[/bold] {task.linear_issue_id}")
    console.print()


def display_stats(stats: dict) -> None:
    """Display task statistics."""
    console.print("\n[bold cyan]Task Statistics[/bold cyan]")
    console.print(f"[bold]Total Tasks:[/bold] {stats['total']}")
    
    console.print("\n[bold]By Status:[/bold]")
    for status, count in stats['by_status'].items():
        console.print(f"  {status}: {count}")
    
    console.print("\n[bold]By Priority:[/bold]")
    for priority, count in stats['by_priority'].items():
        console.print(f"  {priority}: {count}")
    console.print()