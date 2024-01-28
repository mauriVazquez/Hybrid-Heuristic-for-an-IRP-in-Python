import base64
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
from django.shortcuts import render
from main import main
from entidades.models import Cliente, Proveedor
from soluciones.models import Solucion, Ruta, Visita
from ZonaTransporte.models import Vehiculo
from django.http import JsonResponse
from datetime import datetime
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
    horizon_length = int(request.GET['HorizonLength'])
    politica_reabastecimiento = request.GET['PoliticaReabastecimiento']
    proveedor_id = request.GET['ProveedorId']
    if soluciones == '{}':
        soluciones = main(
            horizon_length, 
            politica_reabastecimiento,
            proveedor_id,
            str(request.GET.getlist('clientes')),
            int(vehiculo.capacidad)
        ) 
        request.session['soluciones'] = str(soluciones)
    else:
        soluciones = eval(soluciones)
    return render(request, "resultados_hair.html", 
        {
            "soluciones":soluciones, 
            "politica_reabastecimiento":politica_reabastecimiento,
            "horizon_length":horizon_length, 
            "patente_vehiculo":vehiculo.patente
        }
    )


def solucion_viewer(request):
    solucion = request.POST['solucion']
    solucion_dict = eval(solucion)
    solucion = solucion_dict['Solucion']
    rutas = solucion['rutas']
    print(rutas)
    imagenes_base64 = []
    bbox_props = dict(boxstyle='round', facecolor='lightgray', alpha=0.95)

    #Descripcion tabular
    linea = "<tr class='bg-white'><td class='font-mono font-medium text-xs leading-6 text-sky-500'>{}</td><td class='font-mono text-xs leading-6 text-indigo-600 whitespace-pre text-center'>{}</td></tr>"
    descripcion = " <table class='w-full'>"
    descripcion += linea.format("Cliente Stockout", ("SI" if solucion_dict['ClienteStockout'] else "NO") )
    descripcion += linea.format("Cliente Overstock", ("SI" if solucion_dict['ClienteOverstock'] else "NO") )
    descripcion += linea.format("Proveedor Stockout", ("SI" if solucion_dict['ProveedorStockout'] else "NO") )
    descripcion += linea.format("Costo de Solución", str(solucion_dict['Costo']))
    descripcion += linea.format("Etiqueta", str(solucion_dict['Tag']))
    descripcion += linea.format("Iteración", str(solucion_dict['iteracion']))
    descripcion += "</table>"


    # Defino un conjunto de todos clientes presentes en la solución, sin duplicar
    todos_los_clientes = []
    for datos in solucion['rutas'].values():
        if datos['clientes'] not in todos_los_clientes:
            todos_los_clientes += datos['clientes']
    
    #Leo el proveedor 
    proveedor = Proveedor.objects.get(id = solucion['proveedor_id'])

    for t in range(len(rutas)):
        info = ""
        x,y = [],[]
        # Marco el proveedor
        plt.plot(proveedor.coord_x, proveedor.coord_y, color='green', linewidth = 3, marker='*', markersize=24)

        #Marco los clientes
        for index, cliente_id in enumerate(rutas[t]['clientes']):
            cliente = Cliente.objects.get(id = cliente_id)
            print(rutas[t]['cantidades'])
            plt.text(cliente.coord_x, cliente.coord_y, "{}".format(index+1), fontsize=16, bbox=bbox_props, color='red', ha='center', va='center')
            x += [cliente.coord_x]
            y += [cliente.coord_y]
            info += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(index+1, cliente.nombre,cliente.direccion, list(rutas[t]['cantidades'])[index])

        x = [proveedor.coord_x] + x + [proveedor.coord_x] 
        y = [proveedor.coord_y] + y + [proveedor.coord_y]
    
    
        plt.plot(x, y)
        plt.title('Tiempo {}'.format(t+1))
        plt.xticks([])
        plt.yticks([])
        margen = 25
        plt.xlim(min(x) - margen, max(x) + margen)
        plt.ylim(min(y) - margen, max(y) + margen)
        # Guardar el gráfico en un BytesIO para luego convertirlo a base64 
        buffer = BytesIO()
        plt.savefig(buffer, format='jpg')
        plt.close()

        # Convertir el gráfico a base64 
        imagen = '<div class="flex flex-wrap w-1/2">'
        imagen += ' <div class="border-solid border-2 border-sky-200">'
        imagen += '     <img class="w-full" src="data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode('utf-8')+'" alt="T">'
        imagen += '     <table class="w-full"><thead><th>Ref</th><th class="w-5/12">Cliente</th><th class="w-5/12">Direccion</th><th>Cantidad</th></thead><tbody>{}</tbody></table>'.format(info)
        imagen += ' </div>'
        imagen += '</div>'
        imagenes_base64.append(imagen)
    return JsonResponse({'descripcion': descripcion, 'imagenes': imagenes_base64}, status=200)


def guardar_ruta(request):
    solucion = request.POST['selected_solution']
    solucion_dict = eval(solucion)
    politica_reabastecimiento = request.POST['politica_reabastecimiento']
    vehiculo = Vehiculo.objects.get(patente = request.POST['patente_vehiculo'])
    solucion_nueva = Solucion.objects.create(
        vehiculo = vehiculo,
        politica_reabastecimiento = politica_reabastecimiento,
        estado = 0,
        costo = solucion_dict['Costo']
    )
    
    rutas = solucion_dict['Solucion']['rutas']
    for index, ruta in rutas.items(): 
        ruta_nueva = Ruta.objects.create(
            fecha = datetime.now(),
            costo = ruta['costo'],
            solucion = solucion_nueva
        )

        for c in range(len(ruta['clientes'])):
            cliente = Cliente.objects.get(id = list(ruta['clientes'])[c])
            visita_nueva = Visita.objects.create(
                ruta = ruta_nueva,
                cliente = cliente,
                orden = c+1,
                cantidad = list(ruta['cantidades'])[c]
            )
    return render(request, 'ruta_guardada.html')