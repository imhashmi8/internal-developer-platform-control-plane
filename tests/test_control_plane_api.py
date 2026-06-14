import os
from pathlib import Path

TEST_DB = Path("/tmp/idp-control-plane-test.db")
TEST_DB.unlink(missing_ok=True)

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

from fastapi.testclient import TestClient

from app.celery_app import celery_app
from app.main import create_app


def test_create_service_persists_service_and_job(monkeypatch):
    dispatched = []

    def fake_send_task(task_name, kwargs):
        dispatched.append((task_name, kwargs))

    monkeypatch.setattr(celery_app, "send_task", fake_send_task)

    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/services/",
            json={
                "service_name": "catalog-api",
                "team": "checkout",
                "environment": "dev",
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["service"]["service_name"] == "catalog-api"
        assert body["service"]["lifecycle_state"] == "PENDING"
        assert body["job"]["operation_type"] == "CREATE_SERVICE"
        assert body["job"]["state"] == "PENDING"
        assert dispatched == [
            (
                "process_create_service_job",
                {"job_id": body["job"]["job_id"]},
            )
        ]

        services = client.get("/api/v1/services/").json()
        assert len(services) == 1
        assert services[0]["service_name"] == "catalog-api"

        job = client.get(f"/api/v1/jobs/{body['job']['job_id']}").json()
        assert job["service_id"] == body["service"]["id"]


def test_duplicate_service_returns_conflict(monkeypatch):
    monkeypatch.setattr(celery_app, "send_task", lambda *_args, **_kwargs: None)

    with TestClient(create_app()) as client:
        payload = {
            "service_name": "billing-api",
            "team": "finance",
            "environment": "dev",
        }

        assert client.post("/api/v1/services/", json=payload).status_code == 201
        assert client.post("/api/v1/services/", json=payload).status_code == 409
