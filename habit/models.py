from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):

    CATEGORY_NAME = (
        ('hogar',   'hogar'),
        ('escuela', 'escuela'),
        ('trabajo', 'trabajo'),
        ('metas',   'metas'),
        ('otros',   'otros')
        )

    name        = models.CharField(max_length=100, choices=CATEGORY_NAME, default='hogar')
    color       = models.CharField(max_length=25, default='#FF0000')

    def __str__(self):
        return f"{self.name}"

class Habit(models.Model):

    FREQUENCY = (
        ('diario',  'diario'),
        ('semanal', 'semanal'),
        ('mensual', 'mensual')
        )

    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    name         = models.CharField(max_length=100)
    description  = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    frequency    = models.CharField(max_length=50, choices=FREQUENCY, default='diario')
    color        = models.CharField(max_length=25, default='#FF0000')
    category     = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f"{self.name}"

