import uuid
from django.db import models

class Zona(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, auto_created=True, editable=False)
    nombre = models.CharField(help_text="Nombre de la zona", max_length=50,unique=True)
    def __str__(self):
        return self.nombre

class Vehiculo(models.Model):
    patente = models.CharField(max_length=255, primary_key=True, help_text="Patente", unique=True)
    marca = models.CharField(max_length=50, help_text="Nombre de la marca")
    modelo = models.CharField(max_length=50, help_text="Nombre del modelo")
    color = models.CharField(max_length=50, help_text="Color")
    capacidad = models.IntegerField(help_text="Capacidad del vehículo")
    def __str__(self):
        return self.patente

class VehiculoXZona(models.Model):
    vehiculo_id = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    zona_id = models.ForeignKey(Zona, on_delete=models.CASCADE)
    fecha_alta = models.DateField(help_text="Fecha de vinculación")
    fecha_baja = models.DateField(null=True, help_text="Fecha de desvinculación")