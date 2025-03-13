import math
import configparser
from modelos.entidad import Cliente, Proveedor
from modelos.gestores import FactorPenalizacion
class Contexto:
    """
    Representa el contexto de la solución incluyendo parámetros de configuración, proveedor, 
    clientes y la matriz de distancias entre ellos.

    Args:
        horizonte_tiempo (int): Horizonte temporal de la simulación.
        capacidad_vehiculo (float): Capacidad máxima del vehículo.
        proveedor (Proveedor): Información del proveedor.
        clientes (list[Cliente]): Lista de clientes.
        politica_reabastecimiento (str): Política de reabastecimiento.
        alfa (float): Peso del parámetro alfa.
        beta (float): Peso del parámetro beta.
        debug (bool, opcional): Modo de depuración. Por defecto es True.
    """
    def __init__(
        self,
        horizonte_tiempo : int,
        capacidad_vehiculo : int,
        proveedor : Proveedor,
        clientes : list[Cliente],
        politica_reabastecimiento : str,
        debug : bool = True 
    ):
        # Crea un objeto ConfigParser para leer un archivo de configuración
        config = configparser.ConfigParser()
        config.read('hair/config.ini')

        self.politica_reabastecimiento = politica_reabastecimiento
        self.taboo_len = 10
        self.lambda_ttl = float(config['Taboo']['lambda_ttl'])
        self.penalty_min_limit = len(clientes) * horizonte_tiempo
        self.penalty_max_limit = float('inf')
        self.capacidad_vehiculo = capacidad_vehiculo
        self.horizonte_tiempo = horizonte_tiempo
        self.max_iter = 200 * len(clientes) * horizonte_tiempo
        self.jump_iter = self.max_iter // 2
        self.alfa = FactorPenalizacion(self.penalty_min_limit)
        self.beta = FactorPenalizacion(self.penalty_min_limit)
        self.debug = debug

        self.proveedor = Proveedor(
            proveedor.id,
            proveedor.coord_x,
            proveedor.coord_y,
            proveedor.nivel_almacenamiento,
            proveedor.nivel_produccion,
            proveedor.costo_almacenamiento
        )

        self.clientes = []
        for c in clientes:
            distancia_proveedor = self.calcular_distancia(self.proveedor.coord_x, c.coord_x, self.proveedor.coord_y, c.coord_y)
            self.clientes.append(Cliente(
                c.id,
                c.coord_x,
                c.coord_y,
                c.nivel_almacenamiento,
                c.nivel_maximo,
                c.nivel_minimo,
                c.nivel_demanda,
                c.costo_almacenamiento,
                distancia_proveedor
            ))

        self.matriz_distancia = {
            cliente.id: {
                otro_cliente.id: int(self.calcular_distancia(
                    cliente.coord_x, otro_cliente.coord_x,
                    cliente.coord_y, otro_cliente.coord_y
                ))
                for otro_cliente in self.clientes
            }
            for cliente in self.clientes
        }


    def calcular_distancia(self, xi, xj, yi, yj):
        """
        Calcula la distancia euclidiana entre dos puntos.

        Args:
            xi (float): Coordenada X del primer punto.
            xj (float): Coordenada X del segundo punto.
            yi (float): Coordenada Y del primer punto.
            yj (float): Coordenada Y del segundo punto.

        Returns:
            float: Distancia entre los dos puntos.
        """
        return math.sqrt(math.pow(xi - xj, 2) + math.pow(yi - yj, 2))
