from hair_main import hair_execute
import math
import argparse

class Proveedor():
    id : str
    coord_x : float
    coord_y : float
    costo_almacenamiento : float
    nivel_almacenamiento : int
    nivel_produccion : int

    def __init__(self, id, coord_x, coord_y, costo_almacenamiento, nivel_almacenamiento, nivel_produccion):
        self.id = id
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.costo_almacenamiento = costo_almacenamiento
        self.nivel_almacenamiento = nivel_almacenamiento
        self.nivel_produccion = nivel_produccion

class Cliente():
    id: str
    coord_x: float
    coord_y: float
    costo_almacenamiento: float
    nivel_almacenamiento: int
    nivel_maximo: int
    nivel_minimo: int
    nivel_demanda: int

    def __init__(self, id, coord_x, coord_y, costo_almacenamiento, nivel_almacenamiento, nivel_maximo, nivel_minimo, nivel_demanda):
        self.id = id
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.costo_almacenamiento = costo_almacenamiento
        self.nivel_almacenamiento = nivel_almacenamiento
        self.nivel_maximo = nivel_maximo
        self.nivel_minimo = nivel_minimo
        self.nivel_demanda = nivel_demanda

def read_input_irp(filename, horizon_len):
    file_it = iter(read_elem(filename))
    nb_clientes = int(next(file_it)) - 1

    #Tomo el horizon_len del config sólo si no viene por parámetro. Mantenerlo en dos líneas (siempre tiene que ejecutar el next).
    config_horizon_len = int(next(file_it))
    horizon_len = horizon_len if not(horizon_len is None) else config_horizon_len
    
    capacidad_vehiculo = int(next(file_it))
    
    next(file_it)
    coord_x = float(next(file_it))
    coord_y = float(next(file_it))
    nivel_inicial = int(next(file_it))
    nivel_produccion = int(next(file_it))
    costo_almacenamiento = float(next(file_it))
    
    proveedor = Proveedor(0, coord_x, coord_y, costo_almacenamiento, nivel_inicial, nivel_produccion)
   

    clientes = []
    for i in range(1, nb_clientes+1):
        next(file_it)
        coord_x = float(next(file_it))
        coord_y = float(next(file_it))
        nivel_inicial = int(next(file_it))
        max_nivel = int(next(file_it))
        min_nivel = int(next(file_it))
        nivel_demanda = int(next(file_it))
        costo_almacenamiento = float(next(file_it))
        clientes.append(Cliente(i, coord_x, coord_y, costo_almacenamiento, nivel_inicial, max_nivel, min_nivel, nivel_demanda))

    return horizon_len, proveedor, clientes, capacidad_vehiculo

def compute_dist(xi, xj, yi, yj):
    return round(math.sqrt(math.pow(xi - xj, 2) + math.pow(yi - yj, 2)))
    
def read_elem(filename):
    with open(f'./instancias/{filename}') as f:
        return [str(elem) for elem in f.read().split()]
           
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--instancia", type=str, required=True)
    parser.add_argument("--horizon_len", type=int)
    parser.add_argument("--politica_reabastecimiento", type=str)
    parser.add_argument("--multiplicador_tolerancia", type=float)
    args = parser.parse_args()

    instancia = args.instancia
    horizon_len = args.horizon_len
    politica_reabastecimiento = args.politica_reabastecimiento
    multiplicador_tolerancia = args.multiplicador_tolerancia

    horizon_len, proveedor, clientes, capacidad_vehiculo = read_input_irp(instancia, horizon_len)
    
    response = hair_execute(horizon_len, capacidad_vehiculo, proveedor, clientes)