# Monorepo Service Boundaries & Repository Structure

## Repository Principles
This monorepo is organized by platform product boundaries rather than tooling type.

Design goals:
- strong ownership
- reusable modules
- isolated testing
- low blast radius
- clear CI scopes
- template versioning
- policy separation

---

## Top-Level Layout

```text
internal-developer-platform-control-plane/
├── apps/
│   └── control-plane/
├── workers/
│   └── provisioning-worker/
├── infra/
│   ├── terraform/
│   └── helm/
├── gitops/
│   ├── bootstrap/
│   └── applications/
├── templates/
│   ├── fastapi-service/
│   ├── nodejs-api/
│   ├── springboot-service/
│   └── worker-cronjob/
├── policies/
│   ├── kyverno/
│   └── opa/
├── cli/
│   └── idpctl/
├── docs/
├── diagrams/
├── scripts/
└── tests/