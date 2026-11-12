from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.network.client import ResilientNetworkClient
from src.schedulers.habr_career import run_habr_career_job
from src.schedulers.hh_web import run_hh_web_job


def init_scheduler(
    session_factory: async_sessionmaker,
    network_client: ResilientNetworkClient,
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        run_habr_career_job,
        "interval",
        hours=2,
        next_run_time=datetime.now(),
        kwargs={
            "session_factory": session_factory,
            "network_client": network_client,
        },
    )

    scheduler.add_job(
        run_hh_web_job,
        "interval",
        hours=2,
        next_run_time=datetime.now(),
        kwargs={
            "session_factory": session_factory,
            "network_client": network_client,
        },
    )

    return scheduler
