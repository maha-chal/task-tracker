from fastapi import HTTPException, status

from app.models import TaskStatus

VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset({
    (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
    (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
    (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
})


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Validate that a task status change is allowed.

    Checks the ``(current, new)`` pair against ``VALID_TRANSITIONS``. Allowed
    transitions are ToDo->InProgress, InProgress->Done, and Done->InProgress.
    Any other pair (including same-status changes such as ToDo->ToDo) is
    rejected.

    Args:
        current: The task's existing status.
        new: The requested target status.

    Returns:
        None: Returns nothing when the transition is valid.

    Raises:
        HTTPException: 422 Unprocessable Entity if the transition is not in
            ``VALID_TRANSITIONS``; the detail lists the allowed transitions.
    """
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted({f"{f.value}->{t.value}" for f, t in VALID_TRANSITIONS})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status transition from {current.value} to {new.value}. Allowed transitions: {allowed}",
        )
