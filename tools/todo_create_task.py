from __future__ import annotations

import json
from helpers.tool import Tool, Response
from usr.plugins.todo_list.helpers.todos import create_task as _create_task


class CreateTask(Tool):
    """Create a new task in the todo list."""

    async def execute(self, **kwargs) -> Response:
        title = str(self.args.get("title", "")).strip()
        if not title:
            return Response(
                message="Error: title is required to create a task.",
                break_loop=False,
            )

        task_data = {
            "title": title,
            "description": str(self.args.get("description", "")).strip(),
            "status": self.args.get("status", "pending"),
            "priority": self.args.get("priority", "medium"),
            "progress": int(self.args.get("progress", 0)),
            "project": str(self.args.get("project", "")).strip(),
            "agent_profile": str(self.args.get("agent_profile", "")).strip(),
            "tags": self.args.get("tags", []),
        }

        try:
            task = _create_task(task_data)
            return Response(
                message=json.dumps({"ok": True, "task": task}, indent=2, ensure_ascii=False),
                break_loop=False,
            )
        except ValueError as e:
            return Response(
                message=f"Error creating task: {e}",
                break_loop=False,
            )
