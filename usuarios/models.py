from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class Usuario(AbstractUser):
    ROLES = (
        ('Administrador', 'Administrador'),
        ('Vendedor', 'Vendedor'),
        ('Cliente', 'Cliente'),
    )
    ESTADOS = (
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
        ('Pendiente', 'Pendiente'),
    )
    
    # AbstractUser ya incluye first_name, last_name, password, is_active, etc.
    email = models.EmailField(unique=True, max_length=150)
    telefono = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'El número de teléfono debe ingresarse en el formato: "+999999999". Hasta 15 dígitos permitidos.')]
    )
    tipo_usuario = models.CharField(max_length=20, choices=ROLES, default='Cliente')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    
    # Usamos email como identificador principal para el login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.tipo_usuario})"
