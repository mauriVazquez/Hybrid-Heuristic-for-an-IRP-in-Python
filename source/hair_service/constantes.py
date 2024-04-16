import math
import configparser
from modelos.entidad import Cliente, Proveedor

class Constantes():

    def __init__(self, horizon_length, proveedor, vehiculo, clientes) -> None:
        # Crea un objeto ConfigParser, para leer un archivo de configuración
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.politica_reabastecimiento = config['App']['politica_reabastecimiento']
        # self.read_input_irp(config['App']['instancia'])
        self.multiplicador_tolerancia = float(config['App']['multiplicador_tolerancia'])
        self.taboo_len = int(config['Taboo']['list_length'])
        self.lambda_ttl = float(config['Taboo']['lambda_ttl'])
        self.penalty_factor_min = float(config['Penalty_factor']['min_limit'])
        self.penalty_factor_max = float(config['Penalty_factor']['max_limit'])
        self.max_iter = 10 * len(self.clientes) * len(self.clientes) * self.horizon_length * self.horizon_length
        self.jump_iter = 10 * len(self.clientes) * self.horizon_length
        # self.proveedor = Proveedor(proveedor["id"], proveedor["cord"])
        self.proveedor = Proveedor(proveedor["id"],proveedor['coord_x'],proveedor['coord_y'],proveedor['nivel_almacenamiento'],proveedor['nivel_produccion'], proveedor['costo_almacenamiento'])
        self.vehicle_capacity = vehiculo['capacidad']
        self.horizon_length = horizon_length
        
        self.clientes = []
        for cliente in clientes:
            distancia_proveedor = self.compute_distancia_proveedor(cliente['coord_x'],cliente['coord_y'])
            self.clientes.append(Cliente(cliente['id'],cliente['coord_x'],cliente['coord_y'], cliente['nivel_almacenamiento'], cliente['nivel_maximo'], cliente['nivel_minimo'],cliente['nivel_demanda'],cliente['costo_almacenamiento'],distancia_proveedor))
            
        self.matriz_distancia = self.compute_matriz_distancia()

    def read_input_irp(self, filename):
        file_it = iter(self.read_elem(filename))

        nb_clientes = int(next(file_it)) - 1
        self.horizon_length = int(next(file_it))
        self.vehicle_capacity = int(next(file_it))

        next(file_it)
        coord_x_proveedor = float(next(file_it))
        coord_y_proveedor = float(next(file_it))
        nivel_inicial_proveedor = int(next(file_it))
        nivel_produccion_proveedor = int(next(file_it))
        costo_almacenamiento_proveedor = float(next(file_it))
        self.proveedor = Proveedor(0,coord_x_proveedor,coord_y_proveedor,nivel_inicial_proveedor,nivel_produccion_proveedor, costo_almacenamiento_proveedor)
        self.clientes = []
        for i in range(1,nb_clientes+1):
            next(file_it)
            coord_x = float(next(file_it))
            coord_y = float(next(file_it))
            nivel_inicial = int(next(file_it))
            max_nivel = int(next(file_it))
            min_nivel = int(next(file_it))
            nivel_demanda = int(next(file_it))
            costo_almacenamiento = float(next(file_it))
            distancia_proveedor = self.compute_distancia_proveedor(coord_x,coord_y)
            self.clientes.append(Cliente(i,coord_x,coord_y, nivel_inicial, max_nivel, min_nivel,nivel_demanda,costo_almacenamiento,distancia_proveedor))

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
