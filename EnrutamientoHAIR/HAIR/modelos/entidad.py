from copy import deepcopy

class Entidad():
    def __init__(self, id, coord_x, coord_y, nivel_almacenamiento, nivel_minimo, nivel_maximo, costo_almacenamiento) -> None:
        """
        Inicializa una entidad.

        Parámetros:
        - id (int): Identificador único de la entidad.
        - coord_x (float): Coordenada x de la ubicación de la entidad.
        - coord_y (float): Coordenada y de la ubicación de la entidad.
        - nivel_almacenamiento (int): Nivel de almacenamiento de la entidad.
        - nivel_minimo (int): Nivel mínimo de almacenamiento de la entidad.
        - nivel_maximo (int): Nivel máximo de almacenamiento de la entidad.
        - costo_almacenamiento (float): Costo de almacenamiento de la entidad.
        """
        self.id = id
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.nivel_almacenamiento = nivel_almacenamiento
        self.nivel_minimo = nivel_minimo
        self.nivel_maximo = nivel_maximo
        self.costo_almacenamiento = costo_almacenamiento

    def __str__(self) -> str:
        """
        Devuelve una representación en cadena de la entidad.
        """
        return f"{self.__class__.__name__}(id={self.id})"

    def clonar(self):
        return deepcopy(self)

class Cliente(Entidad):
    def __init__(self, id, coord_x, coord_y, nivel_almacenamiento, nivel_minimo, nivel_maximo, costo_almacenamiento, nivel_demanda) -> None:
        """
        Inicializa una entidad de cliente.

        Parámetros:
        - nivel_demanda (int): Nivel de demanda del cliente.
        """
        super().__init__(id, coord_x, coord_y, nivel_almacenamiento, nivel_minimo, nivel_maximo, costo_almacenamiento)
        self.nivel_demanda = nivel_demanda


class Proveedor(Entidad):
    def __init__(self, id, coord_x, coord_y, nivel_almacenamiento, nivel_minimo, nivel_maximo, costo_almacenamiento, nivel_produccion) -> None:
        """
        Inicializa una entidad de proveedor.

        Parámetros:
        - nivel_produccion (int): Nivel de producción del proveedor.
        """
        super().__init__(id, coord_x, coord_y, nivel_almacenamiento, nivel_minimo, nivel_maximo, costo_almacenamiento)
        self.nivel_produccion = nivel_produccion