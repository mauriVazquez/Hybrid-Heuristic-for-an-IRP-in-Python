import math
import random
from random import shuffle, randint
from typing import Set, Tuple
from modelos.solucion import Solucion
from collections import deque
import numpy as np
from modelos.contexto_file import contexto_ejecucion

class Triplets:
    def __init__(self, contexto):
        """
        Inicializa la lista de tripletes con todas las combinaciones posibles de clientes y tiempos.
        """
        self.triplets = []
        self.historial_iteraciones = {}  # Diccionario para almacenar las iteraciones de visita por cliente y tiempo

        for cliente in contexto.clientes:
            for t1 in range(contexto.horizonte_tiempo):
                for t2 in range(contexto.horizonte_tiempo):
                    if t1 != t2:
                        self.triplets.append((cliente, t1, t2))
                        self.historial_iteraciones[(cliente.id, t1)] = 0

    def obtener_triplet_aleatorio(self):
        """
        Obtiene un triplete aleatorio y lo elimina de la lista.

        Returns:
            tuple: Triplete (cliente, tiempo_visitado, tiempo_no_visitado).
        """
        if not self.triplets:
            return None
        return self.triplets.pop(random.randint(0, len(self.triplets) - 1))

    def iteraciones_cliente(self, cliente, tiempo):
        """
        Devuelve el número de iteraciones desde la última vez que el cliente fue visitado en el tiempo dado.

        Args:
            cliente (Cliente): Cliente a consultar.
            tiempo (int): Tiempo en el que se quiere conocer el número de iteraciones sin visita.

        Returns:
            int: Número de iteraciones desde la última visita al tiempo dado.
        """
        return self.historial_iteraciones.get((cliente.id, tiempo), 0)

    def actualizar_iteraciones(self, solucion):
        """
        Actualiza el historial de iteraciones de cada cliente en cada tiempo.

        Args:
            solucion (Solucion): Solución actual para actualizar los tiempos de visita.
        """
        for cliente in solucion.contexto.clientes:
            for t in range(solucion.contexto.horizonte_tiempo):
                if solucion.rutas[t].es_visitado(cliente):
                    self.historial_iteraciones[(cliente.id, t)] = 0  # Reiniciar el contador si fue visitado
                else:
                    self.historial_iteraciones[(cliente.id, t)] += 1  # Aumentar el contador si no fue visitado

    def eliminar_triplets_solucion(self, solucion, jump_iter):
        """
        Elimina tripletes que ya no son válidos después del procedimiento de salto.

        Args:
            solucion (Solucion): La solución actual después del salto.
            jump_iter (int): Número de iteraciones para la limpieza de tripletes.
        """
        nuevos_triplets = []

        for cliente, t1, t2 in self.triplets:
            # Verificar si el cliente sigue siendo válido para moverse en la solución
            if (
                solucion.rutas[t1].es_visitado(cliente) and
                not solucion.rutas[t2].es_visitado(cliente)
            ):
                nuevos_triplets.append((cliente, t1, t2))

        self.triplets = nuevos_triplets  # Actualizar la lista con los tripletes válidos

class FactorPenalizacion:
    """
    Clase que gestiona el factor de penalización utilizado en la optimización.

    Atributos:
        value (float): Valor del factor de penalización.
        contador (int): Contador de iteraciones desde el último ajuste.
        iteraciones_max (int): Número de iteraciones para realizar ajustes.
        soluciones_factibles (int): Número de soluciones factibles encontradas.
    """

    def __init__(self, iteraciones_max: int = 10) -> None:
        """
        Inicializa el factor de penalización y el contador.

        Args:
            iteraciones_max (int, opcional): Número máximo de iteraciones antes de ajustar el factor. Por defecto, 10.

        Returns:
            None
        """
        self.value = 1.0
        self.contador = 0
        self.iteraciones_max = iteraciones_max
        self.soluciones_factibles = 0

    def reiniciar(self) -> None:
        """
        Reinicia el valor del factor de penalización y los contadores.

        Returns:
            None
        """
        self.value = 1.0
        self.contador = 0
        self.soluciones_factibles = 0

    def actualizar(self, es_factible: bool) -> None:
        """
        Actualiza el factor de penalización basado en la factibilidad de las soluciones.

        Args:
            es_factible (bool): True si la solución es factible, False si no lo es.

        Returns:
            None
        """
        contexto = contexto_ejecucion.get()
        self.contador += 1
        if es_factible:
            self.soluciones_factibles += 1

        if self.contador >= self.iteraciones_max:
            if (self.soluciones_factibles == self.iteraciones_max):
                self.value = max(self.value * 0.5, contexto.penalty_min_limit) 
            else:
                self.value = min(self.value * 2, contexto.penalty_max_limit)
            self.contador = 0
            self.soluciones_factibles = 0
        
    def obtener_valor(self) -> float:
        """
        Obtiene el valor actual del factor de penalización.

        Returns:
            float: Valor actual del factor.
        """
        return self.value

