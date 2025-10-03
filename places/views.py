from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Place, Review
from django.db.models import Avg, Q
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import os
import json
import logging
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# ==== NUEVO: servicios y estrategias (DIP + Strategy) ====
from .adapters.google_routing import GoogleRoutingClient
from .adapters.openai_embeddings import OpenAIEmbeddingsClient
from .services import RoutingService, EmbeddingService
from .strategies.ranking import strategy_factory

logger = logging.getLogger(__name__)

# === Configuración ===
GOOGLE_MAPS_API_KEY = getattr(settings, "GOOGLE_MAPS_API_KEY", os.getenv("GOOGLE_MAPS_API_KEY"))

# ========================
#      VISTAS BÁSICAS
# ========================

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def reviews_page(request):
    return render(request, "reviews.html")

def error_404_view(request, exception):
    return render(request, 'places/404.html', status=404)

# ========================
#    BÚSQUEDA / LISTADOS
# ========================

def city_places(request, city_name):
    """
    Listado por ciudad con soporte de ordenamiento vía estrategia:
    ?order=distance|rating|budget|hybrid  (por defecto: hybrid)
    También mantiene el filtro por nombre ?searchPlace=<texto>
    """
    VALID_CITIES = ["medellin", "bogota", "barranquilla"]
    if city_name not in VALID_CITIES:
        return render(request, 'places/404.html', status=404)

    searchTerm = request.GET.get('searchPlace', '').strip()
    order = request.GET.get('order', 'hybrid').strip().lower()

    places = Place.objects.filter(city=city_name)
    if searchTerm:
        places = places.filter(name__icontains=searchTerm)

    # Construir items para Strategy (si faltan campos, se colocan defaults seguros)
    items = []
    for p in places:
        items.append({
            "id": p.id,
            "name": p.name,
            "distance_km": getattr(p, "distance_km", 1.0),  # si lo calculas en otro lado, aquí se usa
            "avg_rating": float(getattr(p, "avg_rating", 0.0)),
            "num_reviews": int(getattr(p, "reviews_count", 0)),
            "cost": float(p.cost or 0.0),
            "obj": p,
        })

    strategy = strategy_factory(order)
    ranked = strategy.rank(items) if items else []
    ranked_places = [it["obj"] for it in ranked] if ranked else places

    return render(request, f'{city_name}.html', {
        'searchTerm': searchTerm,
        'places': ranked_places
    })


def search_places(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"error": "Debe ingresar un término de búsqueda"}, status=400)

    try:
        places = Place.objects.filter(Q(name__icontains=query))

        if not places.exists():
            return JsonResponse([], safe=False)

        results = [{"id": place.id, "name": place.name} for place in places]
        return JsonResponse(results, safe=False)

    except Exception as e:
        logger.exception("Error en search_places")
        return JsonResponse({"error": f"Error interno: {str(e)}"}, status=500)


def get_reviews(request, place_id):
    try:
        place = Place.objects.get(id=place_id)
        reviews = Review.objects.filter(place=place)
        avg_rating = reviews.aggregate(Avg("rating"))["rating__avg"] or 0

        data = {
            "place": place.name,
            "avg_rating": round(avg_rating, 2),
            "reviews": [
                {"user": r.user, "comment": r.comment, "rating": r.rating}
                for r in reviews
            ],
        }
        return JsonResponse(data)

    except Place.DoesNotExist:
        return JsonResponse({"error": "Lugar no encontrado"}, status=404)


# ========================
#   UTILIDADES LOCALES
# ========================

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def ordenar_lugares(lugares, lat_inicio, lon_inicio):
    ruta = []
    restantes = list(lugares)
    while restantes:
        lugar_mas_cercano = min(
            restantes,
            key=lambda lugar: calcular_distancia(lat_inicio, lon_inicio, lugar.latitude, lugar.longitude)
        )
        ruta.append(lugar_mas_cercano)
        lat_inicio, lon_inicio = lugar_mas_cercano.latitude, lugar_mas_cercano.longitude
        restantes.remove(lugar_mas_cercano)
    return ruta


# ========================
#  RUTA CON IA (EMBEDDINGS)
# ========================

