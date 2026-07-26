## todo_get_tasks

Retrieve and filter tasks from the shared todo list. Use this to check pending tasks, find tasks by project/status/priority, or search for specific tasks.

**When to use:**
- User asks about pending tasks, to-dos, or what needs to be done
- You need to check task status or progress
- Looking for tasks in a specific project or with a specific tag
- Reviewing workload or task statistics

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string | no | Get a single task by ID |
| `project` | string | no | Filter by project name |
| `agent_profile` | string | no | Filter by agent profile |
| `status` | string | no | Filter by status: `pending`, `in_progress`, `blocked`, `completed`, `cancelled` |
| `priority` | string | no | Filter by priority: `low`, `medium`, `high`, `urgent` |
| `search` | string | no | Search in title and description |
| `tag` | string | no | Filter by tag |
| `chat_section` | string | no | Filter by linked chat section |

If no filters are provided, returns all tasks sorted by last updated.

### Examples

Get all pending tasks:
```json
{
  "status": "pending"
}
```

Get tasks for a project:
```json
{
  "project": "CheapTravel VIP",
  "status": "pending"
}
```

Search for a task:
```json
{
  "search": "security headers"
}
```

Get a single task:
```json
{
  "task_id": "abc123-def456"
}
```

Returns: `{ ok, tasks, projects, stats, count }` or `{ ok, task }` for single lookup.
