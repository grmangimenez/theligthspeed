from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    contenido = {'nombre_sitio': 'The Light Speed'}
    return render(request, 'home/index.html', contenido)