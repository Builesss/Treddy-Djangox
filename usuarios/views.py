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



# ──────────────────────────────────────────────────────────────
# Dashboard — Patrón Strategy: delegación por rol + stats reales
# ──────────────────────────────────────────────────────────────
@login_required
def dashboard_view(request):
    import json
    from django.db.models import Count
    from productos.models import Producto
    from .models import Usuario

    user = request.user
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    context = {'user': user}

    if user.tipo_usuario == 'Administrador':
        full_tpl    = 'usuarios/dashboards/admin.html'
        partial_tpl = 'usuarios/dashboards/partials/admin.html'
        
        # Chart Data
        roles_qs = Usuario.objects.values('tipo_usuario').annotate(count=Count('tipo_usuario'))
        roles_labels = [item['tipo_usuario'] for item in roles_qs]
        roles_data = [item['count'] for item in roles_qs]
        
        estados_qs = Producto.objects.values('estado').annotate(count=Count('estado'))
        estados_labels = [item['estado'] for item in estados_qs]
        estados_data = [item['count'] for item in estados_qs]

        context.update({
            'total_usuarios':       Usuario.objects.count(),
            'usuarios_activos':     Usuario.objects.filter(estado='Activo').count(),
            'total_productos':      Producto.objects.filter(estado='activo').count(),
            'productos_bajo_stock': Producto.objects.filter(stock__lt=5).count(),
            'chart_roles_labels':   json.dumps(roles_labels),
            'chart_roles_data':     json.dumps(roles_data),
            'chart_estados_labels': json.dumps(estados_labels),
            'chart_estados_data':   json.dumps(estados_data),
        })
    elif user.tipo_usuario == 'Vendedor':
        full_tpl    = 'usuarios/dashboards/vendedor.html'
        partial_tpl = 'usuarios/dashboards/partials/vendedor.html'
        
        cat_qs = Producto.objects.values('categoria').annotate(count=Count('categoria'))
        cat_labels = [item['categoria'] for item in cat_qs]
        cat_data = [item['count'] for item in cat_qs]

        context.update({
            'total_productos':      Producto.objects.count(),
            'productos_activos':    Producto.objects.filter(estado='activo').count(),
            'productos_bajo_stock': Producto.objects.filter(stock__lt=5).count(),
            'categorias':           Producto.objects.values('categoria').distinct().count(),
            'chart_cat_labels':     json.dumps(cat_labels),
            'chart_cat_data':       json.dumps(cat_data),
        })
    else:
        full_tpl    = 'usuarios/dashboards/cliente.html'
        partial_tpl = 'usuarios/dashboards/partials/cliente.html'
        # (Catálogo eliminado del dashboard para evitar duplicación con la pestaña Productos)

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
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from django.http import JsonResponse
                    return JsonResponse({'status': 'success', 'message': f"✅ Usuario creado exitosamente."})
                messages.success(request, "Usuario creado exitosamente desde la administración.")
                return redirect('dashboard')
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


# ──────────────────────────────────────────────────────────────
# Gestión de Usuarios (Admin)
# ──────────────────────────────────────────────────────────────
@login_required
def usuario_list(request):
    from .models import Usuario
    if getattr(request.user, 'tipo_usuario', '') != 'Administrador':
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard')
        
    usuarios = Usuario.objects.all().order_by('-date_joined')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    context = {'usuarios': usuarios}
    template = 'usuarios/partials/usuario_list.html' if is_ajax else 'usuarios/usuario_list.html'
    return render(request, template, context)


@login_required
def usuario_delete(request, pk):
    from .models import Usuario
    if getattr(request.user, 'tipo_usuario', '') != 'Administrador':
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        usuario = Usuario.objects.filter(pk=pk).first()
        if not usuario:
            messages.error(request, "El usuario no existe.")
        elif usuario.pk == request.user.pk:
            messages.error(request, "No puedes eliminar tu propia cuenta.")
        else:
            nombre = usuario.get_full_name() or usuario.email
            usuario.delete()
            messages.success(request, f"Usuario «{nombre}» eliminado correctamente.")
    
    return redirect('usuario_list')


# ──────────────────────────────────────────────────────────────
# Edición de Perfil
# ──────────────────────────────────────────────────────────────
@login_required
def editar_perfil(request):
    from .forms import EditarPerfilForm
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('dashboard')
    else:
        form = EditarPerfilForm(instance=request.user)
        
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    template = 'usuarios/partials/editar_perfil.html' if is_ajax else 'usuarios/editar_perfil.html'
    return render(request, template, {'form': form})
