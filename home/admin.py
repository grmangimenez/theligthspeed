from django.contrib import admin
from .models import Producto, Contacto, Empresa, Etiqueta, Oportunidad, Actividad

# Register your models here.
admin.site.register(Producto)

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'sitio_web', 'fecha_creacion')
    search_fields = ('nombre', 'telefono')
    list_filter = ('fecha_creacion',)

@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'color')
    search_fields = ('nombre',)

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'correo', 'telefono', 'empresa', 'fecha_creacion')
    search_fields = ('nombre', 'correo', 'telefono', 'empresa__nombre')
    list_filter = ('empresa', 'etiquetas', 'fecha_creacion')
    filter_horizontal = ('etiquetas',)

@admin.register(Oportunidad)
class OportunidadAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'contacto', 'valor', 'estado', 'fecha_estimada_cierre', 'fecha_creacion')
    search_fields = ('titulo', 'contacto__nombre')
    list_filter = ('estado', 'fecha_creacion', 'fecha_estimada_cierre')
    date_hierarchy = 'fecha_estimada_cierre'

@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'contacto', 'oportunidad', 'fecha', 'completada')
    search_fields = ('titulo', 'descripcion', 'contacto__nombre')
    list_filter = ('tipo', 'completada', 'fecha', 'fecha_creacion')
    date_hierarchy = 'fecha'
