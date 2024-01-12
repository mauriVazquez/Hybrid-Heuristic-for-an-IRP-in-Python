from django.contrib import admin
from . import models 

@admin.register(models.Solucion)
class SolucionAdmin(admin.ModelAdmin):
    list_display = ["id"]