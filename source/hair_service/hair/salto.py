from modelos.solucion import Solucion
from modelos.ruta import Ruta
from hair.mejora import mip2_asignacion_clientes

def salto(solucion, iterador_principal, triplets) -> Solucion:
    """
    Aplica un salto en la búsqueda tabú moviendo clientes de periodos donde son típicamente visitados
    a periodos donde no han sido visitados recientemente, asegurando que no haya stockout.
    """
    mejor_solucion = solucion.clonar()
    if not triplets.triplets:
        return mejor_solucion  

    cambios_realizados = 0
    while triplets.triplets:
        cliente, tiempo_visitado, tiempo_no_visitado = triplets.obtener_triplet_aleatorio()

        # Verificar que el cliente realmente se encuentra en el tiempo_visitado y no en el tiempo_no_visitado
        if mejor_solucion.rutas[tiempo_visitado].es_visitado(cliente) and (not mejor_solucion.rutas[tiempo_no_visitado].es_visitado(cliente)):

            # Modificar los tiempos de visita del cliente
            tiempos_cliente_modificado = mejor_solucion.tiempos_cliente(cliente)
            tiempos_cliente_modificado = [t for t in tiempos_cliente_modificado if t != tiempo_visitado]  # Eliminar visita original
            tiempos_cliente_modificado.append(tiempo_no_visitado)  # Agregar en el nuevo tiempo

            # Reconstrucción total de las rutas
            nueva_solucion = Solucion(rutas=tuple(Ruta(tuple([]), tuple([])) for _ in solucion.rutas))
            for c in solucion.contexto.clientes:
                for t in range(solucion.contexto.horizonte_tiempo):
                    if (t in tiempos_cliente_modificado) and (c not in nueva_solucion.rutas[t].clientes):
                        nueva_solucion = nueva_solucion.insertar_visita(c, t)  
                    if (t not in tiempos_cliente_modificado) and (c in nueva_solucion.rutas[t].clientes):
                        nueva_solucion = nueva_solucion.eliminar_visita(c, t)  
                    
                    if nueva_solucion.rutas[t].obtener_cantidad_entregada(c):
                        nueva_solucion = nueva_solucion.eliminar_visita(c, t)
                    
                
            # Verificar si la nueva solución es admisible
            if nueva_solucion.es_admisible:
                mejor_solucion = nueva_solucion.clonar()
                cambios_realizados += 1


    if cambios_realizados == 0:
        return solucion.clonar()  # No se realizó ningún cambio válido

    # # Aplicar mip2_asignacion_clientes solo si la solución sigue siendo admisible
    mejor_solucion = mip2_asignacion_clientes(mejor_solucion)
    
    # print(f"SALTO {mejor_solucion}")
    return mejor_solucion
