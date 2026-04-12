# Internal Developer Platform — Business Problem & Product Framing

## Vision
Build a self-service Internal Developer Platform (IDP) that allows engineering teams to bootstrap production-ready services in minutes with built-in security, observability, GitOps, and governance guardrails.

---

## Business Problem
As organizations scale from 5 teams to 50+ teams, service onboarding becomes slow and inconsistent.

Common repeated tasks:
- repository scaffolding
- CI/CD onboarding
- Kubernetes namespace provisioning
- Terraform workspace creation
- IAM role and service account setup
- ArgoCD bootstrap
- dashboards and alerting
- SLO templates
- preview environments
- rollback workflows
- compliance controls

### Existing pain points
- onboarding takes days or weeks
- inconsistent standards
- deployment drift
- weak security controls
- high platform team ticket load
- SRE operational toil
- poor developer experience

---

## Product Goal
Reduce service onboarding time from days to less than 10 minutes.

North Star:
> Golden path as a product

---

## Platform Users
### Developers
- create new services
- preview environments
- promotion workflows
- scorecards

### Platform Team
- reusable templates
- governance
- tenancy controls
- policy enforcement

### SRE
- SLO defaults
- alerts
- rollback standards
- incident ownership

### Security
- audit logs
- image verification
- release controls
- compliance evidence

---

## Platform KPIs
- onboarding lead time
- deployment success rate
- golden path adoption %
- MTTR
- policy violations
- platform NPS
- self-service success %

---

## Service Boundaries
1. Control Plane API
2. Provisioning Engine
3. GitOps Delivery
4. Governance Layer
5. Developer Experience Layer

---

## Roadmap
### v1
- service creation
- namespace automation
- CI/CD bootstrap
- ArgoCD onboarding

### v2
- preview environments
- scorecards
- auto dashboards
- SLO templates

### v3
- Backstage integration
- multi-cloud
- policy marketplace
- Crossplane support