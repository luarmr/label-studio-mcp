# MCP Tools Documentation

This document provides comprehensive documentation for all Model Context Protocol (MCP) tools implemented in this project. Each tool is described with its purpose, parameters, usage, example requests/responses, error cases, and workflow context.

---

## Table of Contents
- [list_projects](#list_projects)
- [create_project](#create_project)
- [import_tasks](#import_tasks)
- [validate_label_config](#validate_label_config)
- [list_tasks](#list_tasks)
- [export_annotations](#export_annotations)
- [get_project_progress](#get_project_progress)
- [list_users](#list_users)
- [list_project_users](#list_project_users)
- [whoami](#whoami)
- [delete_project](#delete_project)
- [get_project](#get_project)
- [get_project_guidelines](#get_project_guidelines)
- [get_label_config](#get_label_config)
- [set_project_published](#set_project_published)
- [update_project_settings](#update_project_settings)
- [update_label_config](#update_label_config)
- [Workflow Examples](#workflow-examples)
- [References & Further Reading](#references--further-reading)

---

## MCP Configuration

To run MCP tools, you need to configure your MCP server(s) in your configuration file. Below is an example configuration for a Label Studio MCP server:

```json
{
  "mcpServers": {
    "label-studio": {
      "command": "~/Code/label-studio-mcp/env/bin/python",
      "args": [
        "~/Code/label-studio-mcp/server.py"
      ],
      "env": {
        "LS_BASE_URL": "https://app.humansignal.com/",
        "LS_API_TOKEN": "<your-api-token>",
        "LS_AUTH_TYPE": "legacy"
      }
    }
  }
}
```

### Field Explanations
- `mcpServers`: The root object for all MCP server configurations.
- `label-studio`: The name/key for this MCP server instance (can be any string).
- `command`: The command to start the MCP server (typically the Python interpreter path from your virtual environment).
- `args`: Arguments to pass to the command (usually the path to the server script).
- `env`: Environment variables for the MCP server process:
  - `LS_BASE_URL`: The base URL of your Label Studio instance. **Replace this with your own Label Studio URL.**
  - `LS_API_TOKEN`: Your Label Studio API token for authentication. **Replace this with your own API token.**
  - `LS_AUTH_TYPE`: The authentication type (e.g., `legacy`).

> **Tip:** If you installed this project using `pip install`, a virtual environment is typically created. Make sure to use the Python interpreter from your environment (e.g., `env/bin/python` or the path shown by `which python` inside your venv).
>
> **Replace all example paths and URLs above with your own local paths and server URLs.**

---

## `list_projects`
**Purpose:**
List projects from Label Studio. Optionally filter by title (case-insensitive substring match) using the 'title' parameter.

**Required Parameters:** None

**Optional Parameters:**
- `page` (int): Page number for pagination (default: 1)
- `title` (str): Filter projects by title (case-insensitive substring match)

**Pagination Details:**
- Fixed page size of 20 items per page
- Response includes pagination metadata:
  - `results`: List of projects
  - `count`: Total number of projects
  - `next`: URL for next page (null if no more pages)
  - `previous`: URL for previous page (null if first page)
- To retrieve all projects, keep incrementing 'page' until 'next' is null

**Example Input:**
```python
result = list_projects(page=1, title="My Project")
```
**Example Output:**
```json
{
  "results": [
    {"id": 1, "title": "My Project 1", "created_by": {"email": "user@example.com"}},
    {"id": 2, "title": "My Project 2", "created_by": {"email": "user2@example.com"}}
  ],
  "count": 42,
  "next": "/api/projects/?page=2",
  "previous": null
}
```

**Error Cases:**
- Network or authentication errors will return a structured error response

**Workflow Context:**
- Typically called before `list_tasks` or `import_tasks` to select a project
- Use pagination to handle large numbers of projects efficiently

---

## `create_project`
**Purpose:**
Create a new project in Label Studio. This is the entry point for setting up a new annotation workflow.

**Required Parameters:**
- `title` (str): Project title (must be unique per workspace)
- `label_config` (str): Label config XML string (must be valid XML)

**Optional Parameters:**
- `description` (str): Project description
- `expert_instruction` (str): Instructions for annotators
- `show_instruction` (bool): Show instructions to annotators
- `show_skip_button` (bool): Allow skipping tasks
- `enable_empty_annotation` (bool): Allow empty annotations
- `show_annotation_history` (bool): Show annotation history
- `organization` (int): Organization ID
- `color` (str): Project color
- `maximum_annotations` (int): Max annotations per task

**Example Input:**
```python
result = create_project(
    title="My Project",
    label_config="<View>...</View>",
    description="A sample project."
)
```
**Example Output:**
```json
{
  "id": 42,
  "title": "My Project",
  "label_config": "<View>...</View>",
  "created_by": {"email": "user@example.com"}
}
```

**Error Cases:**
- Missing required parameters: returns a validation error.
- Invalid label config XML: returns an upstream error from Label Studio.

**Workflow Context:**
- Use before importing tasks or configuring project settings.

---

## `import_tasks`
**Purpose:**
Import a list of tasks into a Label Studio project. Each task is a dictionary matching the project's label config.

**Required Parameters:**
- `project_id` (str): Project ID (as returned by `list_projects`)
- `tasks` (list of dict): List of task dicts (e.g., `{ "video": "https://..." }`)

**Example Input:**
```python
result = import_tasks(
    project_id="42",
    tasks=[{"video": "https://samplelib.com/mp4/sample-5s.mp4"}]
)
```
**Example Output:**
```json
{
  "task_count": 1,
  "annotation_count": 0,
  "prediction_count": 0
}
```

**Error Cases:**
- Invalid or missing project ID: validation error.
- Malformed tasks: validation error or upstream error.

**Workflow Context:**
- Use after creating a project, before annotation begins.

---

## `validate_label_config`
**Purpose:**
Validate a labeling interface XML config for a given project. Ensures the config is well-formed and compatible with Label Studio.

**Required Parameters:**
- `project_id` (str): Project ID
- `label_config` (str): Label config XML string

**Example Input:**
```python
result = validate_label_config(
    project_id="42",
    label_config="<View>...</View>"
)
```
**Example Output:**
```json
{
  "valid": true,
  "warnings": [],
  "errors": []
}
```

**Error Cases:**
- Invalid XML: returns a validation or upstream error.
- Project not found: upstream error.

**Workflow Context:**
- Use before updating a project's label config or when designing new annotation workflows.

---

## `list_tasks`
**Purpose:**
List tasks for a given Label Studio project. Supports pagination, filtering, and includes annotation results when requested.

**Required Parameters:**
- `project_id` (str): Project ID

**Optional Parameters:**
- `page` (int): Page number for pagination
- `page_size` (int): Number of tasks per page
- `filters` (dict): Filtering options (see Label Studio API)
- Additional kwargs: Any other supported query parameters

**Pagination Details:**
- Supports custom page sizes via `page_size` parameter
- Response includes pagination metadata:
  - `tasks`: List of tasks
  - `total`: Total number of tasks
  - `next`: URL for next page (null if no more pages)
  - `previous`: URL for previous page (null if first page)
- To retrieve all tasks, keep incrementing 'page' until 'next' is null

**Example Input:**
```python
result = list_tasks(
    project_id="42",
    page=1,
    page_size=10,
    include_annotations=True  # Example: include annotation results
)
```
**Example Output:**
```json
{
  "tasks": [
    {"id": 101, "video": "https://samplelib.com/mp4/sample-5s.mp4", "annotations": [{"result": ...}]}
  ],
  "total": 100,
  "next": "/api/tasks/?page=2",
  "previous": null
}
```

**Error Cases:**
- Invalid project ID: validation or upstream error
- Network/API errors: upstream error

**Workflow Context:**
- Use to display or process tasks for annotation, review, or export
- Use pagination to handle large numbers of tasks efficiently
- Use to access annotation data for a project by including annotation results

---

## `export_annotations`
**Purpose:**
Export annotations for a given Label Studio project. Supports multiple formats (JSON, CSV, etc.).

**Required Parameters:**
- `project_id` (str): Project ID

**Optional Parameters:**
- `exportType` (str): Format to export (e.g., 'JSON', 'CSV')
- Additional kwargs: Any other supported query parameters

**Example Input:**
```python
result = export_annotations(
    project_id="42",
    exportType="JSON"
)
```
**Example Output:**
```json
{
  "content": [
    {"id": 101, "annotations": [{"result": ...}]}
  ],
  "content_type": "application/json"
}
```

**Error Cases:**
- Invalid project ID: validation or upstream error.
- Export type not supported: validation error.

**Workflow Context:**
- Use to back up, analyze, or transfer annotation data.

---

## `get_project_progress`
**Purpose:**
Extract and return progress metrics from a project's details. Useful for monitoring project status and completion rates.

**Required Parameters:**
- `project_id` (str): Project ID

**Example Input:**
```python
result = get_project_progress(project_id="42")
```
**Example Output:**
```json
{
  "progress": {
    "task_number": 100,
    "finished_task_number": 75,
    "total_annotations_number": 150,
    "total_predictions_number": 50,
    "num_tasks_with_annotations": 80,
    "useful_annotation_number": 120,
    "ground_truth_number": 30,
    "skipped_annotations_number": 5,
    "queue_total": 20,
    "queue_done": 15,
    "overlap_cohort_percentage": 25
  }
}
```

**Error Cases:**
- Invalid project ID: validation error
- No progress metrics found: returns warning message

**Workflow Context:**
- Use for project monitoring and analytics
- Helpful for tracking annotation progress and quality metrics

---

## `list_users`
**Purpose:**
List users from Label Studio. Supports pagination to handle large numbers of users efficiently.

**Required Parameters:** None

**Optional Parameters:**
- `page` (int): Page number for pagination (default: 1)
- `page_size` (int): Number of users per page (default: 20)

**Pagination Details:**
- Default page size of 20 items per page
- Response includes pagination metadata:
  - `results`: List of users
  - `count`: Total number of users
  - `next`: URL for next page (null if no more pages)
  - `previous`: URL for previous page (null if first page)
- To retrieve all users, keep incrementing 'page' until 'next' is null

**Example Input:**
```python
result = list_users(page=1, page_size=20)
```
**Example Output:**
```json
{
  "results": [
    {"id": 1, "email": "user1@example.com", "username": "user1"},
    {"id": 2, "email": "user2@example.com", "username": "user2"}
  ],
  "count": 42,
  "next": "/api/users/?page=2",
  "previous": null
}
```

**Error Cases:**
- Authentication errors: upstream error
- Network issues: upstream error

**Workflow Context:**
- Use before assigning users to projects
- Helpful for user management tasks
- Use pagination to handle large numbers of users efficiently

---

## `list_project_users`
**Purpose:**
List all users assigned to a specific project. Useful for managing project access and permissions.

**Required Parameters:**
- `project_id` (str): Project ID

**Example Input:**
```python
result = list_project_users(project_id="42")
```
**Example Output:**
```json
[
  {"id": 1, "email": "user1@example.com", "username": "user1"},
  {"id": 2, "email": "user2@example.com", "username": "user2"}
]
```

**Error Cases:**
- Invalid project ID: validation error
- Authentication errors: upstream error

**Workflow Context:**
- Use to review project access
- Helpful for project team management

---

## `whoami`
**Purpose:**
Get information about the currently authenticated user. Useful for verifying authentication and user context.

**Parameters:** None

**Example Input:**
```python
result = whoami()
```
**Example Output:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "user",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Error Cases:**
- Authentication errors: upstream error
- Network issues: upstream error

**Workflow Context:**
- Use to verify authentication status
- Helpful for user context verification

---

## `delete_project`
**Purpose:**
Delete a project with a confirmation safeguard. Requires explicit confirmation to prevent accidental deletions.

**Required Parameters:**
- `project_id` (str): Project ID
- `confirm` (bool): Must be set to True to proceed with deletion

**Example Input:**
```python
result = delete_project(project_id="42", confirm=True)
```
**Example Output:**
```json
{
  "success": true,
  "message": "Project 42 deleted."
}
```

**Error Cases:**
- Missing confirmation: returns error message
- Invalid project ID: validation error
- Network issues: upstream error

**Workflow Context:**
- Use with caution for project cleanup
- Always verify project ID before deletion

---

## `get_project`
**Purpose:**
Fetch and return complete project details from the Label Studio API.

**Required Parameters:**
- `project_id` (str): Project ID

**Example Input:**
```python
result = get_project(project_id="42")
```
**Example Output:**
```json
{
  "id": 42,
  "title": "My Project",
  "description": "Project description",
  "label_config": "<View>...</View>",
  "expert_instruction": "Annotation guidelines",
  "created_by": {"email": "user@example.com"},
  "created_at": "2024-03-20T10:00:00Z",
  "is_published": true
}
```

**Error Cases:**
- Invalid project ID: validation error
- Project not found: upstream error

**Workflow Context:**
- Use to get complete project information
- Helpful for project inspection and management

---

## `get_project_guidelines`
**Purpose:**
Extract and return only the guidelines section from the project details.

**Required Parameters:**
- `project_id` (str): Project ID

**Example Input:**
```python
result = get_project_guidelines(project_id="42")
```
**Example Output:**
```json
{
  "guidelines": "Detailed annotation guidelines for the project..."
}
```

**Error Cases:**
- Invalid project ID: validation error
- No guidelines found: returns warning message

**Workflow Context:**
- Use to review project annotation guidelines
- Helpful for quality control and training

---

## `get_label_config`
**Purpose:**
Extract and return only the label configuration from the project details.

**Required Parameters:**
- `project_id` (str): Project ID

**Example Input:**
```python
result = get_label_config(project_id="42")
```
**Example Output:**
```json
{
  "label_config": "<View><Text name=\"text\" value=\"$text\"/><Choices name=\"sentiment\" toName=\"text\"><Choice value=\"Positive\"/><Choice value=\"Negative\"/></Choices></View>"
}
```

**Error Cases:**
- Invalid project ID: validation error
- No label config found: returns warning message

**Workflow Context:**
- Use to review project labeling interface
- Helpful for configuration management

---

## `set_project_published`
**Purpose:**
Set the published status of a project (publish/unpublish).

**Required Parameters:**
- `project_id` (str): Project ID
- `published` (bool): True to publish, False to unpublish

**Example Input:**
```python
result = set_project_published(project_id="42", published=True)
```
**Example Output:**
```json
{
  "id": 42,
  "is_published": true
}
```

**Error Cases:**
- Invalid project ID: validation error
- Invalid published status: validation error

**Workflow Context:**
- Use to control project visibility
- Helpful for project lifecycle management

---

## `update_project_settings`
**Purpose:**
Update project settings and guidelines.

**Required Parameters:**
- `project_id` (str): Project ID

**Optional Parameters:**
- `title` (str): New project title
- `description` (str): New project description
- `expert_instruction` (str): New annotation guidelines

**Example Input:**
```python
result = update_project_settings(
    project_id="42",
    title="Updated Title",
    description="New description"
)
```
**Example Output:**
```json
{
  "id": 42,
  "title": "Updated Title",
  "description": "New description"
}
```

**Error Cases:**
- Invalid project ID: validation error
- No fields provided: validation error
- Invalid field values: upstream error

**Workflow Context:**
- Use to modify project metadata
- Helpful for project maintenance

---

## `update_label_config`
**Purpose:**
Update the label configuration for a project.

**Required Parameters:**
- `project_id` (str): Project ID
- `label_config` (str): New label configuration XML

**Example Input:**
```python
result = update_label_config(
    project_id="42",
    label_config="<View>...</View>"
)
```
**Example Output:**
```json
{
  "id": 42,
  "label_config": "<View>...</View>"
}
```

**Error Cases:**
- Invalid project ID: validation error
- Invalid label config: validation error
- Network issues: upstream error

**Workflow Context:**
- Use to modify project labeling interface
- Helpful for interface evolution

---

## Error Handling
All tools return errors in a consistent format:
```json
{
  "error": {
    "type": "validation_error|upstream_error|internal_error",
    "message": "Error message",
    "status_code": 400|502|500,
    "details": null
  }
}
```

**Example Error Response:**
```json
{
  "error": {
    "type": "validation_error",
    "message": "project_id is required.",
    "status_code": 400,
    "details": null
  }
}
```

---

## Best Practices
- Always validate required parameters before calling a tool.
- Handle errors using the provided error format.
- Refer to this documentation for parameter types and example usage.
- For advanced workflows, chain tools as needed (e.g., create_project → import_tasks → export_annotations).
- Use `list_projects` and `list_tasks` to discover IDs before calling other tools.
- Validate label configs before updating projects.
- Review error messages for actionable feedback.

---

## Workflow Examples

### End-to-End Project Setup and Annotation

```python
# 1. Create a new project
project = create_project(title="Video Project", label_config="<View>...</View>")
project_id = project["id"]

# 2. Import tasks
import_tasks(project_id=project_id, tasks=[{"video": "https://samplelib.com/mp4/sample-5s.mp4"}])

# 3. List tasks
tasks = list_tasks(project_id=project_id)

# 4. Export annotations
export = export_annotations(project_id=project_id, exportType="JSON")
```

### Label Config Validation Before Update
```python
validate_label_config(project_id=project_id, label_config="<View>...</View>")
```

---

## References & Further Reading

- [Label Studio API Documentation](https://labelstud.io/api)
- [Task Master MCP Rules](../.cursor/rules/taskmaster.mdc)
- [Development Workflow Guide](../.cursor/rules/dev_workflow.mdc)
- [Self-Improvement & Rule Maintenance](../.cursor/rules/self_improve.mdc)
- [Cursor Rule Format](../.cursor/rules/cursor_rules.mdc)
- [Project PRD Example](../scripts/example_prd.txt)
- [Second PRD (Project Admin/Analytics)](../scripts/second.prd) 