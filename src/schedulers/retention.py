import structlog
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.config import settings
from src.repositories.vacancy import VacancyRepository

logger = structlog.get_logger()


async def run_data_retention_job(
    session_factory: async_sessionmaker, ttl_days: int | None = None
) -> None:
    effective_ttl = ttl_days if ttl_days is not None else settings.VACANCY_TTL_DAYS

    async with session_factory() as session:
        repo = VacancyRepository(session)
        deleted_count = await repo.delete_older_than(effective_ttl)
        await session.commit()

        logger.info(
            "data_retention_job_completed",
            deleted_count=deleted_count,
            ttl_days=effective_ttl,
        )
