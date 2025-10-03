from typing import Protocol, List, Tuple, Dict

class RoutingClient(Protocol):
    def route(self, waypoints: List[Tuple[float, float]]) -> Dict: ...

class EmbeddingsClient(Protocol):
    def embed(self, texts: List[str]) -> List[List[float]]: ...
