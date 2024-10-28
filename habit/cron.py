from django.utils import timezone
from django.db import models
from .models import Habit, HabitNotification
from datetime import datetime, timedelta

def check_and_generate_notifications():
    """
    Función principal que se ejecutará cada 5 minutos para verificar
    y generar notificaciones según sea necesario
    """
    current_time = timezone.now()

    # Generar notificaciones por frecuencia
    generate_daily_notifications(current_time)
    generate_weekly_notifications(current_time)
    generate_monthly_notifications(current_time)

    # Agrupar notificaciones si hay muchas pendientes
    group_pending_notifications()


def group_pending_notifications():
    """Agrupa notificaciones pendientes si hay muchas"""
    from django.contrib.auth.models import User
    users = User.objects.all()

    for user in users:
        pending = HabitNotification.objects.filter(
            user=user,
            status='pending'
        ).count()

        if pending > 5:  # Si hay más de 5 notificaciones pendientes
            habits = Habit.objects.filter(
                user=user,
                current_progress__lt=models.F('repetitions')
            ).order_by('last_reset')

            # Crear notificación agrupada
            group_notification = HabitNotification.objects.create(
                user=user,
                notification_type='group',
                frequency_type='daily',
                priority=1,
                scheduled_for=timezone.now(),
                message=get_grouped_notification_message(habits)
            )

            # Marcar las notificaciones individuales como leídas
            HabitNotification.objects.filter(
                user=user,
                status='pending'
            ).exclude(id=group_notification.id).update(status='read')


def get_grouped_notification_message(habits):
    """Genera un mensaje para notificaciones agrupadas"""
    pending_habits = []
    for habit in habits:
        remaining = habit.repetitions - habit.current_progress
        if remaining > 0:
            pending_habits.append(f"{habit.name} ({remaining} pendientes)")

    if not pending_habits:
        return "No hay hábitos pendientes"
    elif len(pending_habits) == 1:
        return f"Tienes pendiente: {pending_habits[0]}"
    else:
        habits_text = ", ".join(pending_habits[:2])
        additional = len(pending_habits) - 2
        if additional > 0:
            return f"Hábitos pendientes: {habits_text} y {additional} más"
        return f"Hábitos pendientes: {habits_text}"


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


def get_daily_distribution(repetitions):
    """Distribuye las notificaciones a lo largo del día"""
    if repetitions == 1:
        return [8]
    elif repetitions == 2:
        return [8, 16]
    elif repetitions == 3:
        return [8, 14, 19]
    elif repetitions == 4:
        return [8, 12, 16, 20]
    return [8]


def get_weekly_distribution(repetitions):
    """Distribuye las notificaciones a lo largo de la semana"""
    if repetitions == 1:
        return [0]  # Lunes
    elif repetitions == 2:
        return [0, 3]  # Lunes y Jueves
    elif repetitions == 3:
        return [0, 2, 4]  # Lunes, Miércoles y Viernes
    elif repetitions == 4:
        return [0, 1, 3, 4]  # Lunes, Martes, Jueves y Viernes
    return [0]


def get_monthly_distribution(repetitions):
    """Distribuye las notificaciones a lo largo del mes"""
    if repetitions == 1:
        return [1]
    elif repetitions == 2:
        return [1, 15]
    elif repetitions == 3:
        return [1, 10, 20]
    elif repetitions == 4:
        return [1, 8, 15, 22]
    return [1]