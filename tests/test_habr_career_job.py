from unittest.mock import AsyncMock, Mock, patch

from sqlalchemy import select
from test_habr_career_fetcher import TEST_RESPONSE_TEXT

from src.fetchers.habr_career import HABR_CAREER_URL
from src.models.vacancy import VacancyModel
from src.schedulers.habr_career import run_habr_career_job


async def test_run_habr_career_job(db_session):
    client = AsyncMock()
    response = Mock()

    response.text = TEST_RESPONSE_TEXT
    client.get.return_value = response

    with patch("src.schedulers.habr_career.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value = client

        await run_habr_career_job(db_session)

    client.get.assert_awaited_once_with(HABR_CAREER_URL)

    db_vacancies_object = await db_session.execute(select(VacancyModel))
    db_vacancies = db_vacancies_object.scalars().all()

    assert len(db_vacancies) == 1

    vacancies_by_link = {vacancy.link: vacancy for vacancy in db_vacancies}

    assert "https://career.habr.com/vacancies/10001" in vacancies_by_link

    target_vacancy = vacancies_by_link["https://career.habr.com/vacancies/10001"]

    assert target_vacancy.title == "Python Developer (FastAPI)"
    assert target_vacancy.company_name == "Test Company"
    assert target_vacancy.salary == "от 150 000 ₽"
    assert target_vacancy.link == "https://career.habr.com/vacancies/10001"
