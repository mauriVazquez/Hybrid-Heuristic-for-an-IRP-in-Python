import unittest
from modelos.solucion import Solucion
from modelos.ruta import Ruta
import math
from modelos.entidad import Cliente, Proveedor
from hair.contexto import Contexto
from hair.gestores import FactorPenalizacion, TabuLists
from hair.movimiento import (
    movimiento,
    _variante_eliminacion,
    _variante_insercion,
    _variante_mover_visita,
    _variante_intercambiar_visitas
)
from hair.contexto_file import contexto_contexto

class TestVariantesSolucion(unittest.TestCase):
    solucion    = None
    solucion2   = None
    
    def read_input_irp(self, filename, horizonte_tiempo):
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
        
    def setUp(self):
        # Configurar una solución inicial para las pruebas
        horizonte_tiempo, proveedor, clientes, capacidad_vehiculo = self.read_input_irp("abs1n5.dat", 3)
        alfa = FactorPenalizacion()
        beta = FactorPenalizacion()
        
        contexto = Contexto()
        contexto.inicializar(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, "ML", alfa, beta)
        contexto_contexto.set(contexto)
    
        self.solucion = Solucion([
            Ruta([],[]),
            Ruta([contexto.clientes[4], contexto.clientes[2]], [22,116]),
            Ruta([contexto.clientes[3], contexto.clientes[1], contexto.clientes[0]], [72,105,95])
        ])
        
        self.solucion2 = Solucion([
            Ruta([contexto.clientes[2], contexto.clientes[3], contexto.clientes[4]], [116,24,18]),
            Ruta([contexto.clientes[0], contexto.clientes[1]], [130, 70]),
            Ruta([contexto.clientes[3], contexto.clientes[0]], [72,130])
        ])

    def test_general(self):
        solucion = self.solucion.clonar()
        solucion.refrescar()
        tabulist = TabuLists()
        tabulist.reiniciar()
        for i in range(20):
            solucion = movimiento(solucion, tabulist, i)
            solucion.refrescar()
            self.assertEqual(solucion.es_admisible, True, "La solucion debe ser admisible")
            
            
#     def test_variante_eliminacion(self):
#         """Test para la variante de eliminación."""
#         # #TEST 1
#         # vecindario = _variante_eliminacion(self.solucion)
#         # soluciones_esperadas = [
#         #     # T1= [[],[]]    T2= [[5, 3],[22, 116]]    T3= [[4, 2, 1],[72, 105, 95]]
#         #     [sorted(list([])),   sorted(list([3])),      sorted(list([4,2,1]))],        # Eliminar 5 en T2
#         #     [sorted(list([])),   sorted(list([5])),      sorted(list([4,2,1]))],        # Eliminar 3 en T2
#         #     [sorted(list([])),   sorted(list([5,3])),      sorted(list([2,1]))],        # Eliminar 4 en T3
#         #     [sorted(list([])),   sorted(list([5,3])),      sorted(list([4,1]))],        # Eliminar 2 en T3
#         #     [sorted(list([])),   sorted(list([5,3])),      sorted(list([4,2]))],        # Eliminar 1 en T3
#         # ]
#         # self.assertTrue(len(vecindario) > 0 , "El vecindario 1 está vacío")
#         # for sol in vecindario:
#         #     comparable = [sorted(list(cliente.id for cliente in ruta.clientes)) for ruta in sol.rutas]
#         #     print(sol)
#         #     self.assertIn(comparable, soluciones_esperadas, f"La solución {comparable} no está en las soluciones esperadas.")

