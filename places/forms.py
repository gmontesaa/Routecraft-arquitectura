from django import forms
from .models import Place, Review

class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ["name","description","category","address","city","cost","avg_rating","reviews_count"]

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["place","user","comment","rating"]

