import requests
from random                     import seed
from datetime                   import datetime
from constantes                 import constantes
#Parámetros variables (penalización y triplets)
from modelos.penalty_variables  import alpha, beta
from modelos.tripletManager     import triplet_manager
from modelos.tabulists          import tabulists
#Procedimientos HAIR
from hair.procedures        import inicializacion, movimiento, mejora, salto

def execute(horizon_length, capacidad_vehiculo, proveedor, clientes, politica_reabastecimiento = None):
    # Se inicializa la semilla
    seed(datetime.now().timestamp())
    
    # Se inicializan las constantes globales
    constantes.inicializar(horizon_length, capacidad_vehiculo, proveedor, clientes, politica_reabastecimiento)
    
    # Se inicializan iteradores
    iterador_principal      = 0
    iteraciones_sin_mejoras = 0
    iteraciones_sin_saltar = 0
    
    #Se genera una solución inicial mediante el procedimiento inicializacion, y se almacena como mejor_solucion.
    solucion = inicializacion()
    mejor_solucion = solucion.clonar()
    
    #Mientras la cantidad de iteraciones sin mejoras de mejor_solucion sea menor o igual a MAX_ITER
    while iteraciones_sin_mejoras < constantes.max_iter:
        iterador_principal += 1
        
        #Se aplica el procedimiento movimiento sobre solucion, para obtener una solución vecina sprima
        solucion_prima = movimiento(solucion, iterador_principal)
        
        #Si solucion_prima tiene un costo menor a la mejor_solución
        if solucion_prima.costo < mejor_solucion.costo:
            #Se aplica mejora sobre solucion_prima para encontrar una posible mejora, al resultado se lo almacena como mejor_solucion
            solucion_prima = mejora(solucion_prima, iterador_principal)
            mejor_solucion = solucion_prima.clonar()
            iteraciones_sin_mejoras = 0
            #Se reinicializan los triplets
            triplet_manager.reiniciar()
        else:
            #Se incrementa la cantidad de iteraciones sin mejora en una unidad
            iteraciones_sin_mejoras += 1
        
        #Se asigna a solucion el contenido de solucion_prima
        solucion = solucion_prima.clonar()

        #Si la cantidad de iteraciones sin mejora es múltiplo de JUMP_ITER
        if (iteraciones_sin_mejoras > 0) and ((iteraciones_sin_mejoras % constantes.jump_iter) == 0): 
            solucion = salto(mejor_solucion, iterador_principal)    
            iteraciones_sin_saltar = 0
            alpha.reiniciar()
            beta.reiniciar()
            tabulists.reiniciar()
            triplet_manager.reiniciar()
        else:
            iteraciones_sin_saltar += 1
            if iteraciones_sin_saltar > ((constantes.jump_iter)/2):
                triplet_manager.eliminar_triplets_solucion(solucion)
        
    print("\n-------------------------------MEJOR SOLUCIÓN-------------------------------\n")
    mejor_solucion.imprimir_detalle()
    
    # mejor_solucion.graficar_rutas()
    return mejor_solucion, iterador_principal
    
def async_execute(recorrido_id, horizon_length, capacidad_vehiculo, proveedor, clientes, user_id):
    print(f"iniciado procesamiento del recorrido id: {recorrido_id}")
    mejor_solucion, iterador_principal = execute(horizon_length, capacidad_vehiculo, proveedor, clientes)
    
    url = f"http://hair-app-nginx/api/recorridos/{recorrido_id}/solucion"
    data = {"mejor_solucion": mejor_solucion.to_json(tag="Mejor Solución",iteration=iterador_principal), 'user_id': user_id}
    requests.post(url,json=data)