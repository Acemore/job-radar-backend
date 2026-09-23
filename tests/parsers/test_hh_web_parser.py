import pytest

from src.parsers.hh_web import DEFAULT_COMPANY_NAME, DEFAULT_SALARY, parse_hh_vacancies
from src.schemas.vacancy import VacancyDTO


def test_parse_hh_vacancies_success(hh_mock_data):
    vacancies = parse_hh_vacancies(hh_mock_data)

    assert len(vacancies) == 3
    assert all(isinstance(vacancy, VacancyDTO) for vacancy in vacancies)

    vacancies_by_link = {vacancy.link: vacancy for vacancy in vacancies}

    first_vacancy = vacancies_by_link.get("https://hh.ru/vacancy/137527751")
    assert first_vacancy is not None
    assert first_vacancy.title == "Python Developer (FastAPI)"
    assert first_vacancy.company_name == "HeadHunter Web Team"
    assert first_vacancy.salary == "150000-220000 RUR"

    second_vacancy = vacancies_by_link.get("https://hh.ru/vacancy/137546518")
    assert second_vacancy is not None
    assert second_vacancy.title == "Fullstack-разработчик"
    assert second_vacancy.company_name == "FAIR-METALL"
    assert second_vacancy.salary == "от 8000000 UZS"

    third_vacancy = vacancies_by_link.get("https://hh.ru/vacancy/137533168")
    assert third_vacancy is not None
    assert third_vacancy.title == "DevOps Engineer"
    assert third_vacancy.company_name == "Водород"
    assert third_vacancy.salary == DEFAULT_SALARY


@pytest.mark.parametrize(
    "empty_html", ["", "<html><body></body></html>", "<div>No vacancies here</div>"]
)
def test_parse_hh_vacancies_no_results(empty_html):
    vacancies = parse_hh_vacancies(empty_html)
    assert len(vacancies) == 0


def test_parse_hh_vacancies_empty_or_missing_fields(hh_mock_dirty_data):
    vacancies = parse_hh_vacancies(hh_mock_dirty_data)

    assert len(vacancies) == 2
    assert all(isinstance(vacancy, VacancyDTO) for vacancy in vacancies)

    vacancies_by_link = {vacancy.link: vacancy for vacancy in vacancies}

    v_missing = vacancies_by_link.get("https://hh.ru/vacancy/999999")
    assert v_missing is not None
    assert v_missing.company_name == DEFAULT_COMPANY_NAME
    assert v_missing.salary == DEFAULT_SALARY

    v_partial = vacancies_by_link.get("https://hh.ru/vacancy/888888")
    assert v_partial is not None
    assert v_partial.company_name == DEFAULT_COMPANY_NAME
    assert v_partial.salary == "до 400000"
