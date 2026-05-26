# Todo Tool

Manage tasks in the shared todo list. Tasks are **global** — cross-project, cross-agent — with no access control.

## Tool Name

`todo_tool`

## Action Dispatch

Call as `todo_tool:<action>` where `<action>` is one of the methods below.

---

## Actions

### `todo_tool:create` — Create a new task

| Parameter | Required | Description |
|-----------|----------|-------------|
| `title` | **Yes** | Task title |
| `description` | No | Detailed description |
| `status` | No | One of: `pending`, `in_progress`, `blocked`, `completed`, `cancelled` (default: `pending`) |
| `priority` | No | One of: `low`, `medium`, `high`, `urgent` (default: `medium`) |
| `progress` | No | Integer 0–100 (default: 0) |
| `project` | No | Project name for grouping |
| `agent_profile` | No | Your profile name for self-tracking |
| `tags` | No | Array of tag strings |

Example:
```json
{
    "thoughts": ["Creating a new task for the current work."],
    "tool_name": "todo_tool:create",
    "tool_args": {
        "title": "Implement authentication middleware",
        "description": "Add JWT validation to all API routes",
        "status": "in_progress",
        "priority": "high",
        "project": "sysop",
        "agent_profile": "developer",
        "tags": ["backend", "security"]
    }
}
```

### `todo_tool:list` — List tasks with optional filters

All parameters are optional. Combine any filters.

| Parameter | Description |
|-----------|-------------|
| `project` | Filter by project name |
| `agent_profile` | Filter by agent profile |
| `status` | Filter by status: `pending`, `in_progress`, `blocked`, `completed`, `cancelled` |
| `priority` | Filter by priority: `low`, `medium`, `high`, `urgent` |
| `search` | Search title and description (case-insensitive) |
| `tag` | Filter by tag |
| `chat_section` | Filter by linked chat ID |

Example:
```json
{
    "thoughts": ["Listing all high-priority in-progress tasks."],
    "tool_name": "todo_tool:list",
    "tool_args": {
        "status": "in_progress",
        "priority": "high"
    }
}
```

### `todo_tool:get` — Get a single task by ID

| Parameter | Required | Description |
|-----------|----------|-------------|
| `task_id` | **Yes** | The task UUID |

Example:
```json
{
    "thoughts": ["Retrieving task details."],
    "tool_name": "todo_tool:get",
    "tool_args": {
        "task_id": "abc123-def456-..."
    }
}
```

### `todo_tool:update` — Update an existing task

| Parameter | Required | Description |
|-----------|----------|-------------|
| `task_id` | **Yes** | The task UUID |
| `title` | No | Updated title |
| `description` | No | Updated description |
| `status` | No | Updated status |
| `priority` | No | Updated priority |
| `progress` | No | Updated progress (0–100) |
| `project` | No | Updated project |
| `agent_profile` | No | Updated agent profile |
| `tags` | No | Updated tag array (replaces existing) |

Example:
```json
{
    "thoughts": ["Marking task as completed."],
    "tool_name": "todo_tool:update",
    "tool_args": {
        "task_id": "abc123-def456-...",
        "status": "completed",
        "progress": 100
    }
}
```

### `todo_tool:delete` — Delete a task

| Parameter | Required | Description |
|-----------|----------|-------------|
| `task_id` | **Yes** | The task UUID |
| `confirmed` | **Yes** | Must be `true` — see deletion policy below |

**⚠️ DELETION POLICY (NON-NEGOTIABLE):**

Never delete a task without explicit authorization from the Principal (Wagner dos Santos). If the Principal says "clean up" or "remove", confirm each deletion individually before executing. The tool itself will block deletions unless `confirmed: true` is passed.

Example (only after explicit Principal confirmation):
```json
{
    "thoughts": ["Principal confirmed deletion of this task."],
    "tool_name": "todo_tool:delete",
    "tool_args": {
        "task_id": "abc123-def456-...",
        "confirmed": true
    }
}
```

### `todo_tool:link_chat` — Link a chat section to a task

| Parameter | Required | Description |
|-----------|----------|-------------|
| `task_id` | **Yes** | The task UUID |
| `chat_id` | **Yes** | The chat section ID to link |

Example:
```json
{
    "thoughts": ["Linking current chat to the task for traceability."],
    "tool_name": "todo_tool:link_chat",
    "tool_args": {
        "task_id": "abc123-def456-...",
        "chat_id": "chat_section_xyz"
    }
}
```

### `todo_tool:unlink_chat` — Unlink a chat section from a task

| Parameter | Required | Description |
|-----------|----------|-------------|
| `task_id` | **Yes** | The task UUID |
| `chat_id` | **Yes** | The chat section ID to unlink |

### `todo_tool:stats` — Get task statistics

No parameters required.

Example:
```json
{
    "thoughts": ["Checking overall task statistics."],
    "tool_name": "todo_tool:stats",
    "tool_args": {}
}
```

### `todo_tool:projects` — List all project names

No parameters required.

Example:
```json
{
    "thoughts": ["Listing all projects that have tasks."],
    "tool_name": "todo_tool:projects",
    "tool_args": {}
}
```

---

## Valid Values Reference

**Status:** `pending` · `in_progress` · `blocked` · `completed` · `cancelled`

**Priority:** `low` · `medium` · `high` · `urgent`

---

## Notes

- Tasks are **global** — shared across all projects and agents. There is no access control.
- Set `agent_profile` to your own profile name when creating tasks for self-tracking (e.g., `"developer"`, `"researcher"`).
- Use `project` to group tasks logically.
- Results are sorted by `updated_at` (most recent first).
