from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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
    if getattr(request.user, 'tipo_usuario', '') == 'Cliente':
        messages.error(request, "Acceso denegado. Solo administradores o vendedores pueden crear productos.")
        return redirect('dashboard')
        
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
    if getattr(request.user, 'tipo_usuario', '') == 'Cliente':
        messages.error(request, "Acceso denegado. No tienes permisos para editar.")
        return redirect('dashboard')
        
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
    if getattr(request.user, 'tipo_usuario', '') == 'Cliente':
        messages.error(request, "Acceso denegado. No tienes permisos para eliminar.")
        return redirect('dashboard')
        
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

@login_required
def historial_list(request):
    if getattr(request.user, 'tipo_usuario', '') != 'Administrador':
        return redirect('productos_list')
        
    historial = HistorialProducto.objects.all().order_by('-fecha')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'productos/partials/historial_list.html', {'historial': historial})
    return render(request, 'productos/historial_list.html', {'historial': historial})

@login_required
def mi_historial_list(request):
    """Historial filtrado — solo acciones del vendedor autenticado."""
    if getattr(request.user, 'tipo_usuario', '') not in ('Vendedor', 'Administrador'):
        return redirect('dashboard')

    historial = HistorialProducto.objects.filter(usuario=request.user).order_by('-fecha')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'productos/partials/historial_list.html', {'historial': historial, 'mi_historial': True})
    return render(request, 'productos/historial_list.html', {'historial': historial, 'mi_historial': True})

@login_required
def exportar_csv(request):
    if getattr(request.user, 'tipo_usuario', '') == 'Cliente':
        messages.error(request, "Acceso denegado. No puedes exportar el inventario.")
        return redirect('dashboard')
        
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="inventario_treddy.csv"'},
    )
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nombre', 'Categoria', 'Precio Base', 'Stock', 'Estado', 'Fecha de Creacion'])
    
    productos = Producto.objects.all().order_by('-created_at')
    for p in productos:
        writer.writerow([
            p.id, 
            p.nombre, 
            p.categoria, 
            p.precio_base, 
            p.stock, 
            p.estado, 
            p.created_at.strftime('%Y-%m-%d %H:%M')
        ])
        
    return response


# ──────────────────────────────────────────────────────────────
# Favoritos y Carrito (Cliente)
# ──────────────────────────────────────────────────────────────
from django.http import JsonResponse
from .models import Favorito, Pedido, DetallePedido

@login_required
def toggle_favorito(request, pk):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, pk=pk)
        fav, created = Favorito.objects.get_or_create(usuario=request.user, producto=producto)
        if not created:
            fav.delete()
            return JsonResponse({'status': 'removed'})
        return JsonResponse({'status': 'added'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def favoritos_list(request):
    favoritos = Favorito.objects.filter(usuario=request.user).select_related('producto')
    productos = [fav.producto for fav in favoritos]
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'productos/partials/favoritos_list.html', {'productos': productos})
    return render(request, 'productos/favoritos_list.html', {'productos': productos})

@login_required
def add_to_cart(request, pk):
    if request.method == 'POST':
        # Simulación de carrito en sesión
        cart = request.session.get('cart', {})
        pk_str = str(pk)
        if pk_str in cart:
            cart[pk_str] += 1
        else:
            cart[pk_str] = 1
        request.session['cart'] = cart
        return JsonResponse({'status': 'success', 'cart_count': sum(cart.values())})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for pk, qty in cart.items():
        producto = Producto.objects.filter(pk=pk).first()
        if producto:
            subtotal = float(producto.precio_base) * qty
            total += subtotal
            cart_items.append({
                'producto': producto,
                'cantidad': qty,
                'subtotal': subtotal
            })
            
    context = {'cart_items': cart_items, 'total': total}
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'productos/partials/cart.html', context)
    return render(request, 'productos/cart.html', context)

@login_required
def checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "Tu carrito está vacío.")
            return redirect('view_cart')
            
        pedido = Pedido.objects.create(usuario=request.user, total=0)
        total = 0
        for pk, qty in cart.items():
            producto = Producto.objects.filter(pk=pk).first()
            if producto:
                precio = producto.precio_base
                subtotal = precio * qty
                total += subtotal
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    nombre_producto=producto.nombre,
                    cantidad=qty,
                    precio_unitario=precio
                )
                
        pedido.total = total
        pedido.save()
        request.session['cart'] = {}
        messages.success(request, f"Pedido #{pedido.id} realizado con éxito.")
        return redirect('pedidos_list')
    return redirect('view_cart')

@login_required
def pedidos_list(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-created_at')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'productos/partials/pedidos_list.html', {'pedidos': pedidos})
    return render(request, 'productos/pedidos_list.html', {'pedidos': pedidos})

