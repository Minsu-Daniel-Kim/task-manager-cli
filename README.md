# Task Manager CLI

A powerful and intuitive command-line task management tool with Linear integration.

## Features

- ✅ **Full CRUD Operations** - Create, read, update, and delete tasks with ease
- 🎨 **Beautiful CLI Interface** - Rich terminal UI with colors, tables, and interactive prompts
- 💾 **Persistent Storage** - Tasks are automatically saved locally in JSON format
- 🔍 **Advanced Filtering** - Multiple status/priority filters, date ranges, and presets
- 🔎 **Powerful Search** - Full-text search with regex support
- 📊 **Smart Sorting** - Sort by date, priority, status, or title
- 🔄 **Linear Integration** - Sync your local tasks with Linear issues
- 📊 **Smart Organization** - Priority levels, status tracking, and due dates
- 🏷️ **Flexible Tagging** - Organize tasks with custom tags
- ⚡ **Filter Presets** - Quick access to common views (active, overdue, today)
- 🔄 **Import/Export** - Backup and share tasks with JSON export/import
- 🎯 **Interactive Mode** - Task selection menus and confirmation prompts

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

# Search for tasks
task search "project"

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
task list -s in_progress,done

# Filter by priority
task list --priority high,urgent
task list -p medium

# Filter by tag
task list --tag work,bug

# Use filter presets
task list --preset active      # TODO and IN_PROGRESS tasks
task list --preset overdue     # Past due date
task list --preset today       # Due today

# Sort results
task list --sort priority --order asc
task list --sort due_date --order desc

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

#### `task search <query>`
Search for tasks by keyword with advanced options.

```bash
# Basic search
task search "bug fix"

# Regex search
task search "TASK-\d+" --regex

# Case-sensitive search
task search "BUG" --case-sensitive

# Search with custom sorting
task search "feature" --sort priority --order desc
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

#### `task active`
Quick view of active tasks (TODO and IN_PROGRESS).

```bash
task active
```

#### `task overdue`
Show all overdue tasks.

```bash
task overdue
```

#### `task stats`
Display task statistics.

```bash
task stats
```

Shows breakdown by:
- Status (todo, in_progress, done)
- Priority (low, medium, high, urgent)
- Total task count

### Storage Commands

#### `task export <file>`
Export all tasks to a JSON file.

```bash
task export backup.json
task export ~/Documents/tasks-2024.json
```

#### `task import <file>`
Import tasks from a JSON file.

```bash
# Replace all existing tasks
task import backup.json

# Merge with existing tasks
task import backup.json --merge
```

#### `task storage-info`
Display storage information and data location.

```bash
task storage-info
```

## Filtering and Search

### Multiple Filters
```bash
# Combine multiple filters
task list --status todo,in_progress --priority high,urgent --tag work

# Use filter presets for common views
task list --preset active      # Active tasks
task list --preset overdue     # Overdue tasks
task list --preset today       # Due today
task list --preset high_priority  # High and urgent
task list --preset this_week   # Due this week
task list --preset untagged    # Tasks without tags
task list --preset recent      # Created in last 7 days
```

### Advanced Search
```bash
# Search in title, description, and tags
task search "keyword"

# Regex search for pattern matching
task search "^Fix.*bug$" --regex

# Case-sensitive search
task search "TODO" --case-sensitive

# Search with sorting
task search "feature" --sort priority --order asc
```

### Sorting Options
Available sort fields:
- `created_at` - When the task was created (default)
- `updated_at` - Last modification time
- `due_date` - Task due date
- `priority` - Task priority level
- `status` - Task status
- `title` - Alphabetical by title

## Configuration

Task Manager stores its configuration in `~/.taskmanager/` directory.

You can also use environment variables:

```bash
export TASKMANAGER_DATA_DIR=/custom/path
export LINEAR_API_KEY=your_api_key
export LINEAR_TEAM_ID=TEAM-123
```

## Data Storage

Tasks are automatically saved to:
- **macOS/Linux**: `~/.taskmanager/tasks.json`
- **Windows**: `%USERPROFILE%\.taskmanager\tasks.json`

Backups are created automatically before each save operation.

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