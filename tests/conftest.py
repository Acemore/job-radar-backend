import json
import os
from pathlib import Path

import asyncpg
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.api import app
from src.database import Base, get_sqlalchemy_dsn
from src.models.vacancy import VacancyModel


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
async def seed_vacancies(db_session):
    first_vacancy = VacancyModel(
        title="Python Developer",
        company_name="Google",
        salary="150000",
        link="https://habr.com",
    )
    second_vacancy = VacancyModel(
        title="FastAPI Engineer",
        company_name="Yandex",
        salary="200000",
        link="https://hh.ru",
    )
    vacancies = [first_vacancy, second_vacancy]

    db_session.add_all(vacancies)
    await db_session.commit()

    yield

    await db_session.execute(delete(VacancyModel))
    await db_session.commit()


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


@pytest.fixture(scope="session")
def habr_mock_html() -> str:
    return (
        '<div class="cards-list">'
        '<div class="vacancy-card">'
        '<div class="vacancy-card__title">'
        '<a class="vacancy-card__title-link" href="/vacancies/10001">'
        "Python Developer (FastAPI)"
        "</a>"
        "</div>"
        '<div class="vacancy-card__company">'
        '<a class="vacancy-card__company-title" href="/companies/test_company">'
        "Test Company"
        "</a>"
        "</div>"
        '<div class="vacancy-card__skills">'
        '<span class="vacancy-card__skill">Python</span>'
        '<span class="vacancy-card__skill">FastAPI</span>'
        "</div>"
        '<div class="vacancy-card__salary">'
        '<span class="salary">от 150 000 ₽</span>'
        "</div>"
        "</div>"
        "</div>"
    )


@pytest.fixture(scope="session")
def hh_mock_data() -> dict:
    return {
        "items": [
            {
                "id": "105673892",
                "name": "Python Developer (FastAPI)",
                "salary": {
                    "from": 150000,
                    "to": 220000,
                    "currency": "RUR",
                    "gross": False,
                },
                "employer": {"id": "1455", "name": "HeadHunter API Team"},
                "schedule": {"id": "remote", "name": "Удаленная работа"},
                "employment": {"id": "full", "name": "Полная занятость"},
                "alternate_url": "https://hh.ru",
            }
        ],
        "found": 1,
        "pages": 1,
        "per_page": 20,
        "page": 0,
    }
