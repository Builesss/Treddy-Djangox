from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MinLengthValidator, RegexValidator

class ActiveProductoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

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
    is_deleted = models.BooleanField(default=False)

    objects = ActiveProductoManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        """Soft delete: marcalo como eliminado en lugar de borrarlo físicamente."""
        self.is_deleted = True
        self.save()

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
        return f"{self.accion} - {self.producto.nombre if self.producto else self.nombre} ({self.fecha})"


class Favorito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favoritos')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='favoritos')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'producto')

    def __str__(self):
        return f"{self.usuario.email} - {self.producto.nombre}"


class Pedido(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.email}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    nombre_producto = models.CharField(max_length=150)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.nombre_producto} (Pedido #{self.pedido.id})"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
