# Actividad 4 — Patrón de diseño en Python

## 1. Objetivo
Aplicar un patrón de diseño de Python para mejorar la flexibilidad y mantenibilidad del proyecto.  
El patrón elegido fue **Strategy + Factory**, implementado en la funcionalidad de ordenamiento de lugares.

---

## 2. Contexto del problema
En el listado de lugares (`city_places`), los usuarios pueden querer ordenar resultados de diferentes maneras:
- Por distancia
- Por calificación promedio (rating)
- Por presupuesto (cost)
- O una combinación híbrida

La implementación inicial requería condicionales extensos (`if/else`) en la vista, lo que acoplaba la lógica y hacía difícil agregar nuevos criterios.

---

## 3. Patrón aplicado: Strategy + Factory

### ¿Por qué Strategy?
- Cada forma de ordenar se implementa como una estrategia independiente (`DistanceStrategy`, `RatingStrategy`, `BudgetStrategy`, `HybridStrategy`).  
- Permite **extender fácilmente** la lógica añadiendo una nueva clase de estrategia sin modificar las demás.

### ¿Por qué Factory?
- La función `strategy_factory(code)` devuelve la estrategia adecuada según el parámetro `order` recibido en la vista.
- Se evita duplicar código y se facilita seleccionar la estrategia en tiempo de ejecución.

---

## 4. Implementación

**Archivo:** `places/strategies/ranking.py`

```python
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
