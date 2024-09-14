from itertools import permutations
from constantes import constantes
from modelos.ruta import Ruta
from modelos.solucion import Solucion

class Mip1():
    """
    Clase que implementa el método de mejora de solución MIP1.

    Methods:
        ejecutar(solucion_original): Ejecuta el algoritmo MIP1 para mejorar la solución original.
        costo(solucion, cliente_eliminado=None, eliminado_tiempo=None): Calcula el costo asociado a una solución.

    Attributes:
        No hay atributos públicos, la clase utiliza métodos estáticos.
    """
    @staticmethod
    def ejecutar(solucion_original):
        """
        Ejecuta el algoritmo MIP1 para mejorar la solución original.

        Args:
            solucion_original (TipoDeSolucion): La solución original a mejorar.

        Retorna:
            TipoDeSolucion: La solución mejorada obtenida mediante el algoritmo MIP1.
        """
        costo_minimo = float("inf")
        costo_minimo_solucion = solucion_original.clonar()

        for perm in permutations(range(constantes.horizon_length)):
            solucion_actual = Solucion([Ruta(list(solucion_original.rutas[i].clientes), list(solucion_original.rutas[i].cantidades)) for i in perm])
            
            costo_mip = Mip1.costo(solucion_actual)
            cumple_restricciones = solucion_actual.cumple_restricciones(1)
            if ((costo_mip < costo_minimo) and (cumple_restricciones == 0)):
                costo_minimo = costo_mip
                costo_minimo_solucion = solucion_actual.clonar()

            for cliente in constantes.clientes:
                for tiempo in solucion_actual.T(cliente):
                    solucion_modificada = solucion_actual.clonar()
                    costo_mip = Mip1.costo(solucion_modificada, cliente, tiempo)
                    
                    q = solucion_modificada.rutas[tiempo].remover_visita(cliente)
                    cumple_restricciones = solucion_modificada.cumple_restricciones(1)
                    
                    if ((costo_mip < costo_minimo) and (cumple_restricciones == 0)):
                        costo_minimo = costo_mip
                        costo_minimo_solucion = solucion_modificada.clonar()
        
        return costo_minimo_solucion

    @staticmethod
    def costo(solucion, cliente_eliminado=None, eliminado_tiempo=None):
        """
        Calcula el costo asociado a una solución.

        Args:
            solucion (TipoDeSolucion): La solución para la cual calcular el costo.
            cliente_eliminado (Cliente, optional): Cliente eliminado de la solución.
            eliminado_tiempo (int, optional): Tiempo en el cual se eliminó el cliente.

        Retorna:
            float: El costo total asociado a la solución.
        """

        term_1 =  sum([(constantes.proveedor.costo_almacenamiento * solucion.obtener_niveles_inventario_proveedor()[t]) for t in range(constantes.horizon_length + 1)])

        term_2 = sum([(cliente.costo_almacenamiento * solucion.obtener_niveles_inventario_cliente(cliente)[t]) for t in range(constantes.horizon_length + 1) for cliente in constantes.clientes])

        if cliente_eliminado is None:
            term_3 = 0
        else:
            ruta_actualizada = solucion.rutas[eliminado_tiempo].clonar()
            ruta_actualizada.remover_visita(cliente_eliminado)
            term_3 = solucion.rutas[eliminado_tiempo].obtener_costo() - ruta_actualizada.obtener_costo()
        
        return (term_1 + term_2 - term_3)
    
