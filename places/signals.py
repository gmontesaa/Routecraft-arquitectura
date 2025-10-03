from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from .models import Review, Place

def _recompute(place_id: int):
    agg = Review.objects.filter(place_id=place_id).aggregate(
        avg=Avg("rating"), cnt=Count("id")
    )
    Place.objects.filter(id=place_id).update(
        avg_rating=round(float(agg["avg"] or 0.0), 2),
        reviews_count=int(agg["cnt"] or 0)
    )

@receiver(post_save, sender=Review)
def review_saved(sender, instance, **kwargs):
    _recompute(instance.place_id)

@receiver(post_delete, sender=Review)
def review_deleted(sender, instance, **kwargs):
    _recompute(instance.place_id)
