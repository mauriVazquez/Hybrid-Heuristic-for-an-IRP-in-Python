import requests
from random import seed
from datetime import datetime
from modelos.contexto_file import contexto_ejecucion
from modelos.gestores import Triplets, TabuLists, FactorPenalizacion, SolutionHistory
from modelos.contexto import Contexto
from hair.inicializacion import inicializacion
from hair.movimiento import movimiento
from hair.mejora import mejora
from hair.salto import salto

def execute(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, politica_reabastecimiento=None):
    """
    Ejecuta la heurística híbrida de búsqueda tabú con detección de ciclos y estancamiento.

    Parámetros:
        horizonte_tiempo (int): Horizonte de planificación.
        capacidad_vehiculo (int): Capacidad del vehículo.
        proveedor (obj): Información del proveedor.
        clientes (list): Lista de clientes.
        politica_reabastecimiento (str): Política de reabastecimiento ('OU' o 'ML').

    Returns:
        tuple: Mejor solución encontrada, cantidad de iteraciones y tiempo de ejecución.
    """
    seed(datetime.now().timestamp())
    contexto = Contexto(
        horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, 
        politica_reabastecimiento, FactorPenalizacion(), FactorPenalizacion()
    )
    contexto_ejecucion.set(contexto)
    
    iterador_principal = 0
    iteraciones_sin_mejoras = 0
    tabulists = TabuLists()
    triplets = Triplets(contexto)
    solution_history = SolutionHistory()
    
    max_ciclos_consecutivos = 3  # Número máximo de ciclos permitidos antes de forzar cambio
    max_stagnation = 10          # Número máximo de iteraciones con la misma solución antes de forzar cambio
    
    start = datetime.now()
    solucion = inicializacion()
    tiempo_best = datetime.now()
    mejor_solucion = solucion.clonar()

    while iteraciones_sin_mejoras < contexto.max_iter:
        iterador_principal += 1
        solucion_prima = movimiento(solucion, tabulists, iterador_principal)

        if (solucion_prima.costo < mejor_solucion.costo):
            solucion_prima = mejora(solucion_prima, iterador_principal)
            mejor_solucion = solucion_prima.clonar()
            tiempo_best = datetime.now() - start
            iteraciones_sin_mejoras = 0
        else:
            iteraciones_sin_mejoras += 1
            
        solucion = solucion_prima.clonar()
        solution_history.add_solution(solucion_prima)

        # **Detectar ciclos**
        cycle_length, repetitions = solution_history.detect_cycle()
        if cycle_length > 0 and repetitions >= 3:
            if solution_history.cycle_count >= max_ciclos_consecutivos:
                iteraciones_hasta_salto = contexto.jump_iter - (iteraciones_sin_mejoras % contexto.jump_iter)
                iteraciones_sin_mejoras += int(iteraciones_hasta_salto *0.6)
                iterador_principal += int(iteraciones_hasta_salto *0.6)
                solution_history.clear()
                # print(f"Ciclo detectado ({cycle_length} de longitud, {repetitions} repeticiones)")
                # print(f"Avanzando {int(iteraciones_hasta_salto *0.6)} iteraciones")
                continue

        # **Detectar estancamiento**
        if solution_history.stagnation_count >= max_stagnation:
            iteraciones_hasta_salto = contexto.jump_iter - (iteraciones_sin_mejoras % contexto.jump_iter)
            iteraciones_sin_mejoras += int(iteraciones_hasta_salto *0.6)
            iterador_principal += int(iteraciones_hasta_salto *0.6)
            solution_history.clear()
            # print(f"Estancamiento detectado en la misma solución por {max_stagnation} iteraciones.")
            # print(f"Avanzando {int(contexto.jump_iter / 2)} iteraciones para evitar bloqueo.")
            continue

        # **Aplicar salto si es necesario**
        if (0 < iteraciones_sin_mejoras < contexto.max_iter) and ((iteraciones_sin_mejoras % contexto.jump_iter) == 0):
            solucion = salto(solucion, iterador_principal, triplets)
            contexto.alfa.reiniciar()
            contexto.beta.reiniciar()
            triplets = Triplets(contexto)
            tabulists = TabuLists()
            solution_history.clear()

    print("\n-------------------------------MEJOR SOLUCIÓN-------------------------------\n")
    mejor_solucion.imprimir_detalle()
    print(f"Tiempo best {tiempo_best}")
    execution_time = datetime.now() - start
    mejor_solucion.graficar_rutas()

    return mejor_solucion, iterador_principal, execution_time




def async_execute(plantilla_id, horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, user_id):
    """
    Ejecuta el proceso de optimización de manera asíncrona y envía los resultados a un endpoint.

    Args:
        plantilla_id (int): ID de la plantilla en proceso.
        horizonte_tiempo (int): Horizonte de planificación.
        capacidad_vehiculo (int): Capacidad del vehículo.
        proveedor (obj): Información del proveedor.
        clientes (list): Lista de clientes.
        user_id (int): ID del usuario solicitante.
    """
    print(f"Iniciado procesamiento de la plantilla ID: {plantilla_id}")
    
    mejor_solucion, iterador_principal, execution_time = execute(
        horizonte_tiempo, capacidad_vehiculo, proveedor, clientes
    )

    requests.post(
        url=f"http://nginx/api/plantillas/{plantilla_id}/solucion",
        json={
            "mejor_solucion": mejor_solucion.__json__(tag="Mejor Solución", iteration=iterador_principal),
            "user_id": user_id,
            "execution_time": execution_time.seconds,
        }
    )
