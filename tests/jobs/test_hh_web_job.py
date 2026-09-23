from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, Mock, patch

import httpx
from sqlalchemy import select

from src.exceptions.fetcher import FetcherNetworkError
from src.fetchers.hh_web import HH_VACANCIES_URL
from src.models.vacancy import VacancyModel
from src.schedulers.hh_web import run_hh_web_job


async def test_run_hh_web_job(db_session, hh_mock_data):
    client = AsyncMock()
    response = Mock()

    response.text = hh_mock_data
    client.make_request.return_value = response

    with patch("src.schedulers.hh_web.ResilientNetworkClient") as mock_client:
        mock_client.return_value = client

        @asynccontextmanager
        async def fake_session_factory():
            yield db_session

        await run_hh_web_job(
            session_factory=fake_session_factory, network_client=client
        )

    client.make_request.assert_awaited_once_with(
        HH_VACANCIES_URL,
        params={"text": "Python"},
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            )
        },
    )

    db_vacancies_object = await db_session.execute(select(VacancyModel))
    db_vacancies = db_vacancies_object.scalars().all()

    assert len(db_vacancies) == 3

    vacancies_by_link = {vacancy.link: vacancy for vacancy in db_vacancies}

    target_vacancy = vacancies_by_link.get("https://hh.ru/vacancy/137527751")
    assert target_vacancy is not None
    assert target_vacancy.title == "Python Developer (FastAPI)"
    assert target_vacancy.company_name == "HeadHunter Web Team"
    assert target_vacancy.salary == "150000-220000 RUR"


async def test_run_hh_web_job_fetcher_error(db_session):
    with patch(
        "src.schedulers.hh_web.fetch_hh_vacancies",
        new_callable=AsyncMock,
    ) as mock_fetch:
        fake_network_error = httpx.ConnectError("Network dead")
        mock_fetch.side_effect = FetcherNetworkError(
            "Network failure", original_exception=fake_network_error
        )

        with patch("src.schedulers.hh_web.parse_hh_vacancies") as mock_parser:

            @asynccontextmanager
            async def fake_session_factory():
                yield db_session

            client = AsyncMock()

            await run_hh_web_job(
                session_factory=fake_session_factory, network_client=client
            )

            mock_parser.assert_not_called()
