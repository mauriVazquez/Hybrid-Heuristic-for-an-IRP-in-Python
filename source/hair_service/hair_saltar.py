from modelos.mip2 import Mip2

def saltar(solucion,triplet_manager, iterador_principal):
    solucion_base = solucion.clonar()
    mejor_solucion = solucion.clonar()
    
    #Mientras haya triplets
    while triplet_manager.triplets:
        #Se realizan jumps en función de algún triplet random
        cliente, tiempo_visitado, tiempo_not_visitado = triplet_manager.obtener_triplet_aleatorio() 
        if solucion_base.rutas[tiempo_visitado].es_visitado(cliente) and (not solucion_base.rutas[tiempo_not_visitado].es_visitado(cliente)):    
            cantidad_eliminado = solucion_base.rutas[tiempo_visitado].remover_visita(cliente)
            solucion_base.rutas[tiempo_not_visitado].insertar_visita(cliente, cantidad_eliminado, None)
            if not solucion_base.cliente_tiene_desabastecimiento():
                mejor_solucion = solucion_base.clonar()
                
    #Cuando no se puedan hacer mas saltos, se retorna la respuesta de ejecutar el MIP2 sobre la solución encontrada.
    print(f"Salto ({iterador_principal}): {solucion}")
    return Mip2.ejecutar(mejor_solucion)