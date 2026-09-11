from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.exceptions.fetcher import FetcherNetworkError
from src.network.client import ResilientNetworkClient
from src.network.routing import BaseNodeProvider, NetworkNodeDTO


@pytest.mark.asyncio
async def test_successful_direct_request():
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200

    with patch.object(
        httpx.AsyncClient, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_request.return_value = mock_response

        mock_provider = MagicMock(spec=BaseNodeProvider)
        mock_provider.get_node = AsyncMock()

        client = ResilientNetworkClient(node_provider=mock_provider)
        response = await client.make_request("https://example.com")

        assert response.status_code == 200
        assert mock_request.call_count == 1
        mock_provider.get_node.assert_not_called()


@pytest.mark.asyncio
async def test_switch_to_fallback_on_waf_block():
    mock_403 = MagicMock(spec=httpx.Response)
    mock_403.status_code = 403

    mock_200 = MagicMock(spec=httpx.Response)
    mock_200.status_code = 200

    with patch.object(
        httpx.AsyncClient, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_request.side_effect = [mock_403, mock_200]

        mock_provider = MagicMock(spec=BaseNodeProvider)
        mock_provider.get_node = AsyncMock()
        mock_provider.get_node.return_value = NetworkNodeDTO(
            protocol="http",
            host="test.node",
            port=8000,
        )

        client = ResilientNetworkClient(node_provider=mock_provider)
        response = await client.make_request("https://example.com")

        assert response.status_code == 200
        assert mock_request.call_count == 2
        mock_provider.get_node.assert_called_once()


@pytest.mark.asyncio
async def test_fallback_after_direct_timeout():
    mock_200 = MagicMock(spec=httpx.Response)
    mock_200.status_code = 200

    with patch.object(
        httpx.AsyncClient, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_request.side_effect = [
            httpx.ConnectTimeout("Timeout 1"),
            httpx.ConnectTimeout("Timeout 2"),
            mock_200,
        ]

        mock_provider = MagicMock(spec=BaseNodeProvider)
        mock_provider.get_node = AsyncMock()
        mock_provider.get_node.return_value = NetworkNodeDTO(
            protocol="http",
            host="test.node",
            port=8000,
        )

        client = ResilientNetworkClient(
            node_provider=mock_provider, max_direct_attempts=2, max_fallback_attempts=1
        )
        response = await client.make_request("https://example.com")

        assert response.status_code == 200
        assert mock_request.call_count == 3
        mock_provider.get_node.assert_called_once()


@pytest.mark.asyncio
async def test_waf_block_raises_without_provider():
    mock_403 = MagicMock(spec=httpx.Response)
    mock_403.status_code = 403

    with patch.object(
        httpx.AsyncClient, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_request.return_value = mock_403

        client = ResilientNetworkClient(node_provider=None)
        with pytest.raises(FetcherNetworkError) as exc_info:
            await client.make_request("https://example.com")

        assert mock_request.call_count == 1
        assert "no fallback routing provider configured" in str(exc_info.value)


@pytest.mark.asyncio
async def test_all_routing_paths_exhausted():
    with patch.object(
        httpx.AsyncClient, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_request.side_effect = [
            httpx.ConnectError("Dead 1"),
            httpx.ConnectError("Dead 2"),
        ]

        mock_provider = MagicMock(spec=BaseNodeProvider)
        mock_provider.get_node = AsyncMock()
        mock_provider.get_node.return_value = NetworkNodeDTO(
            protocol="http",
            host="test.node",
            port=8000,
        )

        client = ResilientNetworkClient(
            node_provider=mock_provider, max_direct_attempts=1, max_fallback_attempts=1
        )
        with pytest.raises(FetcherNetworkError) as exc_info:
            await client.make_request("https://example.com")

        assert mock_request.call_count == 2
        mock_provider.get_node.assert_called_once()
        assert "All network routing paths exhausted" in str(exc_info.value)
