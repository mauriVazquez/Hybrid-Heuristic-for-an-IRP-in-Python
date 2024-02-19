import math
import configparser

class Cliente:
    def __init__(self, id, coord_x, coord_y, nivel_inicial, costo_almacenamiento, max_nivel, min_nivel, nivel_demanda, proveedor_x, proveedor_y):
        self.id = id
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.nivel_inicial = nivel_inicial
        self.costo_almacenamiento = costo_almacenamiento
        self.max_nivel = max_nivel
        self.min_nivel = min_nivel
        self.nivel_demanda = nivel_demanda
        self.distancia_proveedor = EntidadesManager.compute_dist(coord_x, proveedor_x, coord_y, proveedor_y)

class Proveedor:
    def __init__(self, id, coord_x, coord_y, nivel_inicial, costo_almacenamiento, nivel_produccion):
        self.id = id
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.nivel_inicial = nivel_inicial
        self.costo_almacenamiento = costo_almacenamiento
        self.nivel_produccion = nivel_produccion

class Parametros:
    def __init__(self, horizon_length, cant_clientes):
        # Crea un objeto ConfigParser, para leer un archivo de configuración
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.horizon_length = int(horizon_length)
        self.politica_reabastecimiento = config['App']['politica_reabastecimiento']
        self.multiplicador_tolerancia = float(config['App']['multiplicador_tolerancia'])
        self.taboo_len = int(config['Taboo']['list_length'])
        self.lambda_ttl = float(config['Taboo']['lambda_ttl'])
        self.penalty_factor_min = float(config['Penalty_factor']['min_limit'])
        self.penalty_factor_max = float(config['Penalty_factor']['max_limit'])
        self.max_iter = 100 * self.horizon_length  * int(cant_clientes)
        self.jump_iter = int(self.max_iter // 2)
    
class Vehiculo:
    def __init__(self, id, capacidad):
        self.id = id
        self.capacidad = capacidad

class EntidadesManager:
    _clientes = []
    _proveedor = None
    _vehiculo = None
    _parametros = None
    _matriz_clientes = []

    #GETS
    @staticmethod
    def obtener_cantidad_clientes():
        return len(EntidadesManager._clientes)
    
    @staticmethod
    def obtener_clientes():
        return EntidadesManager._clientes
    
    @staticmethod
    def obtener_proveedor():
        return EntidadesManager._proveedor
    
    @staticmethod
    def obtener_parametros():
        return EntidadesManager._parametros
    
    @staticmethod
    def obtener_vehiculo():
        return EntidadesManager._vehiculo  
    
    #SETS
    @staticmethod
    def crear_cliente(id, coord_x, coord_y, costo_almacenamiento, nivel_inicial, max_nivel, min_nivel, nivel_demanda, proovedor_x, proovedor_y):
        if id not in EntidadesManager._clientes:
            EntidadesManager._clientes.append(Cliente(id, coord_x, coord_y, nivel_inicial, costo_almacenamiento, max_nivel, min_nivel, nivel_demanda, proovedor_x, proovedor_y))
            EntidadesManager.actualizar_matriz_clientes()
    
    @staticmethod
    def crear_proveedor(id, coord_x, coord_y, costo_almacenamiento, nivel_inicial, nivel_produccion):
        if not EntidadesManager._proveedor:
            EntidadesManager._proveedor = Proveedor(id, coord_x, coord_y, nivel_inicial, costo_almacenamiento, nivel_produccion)
    
    @staticmethod
    def crear_vehiculo(id, capacidad):
        if not EntidadesManager._vehiculo:
            EntidadesManager._vehiculo = Vehiculo(id, capacidad)

    @staticmethod
    def crear_parametros(horizon_length):
        if not EntidadesManager._parametros:
            EntidadesManager._parametros = Parametros(horizon_length, EntidadesManager.obtener_cantidad_clientes())

    #MATRICES DE DISTANCIA
    @staticmethod
    def obtener_matriz_clientes():
        return EntidadesManager._matriz_clientes
    
    @staticmethod
    def actualizar_matriz_clientes():
        EntidadesManager._matriz_clientes = {
            c.id: {
                c2.id: EntidadesManager.compute_dist(c.coord_x, c2.coord_x,c.coord_y,c2.coord_y) 
                for c2 in EntidadesManager._clientes
            } 
            for c in EntidadesManager._clientes
        }

    @staticmethod
    def compute_dist(xi, xj, yi, yj):
        return round(math.sqrt(math.pow(xi - xj, 2) + math.pow(yi - yj, 2)))
    
        
# # Ejemplo de uso
# cliente1 = EntidadesManager.obtener_cliente("Cliente A")
# proveedor1 = EntidadesManager.obtener_proveedor("Proveedor X")