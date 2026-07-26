## Creating Tasks

Create new tasks in the shared todo list. Tasks are global and persist across conversations.

**When to use:**
- Starting a new piece of work that needs tracking
- Breaking down a larger task into subtasks
- User asks you to remember or track something
- Delegating work that needs progress monitoring

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | **yes** | Task title (short, clear) |
| `description` | string | no | Detailed description or notes |
| `status` | string | no | One of: `pending` (default), `in_progress`, `blocked`, `completed`, `cancelled` |
| `priority` | string | no | One of: `low`, `medium` (default), `high`, `urgent` |
| `progress` | integer | no | 0-100 percentage (default: 0) |
| `project` | string | no | Project name (e.g. "CheapTravel VIP") |
| `agent_profile` | string | no | Assigning agent profile |
| `tags` | array | no | List of tag strings |

### Example

```json
{
  "title": "Fix article schema markup",
  "description": "Change NewsArticle to Article/BlogPosting in Squirrly SEO",
  "status": "pending",
  "priority": "high",
  "project": "CheapTravel VIP",
  "tags": ["seo", "schema"]
}
```

Returns: `{ ok, task }` with the created task including its generated `id`.
