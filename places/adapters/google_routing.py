import os, requests
from typing import List, Tuple, Dict

class GoogleRoutingClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")

    def route(self, waypoints: List[Tuple[float, float]]) -> Dict:
        if len(waypoints) < 2:
            raise ValueError("Se requieren al menos origen y destino")

        origin = f"{waypoints[0][0]},{waypoints[0][1]}"
        destination = f"{waypoints[-1][0]},{waypoints[-1][1]}"
        others = waypoints[1:-1]

        params = {"origin": origin, "destination": destination, "key": self.api_key}
        if others:
            params["waypoints"] = "|".join(f"{lat},{lon}" for lat, lon in others)

        r = requests.get(
            "https://maps.googleapis.com/maps/api/directions/json",
            params=params,
            timeout=10  # seguridad/rendimiento
        )
        r.raise_for_status()
        return r.json()
