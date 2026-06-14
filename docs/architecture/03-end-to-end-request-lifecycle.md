# End-to-End Request Lifecycle

## Developer Request
A developer runs:

```bash
idpctl create-service payments-api \
  --team checkout \
  --env dev \
  --wait
```

The CLI issues `POST /api/v1/services/` against the control plane.

## Control Plane Intake
The control plane:
1. Persists a `Service` row in `lifecycle_state = PENDING`.
2. Creates a provisioning `Job` (`operation_type = CREATE_SERVICE`) in `state = PENDING`.
3. Dispatches the Celery task `process_create_service_job` onto the Redis broker.
4. Returns `201 Created` with the `service` and `job` payloads.

A duplicate `service_name` short-circuits with `409 Conflict` and no job is created.

## Asynchronous Provisioning
The provisioning worker consumes the task and:
1. Marks the job `RUNNING` and the service `PROVISIONING`.
2. Renders the golden-path artifacts:
   - `gitops/applications/tenants/{team}/{service}-{env}.yaml` (ArgoCD `Application`)
   - `infra/terraform/tenants/{team}/{service}-{env}.tfvars.json`
   - `docs/runbooks/tenants/{team}/{service}.md`
3. Marks the service `ACTIVE` and the job `SUCCEEDED`, recording the artifact paths.

Any failure rolls the job to `FAILED`.

## Status Resolution
With `--wait`, the CLI polls `GET /api/v1/jobs/{job_id}` every few seconds until
the job reaches a terminal state (`SUCCEEDED` or `FAILED`), then prints the final
job record. Without `--wait`, the developer can poll the same endpoint manually.

## Summary
```text
idpctl ─▶ control plane ─▶ Redis ─▶ worker ─▶ shared DB ◀─ idpctl (poll)
          (PENDING)                  (RUNNING → SUCCEEDED)
```

The request path is fully asynchronous: the API call returns immediately while
provisioning proceeds in the background, and the developer observes progress
through the job-status endpoint.
