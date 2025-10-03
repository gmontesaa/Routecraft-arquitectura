from django.db import models
from django.urls import reverse


class Place(models.Model):
    CITY_CHOICES = [
        ('medellin', 'Medellín'),
        ('bogota', 'Bogotá'),
        ('barranquilla', 'Barranquilla'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    address = models.CharField(max_length=255, default="Dirección no especificada")
    city = models.CharField(max_length=20, choices=CITY_CHOICES)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    url = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='places/images/', null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    embedding = models.JSONField(null=True, blank=True)

    # === NUEVOS CAMPOS PARA NORMALIZACIÓN (Actividad 5) ===
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    reviews_count = models.PositiveIntegerField(default=0)

    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(r.rating for r in reviews) / len(reviews)
        return 0

    def get_absolute_url(self):
        """Permite que las CBV (DetailView, UpdateView, etc.) redirijan bien."""
        return reverse("place_detail", args=[self.pk])

    def __str__(self):
        return f"{self.name} - {self.get_city_display()}"


class Review(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="reviews")
    user = models.CharField(max_length=100, default="Anónimo")
    comment = models.TextField()
    rating = models.IntegerField()  # Suponiendo una calificación de 1 a 5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reseña de {self.user} en {self.place.name}"
