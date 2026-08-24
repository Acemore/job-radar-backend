import datetime
from unittest.mock import Mock

from apscheduler.triggers.interval import IntervalTrigger

from src.schedulers.habr_career import _habr_career_job_worker, init_scheduler


def test_init_scheduler():
    session_factory = Mock()
    scheduler = init_scheduler(session_factory)

    jobs = scheduler.get_jobs()

    assert len(jobs) == 1

    target_job = next(
        (job for job in jobs if job.func == _habr_career_job_worker),
        None,
    )

    assert target_job is not None

    assert target_job.func == _habr_career_job_worker
    assert target_job.kwargs["session_factory"] == session_factory

    assert isinstance(target_job.trigger, IntervalTrigger)
    assert target_job.trigger.interval == datetime.timedelta(hours=2)
