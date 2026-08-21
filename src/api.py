import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database import get_session, get_sqlalchemy_dsn
from src.repositories.vacancy import VacancyRepository
from src.schemas import VacancyDTO, VacancyResponse

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    dsn = os.environ["DATABASE_URL"]
    database_url = get_sqlalchemy_dsn(dsn)

    engine = create_async_engine(database_url)
    app.state.engine = engine

    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    app.state.session_factory = session_factory

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "OK"}


@app.get("/api/vacancies", response_model=list[VacancyResponse])
async def get_all_vacancies(
    session: AsyncSession = Depends(get_session),
) -> list[VacancyDTO]:
    repository = VacancyRepository(session)

    return await repository.get_all()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
