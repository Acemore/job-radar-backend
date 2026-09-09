import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from src.config import settings
from src.database import Base, get_sqlalchemy_dsn
from src.models.vacancy import VacancyModel  # noqa: F401


async def main():
    database_url = get_sqlalchemy_dsn(settings.DATABASE_URL)

    engine = create_async_engine(database_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(main())
