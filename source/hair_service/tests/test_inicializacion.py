import unittest
from modelos.solucion import Solucion
from modelos.ruta import Ruta
import math
from modelos.entidad import Cliente, Proveedor
from hair.constantes import Constantes
from hair.gestores import FactorPenalizacion
from hair.procedimientos.inicializacion import (
    inicializacion
)
from hair.contexto import constantes_contexto

class TestVariantesSolucion(unittest.TestCase):
    solucion    = None
    solucion2   = None
    
    def read_input_irp(self, filename, horizonte_tiempo = None):
        file_it = iter(self.read_elem(filename))
        nb_clientes = int(next(file_it)) - 1

        #Tomo el horizonte_tiempo del config sólo si no viene por parámetro. Mantenerlo en dos líneas (siempre tiene que ejecutar el next).
        config_horizonte_tiempo = int(next(file_it))
        horizonte_tiempo = horizonte_tiempo if not(horizonte_tiempo is None) else config_horizonte_tiempo
        
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
            distancia_proveedor = self.compute_dist(coord_x, proveedor.coord_x, coord_y, proveedor.coord_y)
            clientes.append(Cliente(i, coord_x, coord_y, nivel_almacenamiento, nivel_maximo, nivel_minimo, nivel_demanda, costo_almacenamiento, distancia_proveedor))

        return horizonte_tiempo, proveedor, clientes, capacidad_vehiculo
    
    def compute_dist(self, xi, xj, yi, yj):
        return round(math.sqrt(math.pow(xi - xj, 2) + math.pow(yi - yj, 2)))
       
    def read_elem(self, filename):
        with open(f'./instancias/{filename}') as f:
            return [str(elem) for elem in f.read().split()]
        
    def test_variante_eliminacion(self):
        constantes = Constantes()

        # Generar las combinaciones
        for n in range(5, 51, 5):
            for i in range(1, 6):
                # Configurar una solución inicial para las pruebas
                horizonte_tiempo, proveedor, clientes, capacidad_vehiculo = self.read_input_irp(f'abs{i}n{n}.dat')

                constantes.inicializar(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, "ML", FactorPenalizacion(), FactorPenalizacion())
                constantes_contexto.set(constantes)
                self.solucion = inicializacion()
                self.assertTrue(self.solucion.es_admisible)
            
                
                constantes.inicializar(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, "OU", FactorPenalizacion(), FactorPenalizacion())
                constantes_contexto.set(constantes)
                self.solucion = inicializacion()
                self.assertTrue(self.solucion.es_admisible)
                
       