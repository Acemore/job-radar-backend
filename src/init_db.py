import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

from src.database import Base, get_sqlalchemy_dsn
from src.models.vacancy import VacancyModel  # noqa: F401

load_dotenv()


async def main():
    dsn = os.environ["DATABASE_URL"]
    database_url = get_sqlalchemy_dsn(dsn)

    engine = create_async_engine(database_url)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(main())
