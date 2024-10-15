from hair.mip2              import Mip2
from modelos.tripletManager import triplet_manager

def saltar(solucion, iterador_principal):
    mejor_solucion = solucion.clonar()
    
    if len(triplet_manager.triplets) > 0:
        #Mientras haya triplets
        while triplet_manager.triplets:
            solucion_base = mejor_solucion.clonar()
            
            #Se realizan jumps en función de algún triplet random
            cliente, tiempo_visitado, tiempo_not_visitado = triplet_manager.obtener_triplet_aleatorio() 

            cantidad_eliminado = solucion_base.rutas[tiempo_visitado].remover_visita(cliente)
            solucion_base.refrescar()
            solucion_base.rutas[tiempo_not_visitado].insertar_visita(cliente, cantidad_eliminado, None)
            solucion_base.refrescar()
            
            if all(c >= 0 for c in solucion_base.inventario_clientes[cliente.id - 1]):
                mejor_solucion = solucion_base.clonar()
                    
        #Cuando no se puedan hacer mas saltos, se retorna la respuesta de ejecutar el MIP2 sobre la solución encontrada.
        mejor_solucion = Mip2.ejecutar(mejor_solucion)
        
    triplet_manager.reiniciar()     
    print(f"Salto ({iterador_principal}): {mejor_solucion}")
    return mejor_solucion.clonar()