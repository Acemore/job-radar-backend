from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from src.models.vacancy import VacancyModel
from src.schedulers.retention import run_data_retention_job


async def test_run_retention_job(db_session):
    fresh_vacancy = VacancyModel(
        title="Senior Python Backend Developer",
        company_name="TechFlow",
        salary="250 000 - 320 000 ₽",
        link="https://habr.com",
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )

    old_vacancy = VacancyModel(
        title="Legacy Python Support",
        company_name="OldCorp",
        salary="120 000 ₽",
        link="https://hh.ru",
        created_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=35),
    )

    db_session.add_all([fresh_vacancy, old_vacancy])
    await db_session.commit()

    @asynccontextmanager
    async def fake_session_factory():
        yield db_session

    await run_data_retention_job(session_factory=fake_session_factory, ttl_days=30)

    db_vacancies_object = await db_session.execute(select(VacancyModel))
    db_vacancies = db_vacancies_object.scalars().all()

    assert len(db_vacancies) == 1
    assert db_vacancies[0].link == "https://habr.com"
