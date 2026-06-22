from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Producto, HistorialProducto
from .forms import ProductoForm

@login_required
def producto_list(request):
    productos = Producto.objects.all().order_by('-created_at')
    
    # Comportamiento SPA: si es una petición fetch (AJAX), renderizamos solo el fragmento
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'productos/partials/producto_list.html', {'productos': productos})
    
    # Si es acceso directo
    return render(request, 'productos/producto_list.html', {'productos': productos})

@login_required
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            # Patrón Observer simplificado: Registro en Historial
            HistorialProducto.objects.create(
                producto=producto,
                nombre=producto.nombre,
                precio_base=producto.precio_base,
                stock=producto.stock,
                estado=producto.estado,
                accion='creacion',
                usuario=request.user
            )
            return redirect('productos_list')
    else:
        form = ProductoForm()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'productos/partials/producto_form.html', {'form': form, 'action': 'Crear'})
    return render(request, 'productos/producto_form.html', {'form': form, 'action': 'Crear'})

@login_required
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            producto = form.save()
            HistorialProducto.objects.create(
                producto=producto,
                nombre=producto.nombre,
                precio_base=producto.precio_base,
                stock=producto.stock,
                estado=producto.estado,
                accion='actualizacion',
                usuario=request.user
            )
            return redirect('productos_list')
    else:
        form = ProductoForm(instance=producto)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'productos/partials/producto_form.html', {'form': form, 'action': 'Editar', 'producto': producto})
    return render(request, 'productos/producto_form.html', {'form': form, 'action': 'Editar', 'producto': producto})

@login_required
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        HistorialProducto.objects.create(
            producto=producto,
            nombre=producto.nombre,
            accion='eliminacion',
            usuario=request.user
        )
        producto.delete()
        return redirect('productos_list')
        
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'productos/partials/producto_confirm_delete.html', {'producto': producto})
    return render(request, 'productos/producto_confirm_delete.html', {'producto': producto})
