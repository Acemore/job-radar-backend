import logging

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.exceptions.fetcher import FetcherError
from src.fetchers.hh_api import fetch_hh_vacancies
from src.parsers.hh_api import parse_hh_vacancies
from src.repositories.vacancy import VacancyRepository

logger = logging.getLogger(__name__)


async def run_hh_api_job(session: AsyncSession):
    async with AsyncClient() as client:
        try:
            response_data = await fetch_hh_vacancies(client, "Python")
        except FetcherError as e:
            logger.error(
                "Failed to run HeadHunter API job due to network error: %s",
                e,
                exc_info=True,
            )

            return

    dto_vacancies = parse_hh_vacancies(response_data)

    repo = VacancyRepository(session)
    await repo.create_many(dto_vacancies)


async def _hh_api_job_worker(session_factory: async_sessionmaker):
    async with session_factory() as session:
        await run_hh_api_job(session)
