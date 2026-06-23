from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Producto, HistorialProducto
from .forms import ProductoForm

from django.core.paginator import Paginator

@login_required
def producto_list(request):
    query = request.GET.get('q', '')
    if query:
        productos = Producto.objects.filter(nombre__icontains=query).order_by('-created_at')
    else:
        productos = Producto.objects.all().order_by('-created_at')
    
    paginator = Paginator(productos, 12) # 12 productos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'productos': page_obj} # Usar page_obj en lugar de productos completos
    
    # Comportamiento SPA: si es una petición fetch (AJAX), renderizamos solo el fragmento
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'productos/partials/producto_list.html', context)
    
    # Si es acceso directo
    return render(request, 'productos/producto_list.html', context)

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

from .services import procesar_checkout

@login_required
def checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "Tu carrito está vacío.")
            return redirect('view_cart')
            
        pedido = procesar_checkout(request.user, cart)
        if pedido:
            request.session['cart'] = {}
            messages.success(request, f"Pedido #{pedido.id} realizado con éxito.")
            return redirect('pedidos_list')
        else:
            messages.error(request, "Error procesando el pedido.")
            return redirect('view_cart')
            
    return redirect('view_cart')

@login_required
def pedidos_list(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-created_at')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'productos/partials/pedidos_list.html', {'pedidos': pedidos})
from .utils import render_to_pdf

@login_required
def download_pedido_pdf(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
    detalles = pedido.detalles.all()
    
    context = {
        'pedido': pedido,
        'detalles': detalles,
        'usuario': request.user,
    }
    
    pdf = render_to_pdf('productos/pdf/factura_pedido.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_pedido_{pedido.id}.pdf"'
        return response
    return HttpResponse("Error generando el PDF", status=400)
