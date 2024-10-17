from django.db import models
from django.contrib.auth.models import User

class Habit(models.Model):

    FREQUENCY = (
        ('daily', 'daily'),
        ('weekly', 'weekly'),
        ('monthly', 'monthly')
        )

    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    name        = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    frequency   = models.CharField(max_length=50, choices=FREQUENCY, default='daily')
    color       = models.CharField(max_length=25, default='#FF0000')

    def __str__(self):
        return f"{self.name}"
