from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    contenido = {'nombre_sitio': 'The Light Speed'}
    return render(request, 'home/index.html', contenido)
    
from .models import Producto

def productos_ordenados(request):
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'home/index.html', {
        'nombre_sitio': 'TheLightSpeed',
        'productos': productos
    })