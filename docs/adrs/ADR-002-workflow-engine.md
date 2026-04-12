# ADR-002: Celery + Redis as Workflow Engine

## Status
Accepted

## Context
Provisioning tasks are long-running:
- Terraform apply
- GitHub bootstrap
- ArgoCD app creation
- dashboard generation

## Decision
Use Celery workers with Redis queue.

## Trade-offs
Pros:
- proven ecosystem
- simple operational model
- retry support
- Python-native

Cons:
- weaker workflow visibility than Temporal
- distributed debugging complexity
- queue durability concerns