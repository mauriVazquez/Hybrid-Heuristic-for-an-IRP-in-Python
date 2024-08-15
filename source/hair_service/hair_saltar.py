from modelos.mip2 import Mip2

def saltar(solucion, triplet_manager, iterador_principal):
    mejor_solucion = solucion.clonar()
    
    #Mientras haya triplets
    while triplet_manager.triplets:
        solucion_base = mejor_solucion.clonar()
        
        #Se realizan jumps en función de algún triplet random
        cliente, tiempo_visitado, tiempo_not_visitado = triplet_manager.obtener_triplet_aleatorio() 
           
        cantidad_eliminado = solucion_base.rutas[tiempo_visitado].remover_visita(cliente)
        solucion_base.rutas[tiempo_not_visitado].insertar_visita(cliente, cantidad_eliminado, None)
        
        if all(c >= 0 for c in solucion_base.obtener_niveles_inventario_cliente(cliente)):
            mejor_solucion = solucion_base.clonar()
                
    #Cuando no se puedan hacer mas saltos, se retorna la respuesta de ejecutar el MIP2 sobre la solución encontrada.
    mejor_solucion = Mip2.ejecutar(mejor_solucion)
    print(f"Salto ({iterador_principal}): {mejor_solucion}")
    return mejor_solucion.clonar()