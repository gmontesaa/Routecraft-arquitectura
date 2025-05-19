from django.db import models

class Events (models.Model):
	Nombre_Evento = models.CharField(max_length=200)
	Resumen = models.TextField()
	imagen = models.ImageField(upload_to='places/images/', null=True, blank=True)
	fecha = models.DateField()
	Ciudad = models.CharField(max_length=200)

	def __str__(self): return self.Nombre_Evento
# Create your models here.
