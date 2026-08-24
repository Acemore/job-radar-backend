import httpx

HABR_CAREER_URL = "https://career.habr.com"


async def fetch_habr_career(client: httpx.AsyncClient) -> str:
    try:
        response = await client.get(HABR_CAREER_URL)
    except httpx.TimeoutException as e:
        print(f"[FETCHER] Timeout exception while fetching URL: {e}")
        return ""

    return response.text
