import asyncio
from pathlib import Path
from urllib.parse import urlparse

from src.exceptions.fetcher import FetcherNetworkError
from src.network.client import ResilientNetworkClient
from src.network.routing import NetworkNodeDTO, RoundRobinNodeProvider

CURRENT_DIR = Path(__file__).resolve().parent
NODES_FILE_PATH = CURRENT_DIR.parent / "nodes.txt"


async def get_nodes() -> list[NetworkNodeDTO]:
    content = NODES_FILE_PATH.read_text(encoding="utf-8").strip()
    raw_urls = content.splitlines()

    nodes = []

    for raw_url in raw_urls:
        parsed_url = urlparse(raw_url)

        if not parsed_url.hostname or not parsed_url.port:
            continue

        node = NetworkNodeDTO(
            protocol=parsed_url.scheme, host=parsed_url.hostname, port=parsed_url.port
        )

        nodes.append(node)

    return nodes


async def main():
    nodes = await get_nodes()
    node_provider = RoundRobinNodeProvider(nodes=nodes)
    client = ResilientNetworkClient(node_provider=node_provider, max_direct_attempts=1)

    try:
        response = await client.make_request("https://hh.ru/search/vacancy")

        print(f"Success! Status: {response.status_code}")
    except FetcherNetworkError as e:
        print(e)


if __name__ == "__main__":
    asyncio.run(main())
