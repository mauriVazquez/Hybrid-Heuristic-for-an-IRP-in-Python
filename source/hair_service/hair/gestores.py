import math
import configparser
from random import randint
from typing import List
from modelos.solucion import Solucion
from hair.contexto import constantes_contexto

class Triplets:
    """
    Clase que gestiona tripletes de tiempos y clientes.

    Atributos:
    - triplets: Lista de tripletes, donde cada triplet es de la forma [cliente, tiempo, tiempo_prima].

    Métodos:
    - __init__(): Inicializa la lista de tripletes.
    - obtener_triplet_aleatorio(): Obtiene un triplet aleatorio de la lista.
    - eliminar_triplets_solucion(solucion):  Remueve los triplets correspondientes dada una solucion.
    """

    def __init__(self) -> None:
        """ Inicializa la lista de triplets. """
        self.reiniciar()

    def reiniciar(self) -> None:
        """ Inicializa la lista de triplets. """
        constantes = constantes_contexto.get()
        self.triplets: List[List[int]] = [
            [cliente, t1, t2]
            for cliente in constantes.clientes
            for t1 in range(int(constantes.horizonte_tiempo))
            for t2 in range(int(constantes.horizonte_tiempo)) if t1 != t2
        ]

    def obtener_triplet_aleatorio(self) -> List[int]:
        """ Obtiene un triplet aleatorio de la lista. """
        return self.triplets.pop(randint(0, len(self.triplets) - 1))

    def eliminar_triplets_solucion(self, solucion: Solucion):
        """ Remueve los triplets correspondientes dada una solucion. """     
        self.triplets = [
            triplet for triplet in self.triplets 
            if not (solucion.rutas[triplet[1]].es_visitado(triplet[0]) and solucion.rutas[triplet[2]].es_visitado(triplet[0]))
        ]

class FactorPenalizacion:
    """
    Atributos:
    - value: Valor del factor de penalización.
    - contador: Contador de iteraciones desde el último ajuste.
    - iteraciones_max: Número de iteraciones para realizar ajustes.
    """
    def __init__(self, iteraciones_max : int = 10) -> None:
        """Inicializa el factor de penalización y el contador."""
        self.value                  = 1.0
        self.contador               = 0
        self.iteraciones_max        = iteraciones_max
        self.soluciones_factibles   = 0
        
    def reiniciar(self) -> None:
        """Reinicia el valor y el contador."""
        self.value                  = 1.0
        self.contador               = 0
        self.soluciones_factibles   = 0

    def actualizar(self, es_factible: bool) -> None:
        """
        Actualiza el contador y ajusta el factor de penalización según la factibilidad.

        Args:
            es_factible (bool): True si la solución es factible, False si no lo es.
        """
        #Crea un objeto ConfigParser, para leer un archivo de configuración
        config = configparser.ConfigParser()
        config.read('hair/config.ini')
        self.contador += 1
        if es_factible:
            self.soluciones_factibles += 1

        # Ajustar el factor de penalización cada `iteraciones_max` iteraciones
        if self.contador >= self.iteraciones_max:
            penalty_factor_min = float(config['Penalty_factor']['min_limit'])
            penalty_factor_max = float(config['Penalty_factor']['max_limit'])
            if self.soluciones_factibles == self.iteraciones_max:
                # Todas las soluciones son factibles, reducir penalización
                self.value = max(self.value * 0.5, penalty_factor_min)

            elif self.soluciones_factibles == 0:
                # Todas las soluciones son inviables, aumentar penalización
                self.value = min(self.value * 2, penalty_factor_max)
            
            # Reiniciar el contador y el número de soluciones factibles
            self.contador = 0
            self.soluciones_factibles = 0

    def obtener_valor(self):
        """Obtiene el valor actual del factor de penalización."""
        return self.value
 
class TabuLists:
    """Clase que gestiona las listas tabú para movimientos de una solución."""
    
    def __init__(self) -> None:
        """Inicializa las listas tabú."""
        self.reiniciar()

    def reiniciar(self) -> None:
        """Reinicia las listas tabú."""
        self.lista_r, self.lista_a = [], []

    def __str__(self) -> str:
        """Representación en cadena de la instancia."""
        return f"lista_a: {self.lista_a}, lista_r: {self.lista_r}"

    _obtener_ttl = staticmethod(lambda constantes: constantes.taboo_len + randint(0, math.floor(constantes.lambda_ttl * math.sqrt(len(constantes.clientes) * constantes.horizonte_tiempo))))
    _esta_en_lista = staticmethod(lambda lista, sublista: any(item[0] == sublista for item in lista))
    
    def actualizar(self, solucion : Solucion, solucion_prima : Solucion, main_iterator: int) -> None:
        """Actualiza las listas tabú eliminando entradas expiradas y agregando nuevos movimientos prohibidos."""
        self.lista_a = [item for item in self.lista_a if item[1] > main_iterator]
        self.lista_r = [item for item in self.lista_r if item[1] > main_iterator]
        constantes = constantes_contexto.get()
        for cliente in constantes.clientes:
            self._actualizar_lista_tabú(self.lista_r, set(solucion_prima.tiempos_cliente(cliente)) - set(solucion.tiempos_cliente(cliente)), cliente, main_iterator)
            self._actualizar_lista_tabú(self.lista_a, set(solucion.tiempos_cliente(cliente)) - set(solucion_prima.tiempos_cliente(cliente)), cliente, main_iterator)
    
    def movimiento_permitido(self, solucion_original : Solucion, solucion_prima : Solucion) -> bool:
        """Verifica si los movimientos para llegar de una solución a otra están permitidos."""
        constantes = constantes_contexto.get()
        for cliente in constantes.clientes:
            if any(self._esta_en_lista(self.lista_r, [cliente.id, t]) for t in set(solucion_original.tiempos_cliente(cliente)) - set(solucion_prima.tiempos_cliente(cliente))):
                return False
            if any(self._esta_en_lista(self.lista_a, [cliente.id, t]) for t in set(solucion_prima.tiempos_cliente(cliente)) - set(solucion_original.tiempos_cliente(cliente))):
                return False
        return True
    
    def _actualizar_lista_tabú(self, lista: List, elementos: set, cliente, main_iterator: int) -> None:
        """Agrega movimientos prohibidos a la lista tabú si no están ya presentes."""
        constantes = constantes_contexto.get()
        lista += [[[cliente.id, t], main_iterator + self._obtener_ttl(constantes)] for t in elementos if not self._esta_en_lista(lista, [cliente.id, t])]
