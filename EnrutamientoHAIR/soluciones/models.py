import uuid
from django.db import models
from ZonaTransporte.models import Vehiculo
from entidades.models import Cliente

class Solucion(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, auto_created=True, editable=False)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    politica_reabastecimiento = models.CharField(max_length=100, help_text="Política de reabastecimiento")
    estado = models.IntegerField(help_text="Estado de la solución")
    costo = models.FloatField(help_text="Costo calculado de la solución")
    class Meta:
        verbose_name_plural = "Soluciones" 


class Ruta(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, auto_created=True, editable=False)
    solucion = models.ForeignKey(Solucion, on_delete=models.CASCADE)
    fecha = models.DateField(help_text="Fecha de entrega")
    costo = models.FloatField(help_text="Costo de la ruta calculada")


class Visita(models.Model):
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, auto_created=True, editable=False)
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    orden = models.IntegerField(help_text="Orden de entrega")
    cantidad = models.IntegerField(help_text="Cantidad entregada")
    realizada = models.DateTimeField(help_text="Fecha y hora de visita")
