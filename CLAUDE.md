# Claude Code Instructions

## Project: Task Manager CLI

### Linear Integration Workflow

This project uses Linear for project management with GitHub integration enabled.

#### Branch Naming Convention
- Use Linear's auto-generated branch names: `tea-[issue-number]-[description]`
- Example: `tea-15-add-advanced-search-functionality`

#### Commit Message Format
```
TEA-[issue-number]: [Description]

Examples:
- TEA-15: Implement advanced search with regex support
- TEA-16: Add filter presets for common queries
- TEA-17: Create search result highlighting
```

#### Development Process
1. **Linear Issue Context**: Always reference the Linear issue ID (TEA-XXX)
2. **Implementation**: Follow the requirements and acceptance criteria from Linear
3. **Testing**: Ensure all features work as described in Linear issue
4. **PR Creation**: Use Linear issue ID in PR title for automatic linking

#### Code Standards
- Follow existing code patterns in the repository
- Add comprehensive tests for new features
- Update documentation for user-facing changes
- Use TypeScript for type safety where applicable

#### Feature Implementation Guidelines

**For CLI Features:**
- Use Click framework for command structure
- Add Rich library for beautiful terminal output
- Include progress indicators for long operations
- Provide helpful error messages with suggestions

**For Core Logic:**
- Implement proper error handling and validation
- Add logging for debugging purposes
- Follow SOLID principles
- Write unit tests with good coverage

**For Storage/Persistence:**
- Use JSON for local storage with backup mechanisms
- Implement proper data migration strategies
- Add import/export functionality for data portability

#### Linear Issue Integration
- Each feature should correspond to a Linear issue
- Reference Linear issue URL in code comments for complex features
- Update Linear issue with implementation notes if needed
- Mark issues as "Done" only after PR is merged

#### Specific to This Project
- This is a CLI task management tool with Linear integration
- Focus on developer productivity and beautiful terminal UX
- Support for advanced filtering, search, and organization
- Future integration with Linear API for two-way sync