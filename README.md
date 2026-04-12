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