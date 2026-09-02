from unittest.mock import AsyncMock, Mock

import pytest
from httpx import RequestError, TimeoutException

from src.exceptions.fetcher import FetcherNetworkError, FetcherTimeoutError
from src.fetchers.habr_career import HABR_CAREER_URL, fetch_habr_career


async def test_fetch_habr_career_success(habr_mock_html):
    client = AsyncMock()
    response = Mock()

    response.text = habr_mock_html
    client.get.return_value = response

    response_text = await fetch_habr_career(client)

    assert response_text == habr_mock_html
    client.get.assert_awaited_once_with(HABR_CAREER_URL)


async def test_fetch_habr_career_timeout_raises():
    client = AsyncMock()
    client.get.side_effect = TimeoutException("Timeout exception")

    with pytest.raises(FetcherTimeoutError):
        await fetch_habr_career(client)


async def test_fetch_habr_career_network_error_raises():
    client = AsyncMock()
    client.get.side_effect = RequestError("Request error")

    with pytest.raises(FetcherNetworkError):
        await fetch_habr_career(client)
