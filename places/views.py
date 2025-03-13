from django.shortcuts import render
from django.http import HttpResponse
from .models import Place, Bog, Barr

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