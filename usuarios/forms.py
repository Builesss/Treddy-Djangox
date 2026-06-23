import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Usuario


# ──────────────────────────────────────────────────────────────
# Formulario de Login
# Capa 1 (HTML5 pattern) + Capa 2 (clean methods / Regex)
# ──────────────────────────────────────────────────────────────
class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@treddy.com',
            # Capa 1 — Regex HTML5
            'pattern': r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$',
            'title': 'Ingrese un correo válido.',
        })
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
            # Capa 1 — Regex HTML5: mín. 8 chars, 1 mayúscula, 1 número
            'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d\w\W]{8,}$',
            'title': 'Mínimo 8 caracteres, una mayúscula y un número.',
        })
    )

    def clean_username(self):
        # Capa 2 — Sanitización en el servidor
        username = self.cleaned_data.get('username', '')
        if not re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', username):
            raise ValidationError(_("El correo contiene caracteres no permitidos."))
        return username


# ──────────────────────────────────────────────────────────────
# Formulario de Registro
# Patrón: DRY con UserCreationForm (identificado como ModelForm / DRY)
# ──────────────────────────────────────────────────────────────
class CustomRegistroForm(UserCreationForm):
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'usuario@treddy.com',
            # Capa 1 — Regex HTML5
            'pattern': r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$',
            'required': True,
        })
    )
    first_name = forms.CharField(
        label="Nombre",
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]{2,30}$',
            'title': 'Solo letras, mínimo 2 caracteres.',
        })
    )
    last_name = forms.CharField(
        label="Apellido",
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]{2,30}$',
            'title': 'Solo letras, mínimo 2 caracteres.',
        })
    )
    telefono = forms.CharField(
        label="Teléfono",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^[\d\s\+\-\(\)]{7,15}$',
            'placeholder': '+57 300 000 0000',
        })
    )

    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'telefono', 'password1', 'password2')

    def clean_first_name(self):
        val = self.cleaned_data.get('first_name', '')
        if not re.match(r'^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]{2,30}$', val):
            raise ValidationError(_("El nombre solo puede contener letras."))
        return val

    def clean_last_name(self):
        val = self.cleaned_data.get('last_name', '')
        if not re.match(r'^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]{2,30}$', val):
            raise ValidationError(_("El apellido solo puede contener letras."))
        return val

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if not re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError(_("El correo no es válido."))
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError(_("Ya existe una cuenta con este correo."))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Asignaciones por defecto (Capa 3 — Modelo)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']   # usamos email como username
        user.tipo_usuario = 'Cliente'
        user.estado = 'Activo'
        if commit:
            user.save()
        return user

# ──────────────────────────────────────────────────────────────
# Formulario de Registro para Administradores
# ──────────────────────────────────────────────────────────────
class AdminRegistroForm(CustomRegistroForm):
    tipo_usuario = forms.ChoiceField(
        label="Rol del Usuario",
        choices=Usuario.ROLES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta(CustomRegistroForm.Meta):
        fields = ('first_name', 'last_name', 'email', 'telefono', 'tipo_usuario', 'password1', 'password2')

    def save(self, commit=True):
        # Evitar llamar al save() de CustomRegistroForm que fuerza 'Cliente'
        user = super(CustomRegistroForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        user.tipo_usuario = self.cleaned_data['tipo_usuario']
        user.estado = 'Activo'
        if commit:
            user.save()
        return user


# ──────────────────────────────────────────────────────────────
# Formulario para Editar Perfil (Cliente/Vendedor/Admin)
# ──────────────────────────────────────────────────────────────
class EditarPerfilForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Nombre",
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]{2,30}$',
        })
    )
    last_name = forms.CharField(
        label="Apellido",
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^[a-zA-ZÁÉÍÓÚáéíóúñÑ\s]{2,30}$',
        })
    )
    telefono = forms.CharField(
        label="Teléfono",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'^[\d\s\+\-\(\)]{7,15}$',
        })
    )

    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'telefono')
