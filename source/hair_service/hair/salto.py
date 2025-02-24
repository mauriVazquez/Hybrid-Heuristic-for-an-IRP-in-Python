from modelos.solucion import Solucion 
from hair.mejora import Mip2
import random
import math

def salto(solucion, iterador_principal, triplets) -> Solucion:
    mejor_solucion = solucion.clonar()
    solucion_antes_salto = mejor_solucion.clonar()
    cambios_realizados = 0  
    temperatura = 1000  # Simulated Annealing

    if not triplets.triplets:
        return mejor_solucion  

    # Ordenar tripletes priorizando clientes con más inventario
    triplets.triplets.sort(key=lambda t: mejor_solucion.inventario_clientes[t[0].id][t[1]], reverse=True)

    while triplets.triplets:
        solucion_base = mejor_solucion.clonar()
        triplet = triplets.obtener_triplet_aleatorio()
        if not triplet:
            break  

        cliente, tiempo_visitado, tiempo_no_visitado = triplet
        cantidad_entregada = solucion_base.rutas[tiempo_visitado].obtener_cantidad_entregada(cliente)

        if cantidad_entregada == 0:
            continue


        if tiempo_no_visitado in solucion_base.tiempos_cliente(cliente):
            continue

        capacidad_disponible = solucion_base.contexto.capacidad_vehiculo - solucion_base.rutas[tiempo_no_visitado].obtener_total_entregado()

        cantidad_movida = max(10, min(cantidad_entregada, capacidad_disponible))

        solucion_base = solucion_base.eliminar_visita(cliente, tiempo_visitado)
        solucion_base = solucion_base.insertar_visita(cliente, tiempo_no_visitado, cantidad_movida)

        # **Exploración máxima: Aceptamos cualquier cambio sin importar si el costo aumenta**
        mejor_solucion = solucion_base.clonar()
        cambios_realizados += 1

        # Enfriamiento de Simulated Annealing
        temperatura *= 0.95

        if cambios_realizados == 0:
            break

    if not mejor_solucion.es_admisible:
        mejor_solucion = solucion_antes_salto.clonar()

    if mejor_solucion.es_admisible:
        mejor_solucion = Mip2.ejecutar(mejor_solucion)

    print(f"SALTO {mejor_solucion}")
    return mejor_solucion
