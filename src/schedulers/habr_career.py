import structlog
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.exceptions.fetcher import FetcherError
from src.fetchers.habr_career import fetch_habr_career
from src.network.client import ResilientNetworkClient
from src.parsers.habr_career import parse_habr_vacancies
from src.repositories.vacancy import VacancyRepository

logger = structlog.get_logger()


async def run_habr_career_job(
    session_factory: async_sessionmaker, network_client: ResilientNetworkClient
):
    try:
        html_text = await fetch_habr_career(network_client)
    except FetcherError as e:
        logger.error("habr_career_job_failed", error=str(e), exc_info=True)
        return

    dto_vacancies = parse_habr_vacancies(html_text)

    if not dto_vacancies:
        logger.info("habr_career_job_no_vacancies_found")
        return

    async with session_factory() as session:
        repo = VacancyRepository(session)
        await repo.create_many(dto_vacancies)
        await session.commit()
