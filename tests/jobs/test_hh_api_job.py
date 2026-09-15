from unittest.mock import AsyncMock, Mock, patch

import httpx
from sqlalchemy import select

from src.exceptions.fetcher import FetcherNetworkError
from src.fetchers.hh_api import HH_VACANCIES_URL
from src.models.vacancy import VacancyModel
from src.schedulers.hh_api import run_hh_api_job


async def test_run_hh_api_job(db_session, hh_mock_data):
    client = AsyncMock()
    response = Mock()

    response.json.return_value = hh_mock_data
    client.make_request.return_value = response

    with patch("src.schedulers.hh_api.ResilientNetworkClient") as mock_client:
        mock_client.return_value = client

        await run_hh_api_job(db_session)

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

    assert len(db_vacancies) == 1

    vacancies_by_link = {vacancy.link: vacancy for vacancy in db_vacancies}

    assert "https://hh.ru" in vacancies_by_link

    target_vacancy = vacancies_by_link["https://hh.ru"]

    assert target_vacancy.title == "Python Developer (FastAPI)"
    assert target_vacancy.company_name == "HeadHunter API Team"
    assert target_vacancy.salary == "150000-220000 RUR"
    assert target_vacancy.link == "https://hh.ru"


async def test_run_hh_api_job_fetcher_error(db_session):
    with patch(
        "src.schedulers.hh_api.fetch_hh_vacancies",
        new_callable=AsyncMock,
    ) as mock_fetch:
        fake_network_error = httpx.ConnectError("Network dead")
        mock_fetch.side_effect = FetcherNetworkError(
            "Network failure", original_exception=fake_network_error
        )

        with patch("src.schedulers.hh_api.parse_hh_vacancies") as mock_parser:
            await run_hh_api_job(db_session)

            mock_parser.assert_not_called()
