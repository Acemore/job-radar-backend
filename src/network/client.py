import asyncio

import httpx

from src.exceptions.fetcher import FetcherNetworkError
from src.network.routing import BaseNodeProvider


class ResilientNetworkClient:
    def __init__(
        self,
        node_provider: BaseNodeProvider | None = None,
        max_direct_attempts: int = 2,
        max_fallback_attempts: int = 2,
        backoff_factor: float = 0.5,
    ):
        self.node_provider = node_provider
        self.max_direct_attempts = max_direct_attempts
        self.max_fallback_attempts = max_fallback_attempts
        self.backoff_factor = backoff_factor

    async def make_request(
        self, url: str, method: str = "GET", **kwargs
    ) -> httpx.Response:
        fallback_node_url: str | None = None

        total_attempts = self.max_direct_attempts + self.max_fallback_attempts

        for attempt in range(total_attempts):
            switch_to_fallback = False

            async with httpx.AsyncClient(proxy=fallback_node_url) as client:
                try:
                    response = await client.request(method, url, **kwargs)

                    if response.status_code in (200, 404):
                        return response
                    elif response.status_code in (403, 429):
                        switch_to_fallback = True
                    else:
                        response.raise_for_status()

                except httpx.HTTPError as e:
                    if attempt == self.max_direct_attempts - 1:
                        switch_to_fallback = True
                    elif attempt == total_attempts - 1:
                        raise FetcherNetworkError(
                            f"All network routing paths exhausted. Last error: {e}",
                            original_exception=e,
                        )
                    else:
                        await asyncio.sleep(self.backoff_factor)
                        continue

            if switch_to_fallback:
                if self.node_provider:
                    node = await self.node_provider.get_node()
                    fallback_node_url = node.to_endpoint_url()

                    continue
                else:
                    status_error = httpx.HTTPStatusError(
                        f"Client error {response.status_code} for url {response.url}",
                        request=response.request,
                        response=response,
                    )
                    raise FetcherNetworkError(
                        "Resource unavailable: primary route compromised "
                        "and no fallback routing provider configured",
                        original_exception=status_error,
                    )
