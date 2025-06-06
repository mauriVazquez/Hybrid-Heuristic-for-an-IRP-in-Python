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
    return int(math.dist((xi, yi), (xj, yj)))

class Ruta:
    """
    Clase que representa una ruta de entrega inmutable.

    Contiene la tupla de clientes y las cantidades entregadas a cada uno.
    """

    @staticmethod
    def obtener_costo_recorrido(clientes: tuple[Cliente, ...]) -> float:
        if not clientes:
            return 0.0

        costo_total = 0.0
        costo_total += clientes[0].distancia_proveedor  # Distancia del proveedor al primer cliente

        costo_total += sum(
            compute_dist(c1.coord_x, c2.coord_x, c1.coord_y, c2.coord_y)
            for c1, c2 in zip(clientes, clientes[1:])
        )

        costo_total += clientes[-1].distancia_proveedor  # Distancia del último cliente de vuelta
        return costo_total

    def __init__(self, clientes: tuple[Cliente, ...] = (), cantidades: tuple[int, ...] = ()) -> None:
        """
        Inicializa una ruta con clientes y cantidades entregadas como tuplas inmutables.

        Args:
            clientes (tuple[Cliente], opcional): Tupla de clientes en la ruta.
            cantidades (tuple[int], opcional): Tupla de cantidades entregadas a cada cliente.
        """
        self.clientes = clientes
        self.cantidades = cantidades
        self.costo = self.obtener_costo_recorrido(clientes)

    def __str__(self) -> str:
        """
        Representación en cadena de la ruta.

        Returns:
            str: Representación de los IDs de los clientes y sus cantidades entregadas.
        """
        return f"[{tuple(cliente.id for cliente in self.clientes)}, {self.cantidades}]"

    def __json__(self) -> dict:
        """
        Convierte la ruta a formato JSON.

        Returns:
            dict: Representación JSON de la ruta.
        """
        return {
            "clientes": [str(cliente.id) for cliente in self.clientes],
            "cantidades": self.cantidades,
            "costo": self.costo,
        }

    def clonar(self) -> "Ruta":
        """
        Crea un objeto Ruta con una referencia distinta

        Returns:
            Ruta: objeto clonado.
        """
        return Ruta(self.clientes, self.cantidades)
    
    def obtener_total_entregado(self) -> int:
        """
        Calcula el total de cantidades entregadas en la ruta.

        Returns:
            int: Total de cantidades entregadas.
        """
        return sum(self.cantidades)

    def obtener_cantidad_entregada(self, cliente: Cliente) -> int:
        """
        Obtiene la cantidad entregada a un cliente específico.

        Args:
            cliente (Cliente): Cliente para el que se quiere obtener la cantidad entregada.

        Returns:
            int: Cantidad entregada al cliente.
        """
        if cliente not in self.clientes:
            return 0  # No se encontró el cliente, retornamos 0 por defecto

        return next((self.cantidades[i] for i, c in enumerate(self.clientes) if c == cliente), 0)

    def insertar_visita(self, cliente: Cliente, cantidad: int, indice = None) -> "Ruta":
        clientes_lista = list(self.clientes)
        cantidades_lista = list(self.cantidades)

        # Determinar la mejor posición si no se proporciona un índice
        if indice is None:
            costos = [
                self.obtener_costo_recorrido(tuple(clientes_lista[:pos] + [cliente] + clientes_lista[pos:]))
                for pos in range(len(clientes_lista) + 1)
            ]
            indice = costos.index(min(costos))

        # Insertar cliente y cantidad en la mejor posición
        clientes_lista.insert(indice, cliente)
        cantidades_lista.insert(indice, cantidad)

        return Ruta(tuple(clientes_lista), tuple(cantidades_lista))

    def eliminar_visita(self, cliente: Cliente) -> "Ruta":
        clientes_lista      = list(self.clientes)
        cantidades_lista    = list(self.cantidades)
        if cliente not in clientes_lista:
            return self  # Si el cliente no está, no hacer nada
        indice = clientes_lista.index(cliente)
        clientes_lista.pop(indice)
        cantidades_lista.pop(indice)
        return Ruta(tuple(clientes_lista), tuple(cantidades_lista))

    def modificar_cantidad_cliente(self, cliente: Cliente, cantidad: int) -> "Ruta":
        """
        Modifica la cantidad entregada a un cliente y devuelve una nueva instancia de Ruta.

        Args:
            cliente (Cliente): Cliente al que se modifica la cantidad.
            cantidad (int): Nueva cantidad a asignar.

        Returns:
            Ruta: Nueva instancia con la cantidad modificada.
        """
        clientes_lista = list(self.clientes)
        cantidades_lista = list(self.cantidades)

        if cliente in clientes_lista:
            indice = clientes_lista.index(cliente)
            cantidades_lista[indice] = cantidad

        return Ruta(tuple(clientes_lista), tuple(cantidades_lista))

    def es_igual(self, ruta2: "Ruta") -> bool:
        """
        Verifica si esta ruta es igual a otra.

        Args:
            ruta2 (Ruta): Otra ruta a comparar.

        Returns:
            bool: True si las rutas son iguales, False en caso contrario.
        """
        return (self.clientes == ruta2.clientes) and (self.cantidades == ruta2.cantidades)

    def es_visitado(self, cliente: Cliente) -> bool:
        """
        Verifica si el cliente pertenece a la ruta.

        Args:
            cliente (Cliente): Cliente a buscar.

        Returns:
            bool: True si el cliente está en la ruta, False en caso contrario.
        """
        return cliente in self.clientes
    
    def quitar_cantidad_cliente(self, cliente: Cliente, cantidad: int) -> "Ruta":
        if cliente not in self.clientes:
            return self  # Retorna la misma ruta si el cliente no existe

        nuevas_cantidades = list(self.cantidades)
        indice_cliente = self.clientes.index(cliente)

        nueva_cantidad = max(0, nuevas_cantidades[indice_cliente] - cantidad)

        nuevas_cantidades[indice_cliente] = nueva_cantidad
        return Ruta(clientes=self.clientes, cantidades=tuple(nuevas_cantidades))


    def agregar_cantidad_cliente(self, cliente: Cliente, cantidad: int) -> "Ruta":
        """
        Suma una cantidad a un cliente existente en la ruta, creando una nueva instancia de Ruta.

        Args:
            cliente (Cliente): Cliente al que se resta la cantidad.
            cantidad (int): Cantidad a restar.

        Returns:
            Ruta: Nueva instancia de Ruta con la cantidad actualizada.
        """
        if cliente not in self.clientes:
            return self  # Retorna la misma ruta si el cliente no existe

        # Convertir la tupla a una lista para modificarla
        nuevas_cantidades = list(self.cantidades)
        indice_cliente = self.clientes.index(cliente)

        # Sumar la cantidad
        nuevas_cantidades[indice_cliente] = nuevas_cantidades[indice_cliente] + cantidad

        # Convertir la lista de nuevo a tupla (para mantener inmutabilidad)
        return Ruta(clientes=self.clientes, cantidades=tuple(nuevas_cantidades))
    
    def establecer_cantidad_cliente(self, cliente: Cliente, cantidad: int) -> "Ruta":
        """
        Establece una cantidad a un cliente existente en la ruta, creando una nueva instancia de Ruta.

        Args:
            cliente (Cliente): Cliente al que se resta la cantidad.
            cantidad (int): Cantidad a restar.

        Returns:
            Ruta: Nueva instancia de Ruta con la cantidad actualizada.
        """
        if cliente not in self.clientes:
            return self  # Retorna la misma ruta si el cliente no existe

        # Convertir la tupla a una lista para modificarla
        nuevas_cantidades = list(self.cantidades)
        indice_cliente = self.clientes.index(cliente)

        # Establecer la cantidad
        nuevas_cantidades[indice_cliente] = cantidad

        # Convertir la lista de nuevo a tupla (para mantener inmutabilidad)
        return Ruta(clientes=self.clientes, cantidades=tuple(nuevas_cantidades))
