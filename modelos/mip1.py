from itertools import permutations
from constantes import constantes
from modelos.ruta import Ruta

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

        Returns:
            TipoDeSolucion: La solución mejorada obtenida mediante el algoritmo MIP1.
        """
        costo_minimo = float("inf")
        costo_minimo_solucion = solucion_original.clonar()

        for perm in permutations(range(constantes.horizon_length)):
            solucion_actual = solucion_original.clonar()
            solucion_actual.rutas = [solucion_actual.rutas[i] for i in perm]
            solucion_actual.refrescar()

            costo_mip = Mip1.costo(solucion_actual)
            if costo_mip < costo_minimo and solucion_actual.pass_constraints("MIP1"):
                costo_minimo = costo_mip
                costo_minimo_solucion = solucion_actual.clonar()

            for cliente in constantes.clientes:
                for tiempo in range(constantes.horizon_length):
                    solucion_modificada = solucion_actual.clonar()
                    if solucion_modificada.rutas[tiempo].es_visitado(cliente):
                        costo_mip = Mip1.costo(solucion_modificada, cliente, tiempo)
                        solucion_modificada.remover_visita(cliente, tiempo)
                        solucion_modificada.refrescar()
                        if costo_mip < costo_minimo and solucion_modificada.pass_constraints("MIP1", cliente, tiempo, "REMOVE"):
                            costo_minimo = costo_mip
                            costo_minimo_solucion = solucion_modificada.clonar()

        costo_minimo_solucion.refrescar()
        #print(f"SALIDA MIP1 {costo_minimo_solucion}")
        return costo_minimo_solucion

    @staticmethod
    def costo(solucion, cliente_eliminado=None, eliminado_tiempo=None):
        """
        Calcula el costo asociado a una solución.

        Args:
            solucion (TipoDeSolucion): La solución para la cual calcular el costo.
            cliente_eliminado (Cliente, optional): Cliente eliminado de la solución.
            eliminado_tiempo (int, optional): Tiempo en el cual se eliminó el cliente.

        Returns:
            float: El costo total asociado a la solución.
        """
        solucion.refrescar()

        term_1 = constantes.proveedor.costo_almacenamiento * sum(solucion.B(t) for t in range(constantes.horizon_length + 1))

        term_2 = sum(cliente.costo_almacenamiento * solucion.obtener_niveles_inventario_cliente(cliente)[t]
                    for t in range(constantes.horizon_length + 1)
                    for cliente in constantes.clientes)

        if cliente_eliminado is None:
            term_3 = 0
        else:
            # 3rd term represents the saving
            ruta_actualizada = solucion.rutas[eliminado_tiempo].clonar()
            ruta_actualizada.remover_visita(cliente_eliminado)
            term_3 = solucion.rutas[eliminado_tiempo].obtener_costo() - Ruta.obtener_costo_recorrido(ruta_actualizada.clientes)

        return term_1 + term_2 - term_3 if any(len(ruta.clientes) > 0 for ruta in solucion.rutas) else float("inf")
    
