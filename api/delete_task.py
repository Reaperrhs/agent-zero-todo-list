from helpers.api import ApiHandler, Input, Output, Request, Response
from usr.plugins.todo_list.helpers.todos import delete_task as _delete_task


class DeleteTask(ApiHandler):
    """Delete a task by ID."""

    async def process(self, input: Input, request: Request) -> Output:
        task_id = str(input.get("task_id", "")).strip()
        if not task_id:
            return Response("task_id is required", 400)

        deleted = _delete_task(task_id)
        if not deleted:
            return Response("Task not found", 404)

        return {
            "ok": True,
            "task_id": task_id,
        }