#         #TEST 2
#         vecindario = _variante_eliminacion(self.solucion2)
#         soluciones_esperadas = [   
#             # [[3, 4, 5],[116, 24, 18]]    T2= [[1, 2],[130, 70]]    T3= [[4, 1],[72, 130]]
#             [sorted(list([4,5])),   sorted(list([1,2])),      sorted(list([4,1]))],       # Eliminar 3 en T1
#             [sorted(list([3,5])),   sorted(list([1,2])),      sorted(list([4,1]))],       # Eliminar 4 en T1
#             [sorted(list([3,4])),   sorted(list([1,2])),      sorted(list([4,1]))],       # Eliminar 5 en T1
#             [sorted(list([3,4,5])),   sorted(list([2])),      sorted(list([4,1]))],       # Eliminar 1 en T2
#             [sorted(list([3,4,5])),   sorted(list([1])),      sorted(list([4,1]))],       # Eliminar 2 en T2
#             [sorted(list([3,4,5])),   sorted(list([1,2])),      sorted(list([1]))],       # Eliminar 4 en T3
#             [sorted(list([3,4,5])),   sorted(list([1,2])),      sorted(list([4]))],       # Eliminar 1 en T3
#         ]
#         self.assertTrue(len(vecindario) > 0 , "El vecindario 2 está vacío")
#         for sol in vecindario:
#             comparable = [sorted(list(cliente.id for cliente in ruta.clientes)) for ruta in sol.rutas]
#             print(sol)
#             self.assertIn(comparable, soluciones_esperadas, f"La solución {comparable} no está en las soluciones esperadas.")
            
#     def test_variante_insercion(self):
#         """Test para la variante de inserción."""
#         vecindario = _variante_insercion(self.solucion)
#         soluciones_esperadas = [
#             # T1= [[],[]]    T2= [[5, 3],[22, 116]]    T3= [[4, 2, 1],[72, 105, 95]]
#             [sorted(list([1])),   sorted(list([5,3])),      sorted(list([4,2,1]))],       #Insertar 1 en T1
#             [sorted(list([2])),   sorted(list([5,3])),      sorted(list([4,2,1]))],       #Insertar 2 en T1
#             [sorted(list([3])),   sorted(list([5,3])),      sorted(list([4,2,1]))],       #Insertar 3 en T1
#             [sorted(list([4])),   sorted(list([5,3])),      sorted(list([4,2,1]))],       #Insertar 4 en T1
#             [sorted(list([5])),   sorted(list([5,3])),      sorted(list([4,2,1]))],       #Insertar 5 en T1
#             [sorted(list([])),    sorted(list([5,3,1])),    sorted(list([4,2,1]))],      #Insertar 1 en T2
#             [sorted(list([])),    sorted(list([5,3,2])),    sorted(list([4,2,1]))],      #Insertar 2 en T2
#             [sorted(list([])),    sorted(list([5,3,4])),    sorted(list([4,2,1]))],      #Insertar 4 en T2
#             [sorted(list([])),    sorted(list([5,3])),      sorted(list([4,2,1,3]))],      #Insertar 3 en T3
#             [sorted(list([])),    sorted(list([5,3])),      sorted(list([4,2,1,5]))],      #Insertar 5 en T3
#         ]
#         self.assertTrue(len(vecindario) > 0 , "El vecindario 1 está vacío")
#         for sol in vecindario:
#             comparable = [sorted(list(cliente.id for cliente in ruta.clientes)) for ruta in sol.rutas]
#             print(sol)
#             self.assertIn(comparable, soluciones_esperadas, f"La solución {comparable} no está en las soluciones esperadas.")

#         vecindario = _variante_insercion(self.solucion2)
#         soluciones_esperadas = [
#            # [[3, 4, 5],[116, 24, 18]]    T2= [[1, 2],[130, 70]]    T3= [[4, 1],[72, 130]]
#             [sorted(list([3,4,5,1])),    sorted(list([1,2])),     sorted(list([4,1]))],       #Insertar 1 en T1
#             [sorted(list([3,4,5,2])),    sorted(list([1,2])),     sorted(list([4,1]))],       #Insertar 2 en T1
#             [sorted(list([3,4,5])),      sorted(list([1,2,3])),   sorted(list([4,1]))],       #Insertar 3 en T2
#             [sorted(list([3,4,5])),      sorted(list([1,2,4])),   sorted(list([4,1]))],       #Insertar 4 en T2
#             [sorted(list([3,4,5])),      sorted(list([1,2,5])),   sorted(list([4,1]))],       #Insertar 5 en T2
#             [sorted(list([3,4,5])),      sorted(list([1,2])),     sorted(list([4,1,2]))],     #Insertar 2 en T3
#             [sorted(list([3,4,5])),      sorted(list([1,2])),     sorted(list([4,1,3]))],     #Insertar 3 en T3
#             [sorted(list([3,4,5])),      sorted(list([1,2])),     sorted(list([4,1,5]))],     #Insertar 5 en T3
#         ]
#         self.assertTrue(len(vecindario) > 0 , "El vecindario 2 está vacío")
#         for sol in vecindario:
#             comparable = [sorted(list(cliente.id for cliente in ruta.clientes)) for ruta in sol.rutas]
#             print(sol)
#             self.assertIn(comparable, soluciones_esperadas, f"La solución {comparable} no está en las soluciones esperadas.")

