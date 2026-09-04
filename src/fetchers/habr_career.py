import httpx

from src.exceptions.fetcher import FetcherNetworkError, FetcherTimeoutError
from src.utils.retry import retry

HABR_CAREER_URL = "https://career.habr.com/vacancies"


@retry(attempts=3, delay=1.0)
async def fetch_habr_career(client: httpx.AsyncClient) -> str:
    try:
        response = await client.get(HABR_CAREER_URL)
    except httpx.TimeoutException as e:
        raise FetcherTimeoutError(HABR_CAREER_URL, e)
    except httpx.RequestError as e:
        raise FetcherNetworkError(HABR_CAREER_URL, e)

    return response.text
