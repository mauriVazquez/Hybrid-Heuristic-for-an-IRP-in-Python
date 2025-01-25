import math
import configparser
from itertools import permutations
from random import shuffle, randint
from typing import List, Set, Tuple
from modelos.solucion import Solucion
from modelos.contexto_file import contexto_ejecucion

class Triplets:
    """
    Clase que gestiona tripletes de tiempos y clientes.

    Atributos:
        triplets (List[Tuple[int, int, int]]): Conjunto de tripletes, donde cada triplete es de la forma (cliente, t1, t2).
    """

    def __init__(self) -> None:
        """
        Inicializa la lista de tripletes con todas las combinaciones posibles de clientes 
        y tiempos (t1, t2) dentro del horizonte temporal, siempre que t1 sea diferente a t2.

        Returns:
            None
        """
        contexto = contexto_ejecucion.get()
        self.triplets: List[Tuple[int, int, int]] = [
            (cliente, t1, t2)
            for cliente in contexto.clientes
            for t1, t2 in permutations(range(int(contexto.horizonte_tiempo)), 2)
        ]
        # Barajar la lista al inicio puede evitar patrones repetitivos al seleccionar tripletes aleatorios
        shuffle(self.triplets)

    def obtener_triplet_aleatorio(self) -> Tuple[int, int, int]:
        """
        Obtiene un triplete aleatorio de la lista.

        Returns:
            Tuple[int, int, int]: Triplete aleatorio de la forma (cliente, t1, t2).
        """
        return self.triplets.pop(randint(0, len(self.triplets) - 1))

    def eliminar_triplets_solucion(self, solucion: Solucion) -> None:
        """
        Remueve los tripletes correspondientes a clientes ya visitados según la solución proporcionada.

        Args:
            solucion (Solucion): Solución que contiene las rutas para verificar los clientes visitados.

        Returns:
            None
        """
        self.triplets = [
            triplet for triplet in self.triplets
            if not (
                solucion.rutas[triplet[1]].es_visitado(triplet[0])
                and solucion.rutas[triplet[2]].es_visitado(triplet[0])
            )
        ]

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
        config = configparser.ConfigParser()
        config.read('hair/config.ini')

        self.contador += 1
        if es_factible:
            self.soluciones_factibles += 1

        if self.contador >= self.iteraciones_max:
            min_limit = float(config['Penalty_factor']['min_limit'])
            max_limit = float(config['Penalty_factor']['max_limit'])

            if self.soluciones_factibles == self.iteraciones_max:
                self.value = max(self.value * 0.5, min_limit)
            elif self.soluciones_factibles == 0:
                self.value = min(self.value * 2, max_limit)

            self.reiniciar()

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
        lista_r (Set[Tuple[int, int]]): Conjunto tabú de remociones (cliente, tiempo).
        lista_a (Set[Tuple[int, int]]): Conjunto tabú de adiciones (cliente, tiempo).
    """

    def __init__(self) -> None:
        """
        Inicializa las listas tabú como conjuntos para mejorar la eficiencia de búsqueda.

        Returns:
            None
        """
        self.lista_r: Set[Tuple[int, int]] = set()
        self.lista_a: Set[Tuple[int, int]] = set()

    def __str__(self) -> str:
        """
        Representación en cadena de la instancia.

        Returns:
            str: Representación de las listas tabú.
        """
        return f"lista_a: {list(self.lista_a)}, lista_r: {list(self.lista_r)}"

    @staticmethod
    def _obtener_ttl(contexto) -> int:
        """
        Calcula el tiempo de vida (TTL) para las entradas tabú.

        Args:
            contexto: Contexto que contiene los parámetros relevantes.

        Returns:
            int: Tiempo de vida calculado.
        """
        taboo_len = contexto.taboo_len
        lambda_ttl = contexto.lambda_ttl
        clientes = len(contexto.clientes)
        horizonte_tiempo = contexto.horizonte_tiempo

        # Calcular el TTL basado en los parámetros
        variacion = randint(0, math.floor(lambda_ttl * math.sqrt(clientes * horizonte_tiempo)))
        return taboo_len + variacion

    def actualizar(self, solucion: Solucion, solucion_prima: Solucion, main_iterator: int) -> None:
        """
        Actualiza las listas tabú eliminando entradas expiradas y agregando nuevos movimientos prohibidos.

        Args:
            solucion (Solucion): Solución original.
            solucion_prima (Solucion): Solución modificada.
            main_iterator (int): Iterador principal.

        Returns:
            None
        """
        self._eliminar_expirados(main_iterator)

        contexto = contexto_ejecucion.get()
        for cliente in contexto.clientes:
            # Identificar movimientos de remoción y adición
            elementos_r = set(solucion_prima.tiempos_cliente(cliente)) - set(solucion.tiempos_cliente(cliente))
            elementos_a = set(solucion.tiempos_cliente(cliente)) - set(solucion_prima.tiempos_cliente(cliente))

            self._actualizar_lista_tabú(self.lista_r, elementos_r, cliente, main_iterator, contexto)
            self._actualizar_lista_tabú(self.lista_a, elementos_a, cliente, main_iterator, contexto)

    def _eliminar_expirados(self, main_iterator: int) -> None:
        """
        Elimina las entradas expiradas de las listas tabú.

        Args:
            main_iterator (int): Iterador principal.

        Returns:
            None
        """
        self.lista_r = {item for item in self.lista_r if item[1] > main_iterator}
        self.lista_a = {item for item in self.lista_a if item[1] > main_iterator}

    def movimiento_permitido(self, solucion_original: Solucion, solucion_prima: Solucion) -> bool:
        """
        Verifica si los movimientos para llegar de una solución a otra están permitidos.

        Args:
            solucion_original (Solucion): Solución original.
            solucion_prima (Solucion): Solución modificada.

        Returns:
            bool: True si los movimientos están permitidos, False en caso contrario.
        """
        contexto = contexto_ejecucion.get()
        for cliente in contexto.clientes:
            tiempos_r = set(solucion_original.tiempos_cliente(cliente)) - set(solucion_prima.tiempos_cliente(cliente))
            tiempos_a = set(solucion_prima.tiempos_cliente(cliente)) - set(solucion_original.tiempos_cliente(cliente))

            if any((cliente.id, t) in self.lista_r for t in tiempos_r):
                return False
            if any((cliente.id, t) in self.lista_a for t in tiempos_a):
                return False
        return True

    def _actualizar_lista_tabú(
        self, lista: Set[Tuple[int, int]], elementos: Set[int], cliente, main_iterator: int, contexto
    ) -> None:
        """
        Agrega movimientos prohibidos a la lista tabú si no están ya presentes.

        Args:
            lista (Set[Tuple[int, int]]): Conjunto tabú a actualizar.
            elementos (Set[int]): Conjunto de elementos a agregar.
            cliente: Cliente relacionado.
            main_iterator (int): Iterador principal.
            contexto: Contexto que contiene los parámetros relevantes.

        Returns:
            None
        """
        ttl = self._obtener_ttl(contexto)
        for t in elementos:
            lista.add((cliente.id, t, main_iterator + ttl))
