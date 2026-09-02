from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.schedulers.habr_career import _habr_career_job_worker
from src.schedulers.hh_api import _hh_api_job_worker


def init_scheduler(session_factory: async_sessionmaker) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        _habr_career_job_worker,
        "interval",
        hours=2,
        kwargs={"session_factory": session_factory},
    )

    scheduler.add_job(
        _hh_api_job_worker,
        "interval",
        hours=2,
        kwargs={"session_factory": session_factory},
    )

    return scheduler
