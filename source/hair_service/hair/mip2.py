from constantes import constantes
from modelos.solucion import Solucion
from typing import Type

class Mip2():
    """
    Clase que implementa el método de mejora de solución MIP2.

    Methods:
        ejecutar(solucion): Ejecuta el algoritmo MIP2 para mejorar la solución.
        costo(solucion, cliente, tiempo, operation): Calcula el costo asociado a una solución.

    Attributes:
        No hay atributos públicos, la clase utiliza métodos estáticos.
    """
    @staticmethod
    def ejecutar(solucion: Type["Solucion"]) -> Type["Solucion"]:
        """
        Ejecuta el algoritmo MIP2 para mejorar la solución.

        Args:
            solucion (TipoDeSolucion): La solución original a mejorar.

        Retorna:
            TipoDeSolucion: La solución mejorada obtenida mediante el algoritmo MIP2.
        """
        solucion_costo_minimo   = solucion.clonar()
        costo_minimo            = float("inf")
        
        for cliente in constantes.clientes:
            for tiempo in range(constantes.horizon_length):
                solucion_aux = solucion.clonar()
                operacion = "REMOVE" if solucion.es_visitado(cliente, tiempo) else "INSERT"
                costo_mip = Mip2.funcion_objetivo(solucion_aux, cliente, tiempo, operacion)
                if operacion == "REMOVE":
                    solucion_aux.remover_visita(cliente,tiempo)
                else:
                    solucion_aux.insertar_visita(cliente, tiempo)
                if (costo_mip < costo_minimo) and (solucion_aux.cumple_restricciones(2, cliente, tiempo, operacion) == 0):
                    costo_minimo = costo_mip
                    solucion_costo_minimo = solucion_aux.clonar()
        
        # print(f"SALIDA MIP2 {solucion_costo_minimo}")
        return solucion_costo_minimo

    @staticmethod
    def funcion_objetivo(solucion, cliente, tiempo, operation):
        """
        Calcula el costo asociado a una solución.

        Args:
            solucion (TipoDeSolucion): La solución para la cual calcular el costo.
            cliente (Cliente): El cliente involucrado en la operación.
            tiempo (int): El tiempo en el cual se realiza la operación.
            operation (str): Tipo de operación, "INSERT" o "REMOVE".

        Retorna:
            float: El costo total asociado a la solución después de realizar la operación.
        """
        niveles_proveedor = solucion.inventario_proveedor
        
        term_1 = constantes.proveedor.costo_almacenamiento * sum(niveles_proveedor)

        term_2 = sum([
            (cliente.costo_almacenamiento * sum(solucion.inventario_clientes[cliente.id - 1]))
            for cliente in constantes.clientes
        ])
        
        if operation != "REMOVE":
            term_3 = 0
        else:
            aux_ruta = solucion.rutas[tiempo].clonar()
            aux_ruta.remover_visita(cliente)
            term_3 = solucion.rutas[tiempo].obtener_costo() - aux_ruta.obtener_costo()
            

        if operation != "INSERT":
            term_4 = 0
        else:
            solucion_aux = solucion.clonar()
            solucion_aux.insertar_visita(cliente, tiempo)
            term_4 = solucion_aux.rutas[tiempo].obtener_costo() - solucion.rutas[tiempo].obtener_costo()

        return term_1 + term_2 - term_3 + term_4
