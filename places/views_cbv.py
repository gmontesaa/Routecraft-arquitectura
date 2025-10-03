from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Place, Review
from .forms import PlaceForm, ReviewForm

class PlaceListView(ListView):
    model = Place
    paginate_by = 12
    template_name = "places/place_list.html"

class PlaceDetailView(DetailView):
    model = Place
    template_name = "places/place_detail.html"

class PlaceCreateView(LoginRequiredMixin, CreateView):
    model = Place
    form_class = PlaceForm
    success_url = reverse_lazy("place_list")

class PlaceUpdateView(LoginRequiredMixin, UpdateView):
    model = Place
    form_class = PlaceForm
    success_url = reverse_lazy("place_list")

class PlaceDeleteView(LoginRequiredMixin, DeleteView):
    model = Place
    success_url = reverse_lazy("place_list")

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    def get_success_url(self): return self.object.place.get_absolute_url()
