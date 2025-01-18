from modelos.solucion import Solucion
from hair.mejora import Mip2

def salto(solucion, iterador_principal, triplets) -> Solucion:
    mejor_solucion = solucion.clonar()
    if len(triplets.triplets) > 0:
        #Mientras haya triplets
        while triplets.triplets:
            solucion_base = mejor_solucion.clonar()
            
            #Se realizan jumps en función de algún triplet random
            cliente, tiempo_visitado, tiempo_not_visitado = triplets.obtener_triplet_aleatorio() 

            cantidad_eliminado = solucion_base.rutas[tiempo_visitado].eliminar_visita(cliente)
            solucion_base.refrescar()
            solucion_base.rutas[tiempo_not_visitado].insertar_visita(cliente, cantidad_eliminado, None)
            solucion_base.refrescar()
            
            if all(c >= 0 for c in solucion_base.inventario_clientes.get(cliente.id, None)):
                mejor_solucion = solucion_base.clonar()
                    
        #Cuando no se puedan hacer mas saltos, se retorna la respuesta de ejecutar el MIP2 sobre la solución encontrada.
        mejor_solucion = Mip2.ejecutar(mejor_solucion)
    
    mejor_solucion.refrescar()
    print(f"Salto ({iterador_principal}): {mejor_solucion}")
    return mejor_solucion.clonar()
