from unittest.mock import AsyncMock, Mock

from httpx import TimeoutException

from src.fetchers.habr_career import HABR_CAREER_URL, fetch_habr_career

TEST_RESPONSE_TEXT = (
    '<div class="cards-list">'
    '<div class="vacancy-card">'
    '<div class="vacancy-card__title">'
    '<a class="vacancy-card__title-link" href="/vacancies/10001">'
    "Python Developer (FastAPI)"
    "</a>"
    "</div>"
    '<div class="vacancy-card__company">'
    '<a class="vacancy-card__company-title" href="/companies/test_company">'
    "Test Company"
    "</a>"
    "</div>"
    '<div class="vacancy-card__skills">'
    '<span class="vacancy-card__skill">Python</span>'
    '<span class="vacancy-card__skill">FastAPI</span>'
    "</div>"
    '<div class="vacancy-card__salary">'
    '<span class="salary">от 150 000 ₽</span>'
    "</div>"
    "</div>"
    "</div>"
)


async def test_fetch_habr_career_success():
    client = AsyncMock()
    response = Mock()

    response.text = TEST_RESPONSE_TEXT
    client.get.return_value = response

    response_text = await fetch_habr_career(client)

    assert response_text == TEST_RESPONSE_TEXT
    client.get.assert_awaited_once_with(HABR_CAREER_URL)


async def test_fetch_habr_career_timeout():
    client = AsyncMock()

    client.get.side_effect = TimeoutException("Timeout exception")

    response_text = await fetch_habr_career(client)

    assert response_text == ""
    client.get.assert_awaited_once_with(HABR_CAREER_URL)
