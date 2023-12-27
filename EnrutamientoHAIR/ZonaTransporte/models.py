import uuid
from django.db import models
from datetime import datetime
from django.core.validators import MinValueValidator, MaxValueValidator

class Zona(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, auto_created=True, editable=False)
    nombre = models.CharField(help_text="Nombre de la zona", max_length=50,unique=True)
    def __str__(self):
        return self.nombre

class Vehiculo(models.Model):
    patente = models.CharField(max_length=255, primary_key=True, help_text="Patente", unique=True)
    marca = models.CharField(max_length=50, help_text="Nombre de la marca")
    nombre_modelo = models.CharField(max_length=50, help_text="Nombre del modelo")
    anio = models.IntegerField(help_text="Año",  validators=[MinValueValidator(2010), MaxValueValidator(datetime.now().year+1)])
    color = models.CharField(max_length=50, help_text="Color")
    capacidad = models.IntegerField(help_text="Capacidad del vehículo")
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE)
    def __str__(self):
        return self.patente
