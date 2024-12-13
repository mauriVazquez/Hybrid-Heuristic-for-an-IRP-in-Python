import requests
from random                     import seed
from datetime                   import datetime
from hair.contexto import constantes_contexto
#Parámetros variables (penalización y triplets)
from hair.gestores           import Triplets, TabuLists, FactorPenalizacion
#Procedimientos HAIR
from hair.constantes import Constantes
from hair.procedimientos.inicializacion import inicializacion
from hair.procedimientos.movimiento import movimiento
from hair.procedimientos.mejora import mejora
from hair.procedimientos.salto import salto


def execute(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, politica_reabastecimiento = None):
    """
    Algoritmo principal que ejecuta la heurística híbrida de búsqueda tabú para el problema de enrutamiento de inventario.

    Parámetros:
        horizonte_tiempo (int): Horizonte de planificación.
        capacidad_vehiculo (int): Capacidad del vehículo.
        proveedor (obj): Información del proveedor.
        clientes (list): Lista de clientes.
        politica_reabastecimiento (str): Política de reabastecimiento ('OU' o 'ML').

    Returns:
        tuple: Mejor solución encontrada, cantidad de iteraciones y tiempo de ejecución.
    """
    # Inicialización de la semilla, iteradores y constantes
    seed(datetime.now().timestamp())
    constantes = Constantes()
    constantes.inicializar(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, politica_reabastecimiento, FactorPenalizacion(), FactorPenalizacion())
    constantes_contexto.set(constantes)
    
    start = datetime.now()
    iterador_principal = 0
    iteraciones_sin_mejoras = 0
    iteraciones_sin_saltar = 0
    triplets = Triplets()
    tabulists = TabuLists()
    
    
    try:
        # Aplicar el procedimiento de inicialización
        solucion = inicializacion()
        mejor_solucion = solucion.clonar()
    except Exception as e:
        print(f"Error durante la inicialización: {e}")
        return None, iterador_principal, datetime.now() - start
    
    # Bucle principal del algoritmo
    while iteraciones_sin_mejoras < constantes.max_iter:
        iterador_principal += 1
        # print(f"Constantes en la {iteraciones_sin_mejoras} iteracion")
        # print(constantes.alfa.value)
        # print(constantes.beta.value)

        # Aplicar el procedimiento de movimiento
        try:
            solucion_prima = movimiento(solucion, tabulists, iterador_principal)
        except Exception as e:
            print(f"Error en el procedimiento de movimiento: {e}")
            break

        # Evaluar si la nueva solución es mejor
        if solucion_prima.costo < mejor_solucion.costo:
            try:
                solucion_prima = mejora(solucion_prima, iterador_principal)
                mejor_solucion = solucion_prima.clonar()
                iteraciones_sin_mejoras = 0
            except Exception as e:
                print(f"Error en el procedimiento de mejora: {e}")
                break
        else:
            iteraciones_sin_mejoras += 1

        # Actualizar la solución actual
        solucion = solucion_prima.clonar()

        # Procedimiento de salto
        if (iteraciones_sin_mejoras) > 0 and ((iteraciones_sin_mejoras % constantes.jump_iter) == 0):
            try:
                solucion = salto(solucion, iterador_principal, triplets)
                iteraciones_sin_saltar = 0
                constantes.alfa.reiniciar()
                constantes.beta.reiniciar()
                tabulists.reiniciar()
                triplets.reiniciar()
            except Exception as e:
                print(f"Error en el procedimiento de salto: {e}")
                break
        else:
            iteraciones_sin_saltar += 1
            if iteraciones_sin_saltar > (constantes.jump_iter / 2):
                triplets.eliminar_triplets_solucion(solucion)

    # Mostrar la mejor solución encontrada
    print("\n-------------------------------MEJOR SOLUCIÓN-------------------------------\n")
    mejor_solucion.imprimir_detalle()
    execution_time = datetime.now() - start
    mejor_solucion.graficar_rutas()
    return mejor_solucion, iterador_principal, execution_time
    
def async_execute(plantilla_id, horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, user_id):
    print(f"iniciado procesamiento del plantilla id: {plantilla_id}")
    mejor_solucion, iterador_principal, execution_time = execute(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes)
    
    requests.post(
        url     = f"http://nginx/api/plantillas/{plantilla_id}/solucion",
        json    = {
            "mejor_solucion": mejor_solucion.to_json(tag="Mejor Solución",iteration=iterador_principal), 
            'user_id'       : user_id,
            'execution_time': execution_time.seconds 
        }
    )