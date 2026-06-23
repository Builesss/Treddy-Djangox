from django.urls import path
from . import views

urlpatterns = [
    path('', views.producto_list, name='productos_list'),
    path('crear/', views.producto_create, name='producto_create'),
    path('editar/<int:pk>/', views.producto_update, name='producto_update'),
    path('eliminar/<int:pk>/', views.producto_delete, name='producto_delete'),
    path('historial/', views.historial_list, name='historial_list'),
    path('exportar/', views.exportar_csv, name='exportar_csv'),
    
    # Cliente / E-commerce
    path('favorito/toggle/<int:pk>/', views.toggle_favorito, name='toggle_favorito'),
    path('favoritos/', views.favoritos_list, name='favoritos_list'),
    path('carrito/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('carrito/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('pedidos/', views.pedidos_list, name='pedidos_list'),
]
