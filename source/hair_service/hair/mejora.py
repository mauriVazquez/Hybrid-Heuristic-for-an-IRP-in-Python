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
        """
        Implementa MIP1 para reasignar rutas a distintos periodos sin cambiar su estructura.
        Adapta la solución dependiendo de si la política es OU o ML.
        """
        mejor_solucion = solucion_original.clonar()
        costo_minimo = solucion_original.costo
        contexto = solucion_original.contexto

        for tiempo in range(contexto.horizonte_tiempo):
            for ruta_idx, ruta in enumerate(solucion_original.rutas):  
                solucion_actual = solucion_original.reasignar_ruta(ruta, tiempo)

                if cumple_restricciones(solucion_actual, 1) == 0:
                    # Cálculo de costos de inventario y transporte
                    costo_inventario = sum(
                        contexto.proveedor.costo_almacenamiento * solucion_actual.inventario_proveedor[t] +
                        sum(cliente.costo_almacenamiento * solucion_actual.inventario_clientes[cliente.id][t] for cliente in contexto.clientes)
                        for t in range(contexto.horizonte_tiempo)
                    )

                    costo_transporte = sum(ruta.costo for ruta in solucion_actual.rutas)

                    # Ahorro en transporte por eliminación de clientes
                    ahorro_remocion = sum(
                        solucion_actual.calcular_ahorro_remocion(cliente, tiempo)
                        for cliente in contexto.clientes
                    )

                    # **Aplicación de la política OU en MIP1**
                    if contexto.politica_reabastecimiento == "OU":
                        for cliente in ruta.clientes:
                            xjt = solucion_actual.rutas[tiempo].obtener_cantidad_entregada(cliente)
                            tiempos_cliente = solucion_actual.tiempos_cliente(cliente)
                            t_next = next((t_s for t_s in tiempos_cliente if t_s > tiempo), None)

                            if t_next is not None:
                                cantidad_en_siguiente = solucion_actual.rutas[t_next].obtener_cantidad_entregada(cliente)
                                cantidad_transferible = min(xjt, cliente.nivel_maximo - cantidad_en_siguiente)

                                if cantidad_transferible > 0:
                                    solucion_actual = solucion_actual.eliminar_visita(cliente, tiempo)
                                    solucion_actual = solucion_actual.insertar_visita(cliente, t_next, cantidad_en_siguiente + cantidad_transferible)

                                if cantidad_transferible < xjt:
                                    solucion_actual = solucion_actual.insertar_visita(cliente, tiempo, xjt - cantidad_transferible)

                    # **Aplicación de la política ML en MIP1**
                    if contexto.politica_reabastecimiento == "ML":
                        for cliente in ruta.clientes:
                            xjt = solucion_actual.rutas[tiempo].obtener_cantidad_entregada(cliente)
                            y_min = min(xjt, min(solucion_actual.inventario_clientes[cliente.id][tiempo+1:], default=xjt))

                            if solucion_actual.inventario_clientes[cliente.id][tiempo] - y_min >= cliente.nivel_minimo:
                                solucion_actual = solucion_actual.quitar_cantidad_cliente(cliente, tiempo, y_min)

                    costo_nuevo = costo_inventario + costo_transporte - ahorro_remocion

                    if costo_nuevo < costo_minimo:
                        mejor_solucion = solucion_actual.clonar()
                        costo_minimo = costo_nuevo

        return mejor_solucion

