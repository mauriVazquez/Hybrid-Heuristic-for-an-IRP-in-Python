from hair.contexto import constantes_contexto
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
        constantes = constantes_contexto.get()
        solucion_costo_minimo   = solucion.clonar()
        costo_minimo            = float("inf")
        
        for cliente in constantes.clientes:
            for tiempo in range(constantes.horizonte_tiempo):
                solucion_aux = solucion.clonar()
                if solucion.es_visitado(cliente, tiempo):
                    #Remover = 1   
                    operacion = "REMOVE"
                    costo_mip = Mip2.funcion_objetivo(solucion_aux, cliente, tiempo, operacion)
                else: 
                    #Insertar = 2
                    operacion = "INSERT"
                    costo_mip = Mip2.funcion_objetivo(solucion_aux, cliente, tiempo, 2)

                if (costo_mip < costo_minimo) and (solucion_aux.cumple_restricciones(2, cliente, tiempo, operacion) == 0):
                    costo_minimo = costo_mip
                    solucion_costo_minimo = solucion_aux.clonar()
        
        # print(f"SALIDA MIP2 {solucion_costo_minimo}")
        return solucion_costo_minimo

    @staticmethod
    def funcion_objetivo(solucion, cliente, tiempo, operacion):
        """
        Calcula el costo asociado a una solución.

        Args:
            solucion (TipoDeSolucion): La solución para la cual calcular el costo.
            cliente (Cliente): El cliente involucrado en la operación.
            tiempo (int): El tiempo en el cual se realiza la operación.
            operacion (str): Tipo de operación, "REMOVE" o "INSERT".

        Retorna:
            float: El costo total asociado a la solución después de realizar la operación.
        """
        constantes = constantes_contexto.get()
        costo_ruta_original = solucion.rutas[tiempo].obtener_costo()
        if operacion == "REMOVE":
            solucion.remover_visita(cliente, tiempo)
            term_3 = costo_ruta_original - solucion.rutas[tiempo].obtener_costo()
            term_4 = 0
        else:
            solucion.insertar_visita(cliente, tiempo)
            term_3 = 0
            term_4 = solucion.rutas[tiempo].obtener_costo() - costo_ruta_original
        
        term_1 = constantes.proveedor.costo_almacenamiento * sum(solucion.inventario_proveedor)

        term_2 = sum([
            (cliente.costo_almacenamiento * sum(solucion.inventario_clientes.get(cliente.id)))
            for i, cliente in enumerate(constantes.clientes)
        ])
        
        return term_1 + term_2 - term_3 + term_4
