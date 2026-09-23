import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings
from src.database import get_sqlalchemy_dsn
from src.network.client import ResilientNetworkClient
from src.schedulers.habr_career import run_habr_career_job
from src.schedulers.hh_web import run_hh_web_job


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

    # await session.commit()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
