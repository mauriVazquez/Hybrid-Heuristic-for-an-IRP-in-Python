import math
from constantes import constantes
from random import randint, seed
from datetime import datetime

def obtener_ttl() -> int:
    """
    Genera un valor aleatorio para el tiempo de vida de un movimiento tabú.

    Returns:
    - int: Tiempo de vida aleatorio.
    """
    seed(datetime.now().microsecond)
    lambda_ttl = constantes.lambda_ttl
    cant_clientes = len(constantes.clientes)
    horizon_len = constantes.horizon_length
    return constantes.taboo_len + randint(0, math.floor(lambda_ttl * math.sqrt(cant_clientes * horizon_len)))

class TabuLists:
    @staticmethod
    def esta_en_lista(mi_lista, sublista_a_buscar):
        encontrado = False
        for elemento in mi_lista:
            if isinstance(elemento, list) and len(elemento) > 0 and elemento[0] == sublista_a_buscar:
                encontrado = True
                break
        return encontrado

    """
    Clase que gestiona las listas tabú para movimientos de una solución.

    Atributos:
    - lista_r: Lista tabú de movimientos de tipo "remove" (eliminar).
    - lista_a: Lista tabú de movimientos de tipo "add" (agregar).

    Métodos:
    - actualizar(solucion, solucion_prima, main_iterator): Actualiza las listas tabú.
    - __str__(): Representación en cadena de la instancia.
    - esta_prohibido_agregar(i, t): Verifica si un movimiento de tipo "add" está prohibido.
    - esta_prohibido_quitar(i, t): Verifica si un movimiento de tipo "remove" está prohibido.
    """
    def __init__(self) -> None:
        """
        Inicializa las listas tabú.
        """
        self.lista_r = []
        self.lista_a = []

    def __str__(self) -> str:
        """
        Representación en cadena de la instancia.
        """
        return f"lista_a: {self.lista_a}, lista_r: {self.lista_r}"
    
    def actualizar(self, solucion, solucion_prima, main_iterator: int) -> None:
        """
        Actualiza las listas tabú, eliminando aquellas cuyo tiempo de vida haya finalizado
        y agregando nuevos movimientos prohibidos.

        Parameters:
        - solucion: Solución actual.
        - solucion_prima: Solución vecina.
        - main_iterator: Iterador principal del algoritmo.
        """
        self._limpiar_listas_tabu(main_iterator)
        self._agregar_nuevos_movimientos_prohibidos(solucion, solucion_prima, main_iterator)

    def _limpiar_listas_tabu(self, main_iterator: int) -> None:
        """
        Elimina movimientos tabú cuyo tiempo de vida ha finalizado.

        Parameters:
        - main_iterator: Iterador principal del algoritmo.
        """
        self.lista_a = [element for element in self.lista_a if element[1] > main_iterator]
        self.lista_r = [element for element in self.lista_r if element[1] > main_iterator]

    def _agregar_nuevos_movimientos_prohibidos(self, solucion, solucion_prima, main_iterator: int) -> None:
        """
        Agrega nuevos movimientos prohibidos a las listas tabú.

        Parameters:
        - solucion: Solución actual.
        - solucion_prima: Solución vecina.
        - main_iterator: Iterador principal del algoritmo.
        """
        for cliente in constantes.clientes:
            conjuntoT_s = solucion.T(cliente)
            conjuntoT_sprima = solucion_prima.T(cliente)
            self._agregar_a_lista_a(cliente, conjuntoT_s, conjuntoT_sprima, main_iterator)
            self._agregar_a_lista_r(cliente, conjuntoT_s, conjuntoT_sprima, main_iterator)

    def _agregar_a_lista_a(self, cliente, conjuntoT_s, conjuntoT_sprima, main_iterator: int) -> None:
        """
        Agrega movimientos de tipo "add" a la lista tabú.

        Parameters:
        - cliente: Cliente actual.
        - conjuntoT_s: Conjunto T de la solución actual.
        - conjuntoT_sprima: Conjunto T de la solución vecina.
        - main_iterator: Iterador principal del algoritmo.
        """
        elementos_a_agregar = set(conjuntoT_s) - set(conjuntoT_sprima)
        self.lista_a += [[[cliente.id, t], main_iterator + obtener_ttl()] for t in elementos_a_agregar
                            if not tabulists.esta_en_lista(self.lista_a, [cliente.id, t])]

    def _agregar_a_lista_r(self, cliente, conjuntoT_s, conjuntoT_sprima, main_iterator: int) -> None:
        """
        Agrega movimientos de tipo "remove" a la lista tabú.

        Parameters:
        - cliente: Cliente actual.
        - conjuntoT_s: Conjunto T de la solución actual.
        - conjuntoT_sprima: Conjunto T de la solución vecina.
        - main_iterator: Iterador principal del algoritmo.
        """
        elementos_a_agregar = set(conjuntoT_sprima) - set(conjuntoT_s)
        self.lista_r += [[[cliente.id, t], main_iterator + obtener_ttl()] for t in elementos_a_agregar
                         if not tabulists.esta_en_lista(self.lista_r, [cliente.id, t])]

    def esta_prohibido_agregar(self, i: int, t: int) -> bool:
        """
        Verifica si un movimiento de tipo "add" está prohibido.

        Parameters:
        - i: Identificador del cliente.
        - t: Tiempo del movimiento.

        Returns:
        - bool: True si el movimiento está prohibido, False en caso contrario.
        """
        return any(elemento[0] == [i, t] for elemento in self.lista_a)

    def esta_prohibido_quitar(self, i: int, t: int) -> bool:
        """
        Verifica si un movimiento de tipo "remove" está prohibido.

        Parameters:
        - i: Identificador del cliente.
        - t: Tiempo del movimiento.

        Returns:
        - bool: True si el movimiento está prohibido, False en caso contrario.
        """
        return any(elemento[0] == [i, t] for elemento in self.lista_r)

tabulists = TabuLists()