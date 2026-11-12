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

        async with ResilientNetworkClient(node_provider=mock_provider) as client:
            response = await client.make_request("https://example.com")

            assert response.status_code == 200

        assert mock_request.call_count == 1
        mock_provider.get_node.assert_not_called()


@pytest.mark.asyncio
async def test_switch_to_fallback_on_waf_block():
    fake_request = httpx.Request("GET", "https://example.com")

    mock_403 = httpx.Response(status_code=403, request=fake_request)
    mock_200 = httpx.Response(status_code=200, request=fake_request)

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

        async with ResilientNetworkClient(node_provider=mock_provider) as client:
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

        async with ResilientNetworkClient(
            node_provider=mock_provider, max_direct_attempts=2, backoff_factor=0.0
        ) as client:
            response = await client.make_request("https://example.com")

            assert response.status_code == 200

        assert mock_request.call_count == 3
        mock_provider.get_node.assert_called_once()


@pytest.mark.asyncio
async def test_waf_block_raises_without_provider():
    fake_request = httpx.Request("GET", "https://example.com")
    mock_403 = httpx.Response(status_code=403, request=fake_request)

    with patch.object(
        httpx.AsyncClient, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_request.return_value = mock_403

        async with ResilientNetworkClient(node_provider=None) as client:
            with pytest.raises(FetcherNetworkError) as exc_info:
                await client.make_request("https://example.com")

            assert "no fallback routing provider configured" in str(exc_info.value)

        assert mock_request.call_count == 1


@pytest.mark.asyncio
async def test_all_routing_paths_exhausted():
    fake_request = httpx.Request("GET", "https://example.com")
    mock_403 = httpx.Response(status_code=403, request=fake_request)

    with patch.object(
        httpx.AsyncClient, "request", new_callable=AsyncMock
    ) as mock_request:
        mock_request.side_effect = [mock_403, httpx.ConnectError("ConnectError")]

        node = NetworkNodeDTO(
            protocol="http",
            host="test.node",
            port=8000,
        )

        mock_provider = MagicMock(spec=BaseNodeProvider)
        mock_provider.get_node = AsyncMock()
        mock_provider.get_node.side_effect = [node, node]

        async with ResilientNetworkClient(node_provider=mock_provider) as client:
            with pytest.raises(FetcherNetworkError) as exc_info:
                await client.make_request("https://example.com")

            assert "All network routing paths exhausted" in str(exc_info.value)

        assert mock_request.call_count == 2
        assert mock_provider.get_node.call_count == 2


@pytest.mark.asyncio
async def test_session_reuse_for_same_gateway():
    with patch("src.network.client.httpx.AsyncClient") as mock_async_client_cls:
        mock_instance = AsyncMock()
        mock_instance.request.return_value = httpx.Response(status_code=200)

        mock_async_client_cls.return_value = mock_instance

        async with ResilientNetworkClient() as client:
            await client.make_request("https://example.com")
            await client.make_request("https://example.com")

        mock_async_client_cls.assert_called_once()
        assert mock_instance.request.call_count == 2


@pytest.mark.asyncio
async def test_context_manager_closes_all_sessions():
    fake_request = httpx.Request("GET", "https://example.com")

    mock_direct_session = AsyncMock()
    mock_direct_session.request.return_value = httpx.Response(
        status_code=403,
        request=fake_request,
    )

    mock_fallback_session = AsyncMock()
    mock_fallback_session.request.return_value = httpx.Response(
        status_code=200,
        request=fake_request,
    )

    mock_provider = MagicMock(spec=BaseNodeProvider)
    mock_provider.get_node = AsyncMock()
    mock_provider.get_node.return_value = NetworkNodeDTO(
        protocol="http",
        host="test.node",
        port=8000,
    )

    with patch("src.network.client.httpx.AsyncClient") as mock_async_client_cls:
        mock_async_client_cls.side_effect = [mock_direct_session, mock_fallback_session]

        async with ResilientNetworkClient(node_provider=mock_provider) as client:
            response = await client.make_request("https://example.com")

            assert response.status_code == 200
            assert len(client._sessions) == 2

        mock_direct_session.aclose.assert_awaited_once()
        mock_fallback_session.aclose.assert_awaited_once()
        assert len(client._sessions) == 0
