import json

from selectolax.lexbor import LexborHTMLParser

from src.parsers.constants import (
    DEFAULT_COMPANY_NAME,
    # DEFAULT_LINK,
    DEFAULT_SALARY,
    DEFAULT_VACANCY_TITLE,
)
from src.schemas import VacancyDTO


def parse_hh_vacancies(html_text: str) -> list[VacancyDTO]:
    parser = LexborHTMLParser(html_text)
    template_node = parser.css_first("template#HH-Lux-InitialState")

    if template_node:
        raw_html = template_node.html

        if not raw_html:
            return []

        start_idx = raw_html.find("{")
        end_idx = raw_html.rfind("}") + 1

        if start_idx == -1 or end_idx == 0:
            return []

        json_str = raw_html[start_idx:end_idx]

        template_node_dict = json.loads(json_str)

        raw_vacancies = template_node_dict.get("vacancySearchResult", {}).get(
            "vacancies", []
        )
    else:
        return []

    vacancies = []

    for raw_vacancy in raw_vacancies:
        title = raw_vacancy.get("name", DEFAULT_VACANCY_TITLE)

        company_dict = raw_vacancy.get("company") or {}
        company_name = company_dict.get("visibleName", DEFAULT_COMPANY_NAME)
        if not company_name:
            company_name = DEFAULT_COMPANY_NAME

        link = f"https://hh.ru/vacancy/{raw_vacancy.get('vacancyId')}"

        comp = raw_vacancy.get("compensation") or {}
        if not comp or comp.get("noCompensation") is True:
            salary = DEFAULT_SALARY
        else:
            s_from = comp.get("from")
            s_to = comp.get("to")
            currency = comp.get("currencyCode", "")

            if s_from is not None and s_to is not None:
                salary = f"{s_from}-{s_to} {currency}".strip()
            elif s_from is not None:
                salary = f"от {s_from} {currency}".strip()
            elif s_to is not None:
                salary = f"до {s_to} {currency}".strip()
            else:
                salary = DEFAULT_SALARY

        vacancy = VacancyDTO(
            title=title, company_name=company_name, salary=salary, link=link
        )

        vacancies.append(vacancy)

    return vacancies
