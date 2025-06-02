# Task Manager CLI

A powerful and intuitive command-line task management tool with Linear integration.

## Features

- ✅ **Full CRUD Operations** - Create, read, update, and delete tasks with ease
- 🎨 **Beautiful CLI Interface** - Rich terminal UI with colors and tables
- 💾 **Persistent Storage** - Tasks are saved locally in JSON format
- 🔍 **Advanced Filtering** - Search and filter tasks by status, priority, tags, and more
- 🔄 **Linear Integration** - Sync your local tasks with Linear issues
- 📊 **Smart Organization** - Priority levels, status tracking, and due dates
- 🏷️ **Flexible Tagging** - Organize tasks with custom tags

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/task-manager-cli.git
cd task-manager-cli

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Quick Start

```bash
# Create your first task interactively
task add

# Quick add with just a title
task add --quick

# List all tasks
task list

# List with summary statistics
task list --summary

# Show today's tasks and overdue items
task today

# Update a task (interactive mode)
task update abc123 --interactive

# Mark a task as done
task done abc123

# Clear all completed tasks
task clear
```

## Commands

### Task Management

#### `task add`
Create a new task with interactive prompts for all fields.

```bash
# Interactive mode (default)
task add

# Quick mode - just enter title
task add --quick
```

Features:
- Priority levels with visual indicators (🟢 low, 🟡 medium, 🟠 high, 🔴 urgent)
- Flexible due date input (YYYY-MM-DD, today, tomorrow, +7)
- Tag validation and multi-tag support
- Task summary preview before creation

#### `task list`
Display tasks in a beautiful table with filtering options.

```bash
# List all tasks
task list

# Filter by status
task list --status todo
task list -s in_progress

# Filter by priority
task list --priority high,urgent
task list -p medium

# Filter by tag
task list --tag work
task list -t bug

# Show summary statistics
task list --summary
```

#### `task show <id>`
Display detailed information about a specific task.

```bash
# Default detailed view
task show abc123

# JSON format
task show abc123 --format json

# Markdown format
task show abc123 --format markdown
```

#### `task update [id]`
Update task properties with multiple options.

```bash
# Update specific fields
task update abc123 --title "New Title" --priority high

# Interactive mode - prompts for each field
task update abc123 --interactive

# Update without specifying ID (selection menu)
task update

# Add/remove tags
task update abc123 --add-tag feature --remove-tag bug

# Update due date
task update abc123 --due-date tomorrow
```

#### `task delete [id]`
Delete a task with confirmation.

```bash
# Delete with confirmation prompt
task delete abc123

# Skip confirmation
task delete abc123 --force

# Delete without ID (selection menu)
task delete
```

#### `task done [id]`
Mark a task as complete or undo completion.

```bash
# Mark as done
task done abc123

# Undo completion (mark as todo)
task done abc123 --undo

# Without ID (shows selection menu)
task done
```

### Utility Commands

#### `task today`
Show tasks due today or overdue.

```bash
task today
```

Displays:
- ⚠️ Overdue tasks (in red)
- 📅 Tasks due today (in yellow)

#### `task clear`
Remove all completed tasks interactively.

```bash
task clear
```

Shows all completed tasks and asks for confirmation before deleting.

#### `task stats`
Display task statistics.

```bash
task stats
```

Shows breakdown by:
- Status (todo, in_progress, done)
- Priority (low, medium, high, urgent)
- Total task count

### Filtering and Search

```bash
# Filter by status
task list --status todo,in_progress

# Filter by priority
task list --priority high,urgent

# Search in title and description
task search "keyword"

# Complex filtering
task list --status todo --priority high --tag work
```

### Linear Integration

```bash
# Configure Linear API
task config linear

# Pull issues from Linear
task linear pull

# Push a task to Linear
task linear push <task-id>

# Check sync status
task linear status
```

## Configuration

Task Manager stores its configuration in `~/.taskmanager/config.json`.

You can also use environment variables:

```bash
export TASKMANAGER_DATA_DIR=/custom/path
export LINEAR_API_KEY=your_api_key
export LINEAR_TEAM_ID=TEAM-123
```

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=taskmanager

# Format code
black taskmanager tests

# Run linter
flake8 taskmanager tests
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Click](https://click.palletsprojects.com/) for CLI parsing
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Integrated with [Linear](https://linear.app/) for issue tracking