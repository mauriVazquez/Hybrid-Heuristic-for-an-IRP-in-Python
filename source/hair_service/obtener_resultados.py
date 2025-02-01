from hair.main import execute
import math
import os
from modelos.entidad import Cliente, Proveedor

def procesar_datos(rp, filename):
    # Definimos las listas para almacenar cada columna
    costos = []
    tiempos = []
    iteraciones = []
    filepath = os.path.join('resultados',rp, filename)
    with open(filepath, 'r') as file:
        for line in file:
            # Separamos cada línea en sus componentes
            costo, tiempo, iteracion = line.split()
            
            # Convertimos los valores y los agregamos a sus respectivas listas
            costos.append(float(costo))
            
            # Convertimos el tiempo (en formato HH:MM:SS) a segundos para simplificar el cálculo
            h, m, s = map(float, tiempo.split(":"))
            total_seconds = h * 3600 + m * 60 + s
            tiempos.append(total_seconds)
            
            iteraciones.append(int(iteracion))   

    os.makedirs(os.path.join('resultados', 'estadistica', rp), exist_ok=True)
    filepath = os.path.join('resultados', 'estadistica', rp, filename)
    # Escribir el resultado en el archivo en modo de adición (append)
    with open(filepath, 'a') as file:
        file.write(f"pro_c {sum(costos) / len(costos)} \n") 
        file.write(f"max_c {max(costos)} \n") 
        file.write(f"min_c {min(costos)} \n") 
        file.write(f"pro_t {sum(tiempos) / len(tiempos)} \n") 
        file.write(f"max_t {max(tiempos)} \n") 
        file.write(f"min_t {min(tiempos)} \n") 
        file.write(f"pro_i {sum(iteraciones) / len(iteraciones)} \n") 
        file.write(f"max_i {max(iteraciones)} \n") 
        file.write(f"min_i {min(iteraciones)} \n") 
        
def escribir_resultado(rp, filename, mejor_solucion, iterador, execution_time):
    # Crear el directorio `/resultados` si no existe
    os.makedirs('resultados', exist_ok=True)
    os.makedirs(os.path.join('resultados',rp), exist_ok=True)

    # Ruta completa del archivo
    filepath = os.path.join('resultados',rp, filename)

    # Escribir el resultado en el archivo en modo de adición (append)
    with open(filepath, 'a') as file:
        solucion = mejor_solucion.__json__("iteration", "a")
        file.write(f"{solucion['costo']} {execution_time} {iterador} \n")  # Agrega una nueva línea después de cada resultado
        
def read_input_irp(filename):
    file_it = iter(read_elem(filename))
    nb_clientes = int(next(file_it)) - 1
    horizonte_tiempo = int(next(file_it))
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

    return horizonte_tiempo, proveedor, clientes, capacidad_vehiculo

def compute_dist(xi, xj, yi, yj):
    return round(math.sqrt(math.pow(xi - xj, 2) + math.pow(yi - yj, 2)))
    
def read_elem(filename):
    with open(f'./instancias/{filename}') as f:
        return [str(elem) for elem in f.read().split()]
           
if __name__ == '__main__':
    filenames = [
        'abs1n5.dat',
        'abs2n10.dat',
        # 'abs3n15.dat',
        # 'abs4n20.dat',
        # 'abs5n25.dat',
        # 'abs1n30.dat',
        # 'abs2n35.dat',
        # 'abs3n40.dat',
        # 'abs4n45.dat',
        # 'abs5n50.dat',
    ]
    for filename in filenames:
        for rp in ['OU', 'ML']:
            for i in range(3):
                horizonte_tiempo, proveedor, clientes, capacidad_vehiculo = read_input_irp(filename)
                mejor_solucion, iterador, execution_time = execute(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, rp, True)
                
                escribir_resultado(rp, filename, mejor_solucion, iterador, execution_time)
            procesar_datos(rp, filename)