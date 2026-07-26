## Updating Tasks

Update existing tasks in the todo list. Modify title, status, priority, progress, or any other field.

**When to use:**
- Marking a task as in-progress, completed, or blocked
- Updating task progress percentage
- Changing priority or adding notes to a task
- Reassigning a task to a different project or agent

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string | **yes** | ID of the task to update |
| `title` | string | no | Updated task title |
| `description` | string | no | Updated description or notes |
| `status` | string | no | One of: `pending`, `in_progress`, `blocked`, `completed`, `cancelled` |
| `priority` | string | no | One of: `low`, `medium`, `high`, `urgent` |
| `progress` | integer | no | 0-100 percentage |
| `project` | string | no | Project name |
| `agent_profile` | string | no | Assigning agent profile |
| `tags` | array | no | Updated list of tags |

Only include fields you want to change. Omitted fields keep their current values.

### Examples

Mark task as completed:
```json
{
  "task_id": "abc123-def456",
  "status": "completed",
  "progress": 100
}
```

Update progress and add notes:
```json
{
  "task_id": "abc123-def456",
  "status": "in_progress",
  "progress": 60,
  "description": "Research phase done, drafting content now."
}
```

Returns: `{ ok, task }` with the updated task.
