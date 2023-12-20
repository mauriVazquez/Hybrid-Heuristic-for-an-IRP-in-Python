from django.contrib import admin
from . import models
from localidades.models import Provincia

class ProvinciasAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)
    ordering = ['nombre']

class DepartamentosAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)
    ordering = ['nombre']

class LocalidadesAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)
    ordering = ['nombre']