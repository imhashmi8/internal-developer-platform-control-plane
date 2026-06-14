# Internal Developer Platform — Control Plane

A reference **Internal Developer Platform (IDP)** that lets application teams
self-service new services through a golden path, while the platform team keeps
ownership of multi-tenant isolation, GitOps delivery, and policy governance.

It demonstrates staff-level platform engineering: a versioned control-plane API,
an async provisioning workflow, Terraform/Helm/GitOps scaffolding, policy packs,
golden-path templates, and a CLI — wired together so a developer can go from
"I need a service" to provisioned platform artifacts in one command.

---

## What we are trying to achieve

Spinning up a new production-ready service usually means hand-rolling a
namespace, RBAC, a Helm chart, an ArgoCD app, Terraform inputs, and a runbook —
slow, inconsistent, and error-prone. This platform turns that into a
**self-service golden path**:

- **Developers** request a service (`idpctl create-service ...` or the API) and
  get consistent, policy-compliant platform artifacts back — without learning
  Kubernetes, Terraform, or ArgoCD.
- **The platform team** owns the golden path centrally: tenant isolation, labels,
  policy, and delivery model are enforced once and inherited by every service.
- Everything is **API-first and async**, so the same flow works from a CLI, a
  future web portal, or CI.

---

## How it works (end-to-end flow)

```mermaid
flowchart LR
    Dev[Developer] -->|idpctl / Swagger UI| API[Control Plane API - FastAPI]
    API -->|persist Service + Job| DB[(Postgres)]
    API -->|dispatch task by name| Broker[(Redis broker)]
    Broker --> Worker[Provisioning Worker - Celery]
    Worker -->|update lifecycle| DB
    Worker -->|render artifacts| Artifacts[GitOps + Terraform + Runbook]
    Dev -->|poll GET /jobs/id| API
```

1. A developer calls **`POST /api/v1/services/`** (via `idpctl` or the Swagger UI).
2. The control plane persists a `Service` (`PENDING`) and a provisioning `Job`
   (`PENDING`), then dispatches the Celery task `process_create_service_job` onto
   Redis. The API returns immediately — it never blocks on provisioning.
3. The **provisioning worker** consumes the task, marks the job `RUNNING` /
   service `PROVISIONING`, and renders the golden-path artifacts.
4. On success the job becomes `SUCCEEDED` and the service `ACTIVE`, with the
   generated artifact paths recorded on the job.
5. The developer polls **`GET /api/v1/jobs/{job_id}`** (the CLI's `--wait` flag
   automates this) until the job reaches a terminal state.

The control plane and worker share **only** the database and the Redis broker;
the task is dispatched by name, so the API has no import-time dependency on
worker code.

### Generated artifacts

For `service=payments-api`, `team=checkout`, `env=dev` the worker produces:

| Artifact | Path | Purpose |
|----------|------|---------|
| ArgoCD `Application` | `gitops/applications/tenants/checkout/payments-api-dev.yaml` | GitOps delivery into the tenant namespace |
| Terraform inputs | `infra/terraform/tenants/checkout/payments-api-dev.tfvars.json` | Tenant namespace + label contract |
| Runbook | `docs/runbooks/tenants/checkout/payments-api.md` | On-call ownership & first checks |

---

## Repository structure

```text
apps/control-plane/        FastAPI control plane (API, models, schemas, db)
workers/provisioning-worker/  Celery worker that renders platform artifacts
cli/idpctl/                idpctl self-service CLI
infra/terraform/           Root module + tenant-namespace module
infra/helm/idp-service/    Helm chart for the platform service
gitops/bootstrap/          ArgoCD app-of-apps + projects
policies/opa/              OPA/Rego service scorecard
policies/kyverno/          Kyverno tenant-baseline policies
templates/                 Golden-path service templates (fastapi, node, spring, cron)
docs/architecture/         Architecture docs (01–08)
docs/adrs/                 Architecture Decision Records
docs/runbooks/             Operational runbooks
tests/                     Control-plane API + end-to-end worker tests
```

## Architecture decisions

- **FastAPI** control plane (versioned `/api/v1`, async-friendly, OpenAPI docs)
- **Celery + Redis** workflow engine for async provisioning jobs
- **Postgres** as the shared system-of-record (SQLite fallback for zero-infra dev)
- **GitOps (ArgoCD) app-of-apps** delivery model
- Multi-tenant boundaries via namespace isolation, label inheritance, and policy

See [docs/architecture/](docs/architecture/) and [docs/adrs/](docs/adrs/) for the
full reasoning, and [08-roadmap](docs/architecture/08-roadmap-and-future-extensibility.md)
for what is intentionally future scope (preview envs, promotions, scorecards API,
Backstage, multi-cloud).

