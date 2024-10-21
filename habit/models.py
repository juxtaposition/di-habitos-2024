from django.db import models
from django.contrib.auth.models import User

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

    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    name         = models.CharField(max_length=100)
    description  = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    frequency    = models.CharField(max_length=50, choices=FREQUENCY, default='Diario')
    color        = models.CharField(max_length=25, default='#FF0000')
    category     = models.ForeignKey(Category, on_delete=models.CASCADE, default=1, related_name='habits')

    def __str__(self):
        return f"{self.name}"

