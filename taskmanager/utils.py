"""
Utility functions for enhanced CLI interactions.
"""

import time
from typing import Optional, List, Callable, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.text import Text
from datetime import datetime


console = Console()


def show_spinner(message: str, task: Callable[[], Any]) -> Any:
    """
    Show a spinner while executing a task.
    
    Args:
        message: Message to display
        task: Function to execute
        
    Returns:
        Result of the task function
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        progress.add_task(description=message, total=None)
        time.sleep(0.5)  # Show spinner for at least 0.5s for UX
        return task()


def format_datetime(dt: Optional[datetime]) -> str:
    """Format datetime for display."""
    if not dt:
        return "-"
    
    today = datetime.now().date()
    dt_date = dt.date()
    
    if dt_date == today:
        return f"Today {dt.strftime('%H:%M')}"
    elif (dt_date - today).days == 1:
        return f"Tomorrow {dt.strftime('%H:%M')}"
    elif (dt_date - today).days == -1:
        return f"Yesterday {dt.strftime('%H:%M')}"
    elif -7 < (dt_date - today).days < 7:
        return dt.strftime("%A %H:%M")
    else:
        return dt.strftime("%Y-%m-%d %H:%M")


def prompt_date(prompt_text: str, allow_empty: bool = True) -> Optional[datetime]:
    """
    Prompt for a date with various input formats.
    
    Supports:
    - YYYY-MM-DD
    - today, tomorrow, yesterday
    - +N (N days from now)
    - Day names (monday, tuesday, etc.)
    """
    date_str = Prompt.ask(prompt_text, default="" if allow_empty else None)
    
    if not date_str and allow_empty:
        return None
    
    date_str = date_str.lower().strip()
    
    # Handle relative dates
    if date_str == "today":
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_str == "tomorrow":
        from datetime import timedelta
        return (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_str == "yesterday":
        from datetime import timedelta
        return (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_str.startswith("+"):
        try:
            from datetime import timedelta
            days = int(date_str[1:])
            return (datetime.now() + timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            pass
    
    # Try standard date format
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        console.print("[yellow]Invalid date format. Please use YYYY-MM-DD or relative dates.[/yellow]")
        return prompt_date(prompt_text, allow_empty)


def prompt_tags(prompt_text: str = "Tags (comma-separated, optional)") -> List[str]:
    """Prompt for tags with validation."""
    tags_str = Prompt.ask(prompt_text, default="")
    if not tags_str:
        return []
    
    # Parse and clean tags
    tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
    
    # Validate tag format (alphanumeric and hyphens only)
    valid_tags = []
    for tag in tags:
        if all(c.isalnum() or c in "-_" for c in tag):
            valid_tags.append(tag)
        else:
            console.print(f"[yellow]Warning: Invalid tag '{tag}' ignored (use only letters, numbers, hyphens)[/yellow]")
    
    return valid_tags


def show_success(message: str) -> None:
    """Display a success message with icon."""
    console.print(f"[green]✅ {message}[/green]")


def show_error(message: str) -> None:
    """Display an error message with icon."""
    console.print(f"[red]❌ {message}[/red]")


def show_warning(message: str) -> None:
    """Display a warning message with icon."""
    console.print(f"[yellow]⚠️  {message}[/yellow]")


def show_info(message: str) -> None:
    """Display an info message with icon."""
    console.print(f"[blue]ℹ️  {message}[/blue]")


def create_header(title: str, subtitle: Optional[str] = None) -> None:
    """Create a beautiful header for commands."""
    header_text = Text(title, style="bold cyan")
    if subtitle:
        header_text.append(f"\n{subtitle}", style="dim")
    
    panel = Panel(
        header_text,
        expand=False,
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(panel)
    console.print()


def confirm_action(message: str, default: bool = False) -> bool:
    """
    Enhanced confirmation prompt.
    
    Args:
        message: Confirmation message
        default: Default value if Enter is pressed
        
    Returns:
        True if confirmed, False otherwise
    """
    return Confirm.ask(message, default=default)


def select_from_list(
    items: List[Any],
    prompt_text: str,
    display_func: Optional[Callable[[Any], str]] = None
) -> Optional[Any]:
    """
    Let user select from a list of items.
    
    Args:
        items: List of items to choose from
        prompt_text: Prompt message
        display_func: Function to convert item to display string
        
    Returns:
        Selected item or None if cancelled
    """
    if not items:
        return None
    
    if display_func is None:
        display_func = str
    
    # Display options
    console.print(f"\n[bold]{prompt_text}[/bold]")
    for i, item in enumerate(items, 1):
        console.print(f"  {i}. {display_func(item)}")
    
    # Get selection
    while True:
        choice = IntPrompt.ask(
            "\nSelect option (0 to cancel)",
            default=0,
            show_default=False
        )
        
        if choice == 0:
            return None
        elif 1 <= choice <= len(items):
            return items[choice - 1]
        else:
            show_warning(f"Please select a number between 1 and {len(items)}")


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_task_summary(task) -> str:
    """Format a task for selection display."""
    from .models import TaskStatus, TaskPriority
    from .display import get_status_display, get_priority_display
    
    status_icon = {
        TaskStatus.TODO: "📋",
        TaskStatus.IN_PROGRESS: "🔄",
        TaskStatus.DONE: "✅"
    }.get(task.status, "")
    
    priority_color = {
        TaskPriority.LOW: "green",
        TaskPriority.MEDIUM: "yellow",
        TaskPriority.HIGH: "orange1",
        TaskPriority.URGENT: "red"
    }.get(task.priority, "white")
    
    return f"{status_icon} [{priority_color}]{truncate_text(task.title)}[/{priority_color}] (ID: {task.short_id})"