---

## Prerequisites

- Python **3.11+**
- [`uv`](https://github.com/astral-sh/uv) (used by the `make run-*` targets)
- Docker (for the local Postgres + Redis via `make up`)
- `make`

## Setup

```bash
# 1. Start Postgres + Redis
make up

# 2. Install the control plane, worker, and CLI (editable)
make install
```

Configuration lives in `.env` (copy from `.env.example`). Key variables:

```bash
DATABASE_URL=postgresql://idp:idp@127.0.0.1:5432/idp
REDIS_URL=redis://localhost:6379/0
```

> When you move to a managed/cloud database later, only `DATABASE_URL` changes.

## Run

```bash
# Terminal 1 — control plane (http://127.0.0.1:8000)
make run-control-plane

# Terminal 2 — provisioning worker
make run-worker
```

---

## How to test

There are three ways to exercise the workflow.

### 1. Automated tests (fastest — no Docker/Redis needed)

```bash
make test          # or: pytest tests -v
```

Runs the control-plane API tests **and** an end-to-end test that drives the real
provisioning task and asserts the `PENDING → ACTIVE` lifecycle plus the generated
GitOps/Terraform/runbook artifacts. Expected: **3 passed**.

### 2. CLI (the developer self-service path)

With the control plane and worker running:

```bash
idpctl create-service payments-api --team checkout --env dev --wait
```

The CLI creates the service, then polls the job until it reports `SUCCEEDED`
(~5s) with the three artifact paths. Other commands:

```bash
idpctl list-services
idpctl list-jobs
idpctl get-job <job_id>
```

### 3. Swagger UI (interactive API)

The FastAPI control plane serves interactive docs automatically:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

In Swagger UI:

1. **POST `/api/v1/services/`** → *Try it out* → body
   `{ "service_name": "orders-api", "team": "checkout", "environment": "dev" }`
   → *Execute*. The `201` response returns the `service` and a `job_id`.
2. **GET `/api/v1/jobs/{job_id}`** → paste the `job_id` → *Execute*; re-run until
   `state` is `SUCCEEDED`.
3. **GET `/api/v1/services/`** → your service shows `lifecycle_state: ACTIVE`.

### Verify the result (any path)

```bash
ls gitops/applications/tenants/checkout/    # <service>-<env>.yaml
ls infra/terraform/tenants/checkout/        # <service>-<env>.tfvars.json
ls docs/runbooks/tenants/checkout/          # <service>.md

curl -s http://127.0.0.1:8000/api/v1/health/      # {"status":"healthy", ...}
curl -s http://127.0.0.1:8000/api/v1/services/    # service is ACTIVE
```

---

## API reference

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/api/v1/health/` | Control-plane + database readiness |
| `GET`  | `/api/v1/services/` | List services |
| `POST` | `/api/v1/services/` | Create a service (returns `service` + `job`); `409` on duplicate name |
| `GET`  | `/api/v1/jobs/` | List provisioning jobs |
| `GET`  | `/api/v1/jobs/{job_id}` | Get a job by id (`404` if unknown) |

Full request/response and DB-entity contracts:
[07-control-plane-api-contracts](docs/architecture/07-control-plane-api-contracts.md).

---

## Troubleshooting

- **`role "idp" does not exist` / connection refused on 5432** — a local Postgres
  (e.g. Homebrew) may be holding port `5432` and shadowing the Docker container.
  Either stop it (`brew services stop postgresql@<v>`) so Docker serves `5432`,
  or create the role/db in your local Postgres:
  ```bash
  psql -d postgres -c "CREATE ROLE idp LOGIN PASSWORD 'idp' CREATEDB;"
  psql -d postgres -c "CREATE DATABASE idp OWNER idp;"
  ```
- **`409 Conflict` on create** — `service_name` must be unique. Use a new name, or
  clear dev data:
  `psql "$DATABASE_URL" -c "DELETE FROM jobs; DELETE FROM services;"`
- **Worker `ModuleNotFoundError`** — run `make install` so the worker venv has its
  dependencies (including the Postgres driver).
- **`/health` reports `degraded`** — the database was unreachable at startup;
  fix `DATABASE_URL` / infra and restart the control plane.

---

## Roadmap

- **v1:** service creation, namespace provisioning, ArgoCD onboarding, scorecards, dashboards
- **v2:** preview environments, promotions/rollback, drift detection, cost attribution
- **v3:** Backstage integration, multi-cluster/multi-cloud, policy marketplace

See [08-roadmap-and-future-extensibility](docs/architecture/08-roadmap-and-future-extensibility.md).
