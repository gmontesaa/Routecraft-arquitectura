from django.urls import path
from .views_cbv import (
    PlaceListView, PlaceDetailView, PlaceCreateView,
    PlaceUpdateView, PlaceDeleteView, ReviewCreateView
)

urlpatterns = [
    path("places/", PlaceListView.as_view(), name="place_list"),
    path("places/<int:pk>/", PlaceDetailView.as_view(), name="place_detail"),
    path("places/create/", PlaceCreateView.as_view(), name="place_create"),
    path("places/<int:pk>/edit/", PlaceUpdateView.as_view(), name="place_update"),
    path("places/<int:pk>/delete/", PlaceDeleteView.as_view(), name="place_delete"),
    path("reviews/create/", ReviewCreateView.as_view(), name="review_create"),
]
