from helpers.api import ApiHandler, Input, Output, Request, Response
from usr.plugins.todo_list.helpers.todos import create_task


class CreateTask(ApiHandler):
    """Create a new task."""

    async def process(self, input: Input, request: Request) -> Output:
        title = str(input.get("title", "")).strip()
        if not title:
            return Response("title is required", 400)

        try:
            task = create_task(input)
            return {
                "ok": True,
                "task": task,
            }
        except ValueError as e:
            return Response(str(e), 400)
