import math
import configparser
from modelos.entidad import Cliente, Proveedor

class Constantes():
    def __init__(self) -> None:
        #Crea un objeto ConfigParser, para leer un archivo de configuración
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.politica_reabastecimiento = config['App']['politica_reabastecimiento']
        self.taboo_len = int(config['Taboo']['list_length'])
        self.lambda_ttl = float(config['Taboo']['lambda_ttl'])
        self.penalty_factor_min = float(config['Penalty_factor']['min_limit'])
        self.penalty_factor_max = float(config['Penalty_factor']['max_limit'])
        
        self.max_iter = 0 
        self.jump_iter = 0
        self.proveedor = None
        self.capacidad_vehiculo = None
        self.horizonte_tiempo = None
        self.clientes = []
        self.matriz_distancia = []
     
    def inicializar(self,horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, politica_reabastecimiento) -> None:
        self.capacidad_vehiculo         = capacidad_vehiculo
        self.horizonte_tiempo           = horizonte_tiempo
        self.max_iter                   = 200 * len(clientes)  * horizonte_tiempo
        self.jump_iter                  = self.max_iter // 2
        if politica_reabastecimiento:     
            self.politica_reabastecimiento = politica_reabastecimiento
        
        self.proveedor = Proveedor(
            proveedor.id,
            proveedor.coord_x,
            proveedor.coord_y,
            proveedor.nivel_almacenamiento,
            proveedor.nivel_produccion,
            proveedor.costo_almacenamiento
        )
        
        self.clientes = []
        for cliente in clientes:
            distancia_proveedor = self.calcular_distancia_proveedor(cliente.coord_x,cliente.coord_y) 
            self.clientes.append(Cliente(
                cliente.id,
                cliente.coord_x,
                cliente.coord_y,
                cliente.nivel_almacenamiento,
                cliente.nivel_maximo,
                cliente.nivel_minimo,
                cliente.nivel_demanda,
                cliente.costo_almacenamiento,
                distancia_proveedor
            ))
          
        self.matriz_distancia = self.compute_matriz_distancia()
        

    # Compute the distancia matriz
    def compute_matriz_distancia(self):
        return {
            c.id: {
                c2.id: self.compute_dist(c.coord_x, c2.coord_x, c.coord_y, c2.coord_y)
                for c2 in self.clientes
            }
            for c in self.clientes
        }
        
    # Calcular distancias al proveedor
    def calcular_distancia_proveedor(self, coord_x, coord_y):
        return self.compute_dist(self.proveedor.coord_x, coord_x, self.proveedor.coord_y, coord_y) 

    #Distancia entre dos puntos
    def compute_dist(self, xi, xj, yi, yj):
        return math.sqrt(math.pow(xi - xj, 2) + math.pow(yi - yj, 2))


constantes = Constantes()
