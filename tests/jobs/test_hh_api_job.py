from unittest.mock import AsyncMock, Mock, patch

from sqlalchemy import select

from src.exceptions.fetcher import FetcherTimeoutError
from src.fetchers.hh_api import HH_VACANCIES_URL
from src.models.vacancy import VacancyModel
from src.schedulers.hh_api import run_hh_api_job


async def test_run_hh_api_job(db_session, hh_mock_data):
    client = AsyncMock()
    response = Mock()

    response.json.return_value = hh_mock_data
    client.get.return_value = response

    with patch("src.schedulers.hh_api.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value = client

        await run_hh_api_job(db_session)

    client.get.assert_awaited_once_with(HH_VACANCIES_URL, params={"text": "Python"})

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
        mock_fetch.side_effect = FetcherTimeoutError(
            "https://hh.ru",
            Exception("timeout"),
        )

        with patch("src.schedulers.hh_api.parse_hh_vacancies") as mock_parser:
            await run_hh_api_job(db_session)

            mock_parser.assert_not_called()
