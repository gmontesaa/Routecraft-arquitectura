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
    path('', placesviews.home, name='home'),  # Ruta para la página principal
    path('about/', placesviews.about, name='about'),
    
    # Rutas para ciudades
    path('ciudades/medellin/', placesviews.medellin, name='medellin'),
    path('ciudades/bogota/', placesviews.bogota, name='bogota'),
    path('ciudades/barranquilla/', placesviews.barranquilla, name='barranquilla'),

    # Rutas para cuentas de usuario
    path('accounts/', include('accounts.urls')),

    # Ruta para agregar reseñas
    path('add_review/<int:place_id>/<str:city>/', placesviews.add_review, name='add_review'), 

    path('reviews/', placesviews.reviews_page, name='reviews_page'),
]

# Servir archivos estáticos en modo de desarrollo
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
