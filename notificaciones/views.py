from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import Notificacion, PreferenciasNotificacion
from django.http import JsonResponse

# Create your views here.
@login_required
def configurar_notificaciones(request):
    usuario = request.user

    try:
        preferencias = PreferenciasNotificacion.objects.get(usuario=usuario)
    except PreferenciasNotificacion.DoesNotExist:
        preferencias = PreferenciasNotificacion(usuario=usuario)

    if request.method == 'POST':
        recibir_promociones = request.POST.get('recibir_promociones', False) == 'on'
        frecuencia = request.POST.get('frecuencia', 'semanal')

        # Guardar preferencias
        preferencias.recibir_promociones = recibir_promociones
        preferencias.frecuencia = frecuencia
        preferencias.save()

        return redirect('habit_list')

    # Obtener notificaciones del usuario (leídas y no leídas)
    notificaciones = Notificacion.objects.filter(usuario=usuario).order_by('-fecha_creacion')

    contexto = {
        'preferencias': preferencias,
        'notificaciones': notificaciones,  # Pasar todas las notificaciones
    }
    return render(request, 'notify/settings.html', contexto)

def enviar_notificaciones():
    # Filtrar los usuarios que deben recibir notificaciones según su preferencia de frecuencia
    hoy = datetime.now()

    usuarios_diarios = PreferenciasNotificacion.objects.filter(frecuencia='diaria')
    usuarios_semanales = PreferenciasNotificacion.objects.filter(frecuencia='semanal')
    usuarios_mensuales = PreferenciasNotificacion.objects.filter(frecuencia='mensual')

    for preferencias in usuarios_diarios:
        Notificacion.objects.create(usuario=preferencias.usuario, mensaje="¡Promoción diaria!")

    if hoy.weekday() == 0:  # Enviar notificaciones semanales solo los lunes
        for preferencias in usuarios_semanales:
            Notificacion.objects.create(usuario=preferencias.usuario, mensaje="¡Promoción semanal!")

    if hoy.day == 22:  # Enviar notificaciones mensuales solo el primer día del mes
        for preferencias in usuarios_mensuales:
            Notificacion.objects.create(usuario=preferencias.usuario, mensaje="¡Promoción mensual!")
    

@login_required
def marcar_notificaciones_leidas(request):
    if request.method == 'POST':
        try:
            usuario = request.user

            Notificacion.objects.filter(usuario=usuario, leido=False).update(leido=True)

            return JsonResponse({'status': 'ok'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=400)