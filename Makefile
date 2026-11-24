.PHONY: db-reset db-migrate upgrade typecheck clean

db-reset:
	@echo "=== Dropping and recreating database architecture ==="
	docker compose exec -T db dropdb -U postgres --if-exists job_radar
	docker compose exec -T db createdb -U postgres job_radar
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

typecheck: ## Run static typing check via mypy daemon
	uv run dmypy run -- --config-file pyproject.toml .

clean: ## Clear python, pytest, ruff, mypy cache
	find . -type d -name "__pycache__" -not -path "./.venv/*" -exec rm -rf {} +
	uv run dmypy stop || true
	rm -rf .pytest_cache .ruff_cache .mypy_cache .dmypy.json
