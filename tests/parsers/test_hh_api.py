from src.parsers.hh_api import parse_hh_vacancies


def test_parse_hh_vacancies_success(hh_mock_data):
    vacancies = parse_hh_vacancies(hh_mock_data)

    assert len(vacancies) == 1

    vacancies_by_link = {vacancy.link: vacancy for vacancy in vacancies}

    assert "https://hh.ru" in vacancies_by_link

    assert vacancies_by_link["https://hh.ru"].title == "Python Developer (FastAPI)"
    assert vacancies_by_link["https://hh.ru"].company_name == "HeadHunter API Team"
    assert vacancies_by_link["https://hh.ru"].salary == "150000-220000 RUR"


def test_parse_hh_vacancies_empty_or_missing_fields(hh_mock_dirty_data):
    vacancies = parse_hh_vacancies(hh_mock_dirty_data)

    assert len(vacancies) == 2

    vacancies_by_link = {vacancy.link: vacancy for vacancy in vacancies}

    assert "https://test1.ru" in vacancies_by_link

    assert vacancies_by_link["https://test1.ru"].company_name == "Компания не указана"
    assert vacancies_by_link["https://test1.ru"].salary == "Зарплата не указана"

    assert "https://test2.ru" in vacancies_by_link

    assert vacancies_by_link["https://test2.ru"].salary == "до 400000 EUR"
