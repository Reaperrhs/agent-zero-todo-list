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

    blocked_by = data.get("blocked_by", [])
    if isinstance(blocked_by, str):
        blocked_by = [bid.strip() for bid in blocked_by.split(",") if bid.strip()]
    blocked_by = [str(bid) for bid in blocked_by if str(bid).strip()]

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
        "blocked_by": blocked_by,
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
        # Validate blocked_by references exist
        for bid in task.get("blocked_by", []):
            if bid not in todos:
                raise ValueError(f"blocked_by: task '{bid}' not found")
        # Validate no circular deps (task can't block itself since it doesn't exist yet,
        # but check if any referenced blocker is blocked by... well, the new task doesn't
        # exist yet so this is implicitly safe. Still, check referenced tasks exist.)
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
        if "blocked_by" in data:
            new_blocked = data["blocked_by"]
            if isinstance(new_blocked, str):
                new_blocked = [bid.strip() for bid in new_blocked.split(",") if bid.strip()]
            new_blocked = [str(bid) for bid in new_blocked if str(bid).strip()]
            # Validate referenced task IDs exist
            for bid in new_blocked:
                if bid not in todos:
                    raise ValueError(f"blocked_by: task '{bid}' not found")
            # Circular dependency check: would adding these blockers create a cycle?
            for bid in new_blocked:
                if _would_cycle(todos, task_id, bid):
                    raise ValueError(
                        f"Circular dependency: task '{bid}' is already (directly or indirectly) blocked by '{task_id}'"
                    )
            task["blocked_by"] = new_blocked
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


def _would_cycle(todos: dict, source_id: str, blocker_id: str) -> bool:
    """Check if making source_id blocked by blocker_id would create a cycle.

    Walk the blocker chain from blocker_id — if we ever reach source_id,
    it's circular.
    """
    visited = set()
    current = blocker_id
    while current:
        if current == source_id:
            return True
        if current in visited:
            break
        visited.add(current)
        task = todos.get(current)
        if not task:
            break
        blockers = task.get("blocked_by", [])
        # Check all blockers' chains
        if any(_would_cycle(todos, source_id, bid) for bid in blockers if bid != current):
            return True
        # Also check: if source_id is in this task's blocked_by, it's direct
        if source_id in blockers:
            return True
        break
    # Walk upward: check if blocker_id itself is blocked (directly or indirectly) by source_id
    # via the blocked_by chains of all tasks reachable from blocker_id
    queue = [blocker_id]
    visited2 = set()
    while queue:
        current = queue.pop(0)
        if current in visited2:
            continue
        visited2.add(current)
        task_obj = todos.get(current)
        if not task_obj:
            continue
        for bid in task_obj.get("blocked_by", []):
            if bid == source_id:
                return True
            if bid not in visited2:
                queue.append(bid)
    return False


def get_blocked() -> list[dict]:
    """Return tasks that are currently blocked (at least one non-completed blocker)."""
    with _lock:
        todos = _read_raw()
    result = []
    for t in todos.values():
        blockers = t.get("blocked_by", [])
        if not blockers:
            continue
        # Check if any blocker is not completed/cancelled
        active_blockers = []
        for bid in blockers:
            blocker = todos.get(bid)
            if blocker and blocker.get("status") not in ("completed", "cancelled"):
                active_blockers.append(bid)
        if active_blockers:
            result.append({**t, "_active_blockers": active_blockers})
    return result


def get_unblocked() -> list[dict]:
    """Return tasks that have blocked_by but all blockers are now completed/cancelled."""
    with _lock:
        todos = _read_raw()
    result = []
    for t in todos.values():
        blockers = t.get("blocked_by", [])
        if not blockers:
            continue
        # All blockers must be completed or cancelled
        all_resolved = True
        for bid in blockers:
            blocker = todos.get(bid)
            if not blocker or blocker.get("status") not in ("completed", "cancelled"):
                all_resolved = False
                break
        if all_resolved:
            result.append(t)
    return result


def check_on_complete(task_id: str) -> list[dict]:
    """Check which tasks become unblocked when task_id is marked completed.

    Call this after setting a task to 'completed' status.
    Returns list of newly-unblocked tasks.
    """
    with _lock:
        todos = _read_raw()
    unblocked = []
    for t in todos.values():
        if t["id"] == task_id:
            continue
        blockers = t.get("blocked_by", [])
        if task_id not in blockers:
            continue
        # Check if all OTHER blockers are also resolved
        all_resolved = True
        for bid in blockers:
            if bid == task_id:
                continue
            blocker = todos.get(bid)
            if not blocker or blocker.get("status") not in ("completed", "cancelled"):
                all_resolved = False
                break
        if all_resolved:
            unblocked.append(t)
    return unblocked


def get_stats() -> dict[str, Any]:
    """Return task statistics."""
    with _lock:
        todos = _read_raw()
    all_tasks = list(todos.values())
    stats = {"total": len(all_tasks)}
    for s in VALID_STATUSES:
        stats[s] = len([t for t in all_tasks if t.get("status") == s])
    return stats
