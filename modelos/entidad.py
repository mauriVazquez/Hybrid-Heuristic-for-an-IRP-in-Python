class Entidad():
    """
    Clase base que representa una entidad en el sistema.

    Atributos:
    - id: Identificador único de la entidad.
    - coord_x: Coordenada X de la entidad en el espacio.
    - coord_y: Coordenada Y de la entidad en el espacio.
    - nivel_inicial: Nivel inicial de la entidad.
    - costo_almacenamiento: Costo de almacenamiento asociado a la entidad.
    """

    def __init__(self, id, coord_x, coord_y, nivel_inicial, costo_almacenamiento) -> None:
        """
        Constructor de la clase Entidad.

        Parameters:
        - id: Identificador único de la entidad.
        - coord_x: Coordenada X de la entidad.
        - coord_y: Coordenada Y de la entidad.
        - nivel_inicial: Nivel inicial de la entidad.
        - costo_almacenamiento: Costo de almacenamiento de la entidad.
        """
        self.id = id
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.nivel_inicial = nivel_inicial
        self.costo_almacenamiento = costo_almacenamiento

    def __str__(self) -> str:
        """
        Retorna una representación en cadena del objeto Entidad.

        Returns:
        - str: Representación en cadena del ID de la entidad.
        """
        return str(self.id)


class Cliente(Entidad):
    """
    Clase que representa a un cliente en el sistema.

    Atributos adicionales:
    - max_nivel: Nivel máximo permitido para el cliente.
    - min_nivel: Nivel mínimo permitido para el cliente.
    - nivel_demanda: Nivel de demanda del cliente.
    - distancia_proveedor: Distancia al proveedor desde el cliente.

    Métodos:
    - __init__(id, coord_x, coord_y, nivel_inicial, max_nivel, min_nivel, nivel_demanda, costo_almacenamiento, distancia_proveedor):
        Constructor de la clase Cliente.
    """

    def __init__(self, id, coord_x, coord_y, nivel_inicial, max_nivel, min_nivel, nivel_demanda, costo_almacenamiento, distancia_proveedor) -> None:
        """
        Constructor de la clase Cliente.

        Parameters:
        - max_nivel: Nivel máximo del cliente.
        - min_nivel: Nivel mínimo del cliente.
        - nivel_demanda: Nivel de demanda del cliente.
        - distancia_proveedor: Distancia al proveedor desde el cliente.
        """
        super().__init__(id, coord_x, coord_y, nivel_inicial, costo_almacenamiento)
        self.max_nivel = max_nivel
        self.min_nivel = min_nivel
        self.nivel_demanda = nivel_demanda
        self.distancia_proveedor = distancia_proveedor


class Proveedor(Entidad):
    """
    Clase que representa un proveedor.

    Atributos adicionales:
    - nivel_produccion: Nivel de producción del proveedor.

    Métodos:
    - __init__(id, coord_x, coord_y, nivel_inicial, nivel_produccion, costo_almacenamiento):
        Constructor de la clase Proveedor.
    """

    def __init__(self, id, coord_x, coord_y, nivel_inicial, nivel_produccion, costo_almacenamiento) -> None:
        """
        Constructor de la clase Proveedor.

        Parameters:
        - nivel_produccion: Nivel de producción del proveedor.
        """
        super().__init__(id, coord_x, coord_y, nivel_inicial, costo_almacenamiento)
        self.nivel_produccion = nivel_produccion
