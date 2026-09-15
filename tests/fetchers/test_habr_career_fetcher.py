from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from src.exceptions.fetcher import FetcherNetworkError
from src.fetchers.habr_career import HABR_CAREER_URL, fetch_habr_career


async def test_fetch_habr_career_success(habr_mock_html):
    client = AsyncMock()
    response = Mock()

    response.text = habr_mock_html
    client.make_request.return_value = response

    response_text = await fetch_habr_career(client)

    assert response_text == habr_mock_html
    client.make_request.assert_awaited_once_with(HABR_CAREER_URL)


async def test_fetch_habr_career_network_error_raises():
    client = AsyncMock()

    fake_network_error = httpx.ConnectError("Network dead")
    client.make_request.side_effect = FetcherNetworkError(
        "Network failure", original_exception=fake_network_error
    )

    with pytest.raises(FetcherNetworkError):
        await fetch_habr_career(client)
