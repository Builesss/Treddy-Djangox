from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomLoginForm, CustomRegistroForm, AdminRegistroForm


# ──────────────────────────────────────────────────────────────
# Login — Capa 2 y 3 de seguridad (validación de estado)
# ──────────────────────────────────────────────────────────────
class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        # Capa 3 — Solo usuarios Activos pueden ingresar
        if self.request.user.estado != 'Activo':
            messages.error(self.request, "Su cuenta no está activa. Contacte al administrador.")
            logout(self.request)
            return reverse_lazy('login')
        return reverse_lazy('dashboard')

    def form_invalid(self, form):
        messages.error(self.request, "Credenciales incorrectas o caracteres no permitidos.")
        return super().form_invalid(form)


# ──────────────────────────────────────────────────────────────
# Dashboard — Patrón Strategy: delegación por rol + stats reales
# ──────────────────────────────────────────────────────────────
@login_required
def dashboard_view(request):
    from productos.models import Producto
    from .models import Usuario

    user = request.user
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    context = {'user': user}

    if user.tipo_usuario == 'Administrador':
        full_tpl    = 'usuarios/dashboards/admin.html'
        partial_tpl = 'usuarios/dashboards/partials/admin.html'
        context.update({
            'total_usuarios':       Usuario.objects.count(),
            'usuarios_activos':     Usuario.objects.filter(estado='Activo').count(),
            'total_productos':      Producto.objects.filter(estado='activo').count(),
            'productos_bajo_stock': Producto.objects.filter(stock__lt=5).count(),
        })
    elif user.tipo_usuario == 'Vendedor':
        full_tpl    = 'usuarios/dashboards/vendedor.html'
        partial_tpl = 'usuarios/dashboards/partials/vendedor.html'
        context.update({
            'total_productos':      Producto.objects.count(),
            'productos_activos':    Producto.objects.filter(estado='activo').count(),
            'productos_bajo_stock': Producto.objects.filter(stock__lt=5).count(),
            'categorias':           Producto.objects.values('categoria').distinct().count(),
        })
    else:
        full_tpl    = 'usuarios/dashboards/cliente.html'
        partial_tpl = 'usuarios/dashboards/partials/cliente.html'

    # SPA: devolvemos solo el fragmento si es AJAX
    template = partial_tpl if is_ajax else full_tpl
    return render(request, template, context)


# ──────────────────────────────────────────────────────────────
# Registro — Abierto (Público) y Privado (Administrador)
# ──────────────────────────────────────────────────────────────
def registro_view(request):
    is_admin = request.user.is_authenticated and getattr(request.user, 'tipo_usuario', '') == 'Administrador'
    FormClass = AdminRegistroForm if is_admin else CustomRegistroForm
    
    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            form.save()
            if is_admin:
                messages.success(request, "Usuario creado exitosamente desde la administración.")
                # Cuando estamos en SPA (o normal), podemos redirigir al dashboard para ver los cambios o dejar que limpie el form.
                # Redireccionaremos a la misma vista de registro para poder crear otro o salir.
                return redirect('registro')
            else:
                messages.success(request, "¡Cuenta creada exitosamente! Ya puedes iniciar sesión.")
                return redirect('login')
    else:
        form = FormClass()
        
    if is_admin:
        template = 'usuarios/partials/admin_registro.html' if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else 'usuarios/admin_registro.html'
    else:
        template = 'usuarios/registro.html'
        
    return render(request, template, {'form': form})


def custom_logout(request):
    logout(request)
    return redirect('login')
