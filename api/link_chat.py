from helpers.api import ApiHandler, Input, Output, Request, Response
from usr.plugins.todo_list.helpers.todos import link_chat as _link_chat, unlink_chat as _unlink_chat


class LinkChat(ApiHandler):
    """Link or unlink a chat section from a task."""

    async def process(self, input: Input, request: Request) -> Output:
        task_id = str(input.get("task_id", "")).strip()
        chat_id = str(input.get("chat_id", "")).strip()
        action = str(input.get("action", "link")).strip().lower()

        if not task_id:
            return Response("task_id is required", 400)
        if not chat_id:
            return Response("chat_id is required", 400)

        if action == "unlink":
            task = _unlink_chat(task_id, chat_id)
        else:
            task = _link_chat(task_id, chat_id)

        if not task:
            return Response("Task not found", 404)

        return {
            "ok": True,
            "task": task,
        }
