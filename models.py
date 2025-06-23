from django.db import models
from django.contrib.auth.models import User

class Ubicacion(models.Model):
    nombre = models.CharField("Nombre de ubicación", max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Ubicaciones"

class Dispositivo(models.Model):
    numero_activo = models.CharField("Número de activo", max_length=50, unique=True)
    descripcion = models.CharField("Descripción", max_length=255)
    marca = models.CharField("Marca", max_length=100)
    modelo = models.CharField("Modelo", max_length=100)
    serie = models.CharField("Número de serie", max_length=100, unique=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name="dispositivos")
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="dispositivos_asignados")
   
    def __str__(self):
        return f"{self.descripcion} ({self.numero_activo})"

class MovimientoDispositivo(models.Model):
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE)
    ubicacion_anterior = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='anterior')
    ubicacion_nueva = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='nueva')
    responsable_anterior = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='responsable_anterior_movimientos'
    )
    responsable_nuevo = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='responsable_nuevo_movimientos'
    )
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dispositivo} movido por {self.usuario} el {self.fecha}"
    
    class Meta:
        ordering = ['-fecha']