class Mip2:
    @staticmethod
    def ejecutar(solucion: Solucion) -> Solucion:
        """
        Implementa MIP2 para modificar la asignación de clientes en rutas sin cambiar la asignación de rutas a periodos.
        Adapta la solución dependiendo de si la política es OU o ML.
        """
        contexto = solucion.contexto
        mejor_solucion = solucion.clonar()
        costo_minimo = solucion.costo

        for cliente in contexto.clientes:
            for tiempo in range(contexto.horizonte_tiempo):
                ruta_actual = solucion.rutas[tiempo]
                cliente_esta = ruta_actual.es_visitado(cliente)

                ahorro_remocion = solucion.calcular_ahorro_remocion(cliente, tiempo) if cliente_esta else 0
                costo_insercion = solucion.calcular_costo_insercion(cliente, tiempo) if not cliente_esta else 0

                if cliente_esta:
                    solucion_modificada = solucion.eliminar_visita(cliente, tiempo)
                else:
                    solucion_modificada = solucion.insertar_visita(cliente, tiempo)

                costo_inventario = sum(
                    contexto.proveedor.costo_almacenamiento * solucion_modificada.inventario_proveedor[t] +
                    sum(cliente.costo_almacenamiento * solucion_modificada.inventario_clientes[cliente.id][t] for cliente in contexto.clientes)
                    for t in range(contexto.horizonte_tiempo)
                )

                costo_transporte = sum(ruta.costo for ruta in solucion_modificada.rutas)

                # **Aplicación de la política OU en MIP2**
                if contexto.politica_reabastecimiento == "OU":
                    if cliente_esta and ahorro_remocion > 0:
                        solucion_modificada = solucion_modificada.eliminar_visita(cliente, tiempo)

                # **Aplicación de la política ML en MIP2**
                if contexto.politica_reabastecimiento == "ML":
                    for tiempo_mod in range(contexto.horizonte_tiempo):  # Iteramos sobre cada período de tiempo
                        ruta_modificada = solucion_modificada.rutas[tiempo_mod]  # Obtener la ruta en el tiempo `tiempo_mod`

                        for cliente_mod in ruta_modificada.clientes:
                            xjt = ruta_modificada.obtener_cantidad_entregada(cliente_mod)
                            y_min = min(xjt, min(solucion_modificada.inventario_clientes[cliente_mod.id][tiempo_mod+1:], default=xjt))

                            if solucion_modificada.inventario_clientes[cliente_mod.id][tiempo_mod] - y_min >= cliente_mod.nivel_minimo:
                                solucion_modificada = solucion_modificada.quitar_cantidad_cliente(cliente_mod, tiempo_mod, y_min)

                        if cliente_mod.costo_almacenamiento < contexto.proveedor.costo_almacenamiento:
                            y_max = cliente_mod.nivel_maximo - max(solucion_modificada.inventario_clientes[cliente_mod.id][t] for t in range(tiempo_mod, contexto.horizonte_tiempo))
                            if y_max > 0:
                                solucion_modificada = solucion_modificada.insertar_visita(cliente_mod, tiempo_mod, y_max)

                costo_nuevo = costo_inventario + costo_transporte - ahorro_remocion + costo_insercion

                if cumple_restricciones(solucion_modificada, 2) == 0:
                    if costo_nuevo < costo_minimo:
                        mejor_solucion = solucion_modificada.clonar()
                        costo_minimo = costo_nuevo

        return mejor_solucion


def cumple_restricciones(solucion, MIP, MIPcliente=None, MIPtiempo=None, operation=None):
    contexto = solucion.contexto
    B = solucion.inventario_proveedor
    I = [solucion.inventario_clientes.get(cliente.id, None) for cliente in contexto.clientes]
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
    
    for t in range(1, contexto.horizonte_tiempo + 1):
        if B[t] < 0 or B[t] != (B[t-1] + r0[t-1] - np.sum(x[:, t-1])):
            return 3  # Inventario insuficiente en el proveedor
    
    for c in range(len(contexto.clientes)):
        for t in range(1, contexto.horizonte_tiempo + 1):
            if I[c][t] < 0 or I[c][t] != (I[c][t - 1] + x[c][t - 1] - ri[c]):
                return 4  # Inventario del cliente no balanceado
    
    if contexto.politica_reabastecimiento == "OU":
        for c in range(len(contexto.clientes)):
            for t in range(contexto.horizonte_tiempo):
                if x[c][t] < (contexto.clientes[c].nivel_maximo * sigma[c][t]) - I[c][t]:
                    return 5  # No se entrega suficiente en OU
                if x[c][t] > (contexto.clientes[c].nivel_maximo - I[c][t]):
                    return 6  # Exceso de inventario en OU
    
    if contexto.politica_reabastecimiento == "ML":
        for c in range(len(contexto.clientes)):
            for t in range(contexto.horizonte_tiempo):
                if x[c][t] > (contexto.clientes[c].nivel_maximo - I[c][t]):
                    return 7  # No se puede exceder el máximo permitido en ML
                if I[c][t] < contexto.clientes[c].nivel_minimo:
                    return 8  # Stock mínimo no respetado en ML
    
    if MIP == 1:
        for r in range(len(solucion.rutas)):
            if np.sum(zr[:, r]) > 1:
                return 9  # Una ruta asignada a más de un tiempo
        for t in range(contexto.horizonte_tiempo):
            if np.sum(zr[t, :]) > 1:
                return 10  # Más de una ruta asignada en un tiempo
    
    if MIP == 2:
        for c in range(len(contexto.clientes)):
            for t in range(contexto.horizonte_tiempo):
                if operation == "INSERT" and c == MIPcliente and t == MIPtiempo and sigma[c][t] == 1:
                    return 21  # No se puede insertar si ya estaba en la ruta
                if operation == "REMOVE" and c == MIPcliente and t == MIPtiempo:
                    if sigma[c][t] == 0:
                        return 22  # No se puede eliminar si no estaba en la ruta
                    if not any(x[c][t_futuro] > 0 for t_futuro in range(t + 1, contexto.horizonte_tiempo)) and I[c][t] < contexto.clientes[c].nivel_minimo:
                        return 23  # No se puede eliminar sin alternativa de entrega ni stock suficiente
    
    for t in range(contexto.horizonte_tiempo):
        if np.sum(x[:, t]) > contexto.capacidad_vehiculo:
            return 24  # Exceso de capacidad del vehículo
    
    return 0  # Todo cumple las restricciones
