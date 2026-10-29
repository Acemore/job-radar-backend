.PHONY: db-reset db-migrate upgrade

db-reset:
	@echo "=== Dropping and recreating database architecture ==="
	docker compose exec -T postgres dropdb -U postgres --if-exists job_radar
	docker compose exec -T postgres createdb -U postgres job_radar
	uv run alembic upgrade head
	@echo "=== Database successfully sterilized and migrated ==="

db-migrate:
	@echo "=== Generating automated database revision script ==="
	uv run alembic revision --autogenerate -m "auto_migration"
	@echo "=== Revision script successfully compiled inside versions/ ==="

upgrade: ## Upgrade lockfile dependencies and sync virtual environment
	uv lock --upgrade
	uv sync
	uv run pre-commit run --all-files
