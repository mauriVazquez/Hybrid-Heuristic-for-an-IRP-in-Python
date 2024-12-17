from hair.contexto import constantes_contexto
from modelos.solucion import Solucion
from modelos.ruta import Ruta

from tsp_local.base import TSP
from tsp_local.kopt import KOpt

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from ortools.linear_solver import pywraplp
from itertools import permutations

def mejora(solucion: Solucion, iterador_principal: int) -> Solucion:
    """
    Aplica un proceso iterativo de mejora a la solución dada utilizando tres tipos diferentes de optimizaciones:
    
    1. Aplicación del modelo MIP1 seguido del tsp_solver.
    2. Fusión de pares consecutivos de rutas y aplicación del modelo MIP2 con ajustes para asegurar factibilidad.
    3. Aplicación directa del modelo MIP2 seguido del algoritmo tsp_solver.

    Args:
        solucion (Solucion): La solución inicial a optimizar.
        iterador_principal (int): Número de la iteración principal actual.

    Returns:
        Solucion: La mejor solución obtenida después de aplicar todas las mejoras.
    """
    constantes = constantes_contexto.get()
    do_continue = True
    mejor_solucion = tsp_solver(None, solucion)

    while do_continue:
        do_continue = False

        # PRIMER TIPO DE MEJORA: MIP1 + TSP Solver
        solucion_prima = Mip1.ejecutar(mejor_solucion)
        solucion_prima = tsp_solver(mejor_solucion, solucion_prima)
        if solucion_prima.costo < mejor_solucion.costo:
            mejor_solucion = solucion_prima.clonar()
            do_continue = True

        # SEGUNDO TIPO DE MEJORA: Merge Consecutivo de Rutas + MIP2
        solucion_merge = mejor_solucion.clonar()
        for i in range(constantes.horizonte_tiempo - 1):
            # Intentar combinar rutas consecutivas
            s1 = mejor_solucion.clonar()
            s1.merge_rutas(i, i + 1)
            aux_solucion = Mip2.ejecutar(s1)
            aux_solucion = tsp_solver(s1, aux_solucion)

            if aux_solucion.es_factible and aux_solucion.costo < solucion_merge.costo:
                solucion_merge = aux_solucion.clonar()

            # Intentar combinar rutas en el orden inverso
            s2 = mejor_solucion.clonar()
            s2.merge_rutas(i + 1, i)
            aux_solucion = Mip2.ejecutar(s2)
            aux_solucion = tsp_solver(s2, aux_solucion)

            if aux_solucion.es_factible and aux_solucion.costo < solucion_merge.costo:
                solucion_merge = aux_solucion.clonar()

        if solucion_merge.costo < mejor_solucion.costo:
            mejor_solucion = solucion_merge.clonar()
            do_continue = True

        # TERCER TIPO DE MEJORA: MIP2 + TSP Solver
        solucion_prima = Mip2.ejecutar(mejor_solucion)
        solucion_prima = tsp_solver(mejor_solucion, solucion_prima)
        if solucion_prima.costo < mejor_solucion.costo:
            mejor_solucion = solucion_prima.clonar()
            do_continue = True

    mejor_solucion.refrescar()
    print(f"Mejora ({iterador_principal}): {mejor_solucion}")
    return mejor_solucion.clonar()


def tsp_solver(solucion: Solucion, solucion_prima: Solucion) -> Solucion:
    """
    Optimiza las rutas de una solución utilizando un solver TSP basado en OR-Tools.

    Args:
        solucion (Solucion): La solución inicial.
        solucion_prima (Solucion): La solución alternativa a optimizar.

    Returns:
        Solucion: La solución optimizada después de aplicar el solver TSP.
    """
    constantes = constantes_contexto.get()
    if ((solucion is not None) and (solucion.es_igual(solucion_prima))):
        aux_solucion = solucion.clonar()
    else:
        if constantes.ortools:
            aux_solucion = tsp_ortools(solucion_prima)
        else:
            aux_solucion = lk(solucion_prima)
    aux_solucion.refrescar()
    return aux_solucion


