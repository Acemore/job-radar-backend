import json
import os
from pathlib import Path

import asyncpg
import psycopg2
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.api import app
from src.database import Base, get_sqlalchemy_dsn


@pytest.fixture(scope="function")
def client(db_engine):
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
async def db_engine(test_db):
    dsn = os.environ["DATABASE_URL"]
    url = get_sqlalchemy_dsn(dsn)

    engine = create_async_engine(url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine):
    async_session = async_sessionmaker(
        db_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
def seed_vacancies(db_engine):
    dsn = os.environ["DATABASE_URL"]
    conn = psycopg2.connect(dsn)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO vacancies
        (title, company_name, salary, link, created_at)
        VALUES
        ('Python Developer', 'Google', 150000, 'https://habr.com', NOW()),
        ('FastAPI Engineer', 'Yandex', 200000, 'https://hh.ru', NOW());
    """)
    conn.commit()

    cursor.close()
    conn.close()

    yield

    conn = psycopg2.connect(dsn)
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
