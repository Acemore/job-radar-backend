from src.network.client import ResilientNetworkClient

HH_VACANCIES_URL = "https://api.hh.ru/vacancies"


async def fetch_hh_vacancies(client: ResilientNetworkClient, query_text: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        )
    }
    query_params = {"text": query_text}

    response = await client.make_request(
        HH_VACANCIES_URL, headers=headers, params=query_params
    )

    return response.json()
