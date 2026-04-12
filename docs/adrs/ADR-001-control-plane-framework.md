# ADR-001: FastAPI as Control Plane Framework

## Status
Accepted

## Context
The platform requires:
- versioned APIs
- OpenAPI docs
- async request handling
- strong Python ecosystem
- Pydantic validation
- fast developer iteration

## Decision
Use FastAPI as the primary control-plane API framework.

## Trade-offs
Pros:
- rapid API development
- strong typing
- async support
- easy OpenAPI generation

Cons:
- Celery integration complexity
- async + sync boundary pitfalls
- team learning curve