import math
from modelos.entidad import Cliente

# Distancia entre dos puntos
def compute_dist(xi, xj, yi, yj) -> float:
    """
    Calcula la distancia euclidiana entre dos puntos dados.

    Args:
        xi (float): Coordenada X del primer punto.
        xj (float): Coordenada X del segundo punto.
        yi (float): Coordenada Y del primer punto.
        yj (float): Coordenada Y del segundo punto.

    Returns:
        float: Distancia euclidiana entre los dos puntos.
    """
    return math.sqrt(math.pow(xi - xj, 2) + math.pow(yi - yj, 2))

class Ruta:
    """
    Clase que representa una ruta de entrega.

    Contiene la lista de clientes y las cantidades entregadas a cada uno.
    """

    @staticmethod
    def obtener_costo_recorrido(clientes : list[Cliente]) -> float:
        """
        Calcula el costo total de un recorrido.

        El costo incluye:
        - Distancia desde el proveedor hasta el primer cliente.
        - Distancia entre clientes consecutivos.
        - Distancia desde el último cliente de regreso al proveedor.

        Args:
            clientes (list[Cliente]): Lista de clientes en el recorrido.

        Returns:
            float: Costo total del recorrido.
        """
        if not clientes:
            return 0.0

        # Distancia del proveedor al primer cliente y del proveedor al último cliente
        costo_total = clientes[0].distancia_proveedor + clientes[len(clientes)-1].distancia_proveedor

        # Suma de distancias entre clientes consecutivos
        costo_total += sum(
            compute_dist(c1.coord_x, c2.coord_x, c1.coord_y, c2.coord_y)
            for c1, c2 in zip(clientes, clientes[1:])
        )

        return costo_total

    def __init__(self, clientes : list[Cliente] = None, cantidades : int = None) -> None:
        """
        Inicializa una ruta con clientes y cantidades entregadas.

        Args:
            clientes (list[Cliente], opcional): Lista de clientes en la ruta.
            cantidades (list[int], opcional): Cantidades entregadas a cada cliente.
        """
        self.clientes   = clientes
        self.cantidades = cantidades
        self.costo      = self.obtener_costo_recorrido(clientes)

    def __str__(self) -> str:
        """
        Representación en cadena de la ruta.

        Returns:
            str: Representación de los IDs de los clientes y sus cantidades entregadas.
        """
        return f"[{[cliente.id for cliente in self.clientes]}, {self.cantidades}]"

    def __json__(self) -> dict:
        """
        Convierte la ruta a formato JSON.

        Returns:
            dict: Representación JSON de la ruta.
        """
        return {
            "clientes"  : [str(cliente.id) for cliente in self.clientes],
            "cantidades": self.cantidades,
            "costo"     : self.costo,
        }

    def clonar(self):
        """
        Crea una copia profunda de la ruta.

        Returns:
            Ruta: Copia de la ruta actual.
        """
        return Ruta(self.clientes[:], self.cantidades[:])

    def obtener_total_entregado(self) -> int:
        """
        Calcula el total de cantidades entregadas en la ruta.

        Returns:
            int: Total de cantidades entregadas.
        """
        return sum(self.cantidades)

    def obtener_cantidad_entregada(self, cliente : Cliente) -> int:
        """
        Obtiene la cantidad entregada a un cliente específico.

        Args:
            cliente (Cliente): Cliente para el que se quiere obtener la cantidad entregada.

        Returns:
            int: Cantidad entregada al cliente.
        """
        return next((self.cantidades[i] for i, c in enumerate(self.clientes) if c == cliente), 0)

    def insertar_visita(self, cliente : Cliente, cantidad : int , indice = None) -> None :
        """
        Inserta una visita a un cliente en la ruta.

        Args:
            cliente (Cliente): Cliente a insertar.
            cantidad (int): Cantidad entregada al cliente.
            indice (int, opcional): Posición donde insertar la visita. Si no se proporciona,
                se elige la posición óptima según el costo.
        """
         # Determinar la posición óptima solo si no se proporciona un índice
        if indice is None:
            # Calcular el costo de insertar en todas las posiciones y elegir la mejor
            costos = [
                self.obtener_costo_recorrido(self.clientes[:pos] + [cliente] + self.clientes[pos:])
                for pos in range(len(self.clientes) + 1)
            ]
            indice = costos.index(min(costos))

        # Insertar cliente y cantidad en la posición determinada
        self.clientes.insert(indice, cliente)
        self.cantidades.insert(indice, cantidad)

        # Actualizar el costo total de la ruta
        self.costo = self.obtener_costo_recorrido(self.clientes)
            
    def eliminar_visita(self, cliente : Cliente) -> int:
        """
        Elimina la visita a un cliente de la ruta.

        Args:
            cliente (Cliente): Cliente a eliminar.

        Returns:
            int: Cantidad removida asociada al cliente.
        """
        indice = next((i for i, c in enumerate(self.clientes) if c.id == cliente.id), None)
        if indice is not None:
            cantidad_removida = self.cantidades.pop(indice)
            self.clientes.pop(indice)
        else:
            cantidad_removida = 0
            
        self.costo = self.obtener_costo_recorrido(self.clientes)
        
        return cantidad_removida

    def agregar_cantidad_cliente(self, cliente : Cliente, cantidad : int) -> None:
        """
        Agrega una cantidad a un cliente existente en la ruta.

        Args:
            cliente (Cliente): Cliente al que se agrega la cantidad.
            cantidad (int): Cantidad a agregar.
        """
        if cliente in self.clientes:
            self.cantidades[self.clientes.index(cliente)] += cantidad

    def quitar_cantidad_cliente(self, cliente : Cliente, cantidad : int) -> None:
        """
        Resta una cantidad a un cliente existente en la ruta.

        Args:
            cliente (Cliente): Cliente al que se resta la cantidad.
            cantidad (int): Cantidad a restar.
        """
        if cliente in self.clientes:
            self.cantidades[self.clientes.index(cliente)] -= cantidad

    def es_igual(self, ruta2 : "Ruta") -> bool:
        """
        Verifica si esta ruta es igual a otra.

        Args:
            ruta2 (Ruta): Otra ruta a comparar.

        Returns:
            bool: True si las rutas son iguales, False en caso contrario.
        """
        return (self.clientes == ruta2.clientes) and (self.cantidades == ruta2.cantidades)

    def es_visitado(self, cliente : Cliente) -> bool:
        """
        Verifica si el cliente pertenece a la ruta.

        Args:
            cliente (Cliente): Cliente a buscar

        Returns:
            bool: True si el cliente está en la ruta, False en caso contrario
        """
        return (cliente in self.clientes)