.PHONY: db-reset db-migrate

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
