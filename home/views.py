from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Producto, Contacto, Empresa, Etiqueta, Oportunidad, Actividad


# Vista principal
def index(request):
    contenido = {'nombre_sitio': 'The Light Speed'}
    return render(request, 'home/index.html', contenido)


def productos_ordenados(request):
    productos = Producto.objects.all().order_by('nombre')
    return render(request, 'home/index.html', {
        'nombre_sitio': 'TheLightSpeed',
        'productos': productos
    })


# Vistas del CRM - Dashboard
def crm_dashboard(request):
    total_contactos = Contacto.objects.count()
    total_oportunidades = Oportunidad.objects.count()
    valor_total_oportunidades = Oportunidad.objects.exclude(estado='perdido').aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    oportunidades_por_estado = Oportunidad.objects.values('estado').annotate(
        count=Count('id')
    )
    
    actividades_recientes = Actividad.objects.all()[:10]
    
    context = {
        'total_contactos': total_contactos,
        'total_oportunidades': total_oportunidades,
        'valor_total_oportunidades': valor_total_oportunidades,
        'oportunidades_por_estado': oportunidades_por_estado,
        'actividades_recientes': actividades_recientes,
    }
    return render(request, 'home/crm/dashboard.html', context)


# Vistas de Contactos
def contactos_list(request):
    query = request.GET.get('q', '')
    empresa_id = request.GET.get('empresa', '')
    etiqueta_id = request.GET.get('etiqueta', '')
    grupo = request.GET.get('grupo', '')
    
    contactos = Contacto.objects.all()
    
    if query:
        contactos = contactos.filter(
            Q(nombre__icontains=query) |
            Q(correo__icontains=query) |
            Q(telefono__icontains=query) |
            Q(empresa__nombre__icontains=query)
        )
    
    if empresa_id:
        contactos = contactos.filter(empresa_id=empresa_id)
    
    if etiqueta_id:
        contactos = contactos.filter(etiquetas__id=etiqueta_id)
    
    # Agrupar por empresa o etiqueta
    if grupo == 'empresa':
        contactos = contactos.order_by('empresa__nombre', 'nombre')
    elif grupo == 'etiqueta':
        contactos = contactos.order_by('etiquetas__nombre', 'nombre')
    
    paginator = Paginator(contactos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    empresas = Empresa.objects.all()
    etiquetas = Etiqueta.objects.all()
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'empresa_id': empresa_id,
        'etiqueta_id': etiqueta_id,
        'grupo': grupo,
        'empresas': empresas,
        'etiquetas': etiquetas,
    }
    return render(request, 'home/crm/contactos_list.html', context)


def contacto_create(request):
    empresas = Empresa.objects.all()
    etiquetas = Etiqueta.objects.all()
    
    if request.method == 'POST':
        try:
            contacto = Contacto.objects.create(
                nombre=request.POST.get('nombre'),
                correo=request.POST.get('correo'),
                telefono=request.POST.get('telefono', ''),
                empresa_id=request.POST.get('empresa') or None,
                notas=request.POST.get('notas', ''),
            )
            etiquetas_ids = request.POST.getlist('etiquetas')
            if etiquetas_ids:
                contacto.etiquetas.set(etiquetas_ids)
            messages.success(request, 'Contacto creado exitosamente.')
            return redirect('contactos_list')
        except Exception as e:
            messages.error(request, f'Error al crear contacto: {str(e)}')
    
    context = {
        'empresas': empresas,
        'etiquetas': etiquetas,
    }
    return render(request, 'home/crm/contacto_form.html', context)


def contacto_edit(request, pk):
    contacto = get_object_or_404(Contacto, pk=pk)
    empresas = Empresa.objects.all()
    etiquetas = Etiqueta.objects.all()
    
    if request.method == 'POST':
        try:
            contacto.nombre = request.POST.get('nombre')
            contacto.correo = request.POST.get('correo')
            contacto.telefono = request.POST.get('telefono', '')
            contacto.empresa_id = request.POST.get('empresa') or None
            contacto.notas = request.POST.get('notas', '')
            contacto.save()
            
            etiquetas_ids = request.POST.getlist('etiquetas')
            contacto.etiquetas.set(etiquetas_ids)
            
            messages.success(request, 'Contacto actualizado exitosamente.')
            return redirect('contactos_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar contacto: {str(e)}')
    
    context = {
        'contacto': contacto,
        'empresas': empresas,
        'etiquetas': etiquetas,
    }
    return render(request, 'home/crm/contacto_form.html', context)


