from .models import Pedido, DetallePedido, Producto
from django.db import transaction

@transaction.atomic
def procesar_checkout(user, cart):
    """
    Procesa la compra del carrito actual.
    Retorna el pedido creado si fue exitoso, o None si el carrito está vacío.
    """
    if not cart:
        return None

    pedido = Pedido.objects.create(usuario=user, total=0)
    total = 0

    for pk, qty in cart.items():
        producto = Producto.objects.filter(pk=pk).first()
        if producto:
            precio = producto.precio_base
            subtotal = precio * qty
            total += subtotal
            
            # Crear detalle del pedido
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                nombre_producto=producto.nombre,
                cantidad=qty,
                precio_unitario=precio
            )
            
            # Descontar stock si la lógica de negocio lo requiere
            if producto.stock >= qty:
                producto.stock -= qty
            else:
                producto.stock = 0 # O rechazar compra si se requiere validación estricta
            producto.save()

    pedido.total = total
    pedido.save()
    return pedido
