import math
from modelos.solucion import Solucion
from modelos.contexto_file import contexto_ejecucion
from modelos.ruta import Ruta

def inicializacion():
    contexto = contexto_ejecucion.get()

    # Crear rutas iniciales como una tupla de objetos Ruta (inmutables)
    solucion = Solucion(tuple(Ruta((), ()) for _ in range(contexto.horizonte_tiempo)))

    for cliente in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            inventario_actual = solucion.inventario_clientes[cliente.id][t]
            if(inventario_actual <= cliente.nivel_minimo):
                if contexto.politica_reabastecimiento == "OU":
                    cantidad_entregada = cliente.nivel_maximo - inventario_actual
                else:
                    cantidad_entregada = min(
                        cliente.nivel_maximo - inventario_actual,
                        solucion.inventario_proveedor[t],
                        contexto.capacidad_vehiculo - solucion.rutas[t].obtener_total_entregado()
                    )
                    if cantidad_entregada <= 0:
                        cantidad_entregada = cliente.nivel_minimo
                # Para modificar rutas, creamos una lista temporal basada en la tupla actual
                solucion = solucion.insertar_visita(cliente, t, cantidad_entregada)
                
    print(f"Inicio {solucion}")
    return solucion
