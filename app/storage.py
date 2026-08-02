import uuid
from datetime import date, datetime, timezone
from typing import Optional

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task and store it in the in-memory store.

    Generates a UUID id and sets both ``created_at`` and ``updated_at`` to the
    current UTC time. A missing description is stored as an empty string.

    Args:
        payload: Validated data for the task to create.

    Returns:
        TaskResponse: The stored task, including its generated id and timestamps.
    """
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=str(uuid.uuid4()),
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        tags=payload.tags,
        created_at=now,
        updated_at=now,
    )
    _tasks[task.id] = task
    return task


def is_overdue(task: TaskResponse) -> bool:
    """Return whether a task is overdue.

    A task is overdue when it has a due date, that due date is before today's
    local date, and its status is not Done.

    Args:
        task: The task to evaluate.

    Returns:
        bool: True if the task is overdue, otherwise False.
    """
    return (
        task.due_date is not None
        and task.due_date < date.today()
        and task.status != TaskStatus.DONE
    )


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    overdue: Optional[bool] = None,
    tag: Optional[str] = None,
) -> list[TaskResponse]:
    """Return stored tasks, optionally filtered.

    Filters are combined with AND. Any filter left as None is not applied.

    Args:
        status: If provided, keep only tasks with this exact status.
        priority: If provided, keep only tasks with this exact priority.
        overdue: If True, keep only overdue tasks (see :func:`is_overdue`).
            A value of False or None applies no overdue filtering.
        tag: If provided, keep only tasks that have this tag. Matching is
            case-insensitive.

    Returns:
        list[TaskResponse]: The tasks matching all applied filters; empty if
            none match.
    """
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [task for task in tasks if task.status == status]
    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]
    if overdue is True:
        tasks = [task for task in tasks if is_overdue(task)]
    if tag is not None:
        tag_lower = tag.lower()
        tasks = [task for task in tasks if tag_lower in (t.lower() for t in task.tags)]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Look up a single task by its id.

    Args:
        task_id: The id of the task to retrieve.

    Returns:
        Optional[TaskResponse]: The matching task, or None if no task has this id.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to an existing task.

    Only fields explicitly set on ``payload`` are changed; unset fields are
    left as-is. ``updated_at`` is refreshed to the current UTC time whenever a
    task is updated. This function does not enforce status-transition rules;
    that check happens in the route handler.

    Args:
        task_id: The id of the task to update.
        payload: The fields to change. Unset fields are ignored.

    Returns:
        Optional[TaskResponse]: The updated task, or None if no task has this id.
    """
    existing = _tasks.get(task_id)
    if existing is None:
        return None
    updates = payload.model_dump(exclude_unset=True)
    updates["updated_at"] = datetime.now(timezone.utc)
    updated = existing.model_copy(update=updates)
    _tasks[task_id] = updated
    return updated


def delete_task(task_id: str) -> bool:
    """Delete a task from the in-memory store.

    Args:
        task_id: The id of the task to delete.

    Returns:
        bool: True if a task was deleted, False if no task had this id.
    """
    if task_id not in _tasks:
        return False
    del _tasks[task_id]
    return True


def _reset() -> None:
    _tasks.clear()
