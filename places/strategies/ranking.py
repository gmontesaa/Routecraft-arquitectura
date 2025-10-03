from abc import ABC, abstractmethod
from typing import List, Dict, Any

class RankingStrategy(ABC):
    @abstractmethod
    def rank(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]: ...

class DistanceStrategy(RankingStrategy):
    def rank(self, items):
        return sorted(items, key=lambda x: x["distance_km"])

class RatingStrategy(RankingStrategy):
    def rank(self, items):
        return sorted(items, key=lambda x: (-x["avg_rating"], x["num_reviews"]))

class BudgetStrategy(RankingStrategy):
    def rank(self, items):
        return sorted(items, key=lambda x: x["cost"])

class HybridStrategy(RankingStrategy):
    def rank(self, items):
        return sorted(items, key=lambda x: (0.4*x["distance_km"] - 0.6*x["avg_rating"] + 0.2*(x["cost"]/100.0)))

def strategy_factory(code: str) -> RankingStrategy:
    m = {
        "distance": DistanceStrategy(),
        "rating": RatingStrategy(),
        "budget": BudgetStrategy(),
        "hybrid": HybridStrategy(),
    }
    return m.get(code, HybridStrategy())
