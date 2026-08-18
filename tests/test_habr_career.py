import pytest

from src.parsers.habr_career import parse_habr_vacancies


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


def test_parse_full_vacancy(mock_vacancy_full):
    vacancies = parse_habr_vacancies(mock_vacancy_full)

    assert len(vacancies) == 1

    vacancy = vacancies[0]

    assert vacancy.title == "Senior Python Developer"
    assert vacancy.company_name == "Cyber Core Tech"
    assert vacancy.salary == "от 250 000 до 350 000 ₽"
    assert vacancy.link == "https://career.habr.com/vacancies/10000123"


def test_parse_alternative_vacancy(mock_vacancy_alternative):
    vacancies = parse_habr_vacancies(mock_vacancy_alternative)

    assert len(vacancies) == 1

    vacancy = vacancies[0]

    assert vacancy.title == "Frontend Engineer (React)"
    assert vacancy.company_name == "ООО Рога и Копыта"
    assert vacancy.salary == "до 4 000 $"
    assert vacancy.link == "https://career.habr.com/vacancies/999999"


def test_parse_empty_vacancy(mock_vacancy_empty):
    vacancies = parse_habr_vacancies(mock_vacancy_empty)

    assert len(vacancies) == 1

    vacancy = vacancies[0]

    assert vacancy.title == "Анонимная вакансия"
    assert vacancy.company_name == "Компания не указана"
    assert vacancy.salary == "Зарплата не указана"
    assert vacancy.link == "Ссылка отсутствует"


def test_parse_multiple_vacancies(mock_vacancy_full, mock_vacancy_alternative):
    multiple_html = mock_vacancy_full + mock_vacancy_alternative

    vacancies = parse_habr_vacancies(multiple_html)

    assert len(vacancies) == 2

    assert vacancies[0].title == "Senior Python Developer"
    assert vacancies[0].link == "https://career.habr.com/vacancies/10000123"

    assert vacancies[1].title == "Frontend Engineer (React)"
    assert vacancies[1].company_name == "ООО Рога и Копыта"
