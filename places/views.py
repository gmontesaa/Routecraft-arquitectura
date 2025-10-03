from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Place, Review
from django.db.models import Avg, Q
from django.views.decorators.csrf import csrf_exempt
import json
from openai import OpenAI
from dotenv import load_dotenv
from django.conf import settings
import os
import random
import logging
from math import radians, sin, cos, sqrt, atan2
import requests
import numpy as np


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def city_places(request, city_name):
    VALID_CITIES = ["medellin", "bogota", "barranquilla"]

    searchTerm = request.GET.get('searchPlace', '')
    places = Place.objects.filter(city=city_name)
    if searchTerm:
        places = places.filter(name__icontains=searchTerm)

    return render(request, f'{city_name}.html', {'searchTerm': searchTerm, 'places': places})


def reviews_page(request):
    return render(request, "reviews.html")


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


def error_404_view(request, exception):
    return render(request, 'places/404.html', status=404)


# Configuraciones y carga de entorno
logger = logging.getLogger(__name__)
load_dotenv()

# SDK nuevo de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GOOGLE_MAPS_API_KEY = settings.GOOGLE_MAPS_API_KEY


# Funciones auxiliares

def obtener_embedding(texto):
    try:
        r = client.embeddings.create(
            model="text-embedding-3-small",
            input=texto
        )
        return np.array(r.data[0].embedding)
    except Exception as e:
        logger.error(f"Error obteniendo embedding: {e}")
        return None


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def ordenar_lugares(lugares, lat_inicio, lon_inicio):
    ruta = []
    while lugares:
        lugar_mas_cercano = min(lugares, key=lambda lugar: calcular_distancia(
            lat_inicio, lon_inicio, lugar.latitude, lugar.longitude))
        ruta.append(lugar_mas_cercano)
        lat_inicio, lon_inicio = lugar_mas_cercano.latitude, lugar_mas_cercano.longitude
        lugares.remove(lugar_mas_cercano)
    return ruta


@csrf_exempt
def ruta_ai_view(request):
    if request.method == "GET":
        return render(request, 'ruta_ai.html', {
            'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY}
                      )

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            ciudad = data.get('ciudad', '').lower()
            presupuesto = data.get('presupuesto', '').lower()
            prompt = data.get('prompt', '').strip()

            if not all([ciudad, presupuesto, prompt]):
                return JsonResponse({'error': 'Todos los campos son requeridos', 'status': 'validation_error'},
                                    status=400)

            prompt_embedding = obtener_embedding(prompt)
            if prompt_embedding is None:
                return JsonResponse({'error': 'No se pudo procesar el prompt con OpenAI', 'status': 'embedding_error'},
                                    status=500)

            prompt_embedding = prompt_embedding / np.linalg.norm(prompt_embedding)
            lugares = Place.objects.filter(city__iexact=ciudad)

            if presupuesto == "bajo":
                lugares = lugares.filter(cost__lte=20000)
            elif presupuesto == "medio":
                lugares = lugares.filter(cost__range=(20001, 80000))
            elif presupuesto == "alto":
                lugares = lugares.filter(cost__gte=80001)

            resultados = []
            for lugar in lugares:
                if lugar.embedding:
                    lugar_embedding = np.array(lugar.embedding)
                    lugar_embedding = lugar_embedding / np.linalg.norm(lugar_embedding)
                    similitud = cosine_similarity(prompt_embedding, lugar_embedding)
                    bonus = 0.1 if any(p in prompt.lower() for p in lugar.category.lower().split()) else 0
                    score_final = similitud + bonus
                    resultados.append({'lugar': lugar, 'score': score_final})

            resultados.sort(key=lambda x: x['score'], reverse=True)
            lugares_recomendados = [r['lugar'] for r in resultados[:5]]

            lugares_data = [{
                'id': lugar.id,
                'name': lugar.name,
                'description': lugar.description,
                'category': lugar.category,
                'cost': float(lugar.cost),
                'address': lugar.address,
                'latitude': lugar.latitude,
                'longitude': lugar.longitude,
                'image_url': request.build_absolute_uri(lugar.image.url) if lugar.image else None,
                'city': lugar.city,
                'score': next(r['score'] for r in resultados if r['lugar'].id == lugar.id)

            } for lugar in lugares_recomendados]

            return JsonResponse({
                'status': 'success',
                'count': len(lugares_data),
                'lugares': lugares_data,
                'query': {
                    'ciudad': ciudad,
                    'presupuesto': presupuesto,
                    'prompt': prompt
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Formato JSON inválido', 'status': 'invalid_json'}, status=400)

        except Exception as e:
            logger.error(f"Error en ruta_ai_view: {str(e)}")
            return JsonResponse({'error': 'Error interno del servidor', 'status': 'server_error', 'details': str(e)},
                                status=500)

    return JsonResponse({'error': 'Método no permitido', 'status': 'method_not_allowed'}, status=405)


@csrf_exempt
def obtener_ruta_google_maps(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            lugares_ids = data.get("lugares_ids", [])

            if not lugares_ids:
                return JsonResponse({"error": "No se recibieron lugares"}, status=400)

            lugares = Place.objects.filter(id__in=lugares_ids).order_by('id')

            if not lugares.exists():
                return JsonResponse({"error": "No se encontraron lugares válidos"}, status=400)

            coordenadas = [f"{lugar.latitude},{lugar.longitude}" for lugar in lugares if
                           lugar.latitude and lugar.longitude]

            if len(coordenadas) < 2:
                return JsonResponse({"error": "Se requieren al menos dos lugares con coordenadas válidas"}, status=400)

            directions_url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                "origin": coordenadas[0],
                "destination": coordenadas[-1],
                "waypoints": "|".join(coordenadas[1:-1]) if len(coordenadas) > 2 else '',
                "key": GOOGLE_MAPS_API_KEY,
                "mode": "driving"
            }

            response = requests.get(directions_url, params=params)
            ruta_data = response.json()

            if ruta_data.get("status") != "OK":
                return JsonResponse({"error": "Error obteniendo la ruta de Google Maps"}, status=500)

            ruta = ruta_data["routes"][0]["overview_polyline"]["points"]
            duracion_total = round(sum(leg["duration"]["value"] for leg in ruta_data["routes"][0]["legs"]) / 60)

            return JsonResponse({
                "ruta": ruta,
                "duracion_total": duracion_total
            })

        except Exception as e:
            logger.error(f"Error en obtener_ruta_google_maps: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)
