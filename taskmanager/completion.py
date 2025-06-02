"""
Shell completion support for Task Manager CLI.
"""

import click
from .cli import cli


def get_task_ids(ctx, args, incomplete):
    """Provide task ID completion."""
    from .manager import TaskManager
    try:
        # Get task manager instance
        manager = TaskManager()
        manager.load()
        
        # Get all task IDs and short IDs
        completions = []
        for task in manager.tasks.values():
            # Add both full ID and short ID
            if task.id.startswith(incomplete) or task.short_id.startswith(incomplete):
                completions.append((task.short_id, f"{task.title[:30]}..."))
        
        return completions
    except:
        return []


def get_statuses(ctx, args, incomplete):
    """Provide status completion."""
    from .models import TaskStatus
    statuses = [s.value for s in TaskStatus]
    return [s for s in statuses if s.startswith(incomplete)]


def get_priorities(ctx, args, incomplete):
    """Provide priority completion."""
    from .models import TaskPriority
    priorities = [p.value for p in TaskPriority]
    return [p for p in priorities if p.startswith(incomplete)]


def get_tags(ctx, args, incomplete):
    """Provide tag completion based on existing tags."""
    from .manager import TaskManager
    try:
        manager = TaskManager()
        manager.load()
        
        # Collect all unique tags
        all_tags = set()
        for task in manager.tasks.values():
            all_tags.update(task.tags)
        
        return [tag for tag in sorted(all_tags) if tag.startswith(incomplete)]
    except:
        return []


# Register shell completion
def init_completion():
    """Initialize shell completion for commands."""
    # Update command completions
    for command in cli.commands.values():
        if hasattr(command, 'params'):
            for param in command.params:
                if param.name == 'task_id':
                    param.shell_complete = get_task_ids
                elif param.name == 'status':
                    param.shell_complete = get_statuses
                elif param.name == 'priority':
                    param.shell_complete = get_priorities
                elif param.name == 'tag':
                    param.shell_complete = get_tags


def install_completion():
    """Print instructions for installing shell completion."""
    shell = click.get_current_context().obj.get('shell', 'bash')
    
    instructions = {
        'bash': """
# Add to ~/.bashrc:
eval "$(_TASK_COMPLETE=bash_source task)"
""",
        'zsh': """
# Add to ~/.zshrc:
eval "$(_TASK_COMPLETE=zsh_source task)"
""",
        'fish': """
# Add to ~/.config/fish/completions/task.fish:
_TASK_COMPLETE=fish_source task | source
"""
    }
    
    click.echo(f"To enable {shell} completion, add the following to your shell configuration:")
    click.echo(instructions.get(shell, instructions['bash']))