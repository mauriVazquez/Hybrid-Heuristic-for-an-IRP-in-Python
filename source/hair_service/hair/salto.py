from modelos.solucion import Solucion
from hair.mejora import mip2_asignacion_clientes
from hair.movimiento import _eliminar_visita, _insertar_visita

def salto(solucion, iterador_principal, triplets) -> Solucion:
    """
    Aplica un salto en la búsqueda tabú moviendo clientes de periodos donde son típicamente visitados
    a periodos donde no han sido visitados recientemente, asegurando que no haya stockout.
    """
    mejor_solucion = solucion.clonar()
    solucion_antes_salto = solucion.clonar()

    if not triplets.triplets:
        return mejor_solucion  

    # Ordenar tripletes priorizando clientes con más inventario
    triplets.triplets.sort(key=lambda t: mejor_solucion.inventario_clientes[t[0].id][t[1]], reverse=True)

    cambios_realizados = 0
    while triplets.triplets:
        cliente, tiempo_visitado, tiempo_no_visitado = triplets.obtener_triplet_aleatorio()
        if not cliente or (tiempo_no_visitado in mejor_solucion.tiempos_cliente(cliente)):
            continue  
        
        nueva_solucion = mejor_solucion.eliminar_visita(cliente, tiempo_visitado)
        nueva_solucion = nueva_solucion.insertar_visita(cliente, tiempo_no_visitado)
        
        if nueva_solucion.es_admisible and nueva_solucion.verificar_politica_reabastecimiento():
            mejor_solucion = nueva_solucion.clonar()
            cambios_realizados += 1

    if cambios_realizados == 0:
        return solucion_antes_salto.clonar()  # No se realizó ningún cambio válido

    # Aplicar mip2_asignacion_clientes solo si la solución sigue siendo admisible
    if mejor_solucion.es_admisible and mejor_solucion.verificar_politica_reabastecimiento():
        mejor_solucion = mip2_asignacion_clientes(mejor_solucion)
    else:
        mejor_solucion = solucion_antes_salto.clonar()

    print(f"SALTO {mejor_solucion}")
    return mejor_solucion
