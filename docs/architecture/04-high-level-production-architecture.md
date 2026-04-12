# High-Level Production Architecture Blueprint

## System Layers

### 1) Developer Experience Layer
Interfaces used by internal teams:
- CLI (`idpctl`)
- developer portal integration
- GitHub app/webhooks
- future UI dashboard

---

### 2) Control Plane Layer
Core orchestration APIs:
- FastAPI service
- authentication / RBAC
- OpenAPI docs
- audit APIs
- service scorecards
- promotion APIs
- rollback APIs

---

### 3) Workflow Orchestration Layer
Background automation:
- Celery workers
- Redis queue
- retry handling
- idempotent task execution
- failure recovery
- webhook dispatchers

---

### 4) Platform State Layer
Persistent platform metadata:
- PostgreSQL
- service catalog
- team ownership
- environments
- lifecycle states
- scorecards
- audit logs

---

### 5) Provisioning Layer
Infrastructure automation:
- Terraform modules
- reusable workspaces
- namespace module
- IAM module
- secrets module
- DB module
- DNS module

---

### 6) GitOps Delivery Layer
Continuous delivery:
- GitOps repo
- ArgoCD app-of-apps
- Argo Rollouts
- Helm charts
- promotion manifests
- rollback manifests

---

### 7) Runtime Platform Layer
Cluster runtime:
- EKS
- namespaces
- workloads
- services
- ingress
- External Secrets
- service accounts
- network policies

---

### 8) Governance & Reliability Layer
Production controls:
- OPA / Kyverno
- Prometheus
- Grafana
- alert routing
- SLO templates
- incident webhooks
- runbook links


## Logical System Flow

```text
Developer / CLI / Portal
            ↓
     FastAPI Control Plane
            ↓
 ┌──────────┼──────────┐
 ↓          ↓          ↓
Postgres   Redis     Celery
  ↓          ↓          ↓
Platform   Job Queue  Workflow Engine
  State
            ↓
    Terraform Modules
            ↓
      GitOps Repository
            ↓
         ArgoCD
            ↓
      EKS Kubernetes
            ↓
Grafana + Prometheus + Policies
```

## Scaling Assumptions

Designed to support:
- 200+ engineering teams
- 1000+ services
- multi-environment deployments
- 100+ daily provisioning workflows
- preview environment burst traffic
- multi-cluster expansion
- future multi-cloud control plane

Key scale boundaries:
- stateless FastAPI horizontal scaling
- Celery worker autoscaling
- Redis HA
- PostgreSQL read replicas
- GitOps repo sharding