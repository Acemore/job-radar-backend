import httpx
from bs4 import BeautifulSoup


async def fetch_html(client: httpx.AsyncClient, url: str) -> str:
    response = await client.get(url)
    return response.text


def parse_vacancies(html_content: str) -> list[dict]:
    soup = BeautifulSoup(html_content, "lxml")
    cards = soup.find_all("div", class_="vacancy_card")

    vacancies_data = []

    for card in cards:
        title = card.find("div", class_="title").text.strip()
        company_name = card.find("div", class_="company_name").text.strip()

        vacancy_data = {
            "title": title,
            "company_name": company_name,
        }

        vacancies_data.append(vacancy_data)

    return vacancies_data
