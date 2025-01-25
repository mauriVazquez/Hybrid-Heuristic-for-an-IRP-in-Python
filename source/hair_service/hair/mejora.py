from modelos.contexto_file import contexto_ejecucion
from modelos.solucion import Solucion
from modelos.ruta import Ruta

import numpy as np

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
    contexto = contexto_ejecucion.get()
    mejor_solucion = tsp_solver(None, solucion)
    
    do_continue = True
    while do_continue:
        do_continue = False
        
        # PRIMER TIPO DE MEJORA: MIP1 + TSP Solver
        solucion_prima = Mip1.ejecutar(mejor_solucion)
        solucion_prima = tsp_solver(mejor_solucion, solucion_prima)
        if solucion_prima.costo < mejor_solucion.costo:
            mejor_solucion = solucion_prima.clonar()
            print("Primer mejora")
            do_continue = True

        # SEGUNDO TIPO DE MEJORA: Merge Consecutivo de Rutas + MIP2
        solucion_merge = mejor_solucion.clonar()
        for i in range(contexto.horizonte_tiempo - 1):
            # Intentar combinar rutas consecutivas
            s1 = mejor_solucion.clonar()
            s1.merge_rutas(i, i + 1)
            aux_solucion = Mip2.ejecutar(s1)
            
            if (not aux_solucion.es_factible()) and (i < contexto.horizonte_tiempo - 2):
                s1.merge_rutas(i + 1, i + 2)

            aux_solucion = Mip2.ejecutar(s1) 
            if(aux_solucion.es_factible()):
                solucion_prima = tsp_solver(s1, aux_solucion)
                if solucion_prima.costo < solucion_merge.costo:
                    solucion_merge = aux_solucion.clonar()

            # Intentar combinar rutas en el orden inverso
            s2 = mejor_solucion.clonar()
            s2.merge_rutas(i + 1, i)
            
            aux_solucion = Mip2.ejecutar(s2)
            if (not aux_solucion.es_factible()) and i > 0:
                s2.merge_rutas(i, i-1)

            aux_solucion = Mip2.ejecutar(s2)
            if aux_solucion.es_factible():
                solucion_prima = tsp_solver(s1, aux_solucion)
                if solucion_prima.costo < solucion_merge.costo:
                    solucion_merge = solucion_prima.clonar()

        if solucion_merge.costo < mejor_solucion.costo:
            print("Segunda mejora")
            mejor_solucion = solucion_merge.clonar()
            do_continue = True

        # TERCER TIPO DE MEJORA: MIP2 + TSP Solver
        solucion_prima = Mip2.ejecutar(mejor_solucion)
        solucion_prima = tsp_solver(mejor_solucion, solucion_prima)
        if solucion_prima.costo < mejor_solucion.costo:
            mejor_solucion = solucion_prima.clonar()
            print("Tercer mejora")
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
    contexto = contexto_ejecucion.get()
    if ((solucion is not None) and (solucion.es_igual(solucion_prima))):
        aux_solucion = solucion.clonar()
    else:
        if contexto.ortools:
            aux_solucion = tsp_ortools(solucion_prima)
        else:
            aux_solucion = lk(solucion_prima)
    aux_solucion.refrescar()
    return aux_solucion


