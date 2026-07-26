## Deleting Tasks

Delete a task from the todo list. Use sparingly — prefer updating status to `cancelled` for traceability.

**When to use:**
- Removing accidentally created or duplicate tasks
- Cleaning up tasks that are no longer relevant

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string | **yes** | ID of the task to delete |

### Example

```json
{
  "task_id": "abc123-def456"
}
```

Returns: `{ ok, task_id, deleted: true }`
