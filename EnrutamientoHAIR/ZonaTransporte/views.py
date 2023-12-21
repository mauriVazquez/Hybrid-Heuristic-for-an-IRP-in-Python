import base64, ast
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')
from io import BytesIO
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from main import main
from entidades.models import Cliente, Proveedor
from ZonaTransporte.models import Vehiculo
import json
from uuid import UUID

def hair_form(request,id):
    clientes = Cliente.objects.filter(zona=id)
    vehiculos = Vehiculo.objects.all()
    proveedor = Proveedor.objects.get(zona=id)
    request.session.pop('soluciones', None)
    return render(request, "iniciar_hair.html", {"clientes": clientes, "proveedor":proveedor, "vehiculos":vehiculos})

def resultados_hair(request):
    soluciones = request.session.get('soluciones', '{}')
    vehiculo = Vehiculo.objects.get(patente = request.GET['vehiculo_patente'])
    if soluciones == '{}':
        soluciones = main(
            int(request.GET['HorizonLength']), 
            request.GET['PoliticaReabastecimiento'], 
            request.GET['ProveedorId'], 
            str(request.GET.getlist('clientes')),
            int(vehiculo.capacidad)
        ) 
        request.session['soluciones'] = str(soluciones)
    else:
        soluciones = eval(soluciones)
    return render(request, "resultados_hair.html", {"soluciones":soluciones})

def solucion_viewer(request):
    solucion = request.COOKIES.get('solucion')
    solucion_dict = eval(solucion)
    print(solucion_dict)
    proveedor_id = solucion_dict['proveedor_id']
    rutas = solucion_dict['rutas']
    imagenes_base64 = []
    proveedor = Proveedor.objects.get(id = proveedor_id)
    for i in range(len(rutas)):
        x = [proveedor.coord_x]+[Cliente.objects.get(id = cliente).coord_x for cliente in rutas[i]['clientes']] + [proveedor.coord_x]
        y = [proveedor.coord_y]+[Cliente.objects.get(id = cliente).coord_y for cliente in rutas[i]['clientes']] + [proveedor.coord_y]
        
        plt.plot(x, y)
        plt.title('Tiempo {}'.format(i+1))
        plt.xticks([])
        plt.yticks([])

        # Guardar el gráfico en un BytesIO para luego convertirlo a base64 
        buffer = BytesIO()
        plt.savefig(buffer, format='jpg')
        plt.close()

        # Convertir el gráfico a base64
        imagenes_base64.append(base64.b64encode(buffer.getvalue()).decode('utf-8'))
    
    return render(request, 'ver_rutas.html', {'imagenes_base64': imagenes_base64})
