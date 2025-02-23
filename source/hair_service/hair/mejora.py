from modelos.solucion import Solucion
from modelos.ruta import Ruta
from itertools import permutations
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
import numpy as np


def mejora(solucion: Solucion, iterador_principal: int) -> Solucion:
    """
    Aplica un procedimiento iterativo de mejoras basado en MIP1, MIP2 y Lin-Kernighan (LK).
    """
    print(solucion)
    mejor_solucion = LK(None, solucion)
    do_continue = True

    while do_continue:
        do_continue = False
        # PRIMERA MEJORA: Aplicación iterativa de MIP1 + LK
        solucion_prima = Mip1.ejecutar(mejor_solucion)
        solucion_prima = LK(mejor_solucion, solucion_prima)
        if solucion_prima.costo < mejor_solucion.costo:
            mejor_solucion = solucion_prima
            do_continue = True
        
        # SEGUNDA MEJORA: Merge de rutas consecutivas en ambas direcciones + MIP2
        solucion_merge = mejor_solucion
        for i in range(solucion.contexto.horizonte_tiempo - 1):
            # Merge hacia adelante (ruta i con ruta i+1)
            s1 = mejor_solucion.merge_rutas(i, i + 1)
            s1 = Mip2.ejecutar(s1)
            if s1.es_factible:
                solucion_prima = LK(s1, solucion_prima)
                if solucion_prima.costo < solucion_merge.costo:
                    solucion_merge = solucion_prima

        # Merge hacia atrás (ruta i con ruta i-1)
        for i in range(1, solucion.contexto.horizonte_tiempo):
            s2 = mejor_solucion.merge_rutas(i - 1, i)  # Ahora en dirección inversa
            s2 = Mip2.ejecutar(s2)

            if s2.es_factible:
                solucion_prima = LK(s2, solucion_prima)
                if solucion_prima.costo < solucion_merge.costo:
                    solucion_merge = solucion_prima

        # Aplicar el mejor resultado de los merges
        if solucion_merge.costo < mejor_solucion.costo:
            mejor_solucion = solucion_merge
            print("VAMO2")
            do_continue = True

        # TERCERA MEJORA: Aplicación de MIP2 + LK
        solucion_prima = Mip2.ejecutar(mejor_solucion)
        solucion_prima = LK(mejor_solucion, solucion_prima)
        if solucion_prima.costo < mejor_solucion.costo:
            mejor_solucion = solucion_prima
            do_continue = True
            print("VAMO3")
            
    print(f"MEJORA {mejor_solucion}")
    return mejor_solucion

def LK(solucion: Solucion, solucion_prima : Solucion) -> Solucion:
    """
    Aplica Lin-Kernighan heurístico para mejorar la solución.
    """
    if ((solucion is not None) and solucion.es_igual(solucion_prima)):
        return solucion_prima.clonar()
        
    iter_sol = solucion_prima.clonar()
    for r, ruta in enumerate(iter_sol.rutas):
        if len(ruta.clientes) > 1:
            clientes = ruta.clientes

            # Crear matriz de distancias original
            matriz_distancia = [
                [iter_sol.contexto.matriz_distancia[c1.id][c2.id] for c1 in clientes]
                for c2 in clientes
            ]

            fila_proveedor = [int(c.distancia_proveedor) for c in clientes]
            fila_proveedor.insert(0, 0)  # Distancia del proveedor a sí mismo

            for i, c in enumerate(clientes):
                matriz_distancia[i].insert(0, int(c.distancia_proveedor))

            # Finalmente, agregar la fila del proveedor a la matriz
            matriz_distancia.insert(0, fila_proveedor)

            iter_sol = optimizar_tsp(iter_sol, r, matriz_distancia)
    return solucion_prima

def optimizar_tsp(solucion, t, distance_matrix):
    # Crear un diccionario para mapear clientes a índices
    cliente_indices = {cliente: i + 1 for i, cliente in enumerate(solucion.rutas[t].clientes)}
    cliente_indices[None] = 0 #indice 0 para el deposito.

    # Crear la matriz de distancias en el orden correcto
    ordered_distance_matrix = [[0] * (len(solucion.rutas[t].clientes) + 1) for _ in range(len(solucion.rutas[t].clientes) + 1)]
    for i in range(len(solucion.rutas[t].clientes) + 1):
        for j in range(len(solucion.rutas[t].clientes) + 1):
            ordered_distance_matrix[i][j] = distance_matrix[i][j]

    # Crear el modelo de enrutamiento
    manager = pywrapcp.RoutingIndexManager(len(ordered_distance_matrix), 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return ordered_distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.time_limit.seconds = len(solucion.contexto.clientes) 

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Extraer la ruta
    route = []
    if solution:
        index = routing.Start(0)
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))

        # Mapear los índices de vuelta a los clientes originales
        clientes_ordenados = [solucion.rutas[t].clientes[i - 1] for i in route if i != 0]
        cantidades_ordenadas = [solucion.rutas[t].obtener_cantidad_entregada(c) for c in clientes_ordenados]
        rutas_modificadas = list(solucion.rutas)
        rutas_modificadas[t] = Ruta(tuple(clientes_ordenados), tuple(cantidades_ordenadas))
        return Solucion(rutas=tuple(rutas_modificadas))
    else:
        return solucion.clonar()

