import requests
from random                 import seed
from datetime               import datetime
from modelos.contexto_file     import contexto_ejecucion
from modelos.gestores          import Triplets, TabuLists, FactorPenalizacion
from modelos.contexto          import Contexto
from hair.inicializacion    import inicializacion
from hair.movimiento        import movimiento
from hair.mejora            import mejora
from hair.salto             import salto


def execute(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, politica_reabastecimiento = None, ortools = False):
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
    # Inicialización de la semilla, iteradores y contexto
    seed(datetime.now().timestamp())
    contexto = Contexto(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, politica_reabastecimiento, FactorPenalizacion(), FactorPenalizacion(), ortools)
    contexto_ejecucion.set(contexto)
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
    while iteraciones_sin_mejoras < contexto.max_iter:
        iterador_principal += 1
        # print(f"Contexto en la {iteraciones_sin_mejoras} iteracion")
        # print(contexto.alfa.value)
        # print(contexto.beta.value)

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
                tiempo_best =  datetime.now() - start
                iteraciones_sin_mejoras = 0
            except Exception as e:
                print(f"Error en el procedimiento de mejora: {e}")
                break
        else:
            iteraciones_sin_mejoras += 1

        # Actualizar la solución actual
        solucion = solucion_prima.clonar()

        # Procedimiento de salto
        if (0 < iteraciones_sin_mejoras < contexto.max_iter) and ((iteraciones_sin_mejoras % contexto.jump_iter) == 0):
            try:
                solucion = salto(solucion, iterador_principal, triplets)
                iteraciones_sin_saltar = 0
                contexto.alfa.reiniciar()
                contexto.beta.reiniciar()
                tabulists = TabuLists()
                triplets = Triplets()
            except Exception as e:
                print(f"Error en el procedimiento de salto: {e}")
                break
        else:
            iteraciones_sin_saltar += 1
            if iteraciones_sin_saltar > (contexto.jump_iter / 2):
                triplets.eliminar_triplets_solucion(solucion)


    # Mostrar la mejor solución encontrada
    print("\n-------------------------------MEJOR SOLUCIÓN-------------------------------\n")
    mejor_solucion.imprimir_detalle()
    print(f"tiempo best {tiempo_best}")
    execution_time = datetime.now() - start
    mejor_solucion.graficar_rutas()
    return mejor_solucion, iterador_principal, execution_time
    
def async_execute(plantilla_id, horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, user_id):
    print(f"iniciado procesamiento del plantilla id: {plantilla_id}")
    mejor_solucion, iterador_principal, execution_time = execute(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes)
    
    requests.post(
        url     = f"http://nginx/api/plantillas/{plantilla_id}/solucion",
        json    = {
            "mejor_solucion": mejor_solucion.__json__(tag="Mejor Solución",iteration=iterador_principal), 
            'user_id'       : user_id,
            'execution_time': execution_time.seconds 
        }
    )