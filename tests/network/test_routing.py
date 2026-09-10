import pytest

from src.network.routing import RoundRobinNodeProvider


def test_endpoint_url_build(node_anonymous, node_authenticated):
    anonymous_node_url = node_anonymous.to_endpoint_url()
    authenticated_node_url = node_authenticated.to_endpoint_url()

    assert anonymous_node_url == "http://185.242.22.10:8080"
    assert (
        authenticated_node_url
        == "socks5://network_user:secure_password_123@94.130.12.44:1080"
    )


@pytest.mark.asyncio
async def test_round_robin_balancing(nodes_list):
    balancer = RoundRobinNodeProvider(nodes_list)

    assert await balancer.get_node() == nodes_list[0]
    assert await balancer.get_node() == nodes_list[1]
    assert await balancer.get_node() == nodes_list[0]
    assert await balancer.get_node() == nodes_list[1]
