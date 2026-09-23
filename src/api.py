from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlparse

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings
from src.database import get_session, get_sqlalchemy_dsn
from src.logger import configure_logging
from src.network.routing import NetworkNodeDTO, RoundRobinNodeProvider
from src.repositories.vacancy import VacancyRepository
from src.schedulers.manager import init_scheduler
from src.schemas import VacancyDTO, VacancyResponse

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    database_url = get_sqlalchemy_dsn(settings.DATABASE_URL)

    engine = create_async_engine(database_url)
    app.state.engine = engine

    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    app.state.session_factory = session_factory

    project_root = Path(__file__).resolve().parent.parent
    nodes_path = project_root / settings.NETWORK_NODES_FILE

    nodes = []

    if nodes_path.exists():
        content = nodes_path.read_text(encoding="utf-8").strip()
        raw_urls = content.splitlines() if content else []

        for raw_url in raw_urls:
            raw_url = raw_url.strip()
            if not raw_url:
                continue

            parsed_url = urlparse(raw_url)
            if not parsed_url.hostname or not parsed_url.port:
                continue

            node = NetworkNodeDTO(
                protocol=parsed_url.scheme,
                host=parsed_url.hostname,
                port=parsed_url.port,
            )

            nodes.append(node)

    node_provider = RoundRobinNodeProvider(nodes=nodes) if nodes else None

    scheduler = init_scheduler(session_factory, node_provider=node_provider)
    if not getattr(app.state, "disable_scheduler_start", False):
        scheduler.start()
    app.state.scheduler = scheduler

    yield

    if scheduler.running:
        scheduler.shutdown()

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