@csrf_exempt  # quítalo si no lo necesitas para solicitudes cross-site
def ruta_ai_view(request):
    """
    POST JSON:
    {
      "ciudad": "medellin",
      "presupuesto": "bajo|medio|alto",
      "prompt": "planes con poco presupuesto y cultura"
    }
    """
    if request.method == "GET":
        return render(request, 'ruta_ai.html', {'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY})

    elif request.method == "POST":
        try:
            data = json.loads(request.body or "{}")
            ciudad = (data.get('ciudad') or '').lower().strip()
            presupuesto = (data.get('presupuesto') or '').lower().strip()
            prompt = (data.get('prompt') or '').strip()

            if not all([ciudad, presupuesto, prompt]):
                return JsonResponse(
                    {'error': 'Todos los campos son requeridos', 'status': 'validation_error'},
                    status=400
                )

            # === DIP: servicio de embeddings ===
            embed_service = EmbeddingService(OpenAIEmbeddingsClient())
            try:
                prompt_vec = np.array(embed_service.create_vectors([prompt])[0], dtype=float)
                prompt_vec = prompt_vec / (np.linalg.norm(prompt_vec) or 1.0)
            except Exception as e:
                logger.exception("Error generando embedding del prompt")
                return JsonResponse(
                    {'error': 'No se pudo procesar el prompt con OpenAI', 'status': 'embedding_error'},
                    status=500
                )

            lugares = Place.objects.filter(city__iexact=ciudad)

            if presupuesto == "bajo":
                lugares = lugares.filter(cost__lte=20000)
            elif presupuesto == "medio":
                lugares = lugares.filter(cost__range=(20001, 80000))
            elif presupuesto == "alto":
                lugares = lugares.filter(cost__gte=80001)

            resultados = []
            for lugar in lugares:
                if hasattr(lugar, "embedding") and lugar.embedding:
                    try:
                        lugar_vec = np.array(lugar.embedding, dtype=float)
                        lugar_vec = lugar_vec / (np.linalg.norm(lugar_vec) or 1.0)
                        similitud = cosine_similarity(prompt_vec, lugar_vec)

                        # Bonus básico: si categoria aparece en prompt
                        bonus = 0.1 if any(p in prompt.lower() for p in (lugar.category or "").lower().split()) else 0.0
                        score_final = float(similitud + bonus)

                        resultados.append({'lugar': lugar, 'score': score_final})
                    except Exception:
                        # Si el embedding tiene formato inesperado, lo ignoramos
                        continue

            resultados.sort(key=lambda x: x['score'], reverse=True)
            lugares_recomendados = [r['lugar'] for r in resultados[:5]]

            lugares_data = [{
                'id': lugar.id,
                'name': lugar.name,
                'description': lugar.description,
                'category': lugar.category,
                'cost': float(lugar.cost or 0.0),
                'address': lugar.address,
                'latitude': lugar.latitude,
                'longitude': lugar.longitude,
                'image_url': request.build_absolute_uri(lugar.image.url) if getattr(lugar, "image", None) else None,
                'city': lugar.city,
                'score': next((r['score'] for r in resultados if r['lugar'].id == lugar.id), 0.0)
            } for lugar in lugares_recomendados]

            return JsonResponse({
                'status': 'success',
                'count': len(lugares_data),
                'lugares': lugares_data,
                'query': {'ciudad': ciudad, 'presupuesto': presupuesto, 'prompt': prompt}
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Formato JSON inválido', 'status': 'invalid_json'}, status=400)
        except Exception as e:
            logger.exception("Error en ruta_ai_view")
            return JsonResponse(
                {'error': 'Error interno del servidor', 'status': 'server_error', 'details': str(e)},
                status=500
            )

    return JsonResponse({'error': 'Método no permitido', 'status': 'method_not_allowed'}, status=405)


# ========================
#   RUTAS GOOGLE MAPS (DIP)
# ========================

@csrf_exempt  # quítalo si no lo necesitas para solicitudes cross-site
def obtener_ruta_google_maps(request):
    """
    POST JSON:
    {
      "lugares_ids": [1,2,3]
    }
    Respuesta:
    { "ruta": <polyline>, "duracion_total": <minutos> }
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data = json.loads(request.body or "{}")
        lugares_ids = data.get("lugares_ids", [])

        if not lugares_ids:
            return JsonResponse({"error": "No se recibieron lugares"}, status=400)

        lugares = Place.objects.filter(id__in=lugares_ids).order_by('id')
        if not lugares.exists():
            return JsonResponse({"error": "No se encontraron lugares válidos"}, status=400)

        # Armar waypoints [(lat, lon), ...]
        coords = []
        for l in lugares:
            if getattr(l, "latitude", None) is not None and getattr(l, "longitude", None) is not None:
                coords.append((float(l.latitude), float(l.longitude)))

        if len(coords) < 2:
            return JsonResponse(
                {"error": "Se requieren al menos dos lugares con coordenadas válidas"},
                status=400
            )

        # === DIP: servicio de ruteo ===
        routing_service = RoutingService(GoogleRoutingClient(api_key=GOOGLE_MAPS_API_KEY))
        polyline, minutes = routing_service.get_polyline_and_minutes(coords)

        return JsonResponse({"ruta": polyline, "duracion_total": minutes})

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    except Exception as e:
        logger.exception("Error en obtener_ruta_google_maps")
        return JsonResponse({"error": str(e)}, status=500)
