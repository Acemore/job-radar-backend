import itertools
from abc import ABC, abstractmethod
from typing import Iterable

from pydantic import BaseModel


class NetworkNodeDTO(BaseModel):
    protocol: str
    host: str
    port: int
    username: str | None = None
    password: str | None = None

    def to_endpoint_url(self) -> str:
        return (
            f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
            if self.username and self.password
            else f"{self.protocol}://{self.host}:{self.port}"
        )


class BaseNodeProvider(ABC):
    @abstractmethod
    async def get_node(self) -> NetworkNodeDTO:
        pass

    @abstractmethod
    def get_nodes_count(self) -> int:
        pass


class RoundRobinNodeProvider(BaseNodeProvider):
    def __init__(self, nodes: Iterable[NetworkNodeDTO]):
        self._nodes = list(nodes)

        if not self._nodes:
            raise ValueError("Node list cannot be empty")

        self.nodes = itertools.cycle(self._nodes)

    async def get_node(self) -> NetworkNodeDTO:
        return next(self.nodes)

    def get_nodes_count(self) -> int:
        return len(self._nodes)