class TabuLists:
    """
    Clase que gestiona las listas tabú para movimientos de una solución.

    Atributos:
        lista_r (Set[Tuple[int, int, int]]): Conjunto tabú de remociones (cliente, tiempo, ttl).
        lista_a (Set[Tuple[int, int, int]]): Conjunto tabú de adiciones (cliente, tiempo, ttl).
    """

    def __init__(self) -> None:
        """
        Inicializa las listas tabú como conjuntos para mejorar la eficiencia de búsqueda.
        """
        self.lista_r: Set[Tuple[int, int, int]] = set()
        self.lista_a: Set[Tuple[int, int, int]] = set()

    def __str__(self) -> str:
        """
        Representación en cadena de la instancia.

        Returns:
            str: Representación de las listas tabú.
        """
        return f"lista_a: {list(self.lista_a)}, lista_r: {list(self.lista_r)}"

    def actualizar(self, solucion: Solucion, solucion_prima: Solucion, main_iterator: int) -> None:
        """
        Actualiza las listas tabú eliminando entradas expiradas y agregando nuevos movimientos prohibidos.

        Args:
            solucion (Solucion): Solución original.
            solucion_prima (Solucion): Solución modificada.
            main_iterator (int): Iterador principal.
        """
        contexto = solucion.contexto
        
        # Primero se eliminan los elementos que correspondan en la iteración actual
        self.lista_r = {item for item in self.lista_r if item[2] > main_iterator}
        self.lista_a = {item for item in self.lista_a if item[2] > main_iterator}

        for cliente in contexto.clientes:
            # Identificar movimientos de remoción y adición
            elementos_r = set(solucion_prima.tiempos_cliente(cliente)) - set(solucion.tiempos_cliente(cliente))
            elementos_a = set(solucion.tiempos_cliente(cliente)) - set(solucion_prima.tiempos_cliente(cliente))

            # Calcular el TTL basado en los parámetros
            variacion = randint(0, math.floor(contexto.lambda_ttl * math.sqrt(len(contexto.clientes) * contexto.horizonte_tiempo)))
            ttl = contexto.taboo_len + variacion
    
            # Agregar los elementos a las listas según corresponda
            for t in elementos_r:
                self.lista_r.add((cliente.id, t, main_iterator + ttl))
            for t in elementos_a:
                self.lista_a.add((cliente.id, t, main_iterator + ttl))

    def movimiento_permitido(self, solucion_original: Solucion, solucion_prima: Solucion) -> bool:
        """
        Verifica si los movimientos para llegar de una solución a otra están permitidos.

        Args:
            solucion_original (Solucion): Solución original.
            solucion_prima (Solucion): Solución modificada.

        Returns:
            bool: True si los movimientos están permitidos, False en caso contrario.
        """
        contexto = solucion_original.contexto
        for cliente in contexto.clientes:
            tiempos_r = set(solucion_original.tiempos_cliente(cliente)) - set(solucion_prima.tiempos_cliente(cliente))
            tiempos_a = set(solucion_prima.tiempos_cliente(cliente)) - set(solucion_original.tiempos_cliente(cliente))

            # Verificar si algún movimiento está prohibido en lista_r
            if any((cliente.id, t, ttl) in self.lista_r for t in tiempos_r for _, _, ttl in self.lista_r):
                return False
            # Verificar si algún movimiento está prohibido en lista_a
            if any((cliente.id, t, ttl) in self.lista_a for t in tiempos_a for _, _, ttl in self.lista_a):
                return False
        return True

class SolutionHistory:
    def __init__(self, max_history=250):
        self.min_cycle_length = 3
        self.max_cycle_length = 12
        self.history = deque(maxlen=max_history)
        self.cycle_count = 0
        self.stagnation_count = 0
        self.last_solution_hash = None
    
    def add_solution(self, solution):
        solution_hash = hash(tuple(frozenset(tuple(sorted(cliente.id for cliente in ruta.clientes))) for ruta in solution.rutas))
        self.history.append(solution_hash)

        if self.last_solution_hash == solution_hash:
            self.stagnation_count += 1
        else:
            self.stagnation_count = 0
        
        self.last_solution_hash = solution_hash
    
    def clear(self):
        self.history.clear()
        self.cycle_count = 0
        self.stagnation_count = 0
    
    def detect_cycle(self):
        if len(self.history) < self.min_cycle_length * 2:
            return 0, 0

        hashes = list(self.history)
        seen = {}

        for i in range(len(hashes)):
            for length in range(self.min_cycle_length, min(self.max_cycle_length, (len(hashes) - i) // 2) + 1):
                sequence = tuple(hashes[i:i + length])
                if sequence in seen:
                    self.cycle_count += 1
                    return length, self.cycle_count
                seen[sequence] = i
        
        return 0, 0

    def is_stagnant(self, threshold=5):
        return self.stagnation_count >= threshold