#     def test_variante_mover_visita(self):
#         """Test para la variante de mover visita."""
#         vecindario = _variante_mover_visita(self.solucion)
#         soluciones_esperadas = [
#             # T1= [[],[]]    T2= [[5, 3],[22, 116]]    T3= [[4, 2, 1],[72, 105, 95]]
#             [sorted(list([1])),  sorted(list([5,3])),     sorted(list([4,2]))],        #Mover 1 de T3 a T1
#             [sorted(list([])),   sorted(list([5,3,1])),   sorted(list([4,2]))],        #Mover 1 de T3 a T2
#             [sorted(list([2])),  sorted(list([5,3])),     sorted(list([4,1]))],        #Mover 2 de T3 a T1
#             [sorted(list([])),   sorted(list([5,3,2])),   sorted(list([4,1]))],        #Mover 2 de T3 a T2
#             [sorted(list([3])),  sorted(list([5])),       sorted(list([4,2,1]))],      #Mover 3 de T2 a T1
#             [sorted(list([])),   sorted(list([5])),       sorted(list([4,2,1,3]))],    #Mover 3 de T2 a T3
#             [sorted(list([5])),  sorted(list([3])),       sorted(list([4,2,1]))],      #Mover 5 de T2 a T1
#             [sorted(list([])),   sorted(list([3])),       sorted(list([4,2,1,5]))],    #Mover 5 de T2 a T3
#             [sorted(list([4])),  sorted(list([5,3])),     sorted(list([2,1]))],        #Mover 4 de T3 a T1
#             [sorted(list([])),   sorted(list([5,3,4])),   sorted(list([2,1]))],        #Mover 4 de T3 a T2
#         ]

#         self.assertTrue(len(vecindario) > 0 , "El vecindario 1 está vacío")
#         for sol in vecindario:
#             comparable = [sorted(list(cliente.id for cliente in ruta.clientes)) for ruta in sol.rutas]
#             self.assertIn(comparable, soluciones_esperadas, f"La solución {comparable} no está en las soluciones esperadas.")
        
#         vecindario = _variante_mover_visita(self.solucion2)
#         soluciones_esperadas = [
#             # [[3, 4, 5],[116, 24, 18]]    T2= [[1, 2],[130, 70]]    T3= [[4, 1],[72, 130]]
#             [sorted(list([4,5])),       sorted(list([1,2,3])),  sorted(list([4,1]))],   #Mover 3 de T1 a T2
#             [sorted(list([4,5])),       sorted(list([1,2])),    sorted(list([4,1,3]))], #Mover 3 de T1 a T3
#             [sorted(list([3,5])),       sorted(list([1,2,4])),  sorted(list([4,1]))],   #Mover 4 de T1 a T2
#             [sorted(list([3,4])),       sorted(list([1,2,5])),  sorted(list([4,1]))],   #Mover 5 de T1 a T2
#             [sorted(list([3,4])),       sorted(list([1,2])),    sorted(list([4,1,5]))], #Mover 5 de T1 a T3
#             [sorted(list([3,4,5,1])),   sorted(list([2])),      sorted(list([4,1]))],   #Mover 1 de T2 a T1
#             [sorted(list([3,4,5,2])),   sorted(list([1])),      sorted(list([4,1]))],   #Mover 2 de T2 a T1
#             [sorted(list([3,4,5])),     sorted(list([1])),      sorted(list([4,1,2]))], #Mover 2 de T2 a T5
#             [sorted(list([3,4,5])),     sorted(list([1,2,4])),  sorted(list([1]))],     #Mover 4 de T3 a T2
#             [sorted(list([3,4,5,1])),   sorted(list([1,2])),    sorted(list([4]))],     #Mover 1 de T3 a T1
#         ]

