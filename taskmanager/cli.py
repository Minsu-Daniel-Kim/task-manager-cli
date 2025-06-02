"""
Main CLI interface for Task Manager.
"""

import click
from rich.console import Console
from rich.table import Table

console = Console()


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
    console.print("[bold green]Creating a new task...[/bold green]")
    console.print("This feature will be implemented in TEA-12")


@cli.command()
@click.option("--status", help="Filter by status (comma-separated)")
@click.option("--priority", help="Filter by priority (comma-separated)")
@click.option("--tag", help="Filter by tag")
def list(status, priority, tag):
    """List all tasks with optional filters."""
    console.print("[bold blue]Task List[/bold blue]")
    
    # Create a sample table for now
    table = Table(title="Tasks")
    table.add_column("ID", style="cyan", width=8)
    table.add_column("Title", style="white")
    table.add_column("Status", style="yellow")
    table.add_column("Priority", style="magenta")
    table.add_column("Due Date", style="green")
    
    # Sample data
    table.add_row("abc123", "Sample Task", "📋 todo", "🟡 medium", "2024-01-20")
    
    console.print(table)
    console.print("\n[dim]Full functionality will be implemented in upcoming features[/dim]")


@cli.command()
@click.argument("task_id")
def show(task_id):
    """Display detailed information about a task."""
    console.print(f"[bold]Task Details for {task_id}[/bold]")
    console.print("This feature will be implemented in TEA-12")


@cli.command()
@click.argument("task_id")
@click.option("--status", help="New status")
@click.option("--priority", help="New priority")
@click.option("--title", help="New title")
def update(task_id, status, priority, title):
    """Update task properties."""
    console.print(f"[yellow]Updating task {task_id}...[/yellow]")
    console.print("This feature will be implemented in TEA-12")


@cli.command()
@click.argument("task_id")
@click.confirmation_option(prompt="Are you sure you want to delete this task?")
def delete(task_id):
    """Delete a task."""
    console.print(f"[red]Deleting task {task_id}...[/red]")
    console.print("This feature will be implemented in TEA-12")


@cli.command()
@click.argument("task_id")
def done(task_id):
    """Mark a task as complete."""
    console.print(f"[green]✅ Marking task {task_id} as done![/green]")
    console.print("This feature will be implemented in TEA-12")


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