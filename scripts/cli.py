import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings
from src.database import get_sqlalchemy_dsn
from src.network.client import ResilientNetworkClient
from src.repositories.vacancy import VacancyRepository
from src.schedulers.habr_career import run_habr_career_job
from src.schedulers.hh_web import run_hh_web_job
from src.utils.analytics import calculate_salary_breakdown, parse_salary_to_numeric


async def main():
    database_url = get_sqlalchemy_dsn(settings.DATABASE_URL)

    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    client = ResilientNetworkClient()

    await run_habr_career_job(session_factory, client)
    await run_hh_web_job(session_factory, client)

    async with session_factory() as session:
        repo = VacancyRepository(session)
        vacancies = await repo.get_all()

        clean_salaries = [
            num_salary
            for v in vacancies
            if (num_salary := parse_salary_to_numeric(v.salary)) is not None
        ]

    stats = calculate_salary_breakdown(clean_salaries)

    if not stats:
        print("Insufficient data to calculate salaries")
    else:
        print(f"Min salary: {stats['min_salary']} RUB")
        print(f"Max salary: {stats['max_salary']} RUB")
        print(f"Avg salary: {stats['avg_salary']} RUB")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
