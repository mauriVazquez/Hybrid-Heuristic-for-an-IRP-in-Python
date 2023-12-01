from modelos.solucion import Solucion
from modelos.penalty_variables import alpha, beta
from modelos.mip2 import Mip2
from modelos.tripletManager import triplet_manager
from modelos.tabulists import tabulists
from constantes import constantes

if __name__ == '__main__':
    #Se inicializan los iteradores
    main_iterator, it_sinmejora = 0, 0
    #Se ejecuta el procedimiento inicialización, devolviendo una primera solución candidata
    solucion = Solucion.inicializar()
    #Se almacena la solución inicial como mejor solución
    mejor_solucion = solucion.clonar()

    #Mientras la cantidad de iteraciones sin mejoras de sbest sea menor o igual a MAX_ITER
    while it_sinmejora <= constantes.max_iter:
        #Se aplica el procedimiento mover sobre solucion, para obtener una solución vecina sprima
        solucion_prima = solucion.mover()

        #Si solucion_prima tiene un costo menor a la mejor_solución
        if solucion_prima.costo < mejor_solucion.costo:
            #Se aplica el procedimiento Mejorar sobre solucion_prima para encontrar una posible mejora sobre solucion_prima
            solucion_prima = Solucion.mejorar(solucion_prima)
            #Se almacena solucion_prima como nueva mejor solución
            mejor_solucion = solucion_prima.clonar()
            print(mejor_solucion)
        else:
            #Se incrementa la cantidad de iteraciones sin mejora en una unidad
            it_sinmejora += 1
        
        #Se incrementa el main iterator en una unidad, y se actualiza la lista tabú
        main_iterator += 1
        tabulists.actualizar(solucion, solucion_prima, main_iterator)
        
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
            #Cuando no se puedan hacer mas saltos, se ejecuta el MIP2 sobre la solución encontrada.
            solucion = Mip2.ejecutar(solucion)
        
    print(mejor_solucion.detail())

# Update alpha and beta (TODO: REVISAR, SON SIEMPRE FEASIBLES)
# alpha.no_factibles() if solucion_prima.es_excedida_capacidad_vehiculo() else alpha.factible()
# beta.no_factibles() if solucion_prima.proveedor_tiene_stockout() else beta.factible()
# print(alpha.value)
        