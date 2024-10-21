from django.db import models
from django.contrib.auth.models import User

class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.usuario.username}: {self.mensaje}"
    
class PreferenciasNotificacion(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    recibir_promociones = models.BooleanField(default=True)
    frecuencia = models.CharField(
        max_length = 10,
        choices = [('diaria','Diaria'), ('semanal','Semanal'), ('mensual', 'Mensual')],
        default = 'semanal'
    )

    def __str__(self):
        return f"Preferencias de {self.usuario.username}"