def tsp_ortools(solucion: Solucion) -> Solucion:
    contexto = contexto_ejecucion.get()
    aux_solucion = solucion.clonar()
    for t in range(contexto.horizonte_tiempo):
        matriz_distancia = _obtener_matriz_distancia(aux_solucion.rutas[t])
        data    = {"distance_matrix": matriz_distancia, "num_vehicles": 1, "depot": 0}
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
    contexto = contexto_ejecucion.get()
    for tiempo in range(contexto.horizonte_tiempo):
        tamano_matriz = len(solucion.rutas[tiempo].clientes)+1
        matriz =  [[0] * tamano_matriz for _ in range(tamano_matriz)]
        # Proveedor distancia
        for indice, cliente in enumerate(solucion.rutas[tiempo].clientes):
            matriz[0][indice+1] = cliente.distancia_proveedor
            matriz[indice+1][0] = cliente.distancia_proveedor
        # Clientes distancias
        for indice, c in enumerate(solucion.rutas[tiempo].clientes):
            for indice2, c2 in enumerate(solucion.rutas[tiempo].clientes):
                matriz[indice+1][indice2+1] = contexto.matriz_distancia[c.id][c2.id]
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
    contexto = contexto_ejecucion.get()
    matriz_distancia = [[0] + [c.distancia_proveedor for c in ruta.clientes]]

    for cliente1 in ruta.clientes:
        fila = [cliente1.distancia_proveedor]
        fila.extend(
            contexto.matriz_distancia[cliente1.id][cliente2.id]
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
        contexto = contexto_ejecucion.get()
        
        # Se realizan todas las permutaciones posibles
        for perm in permutations(range(contexto.horizonte_tiempo)):
            if perm == tuple(range(contexto.horizonte_tiempo)):
                continue  # Omitir la permutación (0, 1, 2)
        
            solucion_actual = Solucion([
                Ruta(list(solucion_original.rutas[i].clientes), list(solucion_original.rutas[i].cantidades)) for i in perm
            ])
            
            # Se calcula la funcion objetivo de la permutacion, que sea menor que el mejor hasta el momento, se asigna como nuevo mejor.
            if (cumple_restricciones(solucion_actual, 1) == 0):
                costo_mip = Mip1.funcion_objetivo(solucion_actual)
                if (costo_mip < costo_minimo):
                    costo_minimo = costo_mip
                    solucion_costo_minimo = solucion_actual.clonar()

            for cliente in contexto.clientes:
                for tiempo in solucion_actual.tiempos_cliente(cliente):
                    solucion_modificada = solucion_actual.clonar()
                    solucion_modificada.eliminar_visita(cliente, tiempo)

                    # Se veirifica que cumpla con las restricciones, retorna 0 si cumple con todas
                    if((cumple_restricciones(solucion_modificada, 1) == 0) and solucion_modificada.es_factible()):
                        # Se calcula la funcion objetivo de la permutacion, que sea menor que el mejor hasta el momento, se asigna como nuevo mejor.
                        ahorro = solucion_actual.rutas[tiempo].costo - solucion_modificada.rutas[tiempo].costo
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
        contexto = contexto_ejecucion.get()
        term_1 = contexto.proveedor.costo_almacenamiento * sum(solucion.inventario_proveedor)
        term_2 = sum([(c.costo_almacenamiento * sum(solucion.inventario_clientes.get(c.id, None))) for c in contexto.clientes])
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
        contexto = contexto_ejecucion.get()
        solucion_costo_minimo   = solucion.clonar()
        costo_minimo            = float("inf")
        
        for cliente in contexto.clientes:
            for tiempo in range(contexto.horizonte_tiempo):
                solucion_aux = solucion.clonar()
                if solucion.rutas[tiempo].es_visitado(cliente):
                    #Remover = 1   
                    operacion = "REMOVE"
                    costo_mip = Mip2.funcion_objetivo(solucion_aux, cliente, tiempo, operacion)
                else: 
                    #Insertar = 2
                    operacion = "INSERT"
                    costo_mip = Mip2.funcion_objetivo(solucion_aux, cliente, tiempo, 2)

                if (costo_mip < costo_minimo) and (cumple_restricciones(solucion_aux, 2, cliente, tiempo, operacion) == 0):
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
        contexto = contexto_ejecucion.get()
        costo_ruta_original = solucion.rutas[tiempo].costo
        if operacion == "REMOVE":
            solucion.eliminar_visita(cliente, tiempo)
            term_3 = costo_ruta_original - solucion.rutas[tiempo].costo
            term_4 = 0
        else:
            solucion.insertar_visita(cliente, tiempo)
            term_3 = 0
            term_4 = solucion.rutas[tiempo].costo - costo_ruta_original
        
        term_1 = contexto.proveedor.costo_almacenamiento * sum(solucion.inventario_proveedor)

        term_2 = sum([
            (cliente.costo_almacenamiento * sum(solucion.inventario_clientes.get(cliente.id)))
            for i, cliente in enumerate(contexto.clientes)
        ])
        
        return term_1 + term_2 - term_3 + term_4

def cumple_restricciones(solucion, MIP, MIPcliente = None, MIPtiempo = None, operation = None):
        contexto = solucion.contexto
        B   = solucion.inventario_proveedor
        I   = [solucion.inventario_clientes.get(cliente.id, None) for cliente in contexto.clientes]
        r0  = [contexto.proveedor.nivel_produccion for t in range(contexto.horizonte_tiempo+1)]
        ri  = [c.nivel_demanda for c in contexto.clientes]
        x   = [
            [solucion.rutas[t].obtener_cantidad_entregada(c) for t in range(contexto.horizonte_tiempo)]
            for c in contexto.clientes
        ]
        x_np = np.array(x)
        theta = [
            [(1 if solucion.rutas[t].es_visitado(c) else 0) for t in range(contexto.horizonte_tiempo)]
            for c in contexto.clientes
        ]
        
        # Variables MIP 2
        v   = [
            [ (1 if ((operation == "INSERT") and (MIPtiempo == t) and (MIPcliente == c)) else 0 ) for t in range(contexto.horizonte_tiempo)]
            for c in contexto.clientes
        ]
        w   = [
            [ (1 if ((operation == "REMOVE") and (MIPtiempo == t) and (MIPcliente == c)) else 0 ) for t in range(contexto.horizonte_tiempo)]
            for c in contexto.clientes
        ]
        sigma = [
            [(1 if solucion.rutas[t].es_visitado(c) else 0) for t in range(contexto.horizonte_tiempo)]
            for c in contexto.clientes
        ]
       
        # Restricción 2: Definición del nivel de inventario del proveedor.
        if (not all([(B[t] == (B[t-1] + r0[t-1] - np.sum( x_np[:, t-1]))) for t in range(1, contexto.horizonte_tiempo+1)])):
            return 2            
        
        # Restricción 3: El nivel de inventario del proveedor debe poder satisfacer la demanda en el tiempo t.
        if (not all(B[t] >= np.sum( x_np[:, t]) for t in range(contexto.horizonte_tiempo))):
            return 3
        
        # Restricción 4: Definición del nivel de inventario de los clientes
        if (not all([(I[c][t] == (I[c][t-1] + x[c][t-1] - ri[c] ))
                for c in range(len(contexto.clientes))
                for t in range(1, contexto.horizonte_tiempo+1)]
        )):
            return 4
        
        if contexto.politica_reabastecimiento == "OU": 
            # Restricción 5: La cantidad entregada al cliente no es menos de la necesaria para llenar el inventario.
            if (not all([(x[c][t] >= ((cliente.nivel_maximo * theta[c][t]) - I[c][t]))
                for c, cliente in enumerate(contexto.clientes)
                for t in range(contexto.horizonte_tiempo)]
            )):
                return 5
        
        # Restricción 6: La cantidad entregada al cliente no debe generar sobreabastecimiento en el cliente.
        if (not all([( x[c][t] <= (cliente.nivel_maximo - I[c][t]) )
            for c, cliente in enumerate(contexto.clientes)
            for t in range(contexto.horizonte_tiempo)]
        )):
            return 6
        
        if contexto.politica_reabastecimiento == "OU":
            # Restricción 7: La cantidad entregada a un cliente es menor o igual al nivel máximo de inventario si es que lo visita.
            if  (not all([( x[c][t] <= (cliente.nivel_maximo * theta[c][t]) )
                for c, cliente in enumerate(contexto.clientes)
                for t in range(contexto.horizonte_tiempo)]
            )):
                return 7
            
        # Restricción 8: La cantidad entregada a los clientes en un t dado, es menor o igual a la capacidad del camión.
        if (not all([np.sum( x_np[:, t]) <= contexto.capacidad_vehiculo for t in range(contexto.horizonte_tiempo)])):
            return 8
        
        if MIP == 1:
            #  Restricción 9: Una ruta solo puede asignarse a un período de tiempo
            if not all(sum(ruta) <= 1 for ruta in sigma):
                return 9

            # Restricción 10: Solo una ruta puede asignarse a un período de tiempo dado
            if not all(sum(tiempo) <= 1 for tiempo in zip(*sigma)):
                return 10

            # Restricción 11: Un cliente puede ser atendido solo si la ruta está asignada
            if not all(x[c][t] <= contexto.clientes[c].nivel_maximo * sigma[c][t] for c in range(len(contexto.clientes)) for t in range(contexto.horizonte_tiempo)):
                return 11

            # Restricción 12: No puede atenderse un cliente si fue removido de la ruta asignada
            if not all(x[c][t] == 0 if w[c][t] else True for c in range(len(contexto.clientes)) for t in range(contexto.horizonte_tiempo)):
                return 12
            
            # Restricción 13: Un cliente puede ser removido solo si su ruta está asignada
            if not all(w[c][t] <= sigma[c][t] for c in range(len(contexto.clientes)) for t in range(contexto.horizonte_tiempo)):
                return 13

            # Restricción 18: Las variables de asignación de rutas (zr_t) deben ser binarias
            if not all(value in [0, 1] for fila in sigma for value in fila):
                return 18

            # Restricción 19: La variable de asignación epsilon_it debe ser binaria
            if not all(value in [0, 1] for fila in theta for value in fila):
                return 19

            # Restricción 20: El inventario en los clientes debe ser mayor o igual a cero
            if not all(I[c][t] >= 0 for c in range(len(contexto.clientes)) for t in range(contexto.horizonte_tiempo)):
                return 20
        
        # Restricción 14: La cantidad entregada a los clientes siempre debe ser mayor o igual a cero
        if not np.all(x_np >= 0):
            return 14
        
        #Restricción 17: Theeta puede tener el valor 0 o 1
        if contexto.politica_reabastecimiento == "OU":
            if not all(value in [0, 1] for fila in theta for value in fila):
                return 17
          
        if MIP == 2:            
            # Restricción 21 (MIP2): Si se inserta una visita, no debe haber una visita existente
            if not all(v[c][t] <= 1 - sigma[c][t] for c in range(len(contexto.clientes)) for t in range(contexto.horizonte_tiempo)):
                return 21

            # Restricción 22 (MIP2): Si se elimina una visita, debe existir previamente una visita
            if not all(w[c][t] <= sigma[c][t] for c in range(len(contexto.clientes)) for t in range(contexto.horizonte_tiempo)):
                return 22
    
            # Restricción 23: La cantidad entregada al cliente i no puede ser mayor a la capacidad máxima
            if not all([ ( x[c][t] <= (cliente.nivel_maximo * (sigma[c][t] + v[c][t] - w[c][t])))
                for c, cliente in enumerate(contexto.clientes)
                for t in range(contexto.horizonte_tiempo)]
            ):
                return 23
            
            #Restricción 24: v_it debe ser 0 o 1
            if not all(value in [0, 1] for fila in v for value in fila):
                return 24
            
            #Restricción 25: w_it debe ser 0 o 1
            if not all(value in [0, 1] for fila in w for value in fila):
                return 25
            
        return 0