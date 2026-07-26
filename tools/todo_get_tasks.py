from __future__ import annotations

import json
from helpers.tool import Tool, Response
from usr.plugins.todo_list.helpers.todos import get_tasks as _get_tasks, get_task, get_projects, get_stats


class GetTasks(Tool):
    """Retrieve and filter tasks from the todo list."""

    async def execute(self, **kwargs) -> Response:
        # Support single task_id lookup
        task_id = self.args.get("task_id")
        if task_id:
            task = get_task(str(task_id).strip())
            if not task:
                return Response(message="Task not found.", break_loop=False)
            return Response(
                message=json.dumps({"ok": True, "task": task}, indent=2),
                break_loop=False,
            )

        # Filtered list
        filters = {
            "project": self.args.get("project"),
            "agent_profile": self.args.get("agent_profile"),
            "status": self.args.get("status"),
            "priority": self.args.get("priority"),
            "search": self.args.get("search"),
            "tag": self.args.get("tag"),
            "chat_section": self.args.get("chat_section"),
        }
        filters = {k: v for k, v in filters.items() if v is not None}

        tasks = _get_tasks(**filters)
        projects = get_projects()
        stats = get_stats()

        result = {
            "ok": True,
            "tasks": tasks,
            "projects": projects,
            "stats": stats,
            "count": len(tasks),
        }

        return Response(
            message=json.dumps(result, indent=2, ensure_ascii=False),
            break_loop=False,
        )
