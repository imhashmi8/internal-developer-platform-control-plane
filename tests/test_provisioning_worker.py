"""End-to-end test of the core self-service flow.

Exercises the real path a developer triggers with
``idpctl create-service ... --wait``:

1. The control plane persists a Service + a provisioning Job (PENDING).
2. The provisioning worker task runs and walks the job through
   PENDING -> RUNNING -> SUCCEEDED while rendering platform artifacts.

Celery's broker/result backend are not involved here: the control plane's
``send_task`` dispatch is covered by ``test_control_plane_api`` and the worker
task is invoked directly so the provisioning logic can be verified without
standing up Redis. The worker's DB session factory is pointed at the control
plane's engine, mirroring the single shared database that ``make up`` provides
via Postgres.
"""

import json
import os
from pathlib import Path

TEST_DB = Path("/tmp/idp-provisioning-worker-test.db")
TEST_DB.unlink(missing_ok=True)

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from fastapi.testclient import TestClient

from app.celery_app import celery_app
from app.db.session import SessionLocal as AppSessionLocal
from app.main import create_app

import worker.tasks as worker_tasks


def test_worker_provisions_service_end_to_end(monkeypatch, tmp_path):
    # The worker shares the control plane's database, and its long-running
    # provisioning step is collapsed so the test stays fast.
    monkeypatch.setattr(worker_tasks, "SessionLocal", AppSessionLocal)
    monkeypatch.setattr(worker_tasks, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(worker_tasks.time, "sleep", lambda *_args, **_kwargs: None)

    # The API only enqueues work; we run the task ourselves below.
    monkeypatch.setattr(celery_app, "send_task", lambda *_args, **_kwargs: None)

    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/services/",
            json={
                "service_name": "payments-api",
                "team": "checkout",
                "environment": "dev",
            },
        )
        assert response.status_code == 201
        body = response.json()
        job_id = body["job"]["job_id"]
        service_id = body["service"]["id"]

        assert body["service"]["lifecycle_state"] == "PENDING"
        assert body["job"]["state"] == "PENDING"

        # Run the real provisioning workflow.
        worker_tasks.process_create_service_job(job_id)

        # Job and service reach their terminal success states.
        job = client.get(f"/api/v1/jobs/{job_id}").json()
        assert job["state"] == "SUCCEEDED"
        assert job["message"] == "Provisioning artifacts generated"
        assert job["service_id"] == service_id

        service = next(
            svc
            for svc in client.get("/api/v1/services/").json()
            if svc["id"] == service_id
        )
        assert service["lifecycle_state"] == "ACTIVE"

    # The three golden-path artifacts are generated on disk.
    gitops = tmp_path / "gitops/applications/tenants/checkout/payments-api-dev.yaml"
    tfvars = tmp_path / "infra/terraform/tenants/checkout/payments-api-dev.tfvars.json"
    runbook = tmp_path / "docs/runbooks/tenants/checkout/payments-api.md"

    assert gitops.exists()
    assert tfvars.exists()
    assert runbook.exists()

    # The job records the artifact paths relative to the repo root.
    for artifact in (gitops, tfvars, runbook):
        assert str(artifact.relative_to(tmp_path)) in job["artifact_path"]

    # GitOps Application targets the tenant namespace with platform labels.
    gitops_content = gitops.read_text()
    assert "kind: Application" in gitops_content
    assert "namespace: checkout-payments-api-dev" in gitops_content
    assert "idp.platform/team: checkout" in gitops_content

    # Terraform inputs capture the tenant contract.
    tf = json.loads(tfvars.read_text())
    assert tf["namespace"] == "checkout-payments-api-dev"
    assert tf["labels"]["idp.platform/service"] == "payments-api"
