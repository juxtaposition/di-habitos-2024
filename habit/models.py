from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta


class Category(models.Model):

    CATEGORY_NAME = (
        ('Hogar',   'Hogar'),
        ('Escuela', 'Escuela'),
        ('Trabajo', 'Trabajo'),
        ('Metas',   'Metas'),
        ('Otros',   'Otros')
        )

    name = models.CharField(max_length=100, choices=CATEGORY_NAME, default='Hogar')
    color = models.CharField(max_length=25, default='#FF0000')

    def __str__(self):
        return f"{self.name}"

class Habit(models.Model):
    FREQUENCY = (
        ('Diario', 'Diario'),
        ('Semanal', 'Semanal'),
        ('Mensual', 'Mensual')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    frequency = models.CharField(max_length=50, choices=FREQUENCY, default='Diario')
    color = models.CharField(max_length=25, default='#FF0000')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1, related_name='habits')
    repetitions = models.PositiveIntegerField(default=1)
    current_progress = models.PositiveIntegerField(default=0)
    last_reset = models.DateTimeField(default=timezone.now)

    def reset_progress_if_needed(self):
        now = timezone.now()
        if self.frequency == 'Diario' and self.last_reset.date() < now.date():
            self.current_progress = 0
            self.last_reset = now
        elif self.frequency == 'Semanal' and (now - self.last_reset).days >= 7:
            self.current_progress = 0
            self.last_reset = now
        elif self.frequency == 'Mensual' and (now.year > self.last_reset.year or now.month > self.last_reset.month):
            self.current_progress = 0
            self.last_reset = now
        self.save()

    def increment_progress(self):
        self.reset_progress_if_needed()
        if self.current_progress < self.repetitions:
            self.current_progress += 1
            self.save()

    def get_progress_percentage(self):
        return (self.current_progress / self.repetitions) * 100 if self.repetitions > 0 else 0


    def __str__(self):
        return f"{self.name}"


class HabitNotification(models.Model):
    NOTIFICATION_TYPE = (
        ('initial', 'Inicial'),
        ('follow_up', 'Seguimiento'),
        ('urgent', 'Urgente'),
        ('group', 'Agrupada')  # Para notificaciones múltiples
    )

    FREQUENCY_TYPE = (
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual')
    )

    PRIORITY_LEVELS = (
        (1, 'Alta'),
        (2, 'Media'),
        (3, 'Baja')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    habit = models.ForeignKey('Habit', on_delete=models.CASCADE, null=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE)
    frequency_type = models.CharField(
        max_length=20,
        choices=FREQUENCY_TYPE,
        default='daily'
    )
    priority = models.IntegerField(choices=PRIORITY_LEVELS, default=2)
    message = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField()
    grouped_habits = models.ManyToManyField('Habit', related_name='grouped_notifications', blank=True)

    class Meta:
        ordering = ['priority', '-created_at']

    def generate_message(self):
        """Genera mensajes motivadores basados en el progreso"""
        if self.notification_type == 'group':
            return self._generate_grouped_message()

        progress = self.habit.current_progress
        total = self.habit.repetitions
        remaining = total - progress
        progress_percentage = (progress / total * 100) if total > 0 else 0

        messages = {
            'daily': {
                'initial': f"¡Buenos días! Hoy tienes {total} repeticiones de {self.habit.name}",
                'follow_up': self._get_progress_message(progress_percentage, remaining),
                'urgent': f"¡Último aviso del día! Te faltan {remaining} repeticiones de {self.habit.name}"
            },
            'weekly': {
                'initial': f"¡Comienza la semana! Tienes {total} repeticiones de {self.habit.name} para esta semana",
                'follow_up': self._get_progress_message(progress_percentage, remaining),
                'urgent': f"¡Último día de la semana! Te faltan {remaining} repeticiones de {self.habit.name}"
            },
            'monthly': {
                'initial': f"¡Nuevo mes! Tu objetivo: {total} repeticiones de {self.habit.name}",
                'follow_up': self._get_progress_message(progress_percentage, remaining),
                'urgent': f"¡Últimos días del mes! Te faltan {remaining} repeticiones de {self.habit.name}"
            }
        }

        return messages[self.frequency_type][self.notification_type]

    def _get_progress_message(self, progress_percentage, remaining):
        """Genera mensajes motivadores basados en el porcentaje de progreso"""
        if progress_percentage == 0:
            return f"¡Comienza con {self.habit.name}! Te faltan {remaining} repeticiones"
        elif progress_percentage < 30:
            return f"¡Buen comienzo! Continúa con {self.habit.name}, faltan {remaining} repeticiones"
        elif progress_percentage < 60:
            return f"¡Vas por buen camino! Completa {remaining} repeticiones más de {self.habit.name}"
        elif progress_percentage < 90:
            return f"¡Ya casi lo logras! Solo {remaining} repeticiones más de {self.habit.name}"
        else:
            return f"¡Última repetición de {self.habit.name}! ¡Tú puedes!"

    def _generate_grouped_message(self):
        """Genera un mensaje para múltiples hábitos agrupados"""
        habits_count = self.grouped_habits.count()
        if habits_count == 0:
            return "No hay hábitos pendientes"

        urgent_habits = [h for h in self.grouped_habits.all() if
                         (h.repetitions - h.current_progress) > 0]

        if len(urgent_habits) == 1:
            habit = urgent_habits[0]
            remaining = habit.repetitions - habit.current_progress
            return f"Tienes {remaining} repeticiones pendientes de {habit.name}"
        else:
            habits_summary = [f"{h.name} ({h.repetitions - h.current_progress} pendientes)"
                              for h in urgent_habits[:3]]
            additional = len(urgent_habits) - 3 if len(urgent_habits) > 3 else 0

            summary = ", ".join(habits_summary[:2])
            if additional > 0:
                return f"Hábitos pendientes: {summary} y {additional} más"
            elif len(habits_summary) > 2:
                return f"Hábitos pendientes: {summary} y {habits_summary[2]}"
            else:
                return f"Hábitos pendientes: {summary}"