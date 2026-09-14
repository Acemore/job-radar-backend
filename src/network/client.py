import asyncio

import httpx

from src.exceptions.fetcher import FetcherNetworkError
from src.network.routing import BaseNodeProvider


class ResilientNetworkClient:
    def __init__(
        self,
        node_provider: BaseNodeProvider | None = None,
        max_direct_attempts: int = 2,
        backoff_factor: float = 0.5,
    ):
        self.node_provider = node_provider
        self.max_direct_attempts = max_direct_attempts
        self.backoff_factor = backoff_factor

    async def make_request(
        self, url: str, method: str = "GET", **kwargs
    ) -> httpx.Response:
        direct_attempts_used = 0

        first_fallback_node_url: str | None = None
        current_fallback_node_url: str | None = None

        last_error: Exception | None = None

        while True:
            switch_to_fallback = False

            async with httpx.AsyncClient(proxy=current_fallback_node_url) as client:
                try:
                    response = await client.request(method, url, **kwargs)

                    if response.status_code not in (200, 404):
                        response.raise_for_status()

                    return response
                except httpx.HTTPError as e:
                    last_error = e

                    if isinstance(
                        e, httpx.HTTPStatusError
                    ) and e.response.status_code in (403, 429):
                        switch_to_fallback = True
                    else:
                        if current_fallback_node_url is None:
                            direct_attempts_used += 1
                            if direct_attempts_used >= self.max_direct_attempts:
                                switch_to_fallback = True
                            else:
                                await asyncio.sleep(self.backoff_factor)
                                continue
                        else:
                            switch_to_fallback = True

            if switch_to_fallback:
                if not self.node_provider:
                    raise FetcherNetworkError(
                        "Resource unavailable: primary route compromised "
                        "and no fallback routing provider configured",
                        original_exception=last_error,
                    )

                next_node = await self.node_provider.get_node()
                next_node_url = next_node.to_endpoint_url()

                if current_fallback_node_url is None:
                    first_fallback_node_url = next_node_url
                    current_fallback_node_url = next_node_url
                else:
                    if next_node_url == first_fallback_node_url:
                        raise FetcherNetworkError(
                            f"All network routing paths exhausted. "
                            f"Last error: {last_error}",
                            original_exception=last_error,
                        )

                    current_fallback_node_url = next_node_url
                    continue
