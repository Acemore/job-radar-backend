import pytest


@pytest.fixture
def mock_vacancy_full():
    return """
    <div class="vacancy-card">
        <div class="vacancy-card__title">
            <a href="/vacancies/10000123">Senior Python Developer</a>
        </div>
        <div class="vacancy-card__company-title">
            <a href="/companies/cyber_core">Cyber Core Tech</a>
        </div>
        <div class="vacancy-card__title-line">
            <div class="salary">
                от&nbsp;250&nbsp;000&nbsp;до&nbsp;350&nbsp;000&nbsp;₽
            </div>
        </div>
    </div>
    """


@pytest.fixture
def mock_vacancy_alternative():
    return """
    <div class="vacancy-card">
        <div class="vacancy-card__title">
            <a href="/vacancies/999999">Frontend Engineer (React)</a>
        </div>
        <div class="vacancy-card__company">ООО Рога и Копыта</div>
        <div class="vacancy-card__salary">до 4 000 $</div>
    </div>
    """


@pytest.fixture
def mock_vacancy_empty():
    return """
    <div class="vacancy-card">
        <div class="vacancy-card__title">
            <a>Анонимная вакансия</a>
        </div>
    </div>
    """


@pytest.fixture(scope="session")
def hh_mock_dirty_data() -> dict:
    return {
        "items": [
            {
                "id": "999999",
                "name": "Python Developer",
                "employer": {},
                "salary": None,
                "alternate_url": "https://test1.ru",
            },
            {
                "id": "888888",
                "name": "Senior FastAPI Engineer",
                "employer": {"name": "Mishka Tech"},
                "salary": {"from": None, "to": 400000, "currency": "EUR"},
                "alternate_url": "https://test2.ru",
            },
        ]
    }
