from __future__ import annotations

import json
from helpers.tool import Tool, Response
from usr.plugins.todo_list.helpers.todos import delete_task as _delete_task


class DeleteTask(Tool):
    """Delete a task from the todo list."""

    async def execute(self, **kwargs) -> Response:
        task_id = str(self.args.get("task_id", "")).strip()
        if not task_id:
            return Response(
                message="Error: task_id is required to delete a task.",
                break_loop=False,
            )

        deleted = _delete_task(task_id)
        if not deleted:
            return Response(
                message=f"Error: Task '{task_id}' not found.",
                break_loop=False,
            )

        return Response(
            message=json.dumps({"ok": True, "task_id": task_id, "deleted": True}, indent=2),
            break_loop=False,
        )
