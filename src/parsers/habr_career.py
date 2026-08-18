from selectolax.lexbor import LexborHTMLParser

from src.schemas import VacancyDTO


def parse_habr_vacancies(html_content: str) -> list[VacancyDTO]:
    parser = LexborHTMLParser(html_content)
    raw_vacancies = parser.css(".vacancy-card")
    vacancies = []

    for raw_vacancy in raw_vacancies:
        title_node = raw_vacancy.css_first(".vacancy-card__title a")
        title = (
            title_node.text(strip=True)
            if title_node
            else "Название вакансии не указано"
        )

        company_node = (
            raw_vacancy.css_first(".vacancy-card__company-title a")
            or raw_vacancy.css_first(".vacancy-card__company a")
            or raw_vacancy.css_first(".vacancy-card__company")
        )
        company_name = (
            company_node.text(strip=True) if company_node else "Компания не указана"
        )

        salary_node = (
            raw_vacancy.css_first(".vacancy-card__salary")
            or raw_vacancy.css_first(".vacancy-card__title-line .salary")
            or raw_vacancy.css_first(".vacancy-card__header .salary")
            or raw_vacancy.css_first(".salary")
        )
        if salary_node:
            raw_salary = salary_node.text(strip=True)
            salary = " ".join(raw_salary.split())
        else:
            salary = "Зарплата не указана"

        link = "Ссылка отсутствует"
        if title_node:
            raw_link = title_node.attributes.get("href")
            if raw_link:
                link = f"https://career.habr.com{raw_link}"

        vacancy = VacancyDTO(
            title=title, company_name=company_name, salary=salary, link=link
        )

        vacancies.append(vacancy)

    return vacancies
