import json
from helpers.tool import Tool, Response
from usr.plugins.todo_list.helpers.todos import (
    create_task,
    get_task,
    get_tasks,
    update_task,
    delete_task,
    link_chat,
    unlink_chat,
    get_stats,
    get_projects,
)


class TodoTool(Tool):
    async def execute(self, **kwargs):
        method = (self.method or kwargs.get("action") or "").strip().lower()

        try:
            if method == "create":
                return await self._create(kwargs)
            elif method == "list":
                return await self._list(kwargs)
            elif method == "get":
                return await self._get(kwargs)
            elif method == "update":
                return await self._update(kwargs)
            elif method == "delete":
                return await self._delete(kwargs)
            elif method == "link_chat":
                return await self._link_chat(kwargs)
            elif method == "unlink_chat":
                return await self._unlink_chat(kwargs)
            elif method == "stats":
                return await self._stats()
            elif method == "projects":
                return await self._projects()
            else:
                return Response(
                    message=(
                        f"Unknown todo_tool method: '{method}'. "
                        "Valid methods: create, list, get, update, delete, "
                        "link_chat, unlink_chat, stats, projects"
                    ),
                    break_loop=False,
                )
        except Exception as e:
            return Response(
                message=f"todo_tool error ({method}): {e}",
                break_loop=False,
            )

    async def _create(self, kwargs):
        data = {}
        for key in ("title", "description", "status", "priority",
                    "progress", "project", "agent_profile", "tags"):
            if key in kwargs:
                data[key] = kwargs[key]

        if not data.get("title"):
            return Response(
                message="todo_tool create: 'title' is required.",
                break_loop=False,
            )

        task = create_task(data)
        return Response(
            message=(
                f"Task created:\n"
                f"  ID: {task['id']}\n"
                f"  Title: {task['title']}\n"
                f"  Status: {task['status']}\n"
                f"  Priority: {task['priority']}\n"
                f"  Project: {task.get('project', '') or '(none)'}\n"
                f"  Agent: {task.get('agent_profile', '') or '(none)'}\n"
                f"  Tags: {', '.join(task.get('tags', [])) or '(none)'}"
            ),
            break_loop=False,
        )

    async def _list(self, kwargs):
        tasks = get_tasks(
            project=kwargs.get("project"),
            agent_profile=kwargs.get("agent_profile"),
            status=kwargs.get("status"),
            priority=kwargs.get("priority"),
            search=kwargs.get("search"),
            tag=kwargs.get("tag"),
            chat_section=kwargs.get("chat_section"),
        )

        if not tasks:
            return Response(
                message="No tasks found matching filters.",
                break_loop=False,
            )

        lines = [f"Found {len(tasks)} task(s):\n"]
        for t in tasks:
            lines.append(
                f"  [{t['id'][:8]}…] {t['title']}\n"
                f"    Status: {t['status']} | Priority: {t['priority']} "
                f"| Progress: {t.get('progress', 0)}%\n"
                f"    Project: {t.get('project', '') or '(none)'} "
                f"| Agent: {t.get('agent_profile', '') or '(none)'}"
            )
        return Response(message="\n".join(lines), break_loop=False)

    async def _get(self, kwargs):
        task_id = kwargs.get("task_id", "")
        if not task_id:
            return Response(
                message="todo_tool get: 'task_id' is required.",
                break_loop=False,
            )

        task = get_task(task_id)
        if not task:
            return Response(
                message=f"Task not found: {task_id}",
                break_loop=False,
            )

        return Response(
            message=(
                f"Task: {task['title']}\n"
                f"  ID: {task['id']}\n"
                f"  Description: {task.get('description', '') or '(none)'}\n"
                f"  Status: {task['status']}\n"
                f"  Priority: {task['priority']}\n"
                f"  Progress: {task.get('progress', 0)}%\n"
                f"  Project: {task.get('project', '') or '(none)'}\n"
                f"  Agent: {task.get('agent_profile', '') or '(none)'}\n"
                f"  Tags: {', '.join(task.get('tags', [])) or '(none)'}\n"
                f"  Chat sections: {', '.join(task.get('chat_sections', [])) or '(none)'}\n"
                f"  Created: {task.get('created_at', '')}\n"
                f"  Updated: {task.get('updated_at', '')}"
            ),
            break_loop=False,
        )

    async def _update(self, kwargs):
        task_id = kwargs.get("task_id", "")
        if not task_id:
            return Response(
                message="todo_tool update: 'task_id' is required.",
                break_loop=False,
            )

        data = {}
        for key in ("title", "description", "status", "priority",
                    "progress", "project", "agent_profile", "tags"):
            if key in kwargs:
                data[key] = kwargs[key]

        if not data:
            return Response(
                message="todo_tool update: no updatable fields provided.",
                break_loop=False,
            )

        task = update_task(task_id, data)
        if not task:
            return Response(
                message=f"Task not found: {task_id}",
                break_loop=False,
            )

        return Response(
            message=(
                f"Task updated:\n"
                f"  ID: {task['id']}\n"
                f"  Title: {task['title']}\n"
                f"  Status: {task['status']}\n"
                f"  Priority: {task['priority']}\n"
                f"  Progress: {task.get('progress', 0)}%"
            ),
            break_loop=False,
        )

    async def _delete(self, kwargs):
        if not kwargs.get("confirmed"):
            return Response(
                message=(
                    "DELETION BLOCKED: Deleting tasks requires explicit "
                    "authorization from the Principal. Ask the Principal "
                    "to confirm deletion before proceeding."
                ),
                break_loop=True,
            )

        task_id = kwargs.get("task_id", "")
        if not task_id:
            return Response(
                message="todo_tool delete: 'task_id' is required.",
                break_loop=False,
            )

        success = delete_task(task_id)
        if success:
            return Response(
                message=f"Task deleted: {task_id}",
                break_loop=False,
            )
        return Response(
            message=f"Task not found (nothing deleted): {task_id}",
            break_loop=False,
        )

    async def _link_chat(self, kwargs):
        task_id = kwargs.get("task_id", "")
        chat_id = kwargs.get("chat_id", "")
        if not task_id or not chat_id:
            return Response(
                message="todo_tool link_chat: both 'task_id' and 'chat_id' are required.",
                break_loop=False,
            )

        task = link_chat(task_id, chat_id)
        if not task:
            return Response(
                message=f"Task not found: {task_id}",
                break_loop=False,
            )

        return Response(
            message=f"Chat {chat_id} linked to task '{task['title']}'. Sections: {task.get('chat_sections', [])}",
            break_loop=False,
        )

    async def _unlink_chat(self, kwargs):
        task_id = kwargs.get("task_id", "")
        chat_id = kwargs.get("chat_id", "")
        if not task_id or not chat_id:
            return Response(
                message="todo_tool unlink_chat: both 'task_id' and 'chat_id' are required.",
                break_loop=False,
            )

        task = unlink_chat(task_id, chat_id)
        if not task:
            return Response(
                message=f"Task not found: {task_id}",
                break_loop=False,
            )

        return Response(
            message=f"Chat {chat_id} unlinked from task '{task['title']}'. Sections: {task.get('chat_sections', [])}",
            break_loop=False,
        )

    async def _stats(self):
        stats = get_stats()
        return Response(
            message=(
                f"Todo Stats:\n"
                f"  Total: {stats.get('total', 0)}\n"
                f"  By status: {json.dumps(stats.get('by_status', {}), indent=2)}\n"
                f"  By priority: {json.dumps(stats.get('by_priority', {}), indent=2)}"
            ),
            break_loop=False,
        )

    async def _projects(self):
        projects = get_projects()
        if not projects:
            return Response(
                message="No projects found.",
                break_loop=False,
            )
        return Response(
            message=f"Projects: {', '.join(projects)}",
            break_loop=False,
        )
