"""
URL configuration for routecraft project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from places import views as placesviews
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', placesviews.home, name='home'),
    path('about/', placesviews.about, name='about'),
    
    # Rutas para funciones espec�ficas
    path('accounts/', include('accounts.urls')),
    path("search_places/", placesviews.search_places, name="search_places"),
    path("reviews/<int:place_id>/", placesviews.get_reviews, name="get_reviews"),
  
    path("reviews/", placesviews.reviews_page, name="reviews_page"),
    path('ruta-ai/', placesviews.ruta_ai_view, name='ruta_ai'), 
    path('obtener-ruta-google/', placesviews.obtener_ruta_google_maps, name='obtener_ruta_google'),
    path('events/',include('events.urls')),

    path("", include("places.urls")),


    # ESTA VA AL FINAL
    path('<str:city_name>/', placesviews.city_places, name='city_places'),
]

# Servir archivos est�ticos en modo de desarrollo
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
