# internal-developer-platform-control-plane

A Staff-level flagship GitHub portfolio project that demonstrates:

- Platform Engineering
- Internal Developer Platform
- Self-service infrastructure
- GitOps delivery
- Terraform automation
- FastAPI control plane
- Kubernetes governance
- Golden paths
- SRE scorecards
- Developer experience engineering

## Architecture Docs
- docs/architecture/01-business-problem-and-product-framing.md
- docs/architecture/02-platform-personas-and-developer-journey.md
- docs/architecture/03-end-to-end-request-lifecycle.md
- docs/architecture/04-high-level-production-architecture.md

## Repository Design
This monorepo is organized by platform product boundaries:
- control plane APIs
- provisioning workers
- Terraform + Helm
- GitOps delivery
- golden path templates
- policy packs
- CLI
- test suites

## Multi-Tenant Design
The platform is built for multi-team scale with:
- tenant namespace isolation
- RBAC boundaries
- secret tenancy
- environment separation
- policy inheritance
- cost attribution readiness

## Control Plane API Design
The platform exposes versioned APIs for:
- service creation
- preview environments
- promotions
- rollback
- scorecards
- async job tracking

## Architecture Decisions
- FastAPI control plane
- Celery workflow engine
- GitOps app-of-apps
- multi-tenant boundaries
- roadmap for Backstage + multi-cloud

## Try the MVP Locally

Start Postgres and Redis:

```bash
make up
```

Install the local packages:

```bash
make install
```

In one terminal, run the control plane:

```bash
make run-control-plane
```

In another terminal, run the provisioning worker:

```bash
make run-worker
```

Create a service through the CLI:

```bash
idpctl create-service payments-api --team checkout --env dev --wait
```

The worker will generate local platform artifacts:

- `gitops/applications/tenants/checkout/payments-api-dev.yaml`
- `infra/terraform/tenants/checkout/payments-api-dev.tfvars.json`
- `docs/runbooks/tenants/checkout/payments-api.md`

Useful API endpoints:

- `GET /api/v1/health/`
- `GET /api/v1/services/`
- `POST /api/v1/services/`
- `GET /api/v1/jobs/`
- `GET /api/v1/jobs/{job_id}`
