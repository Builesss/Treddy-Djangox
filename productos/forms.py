import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio_base', 'stock', 'estado', 'categoria', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'pattern': r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s]{3,150}$', 'title': 'Mínimo 3 caracteres alfanuméricos.'}),
            'precio_base': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'pattern': r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s]+$', 'title': 'Solo letras y números.'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        if len(nombre) < 3:
            raise ValidationError(_("El nombre debe tener al menos 3 caracteres."))
        return nombre

    def clean_precio_base(self):
        precio = self.cleaned_data.get('precio_base')
        if precio is None or precio <= 0:
            raise ValidationError(_("El precio debe ser mayor a cero."))
        return precio

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is None or stock < 0:
            raise ValidationError(_("El stock no puede ser negativo."))
        return stock

    def clean_categoria(self):
        categoria = self.cleaned_data.get('categoria', '')
        if categoria and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s]+$', categoria):
            raise ValidationError(_("La categoría solo puede contener letras y números."))
        return categoria