class Mip1:
    @staticmethod
    def ejecutar(solucion_original: Solucion) -> Solucion:
        mejor_solucion = solucion_original.clonar()
        costo_minimo = solucion_original.costo
        contexto = solucion_original.contexto

        for tiempo in range(contexto.horizonte_tiempo):
            for ruta_idx, ruta in enumerate(solucion_original.rutas):  
                # Reasignar ruta a un nuevo tiempo t sin cambiar su estructura
                solucion_actual = solucion_original.reasignar_ruta(ruta, tiempo)

                if cumple_restricciones(solucion_actual, 1) == 0:
                    # Calcular la nueva función objetivo
                    costo_inventario = sum(
                        contexto.proveedor.costo_almacenamiento * solucion_actual.inventario_proveedor[t] +
                        sum(i.costo_almacenamiento * solucion_actual.inventario_clientes[i.id][t] for i in contexto.clientes)
                        for t in range(contexto.horizonte_tiempo)
                    )

                    costo_ahorro = sum(
                        solucion_actual.calcular_ahorro_remocion(cliente, ruta_idx) * solucion_actual.calcular_ahorro_remocion(cliente, ruta_idx)
                        for cliente in contexto.clientes
                        for ruta_idx in range(len(solucion_actual.rutas))
                    )

                    costo_nuevo = costo_inventario - costo_ahorro

                    if costo_nuevo < costo_minimo:
                        mejor_solucion = solucion_actual.clonar()
                        costo_minimo = costo_nuevo

        return mejor_solucion

class Mip2:
    @staticmethod
    def ejecutar(solucion: Solucion) -> Solucion:
        contexto = solucion.contexto
        mejor_solucion = solucion.clonar()
        costo_minimo = solucion.costo

        for cliente in contexto.clientes:
            for tiempo in range(contexto.horizonte_tiempo):
                ruta_actual = solucion.rutas[tiempo]
                cliente_esta = ruta_actual.es_visitado(cliente)

                # Cálculo de costos y ahorros
                ahorro_remocion = solucion.calcular_ahorro_remocion(cliente, tiempo) if cliente_esta else 0
                costo_insercion = solucion.calcular_costo_insercion(cliente, tiempo) if not cliente_esta else float("inf")

                # Aplicar modificación de la solución
                if cliente_esta:
                    solucion_modificada = solucion.eliminar_visita(cliente, tiempo)
                else:
                    solucion_modificada = solucion.insertar_visita(cliente, tiempo)

                # Evaluación del costo con separación de ahorro e inserción
                costo_nuevo = solucion_modificada.costo - ahorro_remocion + costo_insercion

                if cumple_restricciones(solucion_modificada, 2) == 0:
                    if costo_nuevo < costo_minimo:
                        mejor_solucion = solucion_modificada.clonar()
                        costo_minimo = costo_nuevo

        return mejor_solucion



