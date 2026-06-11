import json
import os
import time
from pathlib import Path

from worker.celery_app import celery_app
from worker.db import SessionLocal

from app.models.job import Job
from app.models.service import Service


REPO_ROOT = Path(os.getenv("PLATFORM_REPO_ROOT", Path(__file__).resolve().parents[3]))


def _slug(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "-")


def _write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _render_artifacts(service: Service) -> list[Path]:
    service_name = _slug(service.service_name)
    team = _slug(service.team)
    environment = _slug(service.environment)
    namespace = f"{team}-{service_name}-{environment}"

    gitops_path = (
        REPO_ROOT
        / "gitops"
        / "applications"
        / "tenants"
        / team
        / f"{service_name}-{environment}.yaml"
    )
    tfvars_path = (
        REPO_ROOT
        / "infra"
        / "terraform"
        / "tenants"
        / team
        / f"{service_name}-{environment}.tfvars.json"
    )
    runbook_path = (
        REPO_ROOT
        / "docs"
        / "runbooks"
        / "tenants"
        / team
        / f"{service_name}.md"
    )

    _write_file(
        gitops_path,
        f"""apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: {service_name}-{environment}
  namespace: argocd
  labels:
    idp.platform/team: {team}
    idp.platform/service: {service_name}
    idp.platform/environment: {environment}
spec:
  project: tenants
  source:
    repoURL: https://github.com/example/{service_name}
    targetRevision: main
    path: deploy/helm
    helm:
      values: |
        service:
          name: {service_name}
          team: {team}
          environment: {environment}
  destination:
    server: https://kubernetes.default.svc
    namespace: {namespace}
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
""",
    )

    _write_file(
        tfvars_path,
        json.dumps(
            {
                "service_name": service_name,
                "team": team,
                "environment": environment,
                "namespace": namespace,
                "labels": {
                    "idp.platform/team": team,
                    "idp.platform/service": service_name,
                    "idp.platform/environment": environment,
                },
            },
            indent=2,
        )
        + "\n",
    )

    _write_file(
        runbook_path,
        f"""# {service_name} Runbook

## Ownership
- Team: {team}
- Environment: {environment}
- Namespace: {namespace}

## Golden Path Defaults
- Deployment is managed through ArgoCD.
- Infrastructure inputs are recorded in `infra/terraform/tenants/{team}/{service_name}-{environment}.tfvars.json`.
- Runtime manifests are represented by `gitops/applications/tenants/{team}/{service_name}-{environment}.yaml`.

## First Checks
1. Check ArgoCD application health for `{service_name}-{environment}`.
2. Check Kubernetes events in namespace `{namespace}`.
3. Confirm service owner labels are present on workloads and alerts.
""",
    )

    return [gitops_path, tfvars_path, runbook_path]


@celery_app.task(name="process_create_service_job")
def process_create_service_job(job_id: str):
    """
    Simulates long-running control-plane provisioning workflow.
    Updates job lifecycle:
    PENDING -> RUNNING -> SUCCEEDED
    """
    db = SessionLocal()
    job = None

    try:
        job = db.query(Job).filter(Job.job_id == job_id).first()

        if not job:
            print(f"[Celery] Job not found: {job_id}")
            return

        print(f"[Celery] Starting job: {job_id}")

        # Step 1: mark job running
        job.state = "RUNNING"
        job.message = "Provisioning service catalog artifacts"
        db.commit()

        service = db.query(Service).filter(Service.id == job.service_id).first()

        if not service:
            raise RuntimeError(f"Service not found for job {job_id}")

        service.lifecycle_state = "PROVISIONING"
        db.commit()

        artifact_paths = _render_artifacts(service)
        time.sleep(5)

        service.lifecycle_state = "ACTIVE"
        job.state = "SUCCEEDED"
        job.message = "Provisioning artifacts generated"
        job.artifact_path = ",".join(
            str(path.relative_to(REPO_ROOT)) for path in artifact_paths
        )
        db.commit()

        print(f"[Celery] Completed job: {job_id}")

    except Exception as exc:
        print(f"[Celery] Failed job {job_id}: {exc}")
        db.rollback()

        if job:
            job.state = "FAILED"
            db.commit()

        raise

    finally:
        db.close()
