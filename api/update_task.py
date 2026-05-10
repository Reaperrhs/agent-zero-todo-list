from helpers.api import ApiHandler, Input, Output, Request, Response
from usr.plugins.todo_list.helpers.todos import update_task as _update_task


class UpdateTask(ApiHandler):
    """Update an existing task."""

    async def process(self, input: Input, request: Request) -> Output:
        task_id = str(input.get("task_id", "")).strip()
        if not task_id:
            return Response("task_id is required", 400)

        task = _update_task(task_id, input)
        if not task:
            return Response("Task not found", 404)

        return {
            "ok": True,
            "task": task,
        }
