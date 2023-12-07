from constantes import constantes

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
    def ejecutar(solucion):
        """
        Ejecuta el algoritmo MIP2 para mejorar la solución.

        Args:
            solucion (TipoDeSolucion): La solución original a mejorar.

        Returns:
            TipoDeSolucion: La solución mejorada obtenida mediante el algoritmo MIP2.
        """
        costo_minimo = float("inf")
        costo_minimo_solucion = solucion.clonar()

        for cliente in constantes.clientes:
            for tiempo in range(constantes.horizon_length):
                solucion_aux = solucion.clonar()
                operacion = "REMOVE" if solucion.rutas[tiempo].es_visitado(cliente) else "INSERT"
                costo_mip = Mip2.costo(solucion_aux, cliente, tiempo, operacion)
                if operacion == "REMOVE":
                    solucion_aux.remover_visita(cliente,tiempo)
                else:
                    solucion_aux.insertar_visita(cliente, tiempo)
                if costo_mip < costo_minimo and solucion_aux.pass_constraints("MIP2", cliente, tiempo, operacion):
                        costo_minimo = costo_mip
                        costo_minimo_solucion = solucion_aux.clonar()
        
        costo_minimo_solucion.refrescar()
        #print(f"SALIDA MIP2 {costo_minimo_solucion}")
        return costo_minimo_solucion

    @staticmethod
    def costo(solucion, cliente, tiempo, operation):
        """
        Calcula el costo asociado a una solución.

        Args:
            solucion (TipoDeSolucion): La solución para la cual calcular el costo.
            cliente (Cliente): El cliente involucrado en la operación.
            tiempo (int): El tiempo en el cual se realiza la operación.
            operation (str): Tipo de operación, "INSERT" o "REMOVE".

        Returns:
            float: El costo total asociado a la solución después de realizar la operación.
        """
        solucion.refrescar()
        if not any(len(ruta.clientes) > 0 for ruta in solucion.rutas):
            return float("inf")
        
        term_1 = sum([constantes.proveedor.costo_almacenamiento * solucion.obtener_niveles_inventario_proveedor()[t]
                      for t in range(constantes.horizon_length+1)])

        term_2 = sum([sum([cliente.costo_almacenamiento * solucion.obtener_niveles_inventario_cliente(cliente)[t]
                    for t in range(constantes.horizon_length)])
                    for cliente in constantes.clientes])

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
