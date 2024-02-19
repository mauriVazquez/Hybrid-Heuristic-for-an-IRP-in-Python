from random import randint
from entidades_manager import EntidadesManager
from modelos.solucion import Solucion

class TripletManager:
    """
    Clase que gestiona tripletes de tiempos y clientes.

    Atributos:
    - triplets: Lista de tripletes, donde cada triplet es de la forma [cliente, tiempo, tiempo_prima].

    Métodos:
    - __init__(): Inicializa la lista de tripletes.
    - obtener_triplet_aleatorio(): Obtiene un triplet aleatorio de la lista.
    - eliminar_triplets_solucion(solucion):  Remueve los triplets correspondientes dada una solucion.
    """
    _instance = None
    triplets = []

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
        Inicializa la lista de triplet.
        """
        self.triplets = [
            [cliente, tiempo, tiempo_prima] 
            for cliente in EntidadesManager.obtener_clientes()
            for tiempo in range(EntidadesManager.obtener_parametros().horizon_length)
            for tiempo_prima in range(EntidadesManager.obtener_parametros().horizon_length)
            if tiempo != tiempo_prima
        ]


    def obtener_triplet_aleatorio(self):
        """
        Obtiene un triplet aleatorio de la lista.

        Retorna:
        - List[int]: Triplet aleatorio.
        """
        return self.triplets.pop(randint(0, len(self.triplets) - 1))

    def eliminar_triplets_solucion(self, solucion: Solucion):
        """
        Remueve los triplets correspondientes dada una solucion.
        """
        self.triplets = [
            triplet for triplet in self.triplets 
            if solucion.rutas[triplet[1]].es_visitado(triplet[0]) and (not solucion.rutas[triplet[2]].es_visitado(triplet[0]))
        ]
triplet_manager = TripletManager()