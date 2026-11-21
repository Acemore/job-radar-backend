import datetime
from unittest.mock import Mock

from apscheduler.triggers.interval import IntervalTrigger

from src.network.client import ResilientNetworkClient
from src.schedulers.habr_career import run_habr_career_job
from src.schedulers.manager import init_scheduler
from src.schedulers.retention import run_data_retention_job


def test_init_scheduler():
    session_factory = Mock()
    network_client = Mock(spec=ResilientNetworkClient)
    scheduler = init_scheduler(session_factory, network_client=network_client)

    jobs = scheduler.get_jobs()

    assert len(jobs) == 3

    target_job_1 = next(
        (job for job in jobs if job.func == run_habr_career_job),
        None,
    )

    assert target_job_1 is not None

    assert target_job_1.func == run_habr_career_job
    assert target_job_1.kwargs["session_factory"] == session_factory
    assert target_job_1.kwargs["network_client"] == network_client

    assert isinstance(target_job_1.trigger, IntervalTrigger)
    assert target_job_1.trigger.interval == datetime.timedelta(hours=2)

    target_job_2 = next(
        (job for job in jobs if job.func == run_data_retention_job),
        None,
    )

    assert target_job_2 is not None

    assert target_job_2.func == run_data_retention_job
    assert target_job_2.kwargs["session_factory"] == session_factory

    assert isinstance(target_job_2.trigger, IntervalTrigger)
    assert target_job_2.trigger.interval == datetime.timedelta(hours=24)
