from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import models

from .models import Habit, HabitNotification
from .forms import HabitForm


@login_required
def habit_list(request):
    if request.user.is_authenticated:
        habits = Habit.objects.filter(user=request.user)
        userQuery = User.objects.get(pk=request.user.id)

        # Actualizar progreso de hábitos
        for habit in habits:
            habit.reset_progress_if_needed()

        # Obtener las notificaciones para mostrar
        notifications = HabitNotification.objects.filter(
            user=request.user,
            status='pending'
        ).order_by('priority', '-created_at')

        pending_notifications_count = notifications.count()

        return render(request, 'home.html', {
            'habits': habits,
            'username': userQuery.first_name,
            'notifications': notifications,
            'pending_notifications_count': pending_notifications_count
        })
    else:
        return redirect('login')


@login_required
def add_habit(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.category_id = form.data.get('category')
            habit.save()
            return JsonResponse({'success': True})
    else:
        form = HabitForm()

    html = render_to_string('habit/habit_form_modal.html', {'form': form}, request=request)
    return JsonResponse({'html': html})


@login_required
def edit_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
    else:
        form = HabitForm(instance=habit)

    html = render_to_string('habit/habit_form_modal.html', {'form': form}, request=request)
    return JsonResponse({'html': html})


@login_required
def delete_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == 'POST':
        # Eliminar notificaciones asociadas
        HabitNotification.objects.filter(habit=habit).delete()
        habit.delete()
        return redirect('habit_list')
    return render(request, 'habit/confirm_delete.html', {'habit': habit})


@login_required
@require_POST
def increment_progress(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    habit.increment_progress()
    return JsonResponse({
        'current_progress': habit.current_progress,
        'progress_percentage': habit.get_progress_percentage(),
        'repetitions': habit.repetitions
    })


@login_required
@require_POST
def mark_notification_as_read(request, notification_id):
    """Marcar una notificación como leída"""
    try:
        notification = get_object_or_404(
            HabitNotification,
            id=notification_id,
            user=request.user
        )
        notification.status = 'read'
        notification.save()
        return JsonResponse({'success': True})
    except HabitNotification.DoesNotExist:
        return JsonResponse({'success': False})


@login_required
def check_new_notifications(request):
    """Verificar si hay nuevas notificaciones"""
    count = HabitNotification.objects.filter(
        user=request.user,
        status='pending',
        created_at__gt=timezone.now() - timezone.timedelta(minutes=1)
    ).count()

    return JsonResponse({
        'new_notifications': count > 0
    })


# Funciones de generación de notificaciones
def generate_daily_notifications(current_time):
    """Genera notificaciones para hábitos diarios"""
    daily_habits = Habit.objects.filter(frequency='Diario')

    for habit in daily_habits:
        # Notificación inicial del día (8:00 AM)
        if current_time.hour == 8 and current_time.minute < 5:
            create_notification(habit, 'initial', 'daily', 2)

        # Notificaciones distribuidas según repeticiones
        distribution = get_daily_distribution(habit.repetitions)
        if current_time.hour in distribution and current_time.minute < 5:
            create_notification(habit, 'follow_up', 'daily', 2)

        # Notificación de urgencia (8:00 PM)
        if current_time.hour == 20 and current_time.minute < 5:
            if habit.current_progress < habit.repetitions:
                create_notification(habit, 'urgent', 'daily', 1)


def generate_weekly_notifications(current_time):
    """Genera notificaciones para hábitos semanales"""
    weekly_habits = Habit.objects.filter(frequency='Semanal')

    for habit in weekly_habits:
        # Notificación inicial de la semana (Lunes 8:00 AM)
        if current_time.weekday() == 0 and current_time.hour == 8:
            create_notification(habit, 'initial', 'weekly', 2)

        # Notificaciones distribuidas
        distribution = get_weekly_distribution(habit.repetitions)
        if current_time.weekday() in distribution and current_time.hour == 9:
            create_notification(habit, 'follow_up', 'weekly', 2)

        # Notificación de urgencia (Domingo)
        if current_time.weekday() == 6 and current_time.hour == 10:
            if habit.current_progress < habit.repetitions:
                create_notification(habit, 'urgent', 'weekly', 1)


def generate_monthly_notifications(current_time):
    """Genera notificaciones para hábitos mensuales"""
    monthly_habits = Habit.objects.filter(frequency='Mensual')

    for habit in monthly_habits:
        # Notificación inicial del mes
        if current_time.day == 1 and current_time.hour == 8:
            create_notification(habit, 'initial', 'monthly', 2)

        # Notificaciones distribuidas
        distribution = get_monthly_distribution(habit.repetitions)
        if current_time.day in distribution and current_time.hour == 9:
            create_notification(habit, 'follow_up', 'monthly', 2)

        # Notificación de urgencia
        if current_time.day >= 28 and habit.current_progress < habit.repetitions:
            create_notification(habit, 'urgent', 'monthly', 1)


# Funciones auxiliares
def get_daily_distribution(repetitions):
    """Distribuye las notificaciones a lo largo del día"""
    distributions = {
        1: [8],
        2: [8, 16],
        3: [8, 14, 19],
        4: [8, 12, 16, 20]
    }
    return distributions.get(repetitions, [8])


def get_weekly_distribution(repetitions):
    """Distribuye las notificaciones a lo largo de la semana"""
    distributions = {
        1: [0],  # Lunes
        2: [0, 3],  # Lunes y Jueves
        3: [0, 2, 4],  # Lunes, Miércoles y Viernes
        4: [0, 1, 3, 4]  # Lunes, Martes, Jueves y Viernes
    }
    return distributions.get(repetitions, [0])


def get_monthly_distribution(repetitions):
    """Distribuye las notificaciones a lo largo del mes"""
    distributions = {
        1: [1],
        2: [1, 15],
        3: [1, 10, 20],
        4: [1, 8, 15, 22]
    }
    return distributions.get(repetitions, [1])


def create_notification(habit, notification_type, frequency_type, priority):
    """Crea una nueva notificación"""
    return HabitNotification.objects.create(
        user=habit.user,
        habit=habit,
        notification_type=notification_type,
        frequency_type=frequency_type,
        priority=priority,
        scheduled_for=timezone.now(),
        message=get_notification_message(habit, notification_type, frequency_type)
    )


def get_notification_message(habit, notification_type, frequency_type):
    """Genera el mensaje para la notificación"""
    progress = habit.current_progress
    total = habit.repetitions
    remaining = total - progress

    messages = {
        'daily': {
            'initial': f"¡Buenos días! Hoy tienes {total} repeticiones de {habit.name}",
            'follow_up': f"Llevas {progress} de {total} repeticiones de {habit.name}",
            'urgent': f"¡Último aviso del día! Te faltan {remaining} repeticiones de {habit.name}"
        },
        'weekly': {
            'initial': f"¡Comienza la semana! Tienes {total} repeticiones de {habit.name}",
            'follow_up': f"Esta semana llevas {progress} de {total} repeticiones de {habit.name}",
            'urgent': f"¡Último día de la semana! Te faltan {remaining} repeticiones de {habit.name}"
        },
        'monthly': {
            'initial': f"¡Nuevo mes! Tu objetivo: {total} repeticiones de {habit.name}",
            'follow_up': f"Este mes llevas {progress} de {total} repeticiones de {habit.name}",
            'urgent': f"¡Últimos días del mes! Te faltan {remaining} repeticiones de {habit.name}"
        }
    }

    return messages[frequency_type][notification_type]