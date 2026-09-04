import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database import get_sqlalchemy_dsn
from src.schedulers.habr_career import run_habr_career_job
from src.schedulers.hh_api import run_hh_api_job

load_dotenv()


async def main():
    dsn = os.environ["DATABASE_URL"]
    database_url = get_sqlalchemy_dsn(dsn)

    engine = create_async_engine(database_url)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with session_factory() as session:
        await run_habr_career_job(session)
        await run_hh_api_job(session)

        await session.commit()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
