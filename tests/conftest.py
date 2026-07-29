import os

import asyncpg
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from src.api import app

load_dotenv()


@pytest.fixture(scope="function")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
async def test_db():
    dsn = os.environ["DATABASE_URL"]
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
            sala INTEGER,
            description TEXT,
            created_at TIMESTAMPTZ NOT NULL
        );
    """)
    await test_conn.close()

    yield

    conn = await asyncpg.connect(dsn)
    await conn.execute("DROP DATABASE IF EXISTS job_radar_test;")
    await conn.close()


@pytest.fixture(scope="function", autouse=True)
async def db_pool(test_db):
    dsn = os.environ["DATABASE_URL"]
    base_dsn, _ = dsn.rsplit("/", 1)
    test_dsn = f"{base_dsn}/job_radar_test"

    pool = await asyncpg.create_pool(test_dsn)
    app.state.pool = pool

    yield pool

    await pool.close()
