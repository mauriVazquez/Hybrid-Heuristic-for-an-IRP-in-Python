import math
from modelos.solucion import Solucion
from modelos.contexto_file import contexto_ejecucion
from modelos.ruta import Ruta

def inicializacion():
    contexto = contexto_ejecucion.get()
    solucion = Solucion()

    for cliente in contexto.clientes:
        nivel_almacenamiento = cliente.nivel_almacenamiento
        nivel_demanda = cliente.nivel_demanda
        nivel_minimo = cliente.nivel_minimo
        nivel_maximo = cliente.nivel_maximo

        tiempo_stockout = max(0, (nivel_almacenamiento - nivel_minimo) // nivel_demanda - 1)
        stockout_frequency = max(1, math.ceil((nivel_maximo - nivel_minimo) / nivel_demanda))

        if tiempo_stockout < contexto.horizonte_tiempo:
            cantidad_a_entregar = min(nivel_maximo, contexto.capacidad_vehiculo)
            solucion.rutas[tiempo_stockout].insertar_visita(cliente, cantidad_a_entregar, len(solucion.rutas[tiempo_stockout].clientes))

        for t in range(tiempo_stockout + stockout_frequency, contexto.horizonte_tiempo, stockout_frequency):
            cantidad_a_entregar = min(nivel_maximo, contexto.capacidad_vehiculo - solucion.rutas[t].obtener_total_entregado())
            if cantidad_a_entregar > 0:
                solucion.rutas[t].insertar_visita(cliente, cantidad_a_entregar, len(solucion.rutas[t].clientes))

    solucion.refrescar()
    print(f"Inicio {solucion}")
    return solucion
