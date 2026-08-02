from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app import storage
from app.business_rules import validate_status_transition
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

app = FastAPI(
    title="Task Tracker API",
    description="A REST API for tracking tasks: CRUD, status-transition rules, due dates, and tags.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "null",
    ],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health_check():
    """Report API liveness.

    Returns:
        dict: A mapping with ``status`` set to ``"ok"`` and ``timestamp`` set
            to the current UTC time in ISO 8601 format.

    Example:
        Request::

            GET /health

        Response::

            {"status": "ok", "timestamp": "2026-08-01T12:00:00+00:00"}
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    The request body is validated against ``TaskCreate`` (unknown fields are
    rejected, the title is required and trimmed, and tags are de-duplicated
    case-insensitively). On success the task is stored and returned with
    HTTP 201. No status-transition rule is applied on creation, so a task may
    be created directly in any status.

    Args:
        payload: The task fields to create.

    Returns:
        TaskResponse: The newly created task, including its generated id and
            timestamps.

    Raises:
        RequestValidationError: Returned by FastAPI as HTTP 422 if the body
            fails ``TaskCreate`` validation (e.g. blank title, title over 200
            characters, a blank tag, or unknown fields).

    Example:
        Request::

            POST /tasks
            {"title": "Write report", "priority": "High", "tags": ["docs"]}
    """
    return storage.add_task(payload)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
    tag: str | None = None,
) -> list[TaskResponse]:
    """List tasks, optionally filtered by query parameters.

    Filters are combined with AND; omitted parameters are not applied.

    Args:
        status: Keep only tasks with this exact status.
        priority: Keep only tasks with this exact priority.
        overdue: When True, return only overdue tasks. False or omitted applies
            no overdue filtering.
        tag: Keep only tasks having this tag (case-insensitive match).

    Returns:
        list[TaskResponse]: Tasks matching all applied filters; empty if none
            match.

    Example:
        Request::

            GET /tasks?status=InProgress&overdue=true&tag=docs
    """
    return storage.get_all_tasks(status=status, priority=priority, overdue=overdue, tag=tag)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Retrieve a single task by id.

    Args:
        task_id: The id of the task to fetch.

    Returns:
        TaskResponse: The requested task.

    Raises:
        HTTPException: 404 Not Found if no task has the given id.

    Example:
        Request::

            GET /tasks/3fa85f64-5717-4562-b3fc-2c963f66afa6
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Apply a partial update to a task.

    Only fields present in the request body are changed. When the body includes
    a new ``status``, that change is checked against the allowed status
    transitions before the update is applied.

    Args:
        task_id: The id of the task to update.
        payload: The fields to change. Unset fields are left unchanged.

    Returns:
        TaskResponse: The updated task.

    Raises:
        HTTPException: 404 Not Found if no task has the given id.
        HTTPException: 422 Unprocessable Entity if a requested status change is
            not an allowed transition (see
            :func:`app.business_rules.validate_status_transition`).
        RequestValidationError: Returned by FastAPI as HTTP 422 if the body
            fails ``TaskUpdate`` validation (e.g. blank title, title over 200
            characters, a blank tag, or unknown fields).

    Example:
        Request::

            PATCH /tasks/3fa85f64-5717-4562-b3fc-2c963f66afa6
            {"status": "InProgress"}
    """
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)
        if existing is None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        validate_status_transition(existing.status, payload.status)

    task = storage.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """Delete a task by id.

    Args:
        task_id: The id of the task to delete.

    Returns:
        None: Responds with HTTP 204 No Content on success.

    Raises:
        HTTPException: 404 Not Found if no task has the given id.

    Example:
        Request::

            DELETE /tasks/3fa85f64-5717-4562-b3fc-2c963f66afa6
    """
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
