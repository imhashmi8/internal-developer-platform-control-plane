# Control Plane APIs, DB Entities & Async Data Flow Contracts

## API Versioning Strategy
All APIs are versioned.

Base path:
```text
/api/v1
```

## Endpoints

### Health
```text
GET /api/v1/health/
```
Returns control-plane liveness and database readiness.

```json
{
  "status": "healthy",
  "service": "idp-control-plane",
  "component": "api",
  "database": "ready"
}
```
`status` is `degraded` and `database` is `unavailable` when the database is not reachable.

### Services
```text
GET  /api/v1/services/
POST /api/v1/services/
```

`POST` accepts a service-creation request:
```json
{
  "service_name": "payments-api",
  "team": "checkout",
  "environment": "dev"
}
```

It persists the service in `PENDING`, enqueues an async provisioning job, and
responds `201 Created`:
```json
{
  "service": {
    "id": 1,
    "service_name": "payments-api",
    "team": "checkout",
    "environment": "dev",
    "lifecycle_state": "PENDING"
  },
  "job": {
    "id": 1,
    "job_id": "job-<uuid>",
    "service_id": 1,
    "operation_type": "CREATE_SERVICE",
    "state": "PENDING",
    "message": "Queued service provisioning workflow",
    "artifact_path": null
  }
}
```
A duplicate `service_name` returns `409 Conflict`.

`GET /api/v1/services/` lists services ordered by id.

### Jobs
```text
GET /api/v1/jobs/
GET /api/v1/jobs/{job_id}
```
`GET /api/v1/jobs/` lists jobs (newest first). `GET /api/v1/jobs/{job_id}`
returns a single job by its `job_id`, or `404 Not Found` if it does not exist.
Clients (including `idpctl --wait`) poll this endpoint until `state` is
`SUCCEEDED` or `FAILED`.

## DB Entities

### Service
| Field | Type | Notes |
|-------|------|-------|
| `id` | int | primary key |
| `service_name` | str | unique |
| `team` | str | owning team |
| `environment` | str | e.g. `dev`, `staging`, `prod` |
| `lifecycle_state` | str | `PENDING` → `PROVISIONING` → `ACTIVE` |

### Job
| Field | Type | Notes |
|-------|------|-------|
| `id` | int | primary key |
| `job_id` | str | unique, public identifier (`job-<uuid>`) |
| `service_id` | int? | owning service |
| `operation_type` | str | e.g. `CREATE_SERVICE` |
| `state` | str | `PENDING` → `RUNNING` → `SUCCEEDED` / `FAILED` |
| `message` | str? | human-readable progress detail |
| `artifact_path` | str? | comma-separated paths of generated artifacts |

## Async Data Flow Contract

```text
idpctl ──POST /services/──▶ control plane
                              │  persist Service (PENDING) + Job (PENDING)
                              │  dispatch Celery task "process_create_service_job"
                              ▼
                           Redis broker
                              ▼
                        provisioning worker
                              │  Job: RUNNING, Service: PROVISIONING
                              │  render GitOps + Terraform + runbook artifacts
                              │  Job: SUCCEEDED, Service: ACTIVE
                              ▼
                        shared control-plane database
                              ▲
idpctl ──GET /jobs/{id}───────┘  (poll until terminal state)
```

The control plane and worker communicate **only** through the shared database
and the Redis broker — the API never blocks on provisioning work. The task is
dispatched by name (`process_create_service_job`), so the control plane has no
import-time dependency on worker code.

Generated artifacts (written under the platform repo root):
- `gitops/applications/tenants/{team}/{service}-{env}.yaml` — ArgoCD `Application`
- `infra/terraform/tenants/{team}/{service}-{env}.tfvars.json` — tenant Terraform inputs
- `docs/runbooks/tenants/{team}/{service}.md` — service runbook
