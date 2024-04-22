import math
import configparser
from modelos.entidad import Cliente, Proveedor

class Constantes():
    def __init__(self) -> None:
        #Crea un objeto ConfigParser, para leer un archivo de configuración
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.politica_reabastecimiento = config['App']['politica_reabastecimiento']
        self.multiplicador_tolerancia = float(config['App']['multiplicador_tolerancia'])
        self.taboo_len = int(config['Taboo']['list_length'])
        self.lambda_ttl = float(config['Taboo']['lambda_ttl'])
        self.penalty_factor_min = float(config['Penalty_factor']['min_limit'])
        self.penalty_factor_max = float(config['Penalty_factor']['max_limit'])
        
        self.max_iter = None
        self.jump_iter = None
        self.proveedor = None
        self.vehicle_capacity = None
        self.horizon_length = None
        self.clientes = []
        self.matriz_distancia = []
     
    def inicializar(self,horizon_length, capacidad_vehiculo, proveedor, clientes) -> None:
        self.max_iter = 10 * len(clientes) * len(clientes) * horizon_length * horizon_length
        self.jump_iter = 10 * len(clientes) * horizon_length

        # self.proveedor = Proveedor(proveedor["id"], proveedor["cord"])
        print(proveedor.id)
        self.proveedor = Proveedor(proveedor.id,proveedor.coord_x,proveedor.coord_y,proveedor.nivel_almacenamiento,proveedor.nivel_produccion, proveedor.costo_almacenamiento)
        self.vehicle_capacity = capacidad_vehiculo
        self.horizon_length = horizon_length
        
        self.clientes = []
        for cliente in clientes:
            distancia_proveedor = self.compute_distancia_proveedor(cliente.coord_x, cliente.coord_y) 
            self.clientes.append(Cliente(cliente.id, cliente.coord_x, cliente.coord_y,  cliente.nivel_almacenamiento, cliente.nivel_maximo, cliente.nivel_minimo, cliente.nivel_demanda, cliente.costo_almacenamiento, distancia_proveedor))
          
        self.matriz_distancia = self.compute_matriz_distancia()
        

    # Compute the distancia matriz
    def compute_matriz_distancia(self):
        return {c.id: {c2.id: self.compute_dist(c.coord_x, c2.coord_x,c.coord_y,c2.coord_y) 
                       for c2 in self.clientes} 
                for c in self.clientes}
       

    # Compute the distancias to the proveedor
    def compute_distancia_proveedor(self, coord_x, coord_y):
        return self.compute_dist(self.proveedor.coord_x, coord_x, self.proveedor.coord_y, coord_y) 

    def compute_dist(self, xi, xj, yi, yj):
        return round(math.sqrt(math.pow(xi - xj, 2) + math.pow(yi - yj, 2)))

    def read_elem(self, filename):
        with open(filename) as f:
            return [str(elem) for elem in f.read().split()]


constantes = Constantes()
