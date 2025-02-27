import requests
import math
import random
from random import seed
from datetime import datetime
from modelos.contexto_file import contexto_ejecucion
from modelos.gestores import Triplets, TabuLists, SolutionHistory
from modelos.contexto import Contexto
from hair.inicializacion import inicializacion
from hair.movimiento import movimiento
from hair.mejora import mejora
from hair.salto import salto

def execute(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, politica_reabastecimiento=None):
    """
    Ejecuta la heurística híbrida de búsqueda tabú con Simulated Annealing (SA) para evitar mínimos locales.
    """
    seed(datetime.now().timestamp())
    contexto = Contexto(
        horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, 
        politica_reabastecimiento
    )
    contexto_ejecucion.set(contexto)

    iterador_principal = 0
    iteraciones_sin_mejoras = 0
    tabulists = TabuLists()
    triplets = Triplets(contexto)
    solution_history = SolutionHistory()

    max_ciclos_consecutivos = 3
    max_stagnation = 5

    start = datetime.now()
    solucion = inicializacion()
    mejor_solucion = solucion.clonar()
    tiempo_best = datetime.now()

    # **Parámetros de Simulated Annealing**
    T = 100.0  # Temperatura inicial
    alpha = 0.99  # Factor de enfriamiento
    T_min = 0.1  # Temperatura mínima

    while iteraciones_sin_mejoras < contexto.max_iter and T > T_min:
        iterador_principal += 1
        solucion_prima = movimiento(solucion, tabulists, iterador_principal)

        delta = solucion_prima.costo - solucion.costo

        if delta < 0:
            # Se acepta porque es mejor solución
            solucion_prima = mejora(solucion_prima, iterador_principal)
            mejor_solucion = solucion_prima.clonar()
            tiempo_best = datetime.now() - start
            iteraciones_sin_mejoras = 0
        else:
            # **Simulated Annealing: Aceptar soluciones peores con cierta probabilidad**
            probabilidad_aceptacion = math.exp(-delta / T)
            if random.random() < probabilidad_aceptacion:
                solucion_prima = mejora(solucion_prima, iterador_principal)
            else:
                iteraciones_sin_mejoras += 1

        solucion = solucion_prima.clonar()
        solution_history.add_solution(solucion_prima)

        # **Reducción de temperatura**
        T *= alpha

        # **Detectar ciclos**
        cycle_length, repetitions = solution_history.detect_cycle()
        if cycle_length > 0 and repetitions >= 3:
            if solution_history.cycle_count >= max_ciclos_consecutivos:
                iteraciones_hasta_salto = contexto.jump_iter - (iteraciones_sin_mejoras % contexto.jump_iter)
                iteraciones_sin_mejoras += int(iteraciones_hasta_salto * 0.5)
                iterador_principal += int(iteraciones_hasta_salto * 0.5)
                solution_history.clear()
                continue

        # **Detectar estancamiento**
        if solution_history.stagnation_count >= max_stagnation:
            iteraciones_hasta_salto = contexto.jump_iter - (iteraciones_sin_mejoras % contexto.jump_iter)
            iteraciones_sin_mejoras += int(iteraciones_hasta_salto * 0.5)
            iterador_principal += int(iteraciones_hasta_salto * 0.5)
            solution_history.clear()
            continue

        # **Aplicar salto si es necesario**
        if (0 < iteraciones_sin_mejoras < contexto.max_iter) and ((iteraciones_sin_mejoras % contexto.jump_iter) == 0):
            solucion = salto(solucion, iterador_principal, triplets)
            contexto.alfa.reiniciar()
            contexto.beta.reiniciar()
            triplets = Triplets(contexto)
            tabulists = TabuLists()
            solution_history.clear()

    print(f"{politica_reabastecimiento} => Tiempo best {tiempo_best}")
    execution_time = int((datetime.now() - start).total_seconds())
    admisibilidad = 'N' if (not mejor_solucion.es_admisible) else ('F' if mejor_solucion.es_factible else 'A')
    return mejor_solucion, iterador_principal, execution_time, admisibilidad

def async_execute(plantilla_id, horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, user_id):
    """
    Ejecuta el proceso de optimización de manera asíncrona y envía los resultados a un endpoint.
    """
    print(f"Iniciado procesamiento de la plantilla ID: {plantilla_id}")

    mejor_solucion, iterador_principal, execution_time, admisibilidad = execute(
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
