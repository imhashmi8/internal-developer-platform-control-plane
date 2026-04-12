.PHONY: help install lint test run-control-plane run-worker up down

help:
	@echo "Available commands:"
	@echo "  make install"
	@echo "  make lint"
	@echo "  make test"
	@echo "  make run-control-plane"
	@echo "  make run-worker"
	@echo "  make up"
	@echo "  make down"

install:
	pip install -U pip
	pip install pre-commit
	cd apps/control-plane && pip install -e .
	cd workers/provisioning-worker && pip install -e .

lint:
	pre-commit run --all-files

test:
	pytest tests -v

run-control-plane:
	cd apps/control-plane && uv run --env-file ../../.env uvicorn app.main:app --reload --port 8000

run-worker:
	cd workers/provisioning-worker && python -m worker.main

up:
	docker compose -f docker-compose.dev.yml up -d

down:
	docker compose -f docker-compose.dev.yml down
