"""
URL configuration for EnrutamientoHAIR project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/hair/results', views.resultados_hair, name='resultados_hair'),
    path('admin/hair/results/solucion', views.solucion_viewer, name='versolucion'),
    path('admin/hair/<str:id>/execute', views.hair_form, name='hair_form'),
    path('admin/hair/guardar_ruta', views.guardar_ruta, name='guardar_ruta'),
    path('admin/', admin.site.urls),
]
