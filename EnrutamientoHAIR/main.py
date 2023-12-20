import sys, json
from random import seed
from datetime import datetime
from HAIR.modelos.solucion import Solucion
from HAIR.modelos.penalty_variables import alpha, beta
from HAIR.modelos.mip2 import Mip2
from HAIR.modelos.tripletManager import triplet_manager
from HAIR.modelos.tabulists import tabulists
from constantes import constantes


def main(horizon_length, politica_reabastecimiento, proveedor_id, clientes):
    soluciones = []
    seed(datetime.now().microsecond)
    constantes.inicializar_valores(horizon_length, politica_reabastecimiento, proveedor_id, clientes)
    #Se inicializan los iteradores
    main_iterator, it_sinmejora = 0, 0
    #Se ejecuta el procedimiento inicialización, devolviendo una primera solución candidata
    solucion = Solucion.inicializar()
    soluciones.append({"Id": len(soluciones)+1, "Tag":"Inicialización", "iteracion":main_iterator, "Solucion":solucion.to_json(), "Costo":solucion.costo, "ClienteOverstock":solucion.cliente_tiene_overstock(), "ClienteStockout":solucion.cliente_tiene_stockout(), "ProveedorStockout":solucion.proveedor_tiene_stockout()})
    #Se almacena la solución inicial comoa mejor solución
    mejor_solucion = solucion.clonar()

    #Mientras la cantidad de iteraciones sin mejoras de sbest sea menor o igual a MAX_ITER
    while it_sinmejora <= constantes.max_iter:
        #Se aplica el procedimiento mover sobre solucion, para obtener una solución vecina sprima
        solucion_prima = solucion.mover()
        tabulists.actualizar(solucion, solucion_prima, main_iterator)
       
        #Si solucion_prima tiene un costo menor a la mejor_solución
        if solucion_prima.costo < mejor_solucion.costo:
            #Se aplica el procedimiento Mejorar sobre solucion_prima para encontrar una posible mejora sobre solucion_prima
            solucion_prima.mejorar()
            #Se almacena solucion_prima como nueva mejor solución
            mejor_solucion = solucion_prima.clonar()
            print(f"MEJORA! ({main_iterator}) {solucion_prima}")
            soluciones.append({"Id": len(soluciones)+1, "Tag":"Mejora", "iteracion":main_iterator, "Solucion":mejor_solucion.to_json(), "Costo":mejor_solucion.costo, "ClienteOverstock":mejor_solucion.cliente_tiene_overstock(), "ClienteStockout":mejor_solucion.cliente_tiene_stockout(), "ProveedorStockout":mejor_solucion.proveedor_tiene_stockout()})
            triplet_manager.__init__()
            it_sinmejora = 0
        else:
            #Se incrementa la cantidad de iteraciones sin mejora en una unidad
            it_sinmejora += 1
        
        #Se incrementa el main iterator en una unidad, y se actualiza la lista tabú
        main_iterator += 1

        #Se asigna a solucion el contenido de solucion_prima
        solucion = solucion_prima.clonar()

        #Si la cantidad de iteraciones sin mejora es múltiple de JUMP_ITER
        if it_sinmejora != 0 and it_sinmejora % constantes.jump_iter == 0: 
            #Mientras haya triplets
            while triplet_manager.triplets:
                #Se realizan jumps en función de algún triplet random
                solucion_jump = solucion.saltar(triplet_manager.obtener_triplet_aleatorio())
                if not solucion_jump.cliente_tiene_stockout():
                    solucion = solucion_jump.clonar()
            triplet_manager.__init__()
            #Cuando no se puedan hacer mas saltos, se ejecuta el MIP2 sobre la solución encontrada.
            solucion = Mip2.ejecutar(solucion)
            print(f"SALTO! ({main_iterator}) {solucion}")
            soluciones.append({"Id": len(soluciones)+1, "Tag":"Salto", "iteracion":main_iterator, "Solucion":solucion.to_json(), "Costo":solucion.costo, "ClienteOverstock":solucion.cliente_tiene_overstock(), "ClienteStockout":solucion.cliente_tiene_stockout(), "ProveedorStockout":solucion.proveedor_tiene_stockout()})
        elif(it_sinmejora % constantes.jump_iter) > (constantes.jump_iter / 2):
            triplet_manager.eliminar_triplets_solucion(solucion)
    
    print("\n-------------------------------MEJOR SOLUCIÓN-------------------------------\n")
    print(mejor_solucion.detail())
    soluciones.append({"Id": len(soluciones)+1, "Tag":"Final", "iteracion":main_iterator, "Solucion":mejor_solucion.to_json(), "Costo":mejor_solucion.costo, "ClienteOverstock":mejor_solucion.cliente_tiene_overstock(), "ClienteStockout":mejor_solucion.cliente_tiene_stockout(), "ProveedorStockout":mejor_solucion.proveedor_tiene_stockout()})
    return soluciones

# Update alpha and beta (TODO: REVISAR, SON SIEMPRE FEASIBLES)
# alpha.no_factibles() if solucion_prima.es_excedida_capacidad_vehiculo() else alpha.factible()
# beta.no_factibles() if solucion_prima.proveedor_tiene_stockout() else beta.factible()
# print(alpha.value)
        