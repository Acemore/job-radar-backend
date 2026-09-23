import structlog
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.exceptions.fetcher import FetcherError
from src.fetchers.hh_web import fetch_hh_vacancies
from src.network.client import ResilientNetworkClient
from src.parsers.hh_web import parse_hh_vacancies
from src.repositories.vacancy import VacancyRepository

logger = structlog.get_logger()


async def run_hh_web_job(
    session_factory: async_sessionmaker, network_client: ResilientNetworkClient
):
    try:
        html_text = await fetch_hh_vacancies(network_client, "Python")
    except FetcherError as e:
        logger.error("hh_web_job_failed", error=str(e), exc_info=True)
        return

    dto_vacancies = parse_hh_vacancies(html_text)

    if not dto_vacancies:
        logger.info("hh_web_job_no_vacancies_found")
        return

    async with session_factory() as session:
        repo = VacancyRepository(session)
        await repo.create_many(dto_vacancies)
        await session.commit()
