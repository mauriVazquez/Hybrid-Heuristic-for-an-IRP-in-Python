import uuid
from django.db import models
from localidades.models import Localidad
from ZonaTransporte.models import Zona

class Entidad(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, auto_created=True, editable=False)
    nombre = models.CharField(max_length=100, help_text="Nombre del cliente")
    localidad = models.ForeignKey(Localidad, on_delete=models.CASCADE)
    direccion = models.CharField(max_length=100, help_text="Dirección")
    coord_x = models.FloatField(help_text="Coordenadas x")
    coord_y = models.FloatField(help_text="Coordenadas y")
    costo_almacenamiento = models.FloatField(help_text="Costo de almacenamiento")
    nivel_almacenamiento = models.IntegerField(help_text="Nivel actual")
    nivel_minimo = models.IntegerField(help_text="Nivel de mínimo")
    nivel_maximo = models.IntegerField(help_text="Nivel máximo")
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE)

class Cliente(Entidad):
    nivel_demanda = models.IntegerField(help_text="Nivel de demanda")
    class Meta:
        verbose_name_plural = "Clientes" 

class Proveedor(Entidad):
    nivel_produccion = models.IntegerField(help_text="Nivel de producción")
    class Meta:
        verbose_name_plural = "Proveedores" 