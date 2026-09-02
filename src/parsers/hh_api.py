from src.parsers.constants import (
    DEFAULT_COMPANY_NAME,
    DEFAULT_LINK,
    DEFAULT_SALARY,
    DEFAULT_VACANCY_TITLE,
)
from src.schemas import VacancyDTO


def parse_hh_vacancies(response_data: dict) -> list[VacancyDTO]:
    raw_vacancies = response_data.get("items", [])
    vacancies = []

    for raw_vacancy in raw_vacancies:
        title = raw_vacancy.get("name", DEFAULT_VACANCY_TITLE)
        company_name = raw_vacancy.get("employer", {}).get("name", DEFAULT_COMPANY_NAME)
        link = raw_vacancy.get("alternate_url", DEFAULT_LINK)

        salary_node = raw_vacancy.get("salary")
        if not salary_node:
            salary = DEFAULT_SALARY
        else:
            salary_floor = salary_node.get("from")
            salary_ceil = salary_node.get("to")
            salary_currency = salary_node.get("currency", "")

            if not salary_floor and not salary_ceil:
                salary = DEFAULT_SALARY
            elif not salary_floor:
                salary = f"до {salary_ceil} {salary_currency}"
            elif not salary_ceil:
                salary = f"от {salary_floor} {salary_currency}"
            else:
                salary = f"{salary_floor}-{salary_ceil} {salary_currency}"

        vacancy = VacancyDTO(
            title=title, company_name=company_name, link=link, salary=salary
        )

        vacancies.append(vacancy)

    return vacancies
