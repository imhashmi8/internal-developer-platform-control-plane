# Multi-Tenant Platform Design, RBAC & Environment Isolation

## Tenant Model
A tenant maps to an engineering team.

Example:
- checkout
- payments
- search
- platform-core

Each tenant owns:
- services
- namespaces
- secrets
- dashboards
- scorecards
- runbooks
- preview environments

---

## Namespace Strategy
Convention:

```text
<team>-<service>-<environment>