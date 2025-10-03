from typing import List, Tuple
from .ports import RoutingClient, EmbeddingsClient

class RoutingService:
    def __init__(self, client: RoutingClient):
        self.client = client

    def get_polyline_and_minutes(self, points: List[Tuple[float, float]]) -> tuple[str, int]:
        data = self.client.route(points)
        route = data["routes"][0]
        poly = route["overview_polyline"]["points"]
        minutes = round(sum(leg["duration"]["value"] for leg in route["legs"]) / 60)
        return poly, minutes

class EmbeddingService:
    def __init__(self, client: EmbeddingsClient):
        self.client = client

    def create_vectors(self, texts: List[str]) -> List[List[float]]:
        return self.client.embed(texts)