#         self.assertTrue(len(vecindario) > 0 , "El vecindario 2 está vacío")
#         for sol in vecindario:
#             comparable = [sorted(list(cliente.id for cliente in ruta.clientes)) for ruta in sol.rutas]
#             self.assertIn(comparable, soluciones_esperadas, f"La solución {comparable} no está en las soluciones esperadas.")

#     def test_variante_intercambiar_visitas(self):
#         # """Test para la variante de intercambiar visitas."""
#         # vecindario = _variante_intercambiar_visitas(self.solucion)
#         # soluciones_esperadas = [
#         #     # T1= [[],[]]    T2= [[5, 3],[22, 116]]    T3= [[4, 2, 1],[72, 105, 95]]
#         #      [sorted(list([])),  sorted(list([1,3])),     sorted(list([4,2,5]))],        #Intercambiar 1 de T3 con 5 de T2
#         #      [sorted(list([])),  sorted(list([5,1])),     sorted(list([4,2,3]))],        #Intercambiar 1 de T3 con 3 de T2
#         #      [sorted(list([])),  sorted(list([4,3])),     sorted(list([5,2,1]))],        #Intercambiar 4 de T3 con 5 de T2
#         #      [sorted(list([])),  sorted(list([5,4])),     sorted(list([3,2,1]))],        #Intercambiar 4 de T3 con 3 de T2
#         #      [sorted(list([])),  sorted(list([2,3])),     sorted(list([4,5,1]))],        #Intercambiar 2 de T3 con 5 de T2
#         #      [sorted(list([])),  sorted(list([5,2])),     sorted(list([4,3,1]))],        #Intercambiar 2 de T3 con 3 de T2
#         # ]
#         # self.assertTrue(len(vecindario) > 0 , "El vecindario1 está vacío")
#         # for sol in vecindario:
#         #     comparable = [sorted(list(cliente.id for cliente in ruta.clientes)) for ruta in sol.rutas]
#         #     self.assertIn(comparable, soluciones_esperadas, f"La solución {comparable} no está en las soluciones esperadas.")
        
#         """Test para la variante de intercambiar visitas."""
#         vecindario = _variante_intercambiar_visitas(self.solucion2)
#         soluciones_esperadas = [
#             # [[3, 4, 5],[116, 24, 18]]    T2= [[1, 2],[130, 70]]    T3= [[4, 1],[72, 130]]
#             [sorted(list([1,4,5])),       sorted(list([3,2])),  sorted(list([4,1]))],   #Intercambiar 3 de T1 con 1 de T2
#             [sorted(list([2,4,5])),       sorted(list([1,3])),  sorted(list([4,1]))],   #Intercambiar 3 de T1 con 2 de T2
#             [sorted(list([1,4,5])),       sorted(list([1,2])),  sorted(list([4,3]))],   #Intercambiar 3 de T1 con 1 de T3
#             [sorted(list([3,1,5])),       sorted(list([4,2])),  sorted(list([4,1]))],   #Intercambiar 4 de T1 con 1 de T2
#             [sorted(list([3,2,5])),       sorted(list([1,4])),  sorted(list([4,1]))],   #Intercambiar 4 de T1 con 2 de T2
#             [sorted(list([3,4,1])),       sorted(list([5,2])),  sorted(list([4,1]))],   #Intercambiar 5 de T1 con 1 de T2           
#             [sorted(list([3,4,2])),       sorted(list([1,5])),  sorted(list([4,1]))],   #Intercambiar 5 de T1 con 2 de T2
#             [sorted(list([3,4,1])),       sorted(list([1,2])),  sorted(list([4,5]))],   #Intercambiar 5 de T1 con 1 de T3
#             [sorted(list([3,4,5])),       sorted(list([1,4])),  sorted(list([2,1]))],   #Intercambiar 2 de T2 con 4 de T3
#         ]
#         self.assertTrue(len(vecindario) > 0 , "El vecindario2 está vacío")
#         for sol in vecindario:
#             comparable = [sorted(list(cliente.id for cliente in ruta.clientes)) for ruta in sol.rutas]
#             self.assertIn(comparable, soluciones_esperadas, f"La solución {comparable} no está en las soluciones esperadas.")
    
if __name__ == "__main__":
    unittest.main()