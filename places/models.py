import requests
from django.db import models

# Create your models here.

import requests
from django.db import models

from django.db import models
import requests

from django.db import models



	
class Place(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    address = models.CharField(max_length=255, default="Dirección no especificada")
    city = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='places/images/', null=True, blank=True)
    
    # Permitir ingresar las coordenadas manualmente
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name



from django.db import models

class Bog(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    address = models.CharField(max_length=255, default="Dirección no especificada")
    city = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='places/images/', null=True, blank=True)
    
    # Permitir ingresar las coordenadas manualmente
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class Barr(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    address = models.CharField(max_length=255, default="Dirección no especificada")
    city = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='places/images/', null=True, blank=True)
    
    # Permitir ingresar las coordenadas manualmente
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    place = models.ForeignKey('Place', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    bog = models.ForeignKey('Bog', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    barr = models.ForeignKey('Barr', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    user_name = models.CharField(max_length=255)
    rating = models.PositiveIntegerField()  # Escala de 1 a 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.rating}/5 en {self.get_place_name()}"

    def get_place_name(self):
        if self.place:
            return self.place.name
        elif self.bog:
            return self.bog.name
        elif self.barr:
            return self.barr.name
        return "Otro"
