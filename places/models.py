from django.db import models

# Create your models here.

class Place (models.Model):
	name = models.CharField(max_length=100)
	description = models.CharField(max_length=300)
	category = models.CharField(max_length=100)
	image = models.ImageField(upload_to='places/images/')
	adress = models.CharField(max_length=150)
	city = models.CharField(max_length=100)
	cost = models.CharField(max_length=100)
	url = models.URLField(blank=True)
	

class Bog (models.Model):
	name = models.CharField(max_length=100)
	description = models.CharField(max_length=300)
	category = models.CharField(max_length=100)
	image = models.ImageField(upload_to='places/images/')
	adress = models.CharField(max_length=150)
	city = models.CharField(max_length=100)
	cost = models.CharField(max_length=100)
	url = models.URLField(blank=True)
	

class Barr (models.Model):
	name = models.CharField(max_length=100)
	description = models.CharField(max_length=300)
	category = models.CharField(max_length=100)
	image = models.ImageField(upload_to='places/images/')
	adress = models.CharField(max_length=150)
	city = models.CharField(max_length=100)
	cost = models.CharField(max_length=100)
	url = models.URLField(blank=True)
	