from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Place, Review
from django.db.models import Avg, Q
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
import openai
from dotenv import load_dotenv
from django.conf import settings
import os
import random
import logging



def home(request):
    # return HttpResponse('<h1>Welcome to home page</h1>')
    # return render(request, 'home.html')
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
            return JsonResponse([], safe=False)  # Devuelve una lista vacía en lugar de error

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
                {"user": r.user.username, "comment": r.comment, "rating": r.rating}
                for r in reviews
            ],
        }
        return JsonResponse(data)

    except Place.DoesNotExist:
        return JsonResponse({"error": "Lugar no encontrado"}, status=404)

def error_404_view(request, exception):
    return render(request, 'places/404.html', status=404)
logger = logging.getLogger(__name__)
import json
import numpy as np
import logging
import openai
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Place
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)

# Función para obtener el embedding desde OpenAI
def obtener_embedding(texto):
    try:
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=texto
        )
        return np.array(response['data'][0]['embedding'])
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error obteniendo embedding: {e}")
        return None

# Función para calcular la similitud coseno
def cosine_similarity(a, b):
    """Calcula similitud coseno entre dos vectores normalizados"""
    return np.dot(a, b)

# Vista principal para manejar la lógica de rutas
@csrf_exempt
def ruta_ai_view(request):
    if request.method == "GET":
        return render(request, 'ruta_ai.html')
    
    elif request.method == "POST":
        try:
            # Leer datos desde el cuerpo de la solicitud como JSON
            data = json.loads(request.body)
            ciudad = data.get('ciudad', '').lower()
            presupuesto = data.get('presupuesto', '').lower()
            prompt = data.get('prompt', '').strip()

            # Validación básica
            if not all([ciudad, presupuesto, prompt]):
                return JsonResponse({
                    'error': 'Todos los campos son requeridos',
                    'status': 'validation_error'
                }, status=400)

            # Obtener embedding del prompt
            prompt_embedding = obtener_embedding(prompt)
            if prompt_embedding is None:
                return JsonResponse({
                    'error': 'No se pudo procesar el prompt con OpenAI',
                    'status': 'embedding_error'
                }, status=500)

            # Normalizar el embedding
            prompt_embedding = prompt_embedding / np.linalg.norm(prompt_embedding)

            # Filtrar lugares en la base de datos
            lugares = Place.objects.filter(city__iexact=ciudad)
            
            
            if presupuesto == "bajo":
                lugares = lugares.filter(cost__lte=20000)
            elif presupuesto == "medio":
                lugares = lugares.filter(cost__range=(20001, 80000))
            elif presupuesto == "alto":
                lugares = lugares.filter(cost__gte=80001)
            elif presupuesto == "todos":
                # No se filtra por costo
                pass


            # Calcular similitud entre el prompt y los lugares
            resultados = []
            for lugar in lugares:
                if lugar.embedding:
                    lugar_embedding = np.array(lugar.embedding)
                    lugar_embedding = lugar_embedding / np.linalg.norm(lugar_embedding)
                    similitud = cosine_similarity(prompt_embedding, lugar_embedding)
                    
                    # Bonus si la categoría coincide con el prompt
                    bonus = 0.1 if any(palabra in prompt.lower() 
                                       for palabra in lugar.category.lower().split()) else 0
                    score_final = similitud + bonus
                    
                    resultados.append({
                        'lugar': lugar,
                        'score': score_final
                    })

            # Ordenar resultados por score y obtener los mejores 5
            resultados.sort(key=lambda x: x['score'], reverse=True)
            lugares_recomendados = [r['lugar'] for r in resultados[:5]]

            # Preparar respuesta JSON
            lugares_data = [{
                'id': lugar.id,
                'name': lugar.name,
                'description': lugar.description,
                'category': lugar.category,
                'cost': float(lugar.cost),
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
            return JsonResponse({
                'error': 'Formato JSON inválido',
                'status': 'invalid_json'
            }, status=400)
            
        except Exception as e:
            logger.error(f"Error en ruta_ai_view: {str(e)}")
            return JsonResponse({
                'error': 'Error interno del servidor',
                'status': 'server_error',
                'details': str(e)
            }, status=500)

    # Manejo de métodos no permitidos
    return JsonResponse({
        'error': 'Método no permitido',
        'status': 'method_not_allowed'
    }, status=405)