def cumple_restricciones(solucion, MIP, MIPcliente=None, MIPtiempo=None, operation=None):
    contexto = solucion.contexto
    B = solucion.inventario_proveedor
    I = [solucion.inventario_clientes[cliente.id] for cliente in contexto.clientes]
    r0 = [contexto.proveedor.nivel_produccion for _ in range(contexto.horizonte_tiempo + 1)]
    ri = [c.nivel_demanda for c in contexto.clientes]
    
    # Matriz de cantidad entregada x_it
    x = np.array([
        [solucion.rutas[t].obtener_cantidad_entregada(c) for t in range(contexto.horizonte_tiempo)]
        for c in contexto.clientes
    ])
    
    # Matriz binaria sigma_it: Indica si el cliente c es visitado en tiempo t
    sigma = np.array([
        [1 if solucion.rutas[t].es_visitado(c) else 0 for t in range(contexto.horizonte_tiempo)]
        for c in contexto.clientes
    ])
    
    # Matriz binaria zr_tr: Indica si la ruta r está asignada al tiempo t
    zr = np.array([
        [1 if solucion.rutas[t] == r else 0 for r in solucion.rutas]
        for t in range(contexto.horizonte_tiempo)
    ])
    
    # Variables de MIP2
    v = np.array([
        [1 if (operation == "INSERT" and MIPtiempo == t and MIPcliente == c) else 0
         for t in range(contexto.horizonte_tiempo)]
        for c in contexto.clientes
    ])
    
    w = np.array([
        [1 if (operation == "REMOVE" and MIPtiempo == t and MIPcliente == c) else 0
         for t in range(contexto.horizonte_tiempo)]
        for c in contexto.clientes
    ])

    # (2) Definición del nivel de inventario del proveedor
    if not all(B[t] == (B[t-1] + r0[t-1] - np.sum(x[:, t-1])) for t in range(1, contexto.horizonte_tiempo+1)):
        return 2

    # (3) El inventario del proveedor debe poder satisfacer la demanda
    if not all(B[t] >= np.sum(x[:, t]) for t in range(contexto.horizonte_tiempo)):
        return 3

    # (4) Definición del inventario de los clientes
    if not all(I[c][t] == (I[c][t-1] + x[c][t-1] - ri[c])
               for c in range(len(contexto.clientes))
               for t in range(1, contexto.horizonte_tiempo+1)):
        return 4

    if contexto.politica_reabastecimiento == "OU":
        # (5) La cantidad entregada no debe ser menor a la necesaria para llenar el inventario
        if not all(x[c][t] >= (contexto.clientes[c].nivel_maximo * sigma[c][t]) - I[c][t]
                   for c in range(len(contexto.clientes))
                   for t in range(contexto.horizonte_tiempo)):
            return 5

    # (6) La cantidad entregada no debe generar sobreabastecimiento en el cliente
    if not all(x[c][t] <= (contexto.clientes[c].nivel_maximo - I[c][t])
               for c in range(len(contexto.clientes))
               for t in range(contexto.horizonte_tiempo)):
        return 6

    # (7) Si el cliente es visitado, no se debe exceder su capacidad máxima
    if contexto.politica_reabastecimiento == "OU":
        if not all(x[c][t] <= (contexto.clientes[c].nivel_maximo * sigma[c][t])
                   for c in range(len(contexto.clientes))
                   for t in range(contexto.horizonte_tiempo)):
            return 7

    # (8) La capacidad total de entrega no debe superar la del vehículo
    if not all(np.sum(x[:, t]) <= contexto.capacidad_vehiculo for t in range(contexto.horizonte_tiempo)):
        return 8

    # 📌 Restricciones MIP1 (Reasignación de rutas)
    if MIP == 1:
        # (9) Una ruta solo puede asignarse a un único período de tiempo
        if not all(np.sum(zr[:, r]) <= 1 for r in range(len(solucion.rutas))):
            return 9

        # (10) Solo una ruta puede asignarse en cada período de tiempo
        if not all(np.sum(zr[t, :]) <= 1 for t in range(contexto.horizonte_tiempo)):
            return 10

        # (11) Un cliente puede ser atendido solo si su ruta está asignada
        if not all(x[c][t] <= contexto.clientes[c].nivel_maximo * np.sum(sigma[c, :] * zr[t, :])
                   for c in range(len(contexto.clientes))
                   for t in range(contexto.horizonte_tiempo)):
            return 11

        # (12) No se puede atender a un cliente si fue removido de la ruta asignada
        if not all(x[c][t] == 0 if w[c][t] else True
                   for c in range(len(contexto.clientes))
                   for t in range(contexto.horizonte_tiempo)):
            return 12

        # (13) Un cliente solo puede ser removido si su ruta está asignada
        if not all(w[c][t] <= np.sum(zr[t, :]) for c in range(len(contexto.clientes)) for t in range(contexto.horizonte_tiempo)):
            return 13

    # 📌 Restricciones MIP2 (Inserción y eliminación de clientes)
    if MIP == 2:
        # (21) No se puede insertar un cliente si ya estaba en la ruta
        if not all(v[c][t] <= 1 - sigma[c][t] for c in range(len(contexto.clientes)) for t in range(contexto.horizonte_tiempo)):
            return 21

        # (22) No se puede eliminar un cliente si no estaba en la ruta
        if not all(w[c][t] <= sigma[c][t] for c in range(len(contexto.clientes)) for t in range(contexto.horizonte_tiempo)):
            return 22

        # (23) Un cliente solo puede ser atendido si fue insertado o ya estaba en la ruta
        if not all(x[c][t] <= contexto.clientes[c].nivel_maximo * (sigma[c][t] - w[c][t] + v[c][t])
                   for c in range(len(contexto.clientes))
                   for t in range(contexto.horizonte_tiempo)):
            return 23

        # (24) `v_it` debe ser binario
        if not all(v[c][t] in [0, 1] for c in range(len(contexto.clientes)) for t in range(contexto.horizonte_tiempo)):
            return 24

        # (25) `w_it` debe ser binario
        if not all(w[c][t] in [0, 1] for c in range(len(contexto.clientes)) for t in range(contexto.horizonte_tiempo)):
            return 25

    return 0 