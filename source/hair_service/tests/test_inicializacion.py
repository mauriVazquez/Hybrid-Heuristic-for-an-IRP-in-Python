import unittest
from modelos.solucion import Solucion
from modelos.ruta import Ruta
import math
from modelos.entidad import Cliente, Proveedor
from modelos.contexto import Contexto
from modelos.gestores import FactorPenalizacion
from hair.inicializacion import inicializacion
from modelos.contexto_file import contexto_ejecucion

class TestVariantesSolucion(unittest.TestCase):
    """
    Clase de prueba para validar variantes en las soluciones generadas
    por el procedimiento de inicialización con políticas OU y ML.
    """
    solucion = None

    def read_input_irp(self, filename, horizonte_tiempo=None):
        """
        Lee los datos de entrada desde un archivo .dat para configurar el IRP.

        Args:
            filename (str): Nombre del archivo de entrada.
            horizonte_tiempo (int, opcional): Horizonte de tiempo. Si no se proporciona,
                se toma del archivo de entrada.

        Returns:
            tuple: Horizonte de tiempo, proveedor, clientes, capacidad del vehículo.
        """
        file_it = iter(self.read_elem(filename))
        nb_clientes = int(next(file_it)) - 1

        # Configurar horizonte de tiempo
        config_horizonte_tiempo = int(next(file_it))
        horizonte_tiempo = horizonte_tiempo if horizonte_tiempo is not None else config_horizonte_tiempo

        capacidad_vehiculo = int(next(file_it))

        # Proveedor
        next(file_it)  # Ignorar línea
        coord_x = float(next(file_it))
        coord_y = float(next(file_it))
        nivel_almacenamiento = int(next(file_it))
        nivel_produccion = int(next(file_it))
        costo_almacenamiento = float(next(file_it))

        proveedor = Proveedor(0, coord_x, coord_y, nivel_almacenamiento, nivel_produccion, costo_almacenamiento)

        # Clientes
        clientes = []
        for i in range(1, nb_clientes + 1):
            next(file_it)  # Ignorar línea
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
        """
        Calcula la distancia euclidiana redondeada entre dos puntos.

        Args:
            xi (float): Coordenada X del primer punto.
            xj (float): Coordenada X del segundo punto.
            yi (float): Coordenada Y del primer punto.
            yj (float): Coordenada Y del segundo punto.

        Returns:
            int: Distancia redondeada entre los dos puntos.
        """
        return round(math.sqrt(math.pow(xi - xj, 2) + math.pow(yi - yj, 2)))

    def read_elem(self, filename):
        """
        Lee los elementos de un archivo y devuelve una lista de strings.

        Args:
            filename (str): Nombre del archivo de entrada.

        Returns:
            list[str]: Lista de elementos del archivo.
        """
        with open(f'./instancias/{filename}') as f:
            return [str(elem) for elem in f.read().split()]

    def test_inicializacion_generates_valid_solution(self):
        """
        Prueba que el procedimiento de inicialización genere una solución válida y determinista.
        """
        for n in range(5, 51, 5):
            for i in range(1, 6):
                horizonte_tiempo, proveedor, clientes, capacidad_vehiculo = self.read_input_irp(f'abs{i}n{n}.dat')
        
                # Pruebas con política ML
                contexto = Contexto(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, "ML", FactorPenalizacion(), FactorPenalizacion(), debug=False)
                contexto_ejecucion.set(contexto)

                solucion = inicializacion()
                
                # Verificar que la solución sea una instancia de la clase esperada
                self.assertIsInstance(solucion, Solucion)

                # Verificar que cada cliente se respete en las restricciones de nivel de inventario
                for cliente in contexto.clientes:
                    inventarios = solucion.inventario_clientes[cliente.id]
                    for t in range(contexto.horizonte_tiempo):
                        self.assertGreaterEqual(inventarios[t], cliente.nivel_minimo)
                        self.assertLessEqual(inventarios[t], cliente.nivel_maximo)

                # Verificar que las rutas estén definidas para cada periodo
                for t, ruta in enumerate(solucion.rutas):
                    self.assertIsInstance(ruta, Ruta)

                # Verificar que la solución sea factible
                self.assertTrue(solucion.es_admisible)
    
    def test_deterministic_solution(self):
        """
        Prueba que el procedimiento de inicialización siempre genere la misma solución
        bajo los mismos parámetros iniciales.
        """
        for n in range(5, 51, 5):
            for i in range(1, 6):
                horizonte_tiempo, proveedor, clientes, capacidad_vehiculo = self.read_input_irp(f'abs{i}n{n}.dat')
        
                # Pruebas con política ML
                contexto = Contexto(horizonte_tiempo, capacidad_vehiculo, proveedor, clientes, "ML", FactorPenalizacion(), FactorPenalizacion(), debug=False)
                contexto_ejecucion.set(contexto)

                solucion_1 = inicializacion()
                solucion_2 = inicializacion()

                # Las soluciones deben ser equivalentes
                self.assertTrue(solucion_1.es_igual(solucion_2))

if __name__ == '__main__':
    unittest.main()
