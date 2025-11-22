from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


# Modelos del CRM

class Empresa(models.Model):
    nombre = models.CharField(max_length=200)
    sitio_web = models.URLField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Etiqueta(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#3498db')  # Color hexadecimal

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Contacto(models.Model):
    nombre = models.CharField(max_length=200)
    correo = models.EmailField(validators=[EmailValidator()])
    telefono = models.CharField(max_length=20, blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True, related_name='contactos')
    notas = models.TextField(blank=True, null=True)
    etiquetas = models.ManyToManyField(Etiqueta, blank=True, related_name='contactos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Oportunidad(models.Model):
    ESTADO_CHOICES = [
        ('nuevo', 'Nuevo'),
        ('en_progreso', 'En Progreso'),
        ('ganado', 'Ganado'),
        ('perdido', 'Perdido'),
    ]

    titulo = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='nuevo')
    fecha_estimada_cierre = models.DateField()
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, related_name='oportunidades')
    notas = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name_plural = 'Oportunidades'

    def __str__(self):
        return f"{self.titulo} - {self.get_estado_display()}"


class Actividad(models.Model):
    TIPO_CHOICES = [
        ('llamada', 'Llamada'),
        ('correo', 'Correo'),
        ('reunion', 'Reunión'),
        ('tarea', 'Tarea'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(default=timezone.now)
    contacto = models.ForeignKey(Contacto, on_delete=models.CASCADE, null=True, blank=True, related_name='actividades')
    oportunidad = models.ForeignKey(Oportunidad, on_delete=models.CASCADE, null=True, blank=True, related_name='actividades')
    completada = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.titulo}"
