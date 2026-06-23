from django.urls import path
from . import views

urlpatterns = [
    path('login/',     views.CustomLoginView.as_view(), name='login'),
    path('logout/',    views.custom_logout,             name='logout'),
    path('dashboard/', views.dashboard_view,            name='dashboard'),
    path('registro/',  views.registro_view,             name='registro'),
    path('usuarios/',  views.usuario_list,              name='usuario_list'),
    path('usuario/eliminar/<int:pk>/',  views.usuario_delete,  name='usuario_delete'),
    path('perfil/editar/', views.editar_perfil,         name='editar_perfil'),
]
