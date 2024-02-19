from entidades_manager import EntidadesManager

class Ruta():
    """
    Clase que representa una ruta de entregas.

    Atributos:
    - clientes: Lista de clientes en la ruta.
    - cantidades: Cantidades entregadas a cada cliente.

    Métodos:
    - obtener_costo_recorrido(clientes) -> float: Calcula el costo total de recorrido para una lista de clientes en una ruta.
    - __init__(clientes, cantidades) -> None: Constructor de la clase Ruta.
    - __str__() -> str: Retorna una representación en cadena del objeto Ruta.
    - clonar(): Crea y devuelve una copia de la instancia actual de la clase Ruta.
    - obtener_costo() -> float: Obtiene el costo total de la ruta.
    - obtener_total_entregado() -> int: Obtiene la cantidad total entregada en la ruta.
    - obtener_cantidad_entregada(cliente) -> int: Obtiene la cantidad entregada a un cliente específico en la ruta.
    - es_excedida_capacidad_vehiculo() -> bool: Verifica si la capacidad del vehículo está excedida.
    - es_visitado(cliente) -> bool: Verifica si un cliente ya ha sido visitado en la ruta.
    - mejor_indice_insercion(cliente) -> int: Encuentra el mejor lugar para insertar un cliente minimizando el costo.
    - insertar_visita(indice, cliente, cantidad): Inserta una visita a un cliente en la ruta en la posición especificada.
    - remover_visita(cliente) -> int: Elimina una visita de un cliente de la ruta.
    - agregar_cantidad_cliente(cliente, cantidad): Añade una cantidad adicional a la entrega a un cliente específico.
    - quitar_cantidad_cliente(cliente, cantidad): Reduce la cantidad entregada a un cliente específico.
    """
    
    @staticmethod
    def obtener_costo_recorrido(clientes) -> float:
        """
        Calcula el costo total de recorrido para una lista de clientes en una ruta.

        Parameters:
        - clientes: Lista de clientes en la ruta.

        Retorna:
        - float: Costo total de recorrido.
        """
        return 0 if not clientes else (
            #Distancia del primero al proveedor + distancia del último al proveedor, mas distancia entre clientes
            clientes[0].distancia_proveedor + clientes[-1].distancia_proveedor +
            sum(EntidadesManager.compute_dist(c1.coord_x, c0.coord_x, c1.coord_y, c0.coord_y)
                for c0, c1 in zip(clientes, clientes[1:]))
            )
    
    def __init__(self, clientes, cantidades) -> None:
        """
        Constructor de la clase Ruta.

        Parameters:
        - clientes: Lista de clientes en la ruta.
        - cantidades: Cantidades entregadas a cada cliente.
        """
        self.clientes = clientes if clientes else []  # Lista de clientes en la ruta
        self.cantidades = cantidades if cantidades else []  # Cantidades entregadas a cada cliente
    
    def __str__(self) -> str:
        """
        Retorna una representación en cadena del objeto Ruta.

        Retorna:
        - str: Representación en cadena de la ruta.
        """
        clientes_ids = [cliente.id for cliente in self.clientes]
        return f"[{clientes_ids},{self.cantidades}]"
    
    def clonar(self):
        """
        Crea y devuelve una copia de la instancia actual de la clase Ruta, manteniendo referencias a Clientes y Cantidades.

        Retorna:
            Ruta: Una nueva instancia de la clase Ruta que es una copia de la ruta actual.
        """
        clientes = [clientes for clientes in self.clientes]
        cantidades = [cantidades for cantidades in self.cantidades]
        return Ruta(clientes,cantidades)
    
    def obtener_costo(self):
        """
        Obtiene el costo total de la ruta.

        Retorna:
        - float: Costo total de la ruta.
        """
        return self.obtener_costo_recorrido(self.clientes)
    
    def obtener_total_entregado(self) -> int:
        """
        Obtiene la cantidad total entregada en la ruta.

        Retorna:
        - int: Cantidad total entregada.
        """
        return sum(self.cantidades)
    
    def obtener_cantidad_entregada(self, cliente) -> int:
        """
        Obtiene la cantidad entregada a un cliente específico en la ruta.

        Parameters:
        - cliente: Cliente para el que se desea obtener la cantidad entregada.

        Retorna:
        - int: Cantidad entregada al cliente.
        """
        return next((self.cantidades[i] for i, it_cliente in enumerate(self.clientes) if it_cliente == cliente), 0)
    
    def es_excedida_capacidad_vehiculo(self) -> bool:
        """
        Verifica si la capacidad del vehículo está excedida.

        Retorna:
        - bool: True si la capacidad está excedida, False en caso contrario.
        """
        return EntidadesManager.obtener_vehiculo().capacidad < self.obtener_total_entregado()
    
    def es_visitado(self, cliente) -> bool:
        """
        Verifica si un cliente ya ha sido visitado en la ruta.

        Parameters:
        - cliente: Cliente a verificar.

        Retorna:
        - bool: True si el cliente ha sido visitado, False en caso contrario.
        """
        return cliente in self.clientes
    
    def mejor_indice_insercion(self, cliente) -> int:
        """
        Encuentra el mejor lugar para insertar un cliente en la ruta minimizando el costo.

        Parameters:
        - cliente: Cliente que se desea insertar.

        Retorna:
        - int: Índice de la mejor posición de inserción.
        """
        min_costo = float("inf")
        mejor_indice = 0
        for pos in range(len(self.clientes) + 1):
            temp_clientes = self.clientes[:pos] + [cliente] + self.clientes[pos:]
            ruta_costo = self.obtener_costo_recorrido(temp_clientes)
            if ruta_costo < min_costo:
                mejor_indice = pos
                min_costo = ruta_costo
        return mejor_indice
    
    def insertar_visita(self, cliente, cantidad, indice):
        """
        Inserta una visita a un cliente en la ruta en la posición especificada.

        Parameters:
        - cliente: Cliente que se desea insertar.
        - cantidad: Cantidad entregada al cliente.
        - indice: Índice de la posición de inserción, si el valor es None, se inserta en el indice más barato.
        """
        if indice is None:
            indice = self.mejor_indice_insercion(cliente)
        self.clientes.insert(indice, cliente)
        self.cantidades.insert(indice, cantidad)

    def remover_visita(self, cliente) -> int:
        """
        Elimina una visita de un cliente de la ruta.

        Parameters:
        - cliente: Cliente que se desea eliminar.

        Retorna:
        - int: Cantidad removida.
        """
        indice = next((i for i, c in enumerate(self.clientes) if c == cliente), None)
        if indice is not None:
            cantidad_removida = self.cantidades.pop(indice)
            self.clientes.pop(indice)
            return cantidad_removida
        return 0
    
    def agregar_cantidad_cliente(self, cliente, cantidad):
        """
        Añade una cantidad adicional a la entrega a un cliente específico.

        Parameters:
        - cliente: Cliente al que se le añadirá la cantidad.
        - cantidad: Cantidad adicional a agregar.
        """
        for i, c in enumerate(self.clientes):
            if c == cliente:
                self.cantidades[i] += cantidad
                break
    
    def quitar_cantidad_cliente(self, cliente, cantidad): 
        """
        Reduce la cantidad entregada a un cliente específico.

        Parameters:
        - cliente: Cliente al que se le reducirá la cantidad.
        - cantidad: Cantidad a reducir.
        """
        self.cantidades[self.clientes.index(cliente)] -= cantidad