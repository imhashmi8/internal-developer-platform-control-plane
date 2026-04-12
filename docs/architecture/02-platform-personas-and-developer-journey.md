# Platform Users, Personas & Developer Journey

## Primary Platform Users

### 1) Application Developers
Goals:
- create new services fast
- reduce infrastructure tickets
- self-service preview environments
- promote safely across environments
- access dashboards and runbooks

Pain points:
- repetitive setup
- unclear deployment standards
- missing observability defaults
- slow namespace creation
- manual IAM requests

---

### 2) Platform Engineers
Goals:
- reusable golden paths
- consistent infra provisioning
- standard CI/CD
- environment governance
- scalable self-service workflows

Pain points:
- repeated onboarding tickets
- inconsistent service patterns
- policy drift
- difficult ownership tracking

---

### 3) SRE / Reliability Team
Goals:
- default SLOs
- standardized alerts
- rollback workflows
- service maturity scorecards

Pain points:
- missing probes
- no runbooks
- inconsistent alert labels
- weak ownership metadata

---

### 4) Security / Governance
Goals:
- mandatory controls
- audit trails
- release approvals
- policy evidence

Pain points:
- missing labels
- secret sprawl
- unverified images
- weak compliance visibility

---

## Developer Journey

### Day 0 — Service Creation
Developer runs:
```bash
idpctl create-service payments-api --template fastapi --env dev