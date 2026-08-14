import json
import os
from pathlib import Path

import asyncpg
import psycopg2
import pytest
from fastapi.testclient import TestClient

from src.api import app


@pytest.fixture(scope="function")
def client(test_db):
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
async def test_db():
    dsn = os.environ["DATABASE_URL"]
    if not dsn:
        raise RuntimeError("DATABASE_URL variable is not set in environment")

    base_dsn, _ = dsn.rsplit("/", 1)
    test_dsn = f"{base_dsn}/job_radar_test"

    conn = await asyncpg.connect(dsn)
    await conn.execute("DROP DATABASE IF EXISTS job_radar_test;")
    await conn.execute("CREATE DATABASE job_radar_test;")
    await conn.close()

    test_conn = await asyncpg.connect(test_dsn)
    await test_conn.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            company_name VARCHAR(255) NOT NULL,
            salary INTEGER,
            description TEXT,
            created_at TIMESTAMPTZ NOT NULL
        );
    """)
    await test_conn.execute("""
        CREATE TABLE IF NOT EXISTS candidate_background (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            body TEXT NOT NULL,
            comments JSONB NOT NULL DEFAULT '[]'::jsonb
        );
    """)
    await test_conn.close()

    os.environ["DATABASE_URL"] = test_dsn

    yield test_dsn

    os.environ["DATABASE_URL"] = dsn

    conn = await asyncpg.connect(dsn)
    await conn.execute("""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = 'job_radar_test'
          AND pid <> pg_backend_pid();
    """)
    await conn.execute("DROP DATABASE IF EXISTS job_radar_test;")
    await conn.close()


@pytest.fixture(scope="function")
def seed_vacancies(test_db):
    conn = psycopg2.connect(test_db)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO vacancies
        (title, company_name, salary, description, created_at)
        VALUES
        ('Python Developer', 'Google', 150000, 'Great job', NOW()),
        ('FastAPI Engineer', 'Yandex', 200000, 'Async power', NOW());
    """)
    conn.commit()

    cursor.close()
    conn.close()

    yield

    conn = psycopg2.connect(test_db)
    cursor = conn.cursor()

    cursor.execute("TRUNCATE TABLE vacancies RESTART IDENTITY;")
    conn.commit()

    cursor.close()
    conn.close()


@pytest.fixture(scope="function")
def github_mock_data():
    tests_dir_path = Path(__file__).parent

    with open(
        f"{tests_dir_path}/fixtures/github_mock.json",
        "r",
        encoding="utf-8",
    ) as f:
        raw_data = f.read()
    data = json.loads(raw_data)

    yield data
