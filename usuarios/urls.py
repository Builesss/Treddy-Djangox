from django.urls import path
from . import views

urlpatterns = [
    path('login/',     views.CustomLoginView.as_view(), name='login'),
    path('logout/',    views.custom_logout,             name='logout'),
    path('dashboard/', views.dashboard_view,            name='dashboard'),
    path('registro/',  views.registro_view,             name='registro'),
]
