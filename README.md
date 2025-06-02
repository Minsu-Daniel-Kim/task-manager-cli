# Task Manager CLI

A powerful and intuitive command-line task management tool with Linear integration.

## Features

- ✅ **Full CRUD Operations** - Create, read, update, and delete tasks with ease
- 🎨 **Beautiful CLI Interface** - Rich terminal UI with colors and tables
- 💾 **Persistent Storage** - Tasks are saved locally in JSON format
- 🔍 **Advanced Filtering** - Multiple status/priority filters, date ranges, and presets
- 🔎 **Powerful Search** - Full-text search with regex support
- 📊 **Smart Sorting** - Sort by date, priority, status, or title
- 🔄 **Linear Integration** - Sync your local tasks with Linear issues
- 📊 **Smart Organization** - Priority levels, status tracking, and due dates
- 🏷️ **Flexible Tagging** - Organize tasks with custom tags
- ⚡ **Filter Presets** - Quick access to common views (active, overdue, today)

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
# Create your first task
task add

# List all tasks
task list

# Update a task status
task update abc123 --status in_progress

# Mark a task as done
task done abc123

# Search for tasks
task search "project"
```

## Commands

### Basic Commands

- `task add` - Create a new task interactively
- `task list` - List all tasks with filtering options
- `task search <query>` - Search tasks by keyword
- `task show <id>` - Display detailed information about a task
- `task update <id>` - Update task properties
- `task delete <id>` - Delete a task
- `task done <id>` - Mark a task as complete
- `task active` - Show active tasks (TODO and IN_PROGRESS)
- `task overdue` - Show overdue tasks
- `task today` - Show tasks due today

### Filtering and Search

```bash
# Filter by multiple statuses
task list --status todo,in_progress

# Filter by multiple priorities
task list --priority high,urgent

# Filter by tags
task list --tag work,urgent

# Use filter presets
task list --preset active      # TODO and IN_PROGRESS tasks
task list --preset overdue     # Past due date
task list --preset today       # Due today
task list --preset high_priority  # HIGH and URGENT

# Sort results
task list --sort priority --order asc
task list --sort due_date --order desc

# Quick preset commands
task active    # Show active tasks
task overdue   # Show overdue tasks
task today     # Show tasks due today

# Search in title, description, and tags
task search "bug fix"

# Regex search
task search "TASK-\d+" --regex

# Case-sensitive search
task search "BUG" --case-sensitive

# Complex filtering
task list --status todo --priority high,urgent --tag work --sort due_date
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