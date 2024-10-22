
from django.urls import path 
from . import views 

urlpatterns = [
    path('settings/', views.configurar_notificaciones, name='configurar_notificaciones'),
    path('user/read/', views.marcar_notificaciones_leidas, name='marcar_notificaciones_leidas'),
]
    