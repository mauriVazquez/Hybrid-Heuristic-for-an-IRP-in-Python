from hair_main import execute
import math
import argparse
from modelos.entidad import Cliente, Proveedor

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
    nivel_almacenamiento = int(next(file_it))
    nivel_produccion = int(next(file_it))
    costo_almacenamiento = float(next(file_it))
    
    proveedor = Proveedor(0, coord_x, coord_y, nivel_almacenamiento, nivel_produccion, costo_almacenamiento)
   

    clientes = []
    for i in range(1, nb_clientes+1):
        next(file_it)
        coord_x = float(next(file_it))
        coord_y = float(next(file_it))
        nivel_almacenamiento = int(next(file_it))
        nivel_maximo = int(next(file_it))
        nivel_minimo = int(next(file_it))
        nivel_demanda = int(next(file_it))
        costo_almacenamiento = float(next(file_it))
        distancia_proveedor = compute_dist(coord_x, proveedor.coord_x, coord_y, proveedor.coord_y)
        clientes.append(Cliente(i, coord_x, coord_y, nivel_almacenamiento, nivel_maximo, nivel_minimo, nivel_demanda, costo_almacenamiento, distancia_proveedor))

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
    
    response = execute(horizon_len, capacidad_vehiculo, proveedor, clientes, politica_reabastecimiento)