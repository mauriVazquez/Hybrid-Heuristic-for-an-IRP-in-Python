from django.db import models

class ReadOnlyModel(models.Model):
    class Meta:
        abstract = True

    # def save(self, *args, **kwargs):
    #     pass

    def delete(self, *args, **kwargs):
        pass

class Provincia(ReadOnlyModel):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    class Meta:
        verbose_name_plural = "Provincias" 
    def __str__(self):
        return self.nombre
from django.db import models

class Departamento(ReadOnlyModel):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = "Departamentos" 
    def __str__(self):
        return self.nombre

class Localidad(ReadOnlyModel):
    id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = "Localidades" 
    def __str__(self):
        return self.nombre
