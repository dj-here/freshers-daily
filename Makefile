.PHONY: help install up down test lint migrate seed run-daily dry-run

help:
	@echo "FreshersDaily commands:"
	@echo "  make up          - Start docker containers"
	@echo "  make down        - Stop docker containers"
	@echo "  make test        - Run backend test suite"
	@echo "  make migrate     - Run database migrations"
	@echo "  make seed        - Seed 150+ Indian tech companies"
	@echo "  make dry-run     - Run end-to-end dry-run daily selection"

up:
	docker compose up -d

down:
	docker compose down

test:
	cd backend && pytest -v

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m app.cli seed --companies

dry-run:
	cd backend && python -m app.cli run-daily --dry-run
