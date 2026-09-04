import httpx

from src.exceptions.fetcher import FetcherNetworkError, FetcherTimeoutError
from src.utils.retry import retry

HH_VACANCIES_URL = "https://api.hh.ru/vacancies"


@retry(attempts=3, delay=1.0)
async def fetch_hh_vacancies(client: httpx.AsyncClient, query_text: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/128.0.0.0 Safari/537.36"
        )
    }
    query_params = {"text": query_text}

    try:
        response = await client.get(
            HH_VACANCIES_URL, headers=headers, params=query_params
        )
    except httpx.TimeoutException as e:
        raise FetcherTimeoutError(HH_VACANCIES_URL, e)
    except httpx.RequestError as e:
        raise FetcherNetworkError(HH_VACANCIES_URL, e)

    return response.json()
