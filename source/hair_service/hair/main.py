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

    max_ciclos_consecutivos = 5
    max_stagnation = 10
    
    # Parámetros de Simulated Annealing
    temperatura_inicial = 200 * contexto.horizonte_tiempo * len(contexto.clientes)
    temperatura_final = max(1, 0.01 * temperatura_inicial)  # Evita que sea demasiado alta
    factor_enfriamiento = 0.95
    temperatura_actual = temperatura_inicial
    ultimo_enfriamiento = 0  # Si lo necesitas para control o ajuste dinámico

    
    start = datetime.now()
    solucion = inicializacion()
    mejor_solucion = solucion.clonar()
    tiempo_best = datetime.now()

    while iteraciones_sin_mejoras < contexto.max_iter:
        iterador_principal += 1
        solucion_prima = movimiento(solucion, tabulists, iterador_principal)

        # Criterio de aceptación de Simulated Annealing
        delta_costo = solucion_prima.costo - solucion.costo
        
        # Si la solución es factible y mejor que la mejor solución encontrada hasta ahora
        if solucion_prima.costo < mejor_solucion.costo:
            # Se acepta porque es mejor solución global
            solucion_prima = mejora(solucion_prima, iterador_principal)
            mejor_solucion = solucion_prima.clonar()
            tiempo_best = datetime.now() - start
            iteraciones_sin_mejoras = 0
        # Criterio de aceptación probabilística de SA
        elif solucion.es_factible and (delta_costo < 0) or (random.random() < -delta_costo / max(temperatura_actual, 1e-10) + 0.1):
            iteraciones_sin_mejoras += 1
        else:
            # No se acepta la solución
            iteraciones_sin_mejoras += 1
            solucion_prima = solucion.clonar()  # Revertimos al estado anterior
     
        solucion = solucion_prima.clonar()
        solution_history.add_solution(solucion_prima)

        # Enfriamiento de la temperatura
        if iterador_principal - ultimo_enfriamiento  > 5:  # Actualizar temperatura cada 10 iteraciones
            ultimo_enfriamiento = iterador_principal
            temperatura_actual = max(temperatura_actual * factor_enfriamiento, temperatura_final)

        # **Detectar ciclos**
        cycle_length, repetitions = solution_history.detect_cycle()
        if cycle_length > 0 and repetitions >= 3:
            if solution_history.cycle_count >= max_ciclos_consecutivos:
                iteraciones_hasta_salto = contexto.jump_iter - (iteraciones_sin_mejoras % contexto.jump_iter)
                iteraciones_sin_mejoras += int(iteraciones_hasta_salto * 0.33)
                iterador_principal += int(iteraciones_hasta_salto * 0.33)
                solution_history.clear()
                
        # **Detectar estancamiento**
        if solution_history.stagnation_count >= max_stagnation:
            iteraciones_hasta_salto = contexto.jump_iter - (iteraciones_sin_mejoras % contexto.jump_iter)
            iteraciones_sin_mejoras += int(iteraciones_hasta_salto * 0.33)
            iterador_principal += int(iteraciones_hasta_salto * 0.33)
            solution_history.clear()
            
        # **Aplicar salto si es necesario**
        if (0 < iteraciones_sin_mejoras < contexto.max_iter) and ((iteraciones_sin_mejoras % contexto.jump_iter) == 0):
            solucion = salto(solucion, iterador_principal, triplets)
            contexto.alfa.reiniciar(contexto.penalty_min_limit)
            contexto.beta.reiniciar(contexto.penalty_min_limit)
            triplets = Triplets(contexto)
            tabulists = TabuLists()
            solution_history.clear()
            
            # Reiniciar temperatura después de un salto
            temperatura_actual = temperatura_inicial

    # mejor_solucion.graficar_rutas()
    mejor_solucion = mejor_solucion.clonar()
    print(f"{len(solucion.contexto.clientes)} {politica_reabastecimiento} => {mejor_solucion.costo}")
    execution_time = int((datetime.now() - start).total_seconds())
    admisibilidad = 'N' if (not mejor_solucion.es_admisible) else ('F' if mejor_solucion.es_factible else 'A')
    # mejor_solucion.imprimir_detalle()
    # mejor_solucion.graficar_rutas()
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
            "execution_time": execution_time,
            "admisibilidad": admisibilidad
        }
    )




# # Algoritmo Híbrido con Simulated Annealing y Búsqueda Tabú

# Este algoritmo combina las técnicas de Búsqueda Tabú y Simulated Annealing para resolver problemas de optimización complejos.

# ## Características principales

# - **Búsqueda Tabú**: Utiliza listas tabú para evitar ciclos y explorar el espacio de soluciones de manera eficiente.
# - **Simulated Annealing**: Permite aceptar soluciones peores con una probabilidad que disminuye con el tiempo, ayudando a escapar de óptimos locales.
# - **Detección de ciclos**: Identifica patrones cíclicos en las soluciones y aplica estrategias para romperlos.
# - **Mecanismo de salto**: Cuando el algoritmo se estanca, realiza saltos para explorar nuevas regiones del espacio de soluciones.

# ## Parámetros de Simulated Annealing

# - **Temperatura inicial**: Controla la probabilidad inicial de aceptar soluciones peores.
# - **Factor de enfriamiento**: Determina qué tan rápido disminuye la temperatura.
# - **Temperatura final**: Umbral mínimo de temperatura.

# ## Estrategia de enfriamiento

# El algoritmo implementa un esquema de enfriamiento geométrico, donde la temperatura se reduce multiplicándola por un factor constante cada cierto número de iteraciones.

# ## Reinicio de temperatura

# La temperatura se reinicia parcialmente en diferentes situaciones:
# - Cuando se detectan ciclos persistentes
# - En situaciones de estancamiento
# - Después de realizar un salto en el espacio de soluciones

# Esto permite balancear la exploración y explotación del espacio de búsqueda.