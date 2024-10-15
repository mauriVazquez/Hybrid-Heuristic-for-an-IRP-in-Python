from itertools import permutations
from constantes import constantes
from modelos.ruta import Ruta
from modelos.solucion import Solucion
from typing import Type

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
    def ejecutar(solucion_original : Type["Solucion"]) -> Type["Solucion"]:
        """
        Ejecuta el algoritmo MIP1 para mejorar la solución original.

        Args:
            solucion_original (TipoDeSolucion): La solución original a mejorar.

        Retorna:
            TipoDeSolucion: La solución mejorada obtenida mediante el algoritmo MIP1.
        """
        solucion_costo_minimo   = solucion_original.clonar()
        costo_minimo            = float("inf")

        # Se realizan todas las permutaciones posibles
        for perm in permutations(range(constantes.horizon_length)):
            if perm == tuple(range(constantes.horizon_length)):
                continue  # Omitir la permutación (0, 1, 2)
        
            solucion_actual = Solucion([
                Ruta(list(solucion_original.rutas[i].clientes), list(solucion_original.rutas[i].cantidades)) for i in perm
            ])
            
            # Se veirifica que cumpla con las restricciones, retorna 0 si cumple con todas
            cumple_restricciones = solucion_actual.cumple_restricciones(1)
            
            # Se calcula la funcion objetivo de la permutacion, que sea menor que el mejor hasta el momento, se asigna como nuevo mejor.
            if (cumple_restricciones == 0):
                costo_mip = Mip1.funcion_objetivo(solucion_actual)
                if (costo_mip < costo_minimo):
                    costo_minimo = costo_mip
                    solucion_costo_minimo = solucion_actual.clonar()

            for cliente in constantes.clientes:
                for tiempo in solucion_actual.T(cliente):
                    solucion_modificada = solucion_actual.clonar()
                    solucion_modificada.remover_visita(cliente, tiempo)

                    # Se veirifica que cumpla con las restricciones, retorna 0 si cumple con todas
                    cumple_restricciones = solucion_modificada.cumple_restricciones(1)
                    if((cumple_restricciones == 0) and solucion_modificada.es_factible):
                        # Se calcula la funcion objetivo de la permutacion, que sea menor que el mejor hasta el momento, se asigna como nuevo mejor.
                        ahorro = solucion_actual.rutas[tiempo].obtener_costo() - solucion_modificada.rutas[tiempo].obtener_costo()
                        costo_mip = Mip1.funcion_objetivo(solucion_modificada, ahorro)
                        if (costo_mip < costo_minimo):
                            costo_minimo = costo_mip
                            solucion_costo_minimo = solucion_modificada.clonar()
        # print(f"SALIDA MIP1 {solucion_costo_minimo}")
        return solucion_costo_minimo

    @staticmethod
    def funcion_objetivo(solucion, ahorro = 0) -> float:
        """
        Calcula el costo asociado a una solución.

        Args:
            solucion (TipoDeSolucion): La solución para la cual calcular el costo.
            ahorro (float, optional): El ahorro en costo de transporte al eliminar al cliente.

        Retorna:
            float: El costo total asociado a la solución.
        """
        term_1 = constantes.proveedor.costo_almacenamiento * sum(solucion.inventario_proveedor)
        term_2 = sum([(c.costo_almacenamiento * sum(solucion.inventario_clientes[c.id - 1])) for c in constantes.clientes])
        term_3 = ahorro
        return (term_1 + term_2 - term_3)
    
