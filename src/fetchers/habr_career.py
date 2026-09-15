from src.network.client import ResilientNetworkClient

HABR_CAREER_URL = "https://career.habr.com/vacancies"


async def fetch_habr_career(client: ResilientNetworkClient) -> str:
    response = await client.make_request(HABR_CAREER_URL)
    return response.text
