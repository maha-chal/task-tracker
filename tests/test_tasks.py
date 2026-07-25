from datetime import date, timedelta

# POST /tasks


def test_create_task_valid_returns_201_with_full_body(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Write tests",
            "description": "Cover the API",
            "status": "InProgress",
            "priority": "High",
            "assignee": "Maha",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write tests"
    assert body["description"] == "Cover the API"
    assert body["status"] == "InProgress"
    assert body["priority"] == "High"
    assert body["assignee"] == "Maha"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post("/tasks", json={"title": "Bad priority", "priority": "Urgent"})
    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    response = client.post("/tasks", json={"title": "Extra field", "unexpected": "value"})
    assert response.status_code == 422


# GET /tasks


def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client, created_task):
    response = client.get("/tasks", params={"status": "Done"})
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "Low one", "priority": "Low"})
    high = client.post("/tasks", json={"title": "High one", "priority": "High"}).json()

    response = client.get("/tasks", params={"priority": "High"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == high["id"]


# GET /tasks/{id}


def test_get_task_by_id_returns_task(client, created_task):
    response = client.get(f"/tasks/{created_task['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created_task["id"]


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    response = client.get("/tasks/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id does-not-exist not found"


# PATCH /tasks/{id}


def test_patch_partial_update_keeps_other_fields(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"title": "Updated title"})
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Updated title"
    assert body["description"] == created_task["description"]
    assert body["status"] == created_task["status"]
    assert body["priority"] == created_task["priority"]
    assert body["assignee"] == created_task["assignee"]


def test_patch_not_found_returns_404(client):
    response = client.patch("/tasks/does-not-exist", json={"title": "New title"})
    assert response.status_code == 404


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "InProgress"})
    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "Done"})
    assert response.status_code == 422


def test_patch_same_status_returns_422(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"status": "ToDo"})
    assert response.status_code == 422


def test_patch_combined_title_change_with_invalid_transition_returns_422_and_title_unchanged(client, created_task):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"title": "New title", "status": "Done"},
    )
    assert response.status_code == 422

    unchanged = client.get(f"/tasks/{created_task['id']}")
    assert unchanged.json()["title"] == created_task["title"]


# DELETE /tasks/{id}


def test_delete_existing_returns_204_no_body(client, created_task):
    response = client.delete(f"/tasks/{created_task['id']}")
    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client):
    response = client.delete("/tasks/does-not-exist")
    assert response.status_code == 404


# due_date and overdue filter


def test_create_task_with_due_date_returns_201_with_due_date(client):
    response = client.post("/tasks", json={"title": "Task with due date", "due_date": "2026-08-01"})
    assert response.status_code == 201
    assert response.json()["due_date"] == "2026-08-01"


def test_create_task_without_due_date_returns_201_with_null_due_date(client):
    response = client.post("/tasks", json={"title": "No due date"})
    assert response.status_code == 201
    assert response.json()["due_date"] is None


def test_create_task_with_invalid_due_date_format_returns_422(client):
    response = client.post("/tasks", json={"title": "Bad date", "due_date": "08/01/2026"})
    assert response.status_code == 422


def test_create_task_with_numeric_due_date_returns_422(client):
    response = client.post("/tasks", json={"title": "Numeric date", "due_date": 20260801})
    assert response.status_code == 422


def test_create_task_with_past_due_date_returns_201(client):
    past_date = (date.today() - timedelta(days=5)).isoformat()
    response = client.post("/tasks", json={"title": "Already late", "due_date": past_date})
    assert response.status_code == 201
    assert response.json()["due_date"] == past_date


def test_patch_due_date_updates_only_that_field(client, created_task):
    response = client.patch(f"/tasks/{created_task['id']}", json={"due_date": "2026-09-01"})
    assert response.status_code == 200
    body = response.json()
    assert body["due_date"] == "2026-09-01"
    assert body["title"] == created_task["title"]
    assert body["description"] == created_task["description"]
    assert body["status"] == created_task["status"]
    assert body["priority"] == created_task["priority"]
    assert body["assignee"] == created_task["assignee"]


def test_patch_omitting_due_date_leaves_it_unchanged(client, created_task):
    client.patch(f"/tasks/{created_task['id']}", json={"due_date": "2026-09-01"})
    response = client.patch(f"/tasks/{created_task['id']}", json={"title": "Renamed"})
    assert response.status_code == 200
    assert response.json()["due_date"] == "2026-09-01"


def test_patch_explicit_null_due_date_clears_it(client, created_task):
    client.patch(f"/tasks/{created_task['id']}", json={"due_date": "2026-09-01"})
    response = client.patch(f"/tasks/{created_task['id']}", json={"due_date": None})
    assert response.status_code == 200
    assert response.json()["due_date"] is None


def test_patch_invalid_due_date_format_returns_422_and_due_date_unchanged(client, created_task):
    client.patch(f"/tasks/{created_task['id']}", json={"due_date": "2026-09-01"})
    response = client.patch(f"/tasks/{created_task['id']}", json={"due_date": "01-09-2026"})
    assert response.status_code == 422

    unchanged = client.get(f"/tasks/{created_task['id']}")
    assert unchanged.json()["due_date"] == "2026-09-01"


def test_list_tasks_overdue_filter_includes_past_due_incomplete_task(client):
    past_date = (date.today() - timedelta(days=1)).isoformat()
    overdue_task = client.post("/tasks", json={"title": "Overdue", "due_date": past_date}).json()

    response = client.get("/tasks", params={"overdue": "true"})

    assert response.status_code == 200
    ids = [task["id"] for task in response.json()]
    assert overdue_task["id"] in ids


def test_list_tasks_overdue_filter_excludes_future_due_date(client):
    future_date = (date.today() + timedelta(days=1)).isoformat()
    client.post("/tasks", json={"title": "Not due yet", "due_date": future_date})

    response = client.get("/tasks", params={"overdue": "true"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_overdue_filter_excludes_null_due_date(client, created_task):
    response = client.get("/tasks", params={"overdue": "true"})
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_overdue_filter_excludes_done_task_with_past_due_date(client):
    past_date = (date.today() - timedelta(days=1)).isoformat()
    task = client.post("/tasks", json={"title": "Late but done", "due_date": past_date}).json()
    client.patch(f"/tasks/{task['id']}", json={"status": "InProgress"})
    client.patch(f"/tasks/{task['id']}", json={"status": "Done"})

    response = client.get("/tasks", params={"overdue": "true"})

    assert response.status_code == 200
    ids = [t["id"] for t in response.json()]
    assert task["id"] not in ids


def test_list_tasks_without_overdue_param_returns_all_tasks_regardless_of_overdue_state(client):
    past_date = (date.today() - timedelta(days=1)).isoformat()
    client.post("/tasks", json={"title": "Overdue", "due_date": past_date})
    client.post("/tasks", json={"title": "Not overdue"})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 2
