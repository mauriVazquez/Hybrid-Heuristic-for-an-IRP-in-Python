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

        # Verificar si cumple con la condición de iteraciones mínimas en el periodo
        if (
            triplets.iteraciones_cliente(cliente, tiempo_visitado) >= solucion.contexto.jump_iter / 2 and
            triplets.iteraciones_cliente(cliente, tiempo_no_visitado) == 0
        ):
            # Verificar capacidad del vehículo antes de mover la entrega
            capacidad_disponible = solucion_base.contexto.capacidad_vehiculo - solucion_base.rutas[tiempo_no_visitado].obtener_total_entregado()
            cantidad_movida = min(cantidad_entregada, capacidad_disponible)

            # Diferenciar la política de reabastecimiento
            if solucion_base.contexto.politica_reabastecimiento == "OU":
                # En OU, la cantidad debe ajustarse al nivel máximo del cliente
                cantidad_movida = min(cantidad_movida, cliente.nivel_maximo - solucion_base.inventario_clientes[cliente.id][tiempo_no_visitado])

                # Asegurar que el cliente no entra en desabastecimiento después del cambio
                if solucion_base.inventario_clientes[cliente.id][tiempo_no_visitado] - cantidad_movida < cliente.nivel_minimo:
                    continue  # Movimiento inválido

            elif solucion_base.contexto.politica_reabastecimiento == "ML":
                # Optimización: Obtener el inventario mínimo futuro una sola vez
                inventario_futuro_min = min(solucion_base.inventario_clientes[cliente.id][tiempo_no_visitado+1:], default=cantidad_movida)

                # En ML, reducir la entrega si no se genera desabastecimiento
                cantidad_movida = min(cantidad_movida, inventario_futuro_min)

                # Asegurar que la cantidad movida no cause desabastecimiento futuro
                if solucion_base.inventario_clientes[cliente.id][tiempo_no_visitado] - cantidad_movida < cliente.nivel_minimo:
                    continue  # Movimiento inválido

            # Aplicar el movimiento
            solucion_base = solucion_base.eliminar_visita(cliente, tiempo_visitado)
            solucion_base = solucion_base.insertar_visita(cliente, tiempo_no_visitado, cantidad_movida)

            # Asegurar que la solución sigue siendo válida después del movimiento
            if solucion_base.es_admisible:
                mejor_solucion = solucion_base.clonar()
                cambios_realizados += 1
            else:
                print(f"⚠️ Movimiento inválido: {cliente.id} en T{tiempo_no_visitado}. Se descarta.")

        # Si no hay más cambios posibles, detener el proceso
        if cambios_realizados == 0:
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