def tsp_ortools(solucion: Solucion) -> Solucion:
    constantes = constantes_contexto.get()
    aux_solucion = solucion.clonar()
    for t in range(constantes.horizonte_tiempo):
        matriz_distancia = _obtener_matriz_distancia(aux_solucion.rutas[t])
        data = {"distance_matrix": matriz_distancia, "num_vehicles": 1, "depot": 0}
        manager = pywrapcp.RoutingIndexManager(len(data["distance_matrix"]), data["num_vehicles"], data["depot"])
        routing = pywrapcp.RoutingModel(manager)

        transit_callback_index = routing.RegisterTransitCallback(
            lambda from_index, to_index: data["distance_matrix"][manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]
        )
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        parametros_busqueda = pywrapcp.DefaultRoutingSearchParameters()
        parametros_busqueda.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

        solucion_modelo = routing.SolveWithParameters(parametros_busqueda)
        if solucion_modelo:
            ruta_optima = []
            index = routing.Start(0)
            while not routing.IsEnd(index):
                siguiente_index = solucion_modelo.Value(routing.NextVar(index))
                if manager.IndexToNode(siguiente_index) != 0:
                    ruta_optima.append(manager.IndexToNode(siguiente_index))
                index = siguiente_index

            nueva_ruta = Ruta(
                [aux_solucion.rutas[t].clientes[indice - 1] for indice in ruta_optima],
                [aux_solucion.rutas[t].cantidades[indice - 1] for indice in ruta_optima]
            )
            aux_solucion.rutas[t] = nueva_ruta.clonar()

    aux_solucion.refrescar()
    return aux_solucion

def lk(solucion: Solucion) -> Solucion:
    aux_solucion = solucion.clonar()
    constantes = constantes_contexto.get()
    for tiempo in range(constantes.horizonte_tiempo):
        tamano_matriz = len(solucion.rutas[tiempo].clientes)+1
        matriz =  [[0] * tamano_matriz for _ in range(tamano_matriz)]
        # Proveedor distancia
        for indice, cliente in enumerate(solucion.rutas[tiempo].clientes):
            matriz[0][indice+1] = cliente.distancia_proveedor
            matriz[indice+1][0] = cliente.distancia_proveedor
        # Clientes distancias
        for indice, c in enumerate(solucion.rutas[tiempo].clientes):
            for indice2, c2 in enumerate(solucion.rutas[tiempo].clientes):
                matriz[indice+1][indice2+1] = constantes.matriz_distancia[c.id][c2.id]
        # Make an instance with all nodes
        TSP.setEdges(matriz)
        path, costo = KOpt(range(len(matriz))).optimise()
        
        aux_solucion.rutas[tiempo] = Ruta(
            [solucion.rutas[tiempo].clientes[indice - 1] for indice in path[1:]],
            [solucion.rutas[tiempo].cantidades[indice - 1] for indice in path[1:]]
        )
    aux_solucion.refrescar()
    return aux_solucion

def _obtener_matriz_distancia(ruta):
    # Crear la matriz de distancias entre los clientes visitados en el tiempo t
    constantes = constantes_contexto.get()
    matriz_distancia = [[0] + [c.distancia_proveedor for c in ruta.clientes]]

    for cliente1 in ruta.clientes:
        fila = [cliente1.distancia_proveedor]
        fila.extend(
            constantes.matriz_distancia[cliente1.id][cliente2.id]
            for cliente2 in ruta.clientes
        )
        matriz_distancia.append(fila)
    return matriz_distancia
    
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
    def ejecutar(solucion_original : Solucion) -> Solucion:
        """
        Ejecuta el algoritmo MIP1 para mejorar la solución original.

        Args:
            solucion_original (TipoDeSolucion): La solución original a mejorar.

        Retorna:
            TipoDeSolucion: La solución mejorada obtenida mediante el algoritmo MIP1.
        """
        solucion_costo_minimo   = solucion_original.clonar()
        costo_minimo            = float("inf")
        constantes = constantes_contexto.get()
        
        # Se realizan todas las permutaciones posibles
        for perm in permutations(range(constantes.horizonte_tiempo)):
            if perm == tuple(range(constantes.horizonte_tiempo)):
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
        constantes = constantes_contexto.get()
        term_1 = constantes.proveedor.costo_almacenamiento * sum(solucion.inventario_proveedor)
        term_2 = sum([(c.costo_almacenamiento * sum(solucion.inventario_clientes.get(c.id, None))) for c in constantes.clientes])
        term_3 = ahorro
        return (term_1 + term_2 - term_3)
    
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
    def ejecutar(solucion: Solucion) -> Solucion:
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
