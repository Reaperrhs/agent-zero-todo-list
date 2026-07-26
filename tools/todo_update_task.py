from __future__ import annotations

import json
from helpers.tool import Tool, Response
from usr.plugins.todo_list.helpers.todos import update_task as _update_task


class UpdateTask(Tool):
    """Update an existing task in the todo list."""

    async def execute(self, **kwargs) -> Response:
        task_id = str(self.args.get("task_id", "")).strip()
        if not task_id:
            return Response(
                message="Error: task_id is required to update a task.",
                break_loop=False,
            )

        # Build update data from provided args (only include fields that were passed)
        update_data = {"task_id": task_id}
        for field in ["title", "description", "status", "priority", "progress",
                      "project", "agent_profile", "tags", "chat_sections"]:
            if field in self.args:
                update_data[field] = self.args[field]

        task = _update_task(task_id, update_data)
        if not task:
            return Response(
                message=f"Error: Task '{task_id}' not found.",
                break_loop=False,
            )

        return Response(
            message=json.dumps({"ok": True, "task": task}, indent=2, ensure_ascii=False),
            break_loop=False,
        )
