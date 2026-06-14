# Local Development Runbook

## Start Dependencies
```bash
make up
```

## Start the API
```bash
make run-control-plane
```

## Start the Worker
```bash
make run-worker
```

## Create a Service
```bash
idpctl create-service payments-api --team checkout --env dev --wait
```

The worker generates:
- `gitops/applications/tenants/<team>/<service>-<env>.yaml`
- `infra/terraform/tenants/<team>/<service>-<env>.tfvars.json`
- `docs/runbooks/tenants/<team>/<service>.md`
