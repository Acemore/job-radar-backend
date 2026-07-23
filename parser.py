import asyncpg
import httpx
from bs4 import BeautifulSoup
from db_manager import save_vacancies


async def fetch_html(client: httpx.AsyncClient, url: str) -> str:
    try:
        response = await client.get(url)
    except httpx.TimeoutException as e:
        print(f"[PARSER] Timeout exception while fetching URL: {e}")
        return ""

    return response.text


def parse_vacancies(html_content: str) -> list[dict]:
    if not html_content:
        return []

    soup = BeautifulSoup(html_content, "lxml")
    cards = soup.find_all("div", class_="vacancy-card")
    vacancies_data = []

    for card in cards:
        title_el = card.find("a", class_="vacancy-card__title-link")
        company_div = card.find("div", class_="vacancy-card__company")
        company_el = company_div.find("a") if company_div else None

        title = title_el.text.strip() if title_el else "No title"
        company_name = (
            company_el.text.strip() if company_el else "No company name"
        )

        vacancy_data = {
            "title": title,
            "company_name": company_name,
        }
        vacancies_data.append(vacancy_data)

    return vacancies_data


async def main():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    url = "https://career.habr.com/vacancies/programmist_python"
    dsn = "postgres://postgres:postgres@127.0.0.1:5432/job_radar"

    async with asyncpg.create_pool(dsn) as pool:
        async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
            html_content = await fetch_html(client, url)
            vacancies = parse_vacancies(html_content)
            await save_vacancies(pool, vacancies)

            print("[СИСТЕМА] Все вакансии успешно сохранены в PostgreSQL!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
