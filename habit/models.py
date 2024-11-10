from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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

    def get_progress_for_date(self, date):
        return self.progress_history.filter(date=date).first()

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
            
            # Guardar el progreso histórico
            today = timezone.now().date()
            progress_record, created = HabitProgress.objects.get_or_create(
                habit=self,
                date=today,
                defaults={'progress': 1}
            )
            
            if not created:
                progress_record.progress += 1
                progress_record.save()
            
            self.save()

    def get_progress_percentage(self):
        return (self.current_progress / self.repetitions) * 100 if self.repetitions > 0 else 0

    def __str__(self):
        return f"{self.name}"
    
class HabitProgress(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='progress_history')
    date = models.DateField()
    progress = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['habit', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.habit.name} - {self.date} - Progress: {self.progress}"

