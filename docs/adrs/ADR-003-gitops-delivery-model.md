# ADR-003: GitOps App-of-Apps Delivery Model

## Status
Accepted

## Context
Platform requires:
- auditability
- rollback safety
- declarative cluster state
- multi-environment overlays

## Decision
Use ArgoCD app-of-apps with Git as source of truth.

## Trade-offs
Pros:
- safe rollbacks
- compliance traceability
- declarative promotion

Cons:
- repo complexity
- manifest sprawl
- sync debugging overhead