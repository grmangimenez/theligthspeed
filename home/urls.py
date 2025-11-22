from django.urls import path
from home import views

urlpatterns = [
    path("",views.index, name='index'),
    path('productos/', views.productos_ordenados, name='productos_ordenados'),
    
    # URLs del CRM - Dashboard
    path('crm/', views.crm_dashboard, name='crm_dashboard'),
    
    # URLs de Contactos
    path('crm/contactos/', views.contactos_list, name='contactos_list'),
    path('crm/contactos/nuevo/', views.contacto_create, name='contacto_create'),
    path('crm/contactos/<int:pk>/', views.contacto_detail, name='contacto_detail'),
    path('crm/contactos/<int:pk>/editar/', views.contacto_edit, name='contacto_edit'),
    path('crm/contactos/<int:pk>/eliminar/', views.contacto_delete, name='contacto_delete'),
    
    # URLs de Oportunidades
    path('crm/oportunidades/', views.oportunidades_list, name='oportunidades_list'),
    path('crm/oportunidades/pipeline/', views.oportunidades_pipeline, name='oportunidades_pipeline'),
    path('crm/oportunidades/nueva/', views.oportunidad_create, name='oportunidad_create'),
    path('crm/oportunidades/<int:pk>/editar/', views.oportunidad_edit, name='oportunidad_edit'),
    path('crm/oportunidades/<int:pk>/eliminar/', views.oportunidad_delete, name='oportunidad_delete'),
    path('crm/oportunidades/<int:pk>/actualizar-estado/', views.oportunidad_update_estado, name='oportunidad_update_estado'),
    
    # URLs de Actividades
    path('crm/actividades/', views.actividades_list, name='actividades_list'),
    path('crm/actividades/nueva/', views.actividad_create, name='actividad_create'),
    path('crm/actividades/<int:pk>/editar/', views.actividad_edit, name='actividad_edit'),
    path('crm/actividades/<int:pk>/eliminar/', views.actividad_delete, name='actividad_delete'),
    path('crm/actividades/<int:pk>/toggle-completada/', views.actividad_toggle_completada, name='actividad_toggle_completada'),
]
