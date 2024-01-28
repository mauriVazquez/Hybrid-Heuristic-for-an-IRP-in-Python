from django.contrib import admin
from django.urls import path
import ZonaTransporte.views as views
app_name = 'ZonaTransporte'
urlpatterns = [
    path('admin/hair/results', views.resultados_hair, name='resultados_hair'),
    path('admin/hair/results/solucion', views.solucion_viewer, name='versolucion'),
    path('admin/hair/<str:id>/execute', views.hair_form, name='hair_form'),
    path('admin/hair/guardar_ruta', views.guardar_ruta, name='guardar_ruta')
]