def contacto_delete(request, pk):
    contacto = get_object_or_404(Contacto, pk=pk)
    if request.method == 'POST':
        contacto.delete()
        messages.success(request, 'Contacto eliminado exitosamente.')
        return redirect('contactos_list')
    
    context = {'contacto': contacto}
    return render(request, 'home/crm/contacto_confirm_delete.html', context)


def contacto_detail(request, pk):
    contacto = get_object_or_404(Contacto, pk=pk)
    oportunidades = contacto.oportunidades.all()
    actividades = contacto.actividades.all()
    
    context = {
        'contacto': contacto,
        'oportunidades': oportunidades,
        'actividades': actividades,
    }
    return render(request, 'home/crm/contacto_detail.html', context)


# Vistas de Oportunidades
def oportunidades_list(request):
    estado = request.GET.get('estado', '')
    contacto_id = request.GET.get('contacto', '')
    
    oportunidades = Oportunidad.objects.all()
    
    if estado:
        oportunidades = oportunidades.filter(estado=estado)
    
    if contacto_id:
        oportunidades = oportunidades.filter(contacto_id=contacto_id)
    
    oportunidades = oportunidades.order_by('-fecha_creacion')
    
    paginator = Paginator(oportunidades, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    contactos = Contacto.objects.all()
    
    context = {
        'page_obj': page_obj,
        'estado': estado,
        'contacto_id': contacto_id,
        'contactos': contactos,
        'estados': Oportunidad.ESTADO_CHOICES,
    }
    return render(request, 'home/crm/oportunidades_list.html', context)


def oportunidades_pipeline(request):
    estados = ['nuevo', 'en_progreso', 'ganado', 'perdido']
    pipeline = {}
    
    for estado in estados:
        pipeline[estado] = Oportunidad.objects.filter(estado=estado).order_by('-fecha_creacion')
    
    context = {
        'pipeline': pipeline,
        'estados': Oportunidad.ESTADO_CHOICES,
    }
    return render(request, 'home/crm/oportunidades_pipeline.html', context)


def oportunidad_create(request):
    if request.method == 'POST':
        try:
            oportunidad = Oportunidad.objects.create(
                titulo=request.POST.get('titulo'),
                valor=request.POST.get('valor'),
                estado=request.POST.get('estado', 'nuevo'),
                fecha_estimada_cierre=request.POST.get('fecha_estimada_cierre'),
                contacto_id=request.POST.get('contacto'),
                notas=request.POST.get('notas', ''),
            )
            messages.success(request, 'Oportunidad creada exitosamente.')
            return redirect('oportunidades_list')
        except Exception as e:
            messages.error(request, f'Error al crear oportunidad: {str(e)}')
    
    contactos = Contacto.objects.all()
    context = {
        'contactos': contactos,
        'estados': Oportunidad.ESTADO_CHOICES,
    }
    return render(request, 'home/crm/oportunidad_form.html', context)


def oportunidad_edit(request, pk):
    oportunidad = get_object_or_404(Oportunidad, pk=pk)
    
    if request.method == 'POST':
        try:
            oportunidad.titulo = request.POST.get('titulo')
            oportunidad.valor = request.POST.get('valor')
            oportunidad.estado = request.POST.get('estado')
            oportunidad.fecha_estimada_cierre = request.POST.get('fecha_estimada_cierre')
            oportunidad.contacto_id = request.POST.get('contacto')
            oportunidad.notas = request.POST.get('notas', '')
            oportunidad.save()
            
            messages.success(request, 'Oportunidad actualizada exitosamente.')
            return redirect('oportunidades_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar oportunidad: {str(e)}')
    
    contactos = Contacto.objects.all()
    context = {
        'oportunidad': oportunidad,
        'contactos': contactos,
        'estados': Oportunidad.ESTADO_CHOICES,
    }
    return render(request, 'home/crm/oportunidad_form.html', context)


def oportunidad_delete(request, pk):
    oportunidad = get_object_or_404(Oportunidad, pk=pk)
    if request.method == 'POST':
        oportunidad.delete()
        messages.success(request, 'Oportunidad eliminada exitosamente.')
        return redirect('oportunidades_list')
    
    context = {'oportunidad': oportunidad}
    return render(request, 'home/crm/oportunidad_confirm_delete.html', context)


def oportunidad_update_estado(request, pk):
    oportunidad = get_object_or_404(Oportunidad, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(Oportunidad.ESTADO_CHOICES).keys():
            oportunidad.estado = nuevo_estado
            oportunidad.save()
            messages.success(request, f'Oportunidad movida a estado: {oportunidad.get_estado_display()}')
        return redirect('oportunidades_pipeline')
    
    return redirect('oportunidades_pipeline')


# Vistas de Actividades
def actividades_list(request):
    tipo = request.GET.get('tipo', '')
    contacto_id = request.GET.get('contacto', '')
    oportunidad_id = request.GET.get('oportunidad', '')
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    completadas = request.GET.get('completadas', '')
    
    actividades = Actividad.objects.all()
    
    if tipo:
        actividades = actividades.filter(tipo=tipo)
    
    if contacto_id:
        actividades = actividades.filter(contacto_id=contacto_id)
    
    if oportunidad_id:
        actividades = actividades.filter(oportunidad_id=oportunidad_id)
    
    if fecha_desde:
        try:
            fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
            actividades = actividades.filter(fecha__gte=fecha_desde_dt)
        except:
            pass
    
    if fecha_hasta:
        try:
            fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d') + timedelta(days=1)
            actividades = actividades.filter(fecha__lt=fecha_hasta_dt)
        except:
            pass
    
    if completadas == 'si':
        actividades = actividades.filter(completada=True)
    elif completadas == 'no':
        actividades = actividades.filter(completada=False)
    
    paginator = Paginator(actividades, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    contactos = Contacto.objects.all()
    oportunidades = Oportunidad.objects.all()
    
    context = {
        'page_obj': page_obj,
        'tipo': tipo,
        'contacto_id': contacto_id,
        'oportunidad_id': oportunidad_id,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'completadas': completadas,
        'contactos': contactos,
        'oportunidades': oportunidades,
        'tipos': Actividad.TIPO_CHOICES,
    }
    return render(request, 'home/crm/actividades_list.html', context)


def actividad_create(request):
    if request.method == 'POST':
        try:
            actividad = Actividad.objects.create(
                tipo=request.POST.get('tipo'),
                titulo=request.POST.get('titulo'),
                descripcion=request.POST.get('descripcion', ''),
                fecha=request.POST.get('fecha') or timezone.now(),
                contacto_id=request.POST.get('contacto') or None,
                oportunidad_id=request.POST.get('oportunidad') or None,
                completada=request.POST.get('completada') == 'on',
            )
            messages.success(request, 'Actividad creada exitosamente.')
            return redirect('actividades_list')
        except Exception as e:
            messages.error(request, f'Error al crear actividad: {str(e)}')
    
    contactos = Contacto.objects.all()
    oportunidades = Oportunidad.objects.all()
    context = {
        'contactos': contactos,
        'oportunidades': oportunidades,
        'tipos': Actividad.TIPO_CHOICES,
    }
    return render(request, 'home/crm/actividad_form.html', context)


def actividad_edit(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)
    
    if request.method == 'POST':
        try:
            actividad.tipo = request.POST.get('tipo')
            actividad.titulo = request.POST.get('titulo')
            actividad.descripcion = request.POST.get('descripcion', '')
            actividad.fecha = request.POST.get('fecha') or timezone.now()
            actividad.contacto_id = request.POST.get('contacto') or None
            actividad.oportunidad_id = request.POST.get('oportunidad') or None
            actividad.completada = request.POST.get('completada') == 'on'
            actividad.save()
            
            messages.success(request, 'Actividad actualizada exitosamente.')
            return redirect('actividades_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar actividad: {str(e)}')
    
    contactos = Contacto.objects.all()
    oportunidades = Oportunidad.objects.all()
    context = {
        'actividad': actividad,
        'contactos': contactos,
        'oportunidades': oportunidades,
        'tipos': Actividad.TIPO_CHOICES,
    }
    return render(request, 'home/crm/actividad_form.html', context)


def actividad_delete(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)
    if request.method == 'POST':
        actividad.delete()
        messages.success(request, 'Actividad eliminada exitosamente.')
        return redirect('actividades_list')
    
    context = {'actividad': actividad}
    return render(request, 'home/crm/actividad_confirm_delete.html', context)


def actividad_toggle_completada(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)
    actividad.completada = not actividad.completada
    actividad.save()
    messages.success(request, f'Actividad marcada como {"completada" if actividad.completada else "pendiente"}.')
    return redirect('actividades_list')
