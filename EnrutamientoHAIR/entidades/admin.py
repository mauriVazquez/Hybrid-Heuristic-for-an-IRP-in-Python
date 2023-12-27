from django.contrib import admin
from . import models 

# @admin.register(models.Entidad)
# class EntidadesAdmin(admin.ModelAdmin):
#     search_fields = ('nombre',)

@admin.register(models.Cliente)
class ClientesAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)
    list_display = ["nombre", "localidad","direccion", "nivel_almacenamiento"]

@admin.register(models.Proveedor)
class ProveedoresAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)
    list_display = ["nombre", "localidad","direccion", "nivel_almacenamiento"]