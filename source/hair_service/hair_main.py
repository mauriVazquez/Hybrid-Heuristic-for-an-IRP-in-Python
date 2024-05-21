import requests
from modelos.solucion_utils import inicializar, mover, mejorar, saltar
from modelos.penalty_variables import alpha, beta
from modelos.tripletManager import triplet_manager
from modelos.tabulists import tabulists
from constantes import constantes
from random import seed
from datetime import datetime

def execute(horizon_length, capacidad_vehiculo, proveedor, clientes, politica_reabastecimiento = None):
    #Se inicializa la semilla, las constantes globales, iteradores y solución inicial
    seed(datetime.now().timestamp())
    constantes.inicializar(horizon_length, capacidad_vehiculo, proveedor, clientes, politica_reabastecimiento)
    main_iterator, it_sinmejora = 0, 0
    solucion = inicializar()    
    
    #Se almacena la solución inicial como mejor solución
    mejor_solucion = solucion.clonar()
    
    #Mientras la cantidad de iteraciones sin mejoras de mejor_solucion sea menor o igual a MAX_ITER
    while it_sinmejora <= constantes.max_iter:
        main_iterator += 1
        
        #Se aplica el procedimiento mover sobre solucion, para obtener una solución vecina sprima
        solucion_prima = mover(solucion)
        tabulists.actualizar(solucion, solucion_prima, main_iterator)
        
        #Si solucion_prima tiene un costo menor a la mejor_solución
        if solucion_prima.costo() < mejor_solucion.costo():
            #Se aplica Mejorar sobre solucion_prima para encontrar una posible mejora, al resultado se lo almacena como mejor_solucion
            mejor_solucion = mejorar(solucion_prima)
            print(f"Mejora ({main_iterator}): {solucion_prima}")
            
            #Se reinicializan los triplets
            triplet_manager.__init__()
            it_sinmejora = 0
        else:
            #Se incrementa la cantidad de iteraciones sin mejora en una unidad
            it_sinmejora += 1
        
        #Se asigna a solucion el contenido de solucion_prima
        solucion = solucion_prima.clonar()

        #Si la cantidad de iteraciones sin mejora es múltiple de JUMP_ITER
        if it_sinmejora != 0 and it_sinmejora % constantes.jump_iter == 0 and it_sinmejora < constantes.max_iter: 
            solucion = saltar(solucion, triplet_manager)
            print(f"Salto ({main_iterator}): {solucion}")
            triplet_manager.__init__()
        elif(it_sinmejora % constantes.jump_iter) > (constantes.jump_iter / 2):
            triplet_manager.eliminar_triplets_solucion(solucion)
        
    print("\n-------------------------------MEJOR SOLUCIÓN-------------------------------\n")
    print(mejor_solucion.detail())

    return mejor_solucion, main_iterator
    
async def async_execute(recorrido_id, horizon_length, capacidad_vehiculo, proveedor, clientes):
    print(f"iniciado procesamiento del recorrido id: {recorrido_id}")
    mejor_solucion, main_iterator = execute(horizon_length, capacidad_vehiculo, proveedor, clientes)
    
    url = f"http://hair-app-nginx/api/recorridos/{recorrido_id}/solucion"
    data = {"mejor_solucion": mejor_solucion.to_json(tag="Mejor Solución",iteration=main_iterator)}
    requests.post(url,json=data)
    
# Update alpha and beta (TODO: REVISAR, SON SIEMPRE FEASIBLES)
# alpha.no_factibles() if solucion_prima.es_excedida_capacidad_vehiculo() else alpha.factible()
# beta.no_factibles() if solucion_prima.proveedor_tiene_stockout() else beta.factible()
# print(alpha.value)
        