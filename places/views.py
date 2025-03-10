from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    #return HttpResponse(' <h1>Welcome to home page</h1>')
    #return render(request,'home.html')
    return render(request,'home.html', {'name':'Juan Manuel Florez Robledo'})


def about(request):
    return render(request, 'about.html')