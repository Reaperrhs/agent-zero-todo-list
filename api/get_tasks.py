from helpers.api import ApiHandler, Input, Output, Request
from usr.plugins.todo_list.helpers.todos import get_tasks as _get_tasks, get_projects, get_agent_profiles, get_stats


class GetTasks(ApiHandler):
    """Return tasks with optional filtering, plus projects and stats."""

    async def process(self, input: Input, request: Request) -> Output:
        filters = {
            "project": input.get("project") or None,
            "agent_profile": input.get("agent_profile") or None,
            "status": input.get("status") or None,
            "priority": input.get("priority") or None,
            "search": input.get("search") or None,
            "tag": input.get("tag") or None,
            "chat_section": input.get("chat_section") or None,
        }
        filters = {k: v for k, v in filters.items() if v is not None}

        tasks = _get_tasks(**filters)
        projects = get_projects()
        agent_profiles = get_agent_profiles()
        stats = get_stats()

        return {
            "ok": True,
            "tasks": tasks,
            "projects": projects,
            "agent_profiles": agent_profiles,
            "stats": stats,
        }
