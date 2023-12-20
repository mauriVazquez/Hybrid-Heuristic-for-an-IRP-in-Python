from django.contrib import admin
from ZonaTransporte.models import Vehiculo, Zona
from entidades.models import Cliente, Proveedor
from django.shortcuts import render
from ZonaTransporte.forms import NameForm
from . import models 
from django.utils.safestring import mark_safe

class ZonasAdmin(admin.ModelAdmin):
    
    @admin.display(description= "")
    def crear_producto_individual(self):
         return mark_safe('<a class="button" href="{0}">Ejecutar</a>'.format('/admin/hair/{0}/execute'.format(self.id)))
    @admin.display(description= "Cantidad de proveedores")
    def cant_proveedores(self, zona):
        return len(Proveedor.objects.filter(zona_id=zona.id))
    @admin.display(description= "Cantidad de clientes")
    def cant_clientes(self, zona):
        return len(Cliente.objects.filter(zona_id=zona.id))
    @admin.display(description= "¿Tiene vehículo asignado?")
    def tiene_vehiculo(self, zona):
        return ('NO' if len(Vehiculo.objects.filter(zona_id=zona.id)) == 0 else 'SI') 
    search_fields = ('nombre',)
    list_display = ['nombre','cant_clientes','cant_proveedores','tiene_vehiculo',crear_producto_individual]

class VehiculosAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)
    list_display = ['patente','marca','modelo','zona']

admin.site.register(Vehiculo, VehiculosAdmin)
admin.site.register(Zona, ZonasAdmin)