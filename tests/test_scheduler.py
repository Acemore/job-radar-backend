import datetime
from unittest.mock import Mock

from apscheduler.triggers.interval import IntervalTrigger

from src.network.client import ResilientNetworkClient
from src.schedulers.habr_career import run_habr_career_job
from src.schedulers.manager import init_scheduler


def test_init_scheduler():
    session_factory = Mock()
    network_client = Mock(spec=ResilientNetworkClient)
    scheduler = init_scheduler(session_factory, network_client=network_client)

    jobs = scheduler.get_jobs()

    assert len(jobs) == 2

    target_job = next(
        (job for job in jobs if job.func == run_habr_career_job),
        None,
    )

    assert target_job is not None

    assert target_job.func == run_habr_career_job
    assert target_job.kwargs["session_factory"] == session_factory
    assert target_job.kwargs["network_client"] == network_client

    assert isinstance(target_job.trigger, IntervalTrigger)
    assert target_job.trigger.interval == datetime.timedelta(hours=2)
