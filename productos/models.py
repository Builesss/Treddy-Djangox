from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MinLengthValidator, RegexValidator

class Producto(models.Model):
    ESTADOS = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )
    
    nombre = models.CharField(max_length=150, validators=[MinLengthValidator(3, 'El nombre debe tener al menos 3 caracteres.')])
    descripcion = models.TextField(blank=True, null=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01, 'El precio debe ser mayor a 0.')])
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0, 'El stock no puede ser negativo.')])
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activo')
    categoria = models.CharField(max_length=100, blank=True, null=True, validators=[RegexValidator(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s]+$', 'La categoría solo debe contener letras y números.')])
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

class HistorialProducto(models.Model):
    ACCIONES = (
        ('creacion', 'Creación'),
        ('actualizacion', 'Actualización'),
        ('eliminacion', 'Eliminación'),
    )
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, related_name='historial')
    nombre = models.CharField(max_length=150, blank=True, null=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField(blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=20, choices=ACCIONES)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.accion} - {self.producto.nombre} ({self.fecha})"
