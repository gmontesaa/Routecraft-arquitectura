from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from .models import Place, Bog, Barr, Review
from .forms import ReviewForm

def home(request):
    # return HttpResponse('<h1>Welcome to home page</h1>')
    # return render(request, 'home.html')
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def medellin(request):
    searchTerm = request.GET.get('searchPlace')
    
    if searchTerm:
        places = Place.objects.filter(name__icontains=searchTerm)
    else:
        places = Place.objects.all()
    
    return render(request, 'medellin.html', {'searchTerm': searchTerm, 'places': places})

def bogota(request):
    searchTerm = request.GET.get('searchPlace')
    
    if searchTerm:
        places = Bog.objects.filter(name__icontains=searchTerm)
    else:
        places = Bog.objects.all()
    
    return render(request, 'bogota.html', {'searchTerm': searchTerm, 'places': places})

def barranquilla(request):
    searchTerm = request.GET.get('searchPlace')
    
    if searchTerm:
        places = Barr.objects.filter(name__icontains=searchTerm)
    else:
        places = Barr.objects.all()
    
    return render(request, 'barranquilla.html', {'searchTerm': searchTerm, 'places': places})


def add_review(request, place_id, city):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            
            if city == "medellin":
                place = get_object_or_404(Place, id=place_id)
                review.place = place
            elif city == "bogota":
                place = get_object_or_404(Bog, id=place_id)
                review.bog = place
            elif city == "barranquilla":
                place = get_object_or_404(Barr, id=place_id)
                review.barr = place
            else:
                return JsonResponse({"error": "Ciudad no válida"}, status=400)

            review.save()
            return JsonResponse({
                "message": "Reseña guardada exitosamente",
                "user_name": review.user_name,
                "rating": review.rating,
                "comment": review.comment,
            })

    return JsonResponse({"error": "Solicitud inválida"}, status=400)

def reviews_page(request):
    query = request.GET.get('search', '')  # Obtener el término de búsqueda
    reviews = None

    if query:
        place = Place.objects.filter(name__icontains=query).first()  # Buscar el lugar
        if place:
            reviews = Review.objects.filter(place=place)  # Obtener sus reseñas

    return render(request, 'reviews.html', {'reviews': reviews, 'query': query})