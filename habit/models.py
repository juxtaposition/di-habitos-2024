from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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

