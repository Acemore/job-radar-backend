import os
from contextlib import asynccontextmanager

import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, Request

from .db_manager import get_vacancies
from .schemas import VacancyResponse

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    dsn = os.environ["DATABASE_URL"]

    async with asyncpg.create_pool(dsn) as pool:
        app.state.pool = pool
        yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check() -> dict:
    return {"status": "OK"}


@app.get("/api/vacancies", response_model=list[VacancyResponse])
async def get_all_vacancies(request: Request) -> list[VacancyResponse]:
    pool = request.app.state.pool

    raw_vacancies = await get_vacancies(pool)

    return [VacancyResponse(**vacancy) for vacancy in raw_vacancies]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.api:app", host="127.0.0.1", port=8000, reload=True)
