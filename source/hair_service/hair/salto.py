from modelos.solucion import Solucion
from hair.mejora import Mip2
import random

def salto(solucion, iterador_principal, triplets) -> Solucion:
    mejor_solucion = solucion.clonar()
    cambios_realizados = 0  

    if not triplets.triplets:
        print("No hay tripletes disponibles para saltar.")
        return mejor_solucion  # No hay cambios posibles

    while triplets.triplets:
        solucion_base = mejor_solucion.clonar()
        triplet = triplets.obtener_triplet_aleatorio()
        if not triplet:
            break  # No hay más tripletes disponibles

        cliente, tiempo_visitado, tiempo_no_visitado = triplet
        cantidad_entregada = solucion_base.rutas[tiempo_visitado].obtener_cantidad_entregada(cliente)

        if cantidad_entregada > 0 and not solucion_base.rutas[tiempo_no_visitado].es_visitado(cliente):
            
            # Verificar capacidad del vehículo antes de mover la entrega
            capacidad_disponible = solucion_base.contexto.capacidad_vehiculo - solucion_base.rutas[tiempo_no_visitado].obtener_total_entregado()
            if cantidad_entregada > capacidad_disponible:
                cantidad_entregada = capacidad_disponible  # Ajustar la cantidad a la capacidad disponible

            solucion_base = solucion_base.eliminar_visita(cliente, tiempo_visitado)
            solucion_base = solucion_base.insertar_visita(cliente, tiempo_no_visitado, cantidad_entregada)

            # 🔍 Asegurar que la solución sigue siendo válida después del movimiento
            if solucion_base.es_admisible:
                mejor_solucion = solucion_base.clonar()
                cambios_realizados += 1
            else:
                print(f"⚠️ Movimiento inválido: {cliente.id} en T{tiempo_no_visitado}. Se descarta.")

        # Si se realizaron suficientes cambios, detener el proceso
        if cambios_realizados >= max(1, len(triplets.triplets) // 3):  
            break

    # Aplicar MIP2 solo si la solución después del salto es admisible
    if mejor_solucion.es_admisible:
        mejor_solucion = Mip2.ejecutar(mejor_solucion)
    else:
        print("⚠️ No se aplica MIP2 porque la solución después del salto no es factible.")

    print(f"Salto realizado en iteración {iterador_principal}: {cambios_realizados} cambios.")
    print(f"SALTO {mejor_solucion}")
    
    # 🔥 Aquí llamamos a la función de eliminación de triplets 🔥
    triplets.eliminar_triplets_solucion(mejor_solucion, solucion.contexto.jump_iter)

    return mejor_solucion
