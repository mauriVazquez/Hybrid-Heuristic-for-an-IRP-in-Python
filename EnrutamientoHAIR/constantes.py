import math, ast
import configparser
import os
from django import setup
from HAIR.modelos.entidad import Cliente as mCliente, Proveedor as mProveedor

class Constantes():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Constantes, cls).__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        # Crea un objeto ConfigParser, para leer un archivo de configuración
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.multiplicador_tolerancia = float(config['App']['multiplicador_tolerancia'])
        self.lambda_ttl = float(config['Taboo']['lambda_ttl'])
        self.taboo_len = int(config['Taboo']['list_length'])
        self.penalty_factor_min = float(config['Penalty_factor']['min_limit'])
        self.penalty_factor_max = float(config['Penalty_factor']['max_limit'])
        self.proveedor = []
        self.clientes = []
        self.horizon_length = 1
        self.max_iter = 10 * len(self.clientes) * len(self.clientes) * self.horizon_length * self.horizon_length + 100
        self.jump_iter = 10 * len(self.clientes) * self.horizon_length + 100
        self.vehicle_capacity = 300
                
    # Compute the distancia matriz
    def compute_matriz_distancia(self):
        return {c.id: {c2.id: self.compute_dist(c.coord_x, c2.coord_x,
        c.coord_y,
        c2.coord_y) 
                       for c2 in self.clientes} 
                for c in self.clientes}
       
    # Compute the distancias to the proveedor
    def compute_distancia_proveedor(self, coord_x, coord_y):
        return self.compute_dist(self.proveedor.coord_x, coord_x, self.proveedor.coord_y, coord_y) 

    def compute_dist(self, xi, xj, yi, yj):
        return round(math.sqrt(math.pow(xi - xj, 2) + math.pow(yi - yj, 2)))
        
    def inicializar_valores(self, horizon_length, politica_reabastecimiento, proveedor_id, clientes):
        from entidades.models import Cliente, Proveedor
        self.horizon_length = horizon_length
        self.politica_reabastecimiento = politica_reabastecimiento
        proveedor =  Proveedor.objects.get(id = proveedor_id)
        self.proveedor = mProveedor(
                proveedor.id,
                proveedor.coord_x, 
                proveedor.coord_y, 
                proveedor.nivel_almacenamiento,
                proveedor.nivel_minimo,
                proveedor.nivel_maximo,
                proveedor.costo_almacenamiento,
                proveedor.nivel_produccion
            )
       
        for cliente in ast.literal_eval(clientes):
            c = Cliente.objects.get(id = cliente)
            mcliente = mCliente(
                c.id,
                c.coord_x, 
                c.coord_y, 
                c.nivel_almacenamiento,
                c.nivel_minimo,
                c.nivel_maximo,
                c.costo_almacenamiento,
                c.nivel_demanda
            )
            self.clientes.append(mcliente.clonar())

        self.max_iter = 10 * len(self.clientes) * len(self.clientes) * self.horizon_length * self.horizon_length
        self.jump_iter = 10 * len(self.clientes) * self.horizon_length
        self.matriz_distancia = self.compute_matriz_distancia()
        self.distancia_proveedor = [{c.id : self.compute_distancia_proveedor(c.coord_x,
        c.coord_y)} for c in self.clientes]

# Establecer la configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EnrutamientoHAIR.settings")
# Inicializar Django
setup()

constantes = Constantes()