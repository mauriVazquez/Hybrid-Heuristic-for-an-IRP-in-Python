from datetime import datetime
from random import randint, seed
from constantes import constantes
from modelos.solucion import Solucion

class TripletManager:
    """
    Clase que gestiona tripletes de tiempos y clientes.

    Atributos:
    - triplets: Lista de tripletes, donde cada triplet es de la forma [cliente, tiempo, tiempo_prima].

    Métodos:
    - __init__(): Inicializa la lista de tripletes.
    - obtener_triplet_aleatorio(): Obtiene un triplet aleatorio de la lista.
    """
    _instance = None

    def __new__(cls):
        """
        Implementación del patrón Singleton para la clase TripletManager.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
        return cls._instance

    def __init__(self) -> None:
        """
        Inicializa la lista de tripletes.
        """
        self.triplets = [
            [cliente.id, tiempo, tiempo_prima] 
            for cliente in constantes.clientes
            for tiempo in range(constantes.horizon_length)
            for tiempo_prima in range(constantes.horizon_length)
            if tiempo != tiempo_prima
        ]


    def obtener_triplet_aleatorio(self):
        """
        Obtiene un triplet aleatorio de la lista.

        Returns:
        - List[int]: Triplet aleatorio.
        """
        # Se define el seed para el random basado en la fecha y hora actual.
        seed(datetime.now().microsecond)
        return self.triplets.pop(randint(0, len(self.triplets) - 1))

triplet_manager = TripletManager()