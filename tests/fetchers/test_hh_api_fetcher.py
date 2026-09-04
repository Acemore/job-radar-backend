from unittest.mock import AsyncMock, Mock

import pytest
from httpx import RequestError, TimeoutException

from src.exceptions.fetcher import FetcherNetworkError, FetcherTimeoutError
from src.fetchers.hh_api import HH_VACANCIES_URL, fetch_hh_vacancies

query_text = "Python"


async def test_fetch_hh_vacancies_success(hh_mock_data):
    client = AsyncMock()
    response = Mock()

    response.json.return_value = hh_mock_data
    client.get.return_value = response

    response_json = await fetch_hh_vacancies(client, query_text=query_text)

    assert response_json == hh_mock_data
    client.get.assert_called_once_with(
        HH_VACANCIES_URL,
        params={"text": query_text},
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            )
        },
    )


async def test_fetch_hh_vacancies_timeout_raises():
    client = AsyncMock()
    client.get.side_effect = TimeoutException("Timeout error")

    with pytest.raises(FetcherTimeoutError):
        await fetch_hh_vacancies(client, query_text=query_text)


async def test_fetch_hh_vacancies_network_error_raises():
    client = AsyncMock()
    client.get.side_effect = RequestError("Timeout error")

    with pytest.raises(FetcherNetworkError):
        await fetch_hh_vacancies(client, query_text=query_text)
