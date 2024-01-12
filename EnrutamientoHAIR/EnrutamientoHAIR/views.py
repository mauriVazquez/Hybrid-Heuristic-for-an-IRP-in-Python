import base64
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
from django.shortcuts import render
from main import main
from entidades.models import Cliente, Proveedor
from ZonaTransporte.models import Vehiculo
from django.http import JsonResponse
matplotlib.use('agg')

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
    solucion = request.POST['solucion']
    solucion_dict = eval(solucion)
    solucion = solucion_dict['Solucion']
    
    # descripcion = []
    descripcion = " <table class=' w-full'>"
    descripcion +="     <tr class='bg-white'><td class='font-mono font-medium text-xs leading-6 text-sky-500'>Cliente Stockout</td><td class='font-mono text-xs leading-6 text-indigo-600 whitespace-pre text-center'>" + ("SI" if solucion_dict['ClienteStockout'] else "NO") +"</td></tr>"
    descripcion +="     <tr class='bg-white'><td class='font-mono font-medium text-xs leading-6 text-sky-500'>Cliente Overstock</td><td class='font-mono text-xs leading-6 text-indigo-600 whitespace-pre text-center'>" + ("SI" if solucion_dict['ClienteOverstock'] else "NO") +"</td></tr>"
    descripcion +="     <tr class='bg-white'><td class='font-mono font-medium text-xs leading-6 text-sky-500'>Proveedor Stockout</td><td class='font-mono text-xs leading-6 text-indigo-600 whitespace-pre text-center'>" + ("SI" if solucion_dict['ProveedorStockout'] else "NO") +"</td></tr>"
    descripcion +="     <tr class='bg-white'><td class='font-mono font-medium text-xs leading-6 text-sky-500'>Costo de Solución</td><td class='font-mono text-xs leading-6 text-indigo-600 whitespace-pre text-center'>"+str(solucion_dict['Costo'])+"</td></tr>"
    descripcion +="     <tr class='bg-white'><td class='font-mono font-medium text-xs leading-6 text-sky-500'>Etiqueta</td><td class='font-mono text-xs leading-6 text-indigo-600 whitespace-pre text-center'>"+str(solucion_dict['Tag'])+"</td></tr>"
    descripcion +="     <tr class='bg-white'><td class='font-mono font-medium text-xs leading-6 text-sky-500'>Iteración</td><td class='font-mono text-xs leading-6 text-indigo-600 whitespace-pre text-center'>"+str(solucion_dict['iteracion'])+"</td></tr>"
    descripcion += "</table>"
    # descripcion += solucion.Solucion


    proveedor_id = solucion['proveedor_id']
    rutas = solucion['rutas']
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
        imagen = '<img width="100%" src="data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode('utf-8')+'" alt="T">'
        imagenes_base64.append(imagen)
    return JsonResponse({'descripcion': descripcion, 'imagenes': imagenes_base64}, status=200)


def guardar_ruta(request):
    solucion = request.POST['solucion'].proveedor_id
    return render(request, 'ruta_guardada.html', {'solucion':solucion})