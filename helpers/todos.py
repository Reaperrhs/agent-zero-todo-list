"""Todo List persistence layer.

Stores tasks in a JSON file with thread-safe access.
Tasks are global (cross-project, cross-agent) with filterable fields.
"""

import json
import os
import threading
import time
import uuid
from typing import Any

_PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_PLUGIN_DIR, "data")
_TODOS_FILE = os.path.join(_DATA_DIR, "todos.json")
_lock = threading.Lock()

VALID_STATUSES = {"pending", "in_progress", "blocked", "completed", "cancelled"}
VALID_PRIORITIES = {"low", "medium", "high", "urgent"}


def _ensure_data_dir():
    os.makedirs(_DATA_DIR, exist_ok=True)


def _read_raw() -> dict[str, dict]:
    """Read all todos from disk. Caller must hold _lock."""
    if not os.path.exists(_TODOS_FILE):
        return {}
    try:
        with open(_TODOS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, IOError):
        return {}


def _save(todos: dict[str, dict]):
    """Atomically write todos to disk. Caller must hold _lock."""
    _ensure_data_dir()
    tmp_path = _TODOS_FILE + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, _TODOS_FILE)


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _new_task(data: dict[str, Any]) -> dict[str, Any]:
    """Validate and build a new task record."""
    title = str(data.get("title", "")).strip()
    if not title:
        raise ValueError("title is required")

    status = data.get("status", "pending")
    if status not in VALID_STATUSES:
        status = "pending"

    priority = data.get("priority", "medium")
    if priority not in VALID_PRIORITIES:
        priority = "medium"

    progress = int(data.get("progress", 0))
    progress = max(0, min(100, progress))

    start_date = str(data.get("start_date", "")).strip() or None
    due_date = str(data.get("due_date", "")).strip() or None

    now = _now()
    return {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": str(data.get("description", "")).strip(),
        "status": status,
        "priority": priority,
        "progress": progress,
        "project": str(data.get("project", "")).strip(),
        "agent_profile": str(data.get("agent_profile", "")).strip(),
        "start_date": start_date,
        "due_date": due_date,
        "chat_sections": list(data.get("chat_sections", [])),
        "tags": [str(t).strip() for t in data.get("tags", []) if str(t).strip()],
        "created_at": now,
        "updated_at": now,
    }


def create_task(data: dict[str, Any]) -> dict[str, Any]:
    """Create a new task and return it."""
    task = _new_task(data)
    with _lock:
        todos = _read_raw()
        todos[task["id"]] = task
        _save(todos)
    return task


def get_tasks(
    project: str | None = None,
    agent_profile: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    search: str | None = None,
    tag: str | None = None,
    chat_section: str | None = None,
) -> list[dict]:
    """Return filtered, sorted list of tasks."""
    with _lock:
        todos = _read_raw()

    result = list(todos.values())

    if project is not None:
        result = [t for t in result if t.get("project", "") == project]
    if agent_profile is not None:
        result = [t for t in result if t.get("agent_profile", "") == agent_profile]
    if status is not None:
        result = [t for t in result if t.get("status") == status]
    if priority is not None:
        result = [t for t in result if t.get("priority") == priority]
    if tag is not None:
        result = [t for t in result if tag in t.get("tags", [])]
    if chat_section is not None:
        result = [t for t in result if chat_section in t.get("chat_sections", [])]
    if search is not None:
        q = search.lower()
        result = [
            t
            for t in result
            if q in t.get("title", "").lower()
            or q in t.get("description", "").lower()
        ]

    result.sort(key=lambda t: t.get("updated_at", ""), reverse=True)
    return result


def get_task(task_id: str) -> dict | None:
    """Get a single task by id."""
    with _lock:
        todos = _read_raw()
    return todos.get(task_id)


def update_task(task_id: str, data: dict[str, Any]) -> dict | None:
    """Update a task. Returns updated task or None if not found."""
    with _lock:
        todos = _read_raw()
        task = todos.get(task_id)
        if not task:
            return None

        if "title" in data:
            title = str(data["title"]).strip()
            if title:
                task["title"] = title
        if "description" in data:
            task["description"] = str(data.get("description", "")).strip()
        if "status" in data:
            status = data["status"]
            if status in VALID_STATUSES:
                task["status"] = status
        if "priority" in data:
            priority = data["priority"]
            if priority in VALID_PRIORITIES:
                task["priority"] = priority
        if "progress" in data:
            progress = int(data["progress"])
            task["progress"] = max(0, min(100, progress))
        if "project" in data:
            task["project"] = str(data.get("project", "")).strip()
        if "agent_profile" in data:
            task["agent_profile"] = str(data.get("agent_profile", "")).strip()
        if "start_date" in data:
            val = str(data.get("start_date", "")).strip() or None
            task["start_date"] = val
        if "due_date" in data:
            val = str(data.get("due_date", "")).strip() or None
            task["due_date"] = val
        if "tags" in data:
            task["tags"] = [str(t).strip() for t in data["tags"] if str(t).strip()]
        if "chat_sections" in data:
            task["chat_sections"] = list(data["chat_sections"])

        task["updated_at"] = _now()
        _save(todos)
        return task


def delete_task(task_id: str) -> bool:
    """Delete a task. Returns True if deleted."""
    with _lock:
        todos = _read_raw()
        if task_id not in todos:
            return False
        del todos[task_id]
        _save(todos)
        return True


def link_chat(task_id: str, chat_id: str) -> dict | None:
    """Link a chat section to a task. Returns updated task or None."""
    with _lock:
        todos = _read_raw()
        task = todos.get(task_id)
        if not task:
            return None
        sections = list(task.get("chat_sections", []))
        if chat_id not in sections:
            sections.append(chat_id)
            task["chat_sections"] = sections
            task["updated_at"] = _now()
            _save(todos)
        return task


def unlink_chat(task_id: str, chat_id: str) -> dict | None:
    """Unlink a chat section from a task. Returns updated task or None."""
    with _lock:
        todos = _read_raw()
        task = todos.get(task_id)
        if not task:
            return None
        sections = list(task.get("chat_sections", []))
        if chat_id in sections:
            sections.remove(chat_id)
            task["chat_sections"] = sections
            task["updated_at"] = _now()
            _save(todos)
        return task


def get_projects() -> list[str]:
    """Return sorted list of unique project names."""
    with _lock:
        todos = _read_raw()
    projects = sorted({t.get("project", "") for t in todos.values() if t.get("project")})
    return projects


def get_agent_profiles() -> list[str]:
    """Return sorted list of unique agent profile names."""
    with _lock:
        todos = _read_raw()
    profiles = sorted({t.get("agent_profile", "") for t in todos.values() if t.get("agent_profile")})
    return profiles


def get_stats() -> dict[str, Any]:
    """Return task statistics."""
    with _lock:
        todos = _read_raw()
    all_tasks = list(todos.values())
    stats = {"total": len(all_tasks)}
    for s in VALID_STATUSES:
        stats[s] = len([t for t in all_tasks if t.get("status") == s])
    return stats
