import requests
from hair_inicializar import inicializar
from hair_mover import mover
from hair_mejorar import mejorar
from hair_saltar import saltar
from modelos.penalty_variables import alpha, beta
from modelos.tripletManager import triplet_manager
from constantes import constantes
from random import seed
from datetime import datetime

def execute(horizon_length, capacidad_vehiculo, proveedor, clientes, politica_reabastecimiento = None):
    #Se inicializa la semilla, las constantes globales, iteradores y solución inicial
    seed(datetime.now().timestamp())
    constantes.inicializar(horizon_length, capacidad_vehiculo, proveedor, clientes, politica_reabastecimiento)
    iterador_principal, iteraciones_sin_mejoras = 0, 0
    solucion = inicializar()
    
    #Se almacena la solución inicial como mejor solución
    mejor_solucion = solucion.clonar()
    
    #Mientras la cantidad de iteraciones sin mejoras de mejor_solucion sea menor o igual a MAX_ITER
    while iteraciones_sin_mejoras <= constantes.max_iter:
        iterador_principal += 1
        
        #Se aplica el procedimiento mover sobre solucion, para obtener una solución vecina sprima
        solucion_prima = mover(solucion, mejor_solucion, iterador_principal)
   
        alpha.no_factibles() if solucion_prima.es_excedida_capacidad_vehiculo() else alpha.factible()
        beta.no_factibles() if solucion_prima.proveedor_tiene_desabastecimiento() else beta.factible()
        
        #Si solucion_prima tiene un costo menor a la mejor_solución
        if solucion_prima.costo() < mejor_solucion.costo():
            #Se aplica Mejorar sobre solucion_prima para encontrar una posible mejora, al resultado se lo almacena como mejor_solucion
            mejor_solucion = mejorar(solucion_prima, iterador_principal)
            
            #Se reinicializan los triplets
            triplet_manager.__init__()
            iteraciones_sin_mejoras = 0
        else:
            #Se incrementa la cantidad de iteraciones sin mejora en una unidad
            iteraciones_sin_mejoras += 1
        
        #Se asigna a solucion el contenido de solucion_prima
        solucion = solucion_prima.clonar()

        #Si la cantidad de iteraciones sin mejora es múltiple de JUMP_ITER
        if (iteraciones_sin_mejoras != 0) and ((iteraciones_sin_mejoras % constantes.jump_iter) == 0) and (iteraciones_sin_mejoras < constantes.max_iter): 
            solucion = saltar(solucion, triplet_manager, iterador_principal)
            alpha.reiniciar()
            beta.reiniciar()
            triplet_manager.__init__()      
        elif(iteraciones_sin_mejoras % constantes.jump_iter) > (constantes.jump_iter / 2):
            triplet_manager.eliminar_triplets_solucion(solucion)
        
    print("\n-------------------------------MEJOR SOLUCIÓN-------------------------------\n")
    mejor_solucion.imprimir_detalle()
    return mejor_solucion, iterador_principal
    
def async_execute(recorrido_id, horizon_length, capacidad_vehiculo, proveedor, clientes, user_id):
    print(f"iniciado procesamiento del recorrido id: {recorrido_id}")
    mejor_solucion, iterador_principal = execute(horizon_length, capacidad_vehiculo, proveedor, clientes)
    
    url = f"http://hair-app-nginx/api/recorridos/{recorrido_id}/solucion"
    data = {"mejor_solucion": mejor_solucion.to_json(tag="Mejor Solución",iteration=iterador_principal), 'user_id': user_id}
    requests.post(url,json=data)