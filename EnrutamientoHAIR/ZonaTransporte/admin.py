from django.contrib import admin
from ZonaTransporte.models import Vehiculo, Zona
from entidades.models import Cliente, Proveedor
from django.urls import reverse
from django.utils.html import format_html

class ZonasAdmin(admin.ModelAdmin):
    @admin.display(description= "")
    def iniciar_hair(self):
        url = reverse('ZonaTransporte:hair_form', args=[self.id])
        return format_html('<a class="button" href="{}">Ejecutar</a>', url)
    @admin.display(description= "Cantidad de proveedores")
    def cant_proveedores(self, zona):
        return len(Proveedor.objects.filter(zona=zona.id))
    @admin.display(description= "Cantidad de clientes")
    def cant_clientes(self, zona):
        return len(Cliente.objects.filter(zona=zona.id))
    search_fields = ('nombre',)
    list_display = ['nombre','cant_clientes','cant_proveedores',iniciar_hair]

class VehiculosAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)
    list_display = ['patente','marca','nombre_modelo']

admin.site.register(Vehiculo, VehiculosAdmin)
admin.site.register(Zona, ZonasAdmin)