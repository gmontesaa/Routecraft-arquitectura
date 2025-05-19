from django.shortcuts import render
from .models import Events

def events(request):
	eventss = Events.objects.all().order_by('-fecha')
	return render (request, 'events.html', {'eventss':eventss})

