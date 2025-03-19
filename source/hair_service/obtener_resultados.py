from hair.main import execute
import math
import os
from modelos.entidad import Cliente, Proveedor

def procesar_datos(rp, filename):
    # Definimos las listas para almacenar cada columna
    costos = []
    tiempos = []
    iteraciones = []
    filepath = os.path.join('resultados',rp, str(len(mejor_solucion.contexto.clientes)), filename)
    with open(filepath, 'r') as file:
        for line in file:
            # Separamos cada línea en sus componentes
            costo, tiempo, iteracion, admisibilidad = line.split()
            
            # Convertimos los valores y los agregamos a sus respectivas listas
            costos.append(float(costo))
            tiempos.append(int(tiempo))
            
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
        
def escribir_resultado(rp, filename, mejor_solucion, iterador, execution_time, admisibilidad):
    # Crear el directorio `/resultados` si no existe
    os.makedirs('resultados', exist_ok=True)
    os.makedirs(os.path.join('resultados', rp, str(len(mejor_solucion.contexto.clientes))), exist_ok=True)

    # Ruta completa del archivo
    filepath = os.path.join('resultados',rp, str(len(mejor_solucion.contexto.clientes)), filename)

    # Escribir el resultado en el archivo en modo de adición (append)
    with open(filepath, 'a') as file:
        solucion = mejor_solucion.__json__("iteration", "a")
        file.write(f"{solucion['costo']} {execution_time} {iterador}  {admisibilidad}\n")  # Agrega una nueva línea después de cada resultado
        
def read_input_irp(filename):
    file_it = iter(read_elem(filename))
    nb_clientes = int(next(file_it)) - 1

    #Tomo el horizonte_tiempo del config sólo si no viene por parámetro. Mantenerlo en dos líneas (siempre tiene que ejecutar el next).
    config_horizonte_tiempo = int(next(file_it))
    horizonte_tiempo = config_horizonte_tiempo
    
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
    return int(math.dist((xi,yi),(xj,yj)))
    
def read_elem(filename):
    with open(f'./instancias/{filename}') as f:
        return [str(elem) for elem in f.read().split()]
           
if __name__ == '__main__':
    # filenames = [
    #     # 'abs1n5.dat', 'abs2n5.dat', 'abs3n5.dat', 'abs4n5.dat','abs5n5.dat',
    #     # 'abs1n10.dat', 'abs2n10.dat', 'abs3n10.dat', 'abs4n10.dat', 'abs5n10.dat',
    #     # 'abs1n15.dat', 'abs2n15.dat', 'abs3n15.dat', 'abs4n15.dat', 'abs5n15.dat',
    #     # 'abs1n20.dat', 'abs2n20.dat', 'abs3n20.dat', 'abs4n20.dat', 'abs5n20.dat',
    #     # 'abs1n25.dat', 'abs2n25.dat', 'abs3n25.dat', 'abs4n25.dat', 'abs5n25.dat',
    #     # 'abs1n30.dat', 'abs2n30.dat', 'abs3n30.dat', 'abs4n30.dat', 'abs5n30.dat',
    #     # 'abs1n35.dat', 'abs2n35.dat', 'abs3n35.dat', 'abs4n35.dat', 'abs5n35.dat',
    #     # 'abs1n40.dat', 'abs2n40.dat', 'abs3n40.dat', 'abs4n40.dat', 'abs5n40.dat',
    #     'abs1n45.dat', 'abs2n45.dat', 'abs3n45.dat', 'abs4n45.dat', 'abs5n45.dat',
    #     # 'abs1n50.dat', 'abs2n50.dat', 'abs3n50.dat', 'abs4n50.dat', 'abs5n50.dat'
    # ]
    
    filenames = [
        'abs5n45.dat',
        'abs3n15.dat',
        'abs1n20.dat',
        'abs5n20.dat',
        'abs3n25.dat',
        'abs4n25.dat',
        'abs2n35.dat',
        'abs2n40.dat',
        'abs1n50.dat',
        'abs4n45.dat',
        'abs3n45.dat',
        'abs1n5.dat',
    ]

    for _ in range(1):            
        for filename in filenames:
            for rp in ['OU']:
                horizonte_tiempo, proveedor, clientes, capacidad_vehiculo = read_input_irp(filename)
                mejor_solucion, iterador, execution_time, admisibilidad = execute(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, rp)
                escribir_resultado(rp, filename, mejor_solucion, iterador, execution_time, admisibilidad)
            # procesar_datos(rp, filename)
    
    
    filenames = [
        'abs5n45.dat',
        'abs2n10.dat',
        'abs3n20.dat',
        'abs5n20.dat',
        'abs2n25.dat',
        'abs1n30.dat',
        'abs3n30.dat',
        'abs4n30.dat',
        'abs5n30.dat',
        'abs2n35.dat',
        'abs3n35.dat',
        'abs4n35.dat',
        'abs5n35.dat',
        'abs1n40.dat',
        'abs3n40.dat',
        'abs5n40.dat',
        'abs1n45.dat',
        'abs2n45.dat',
        'abs4n45.dat',
        'abs3n45.dat',
        'abs1n50.dat',
        'abs4n50.dat',
    ]

    for _ in range(1):            
        for filename in filenames:
            for rp in ['ML']:
                horizonte_tiempo, proveedor, clientes, capacidad_vehiculo = read_input_irp(filename)
                mejor_solucion, iterador, execution_time, admisibilidad = execute(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, rp)
                escribir_resultado(rp, filename, mejor_solucion, iterador, execution_time, admisibilidad)
            # procesar_datos(rp, filename)