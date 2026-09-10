import pytest

from src.network.routing import NetworkNodeDTO


@pytest.fixture
def node_anonymous() -> NetworkNodeDTO:
    return NetworkNodeDTO(protocol="http", host="185.242.22.10", port=8080)


@pytest.fixture
def node_authenticated() -> NetworkNodeDTO:
    return NetworkNodeDTO(
        protocol="socks5",
        host="94.130.12.44",
        port=1080,
        username="network_user",
        password="secure_password_123",
    )


@pytest.fixture
def nodes_list() -> list[NetworkNodeDTO]:
    return [
        NetworkNodeDTO(protocol="http", host="1.1.1.1", port=80),
        NetworkNodeDTO(protocol="http", host="2.2.2.2", port=80),
    ]
