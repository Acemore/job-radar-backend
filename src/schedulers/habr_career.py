import logging

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.exceptions.fetcher import FetcherError
from src.fetchers.habr_career import fetch_habr_career
from src.parsers.habr_career import parse_habr_vacancies
from src.repositories.vacancy import VacancyRepository

logger = logging.getLogger(__name__)


async def run_habr_career_job(session: AsyncSession):
    async with AsyncClient() as client:
        try:
            html_text = await fetch_habr_career(client)
        except FetcherError as e:
            logger.error(
                "Failed to run Habr Career job due to network error: %s",
                e,
                exc_info=True,
            )

            return

    dto_vacancies = parse_habr_vacancies(html_text)

    repo = VacancyRepository(session)
    await repo.create_many(dto_vacancies)


async def _habr_career_job_worker(session_factory: async_sessionmaker):
    async with session_factory() as session:
        await run_habr_career_job(session)
