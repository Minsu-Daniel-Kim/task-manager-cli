# Task Manager CLI - User Guide

Welcome to Task Manager CLI! This guide will help you manage your tasks efficiently, even if you're new to command-line tools.

## What is Task Manager CLI?

Task Manager CLI is a simple yet powerful tool that helps you:
- Keep track of things you need to do (tasks)
- Organize tasks by importance and deadlines
- Find specific tasks quickly
- Never lose your tasks (they're saved automatically)

Think of it as a smart to-do list that lives in your computer's terminal.

## Getting Started

### First Time Setup

1. **Open your terminal** (also called Command Prompt on Windows or Terminal on Mac)
2. **Install the task manager** by following the installation instructions
3. **Type `task` and press Enter** - if you see a help message, you're ready to go!

### Your First Task

Let's create your first task. Type this command and press Enter:

```
task add
```

The program will ask you for:
- **Title**: What do you need to do? (e.g., "Buy groceries")
- **Description**: Any extra details (optional - just press Enter to skip)
- **Priority**: How important is it?
  - 🟢 `low` - Can wait
  - 🟡 `medium` - Normal importance (default)
  - 🟠 `high` - Important
  - 🔴 `urgent` - Do ASAP!
- **Due date**: When does it need to be done? (optional)
  - Type `today`, `tomorrow`, or a date like `2024-12-25`
  - Or just press Enter if there's no deadline
- **Tags**: Labels to organize your tasks (optional)
  - Like "work", "personal", "shopping"

## Essential Commands

Here are the commands you'll use most often:

### 📝 Creating Tasks

**Regular way** (answers questions one by one):
```
task add
```

**Quick way** (just type the title):
```
task add --quick
```
Then just type what you need to do and press Enter!

### 📋 Viewing Your Tasks

**See all your tasks**:
```
task list
```

**See only active tasks** (things you still need to do):
```
task active
```

**See what's due today or overdue**:
```
task today
```

**See overdue tasks** (past their due date):
```
task overdue
```

### ✅ Completing Tasks

When you finish a task, mark it as done:
```
task done abc123
```
(Replace `abc123` with your task's ID shown in the list)

**Tip**: If you don't remember the ID, just type:
```
task done
```
And pick from the list that appears!

### 🔍 Finding Tasks

**Search for a specific task**:
```
task search "groceries"
```

This will find any task with "groceries" in the title, description, or tags.

### ✏️ Updating Tasks

**Change task details**:
```
task update abc123
```

Or update without the ID (pick from a list):
```
task update
```

### 🗑️ Deleting Tasks

**Delete a task** (it will ask for confirmation):
```
task delete abc123
```

**Clean up all completed tasks**:
```
task clear
```

## Real-Life Examples

### Example 1: Managing Daily Chores

```bash
# Add your chores
task add
> Title: Clean the kitchen
> Priority: medium
> Due date: today
> Tags: home,cleaning

task add
> Title: Take out trash
> Priority: high
> Due date: today
> Tags: home

# See what needs to be done today
task today

# Mark as done when completed
task done
# (select "Clean the kitchen" from the list)
```

### Example 2: Planning a Project

```bash
# Add project tasks with tags
task add
> Title: Research competitor prices
> Priority: high
> Due date: 2024-01-15
> Tags: project,research

task add
> Title: Create presentation slides
> Priority: high
> Due date: 2024-01-20
> Tags: project,presentation

# View all project tasks
task list --tag project

# Update when priorities change
task update
# (select "Create presentation slides")
> New priority: urgent
```

### Example 3: Shopping List

```bash
# Quick add shopping items
task add --quick
> Buy milk

task add --quick
> Pick up dry cleaning

task add --quick
> Get birthday card for Mom

# See your shopping tasks
task list --tag shopping

# Check them off as you shop
task done
# (select each item as you complete it)
```

## Organizing with Filters

As your task list grows, use filters to see what matters:

### By Status
- `task list --status todo` - Things to do
- `task list --status in_progress` - Things you're working on
- `task list --status done` - Completed tasks

### By Priority
- `task list --priority urgent,high` - Important tasks only
- `task list --priority low` - Less important tasks

### By Tags
- `task list --tag work` - Work tasks only
- `task list --tag personal` - Personal tasks only

### Combined Filters
```
task list --status todo --priority high --tag work
```
This shows: unfinished + important + work-related tasks

## Pro Tips

### 1. Use Tags Wisely
Create a simple tagging system:
- `work`, `personal`, `home`
- `urgent`, `waiting`, `someday`
- `project-name` for specific projects

### 2. Quick Views
Create shortcuts for common views:
- Morning routine: `task today`
- Work tasks: `task list --tag work --status todo`
- Weekend chores: `task list --tag home --priority high`

### 3. Regular Cleanup
- Weekly: `task clear` to remove completed tasks
- Monthly: `task list --status todo --sort due_date` to review all pending tasks

### 4. Backup Your Tasks
```
task export my-tasks-backup.json
```
This saves all your tasks to a file you can keep safe.

## Keyboard Shortcuts & Tips

- **Up/Down arrows**: Navigate through options in selection menus
- **Tab**: Auto-complete commands
- **Ctrl+C**: Cancel any operation
- **Enter**: Confirm selection or skip optional fields

## Troubleshooting

### "Command not found"
- Make sure you've installed the task manager correctly
- Try closing and reopening your terminal

### "No tasks found"
- You haven't created any tasks yet - use `task add`
- You might be filtering too specifically - try `task list` without filters

### Lost tasks?
- Your tasks are automatically saved
- Check storage location: `task storage-info`
- Restore from backup if you have one: `task import backup.json`

## Getting Help

- Type `task --help` to see all commands
- Type `task <command> --help` for help with a specific command
- Check the README for advanced features

## Summary

The basics you need to remember:
1. `task add` - Create a new task
2. `task list` - See your tasks
3. `task done` - Mark task as complete
4. `task today` - See what's due today
5. `task search "keyword"` - Find specific tasks

That's it! You're ready to start managing your tasks like a pro. Start simple, and explore more features as you get comfortable.

Happy task managing! 🎯