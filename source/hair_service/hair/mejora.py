import math
from modelos.solucion import Solucion
from modelos.ruta import Ruta
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
from ortools.linear_solver import pywraplp
from copy import deepcopy
def mejora(solucion: Solucion, iterador_principal: int) -> Solucion:
    """
    Aplica un procedimiento iterativo de mejoras basado en MIP1, MIP2 y Lin-Kernighan (LK).
    """
    print("LK abs4n5")
    print(solucion)
    mejor_solucion = LK(None, solucion)
    print(mejor_solucion)

    do_continue = True
    
    while do_continue:
        do_continue = False
        # PRIMERA MEJORA: Aplicación iterativa de MIP1 + LK
        solucion_prima = mip1_route_assignment(mejor_solucion)
        solucion_prima = LK(mejor_solucion, solucion_prima)
        if solucion_prima.es_admisible and solucion_prima.cumple_politica() and solucion_prima.costo < mejor_solucion.costo:
            print("MEJORA1")
            mejor_solucion = solucion_prima.clonar()
            do_continue = True
        
        # SEGUNDA MEJORA: Merge de rutas consecutivas en ambas direcciones + MIP2
        solucion_merge = mejor_solucion.clonar()
        # Crear lista de pares de rutas consecutivas
        L = [(i, i + 1) for i in range(len(solucion_merge.rutas) - 1)]
        # Iteración sobre pares de rutas
        for ruta1_idx, ruta2_idx in L:
            # Merge hacia adelante (ruta i con ruta i+1)
            s1 = solucion_merge.merge_rutas(ruta1_idx, ruta2_idx)
            mip2 = mip2_asignacion_clientes(s1)  # Aplicar MIP2
            
            if not mip2.es_admisible:
                if ruta2_idx < solucion.contexto.horizonte_tiempo - 1:
                    rutas_modificadas = [r for r in s1.rutas]
                    r_aux = rutas_modificadas[ruta2_idx].clonar()
                    rutas_modificadas[ruta2_idx] = rutas_modificadas[ruta2_idx + 1].clonar()
                    rutas_modificadas[ruta2_idx + 1] = r_aux.clonar()
                    s1 = Solucion(rutas=tuple(r for r in rutas_modificadas))
                    
            mip2 = mip2_asignacion_clientes(s1)  # Aplicar MIP2
            if mip2.es_admisible:
                mip2 = LK(s1, mip2)
                if mip2.costo < solucion_merge.costo:
                    solucion_merge = mip2.clonar()
       
            # Merge hacia atrás (ruta i+1 con ruta i)
            s2 = solucion_merge.merge_rutas(ruta2_idx, ruta1_idx)
            mip2 = mip2_asignacion_clientes(s2)  # Aplicar MIP2
            
            if not mip2.es_admisible:
                if ruta1_idx > 0:
                    rutas_modificadas = [r for r in s2.rutas]
                    r_aux = rutas_modificadas[ruta1_idx].clonar()
                    rutas_modificadas[ruta1_idx] = rutas_modificadas[ruta1_idx - 1].clonar()
                    rutas_modificadas[ruta1_idx - 1] = r_aux.clonar()
                    s2 = Solucion(rutas=tuple(r for r in rutas_modificadas))
                    
            mip2 = mip2_asignacion_clientes(s2)  # Aplicar MIP2
            if mip2.es_admisible:
                mip2 = LK(s2, mip2)
                if mip2.costo < solucion_merge.costo:
                    solucion_merge = mip2.clonar()
       
        # Aplicar el mejor resultado de los merges
        if solucion_merge.es_admisible and solucion_merge.cumple_politica() and solucion_merge.costo < mejor_solucion.costo:
            print("MEJORA2")
            mejor_solucion = solucion_merge.clonar()
            do_continue = True

        # TERCERA MEJORA: Aplicación de MIP2 + LK
        solucion_prima = mip2_asignacion_clientes(mejor_solucion)
        solucion_prima = LK(mejor_solucion, solucion_prima)
        if solucion_prima.es_admisible and solucion_prima.cumple_politica() and solucion_prima.costo < mejor_solucion.costo:
            print("MEJORA3")
            mejor_solucion = solucion_prima.clonar()
            do_continue = True
            
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
                [int(iter_sol.contexto.matriz_distancia[c1.id][c2.id]) for c1 in clientes]
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
    
    
def mip1_route_assignment(solucion: Solucion):
    contexto = solucion.contexto
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        raise Exception("No se pudo inicializar el solver.")

    sigma = {
        (i.id, r): (1 if (i in r.clientes) else 0)
        for i in contexto.clientes for r in solucion.rutas
    }

    matriz_ahorro = {
        (cliente.id, r): calcular_ahorro_eliminar_cliente(r, cliente)
        for cliente in contexto.clientes 
        for r in solucion.rutas
    }
    
    demanda = {cliente.id: cliente.nivel_demanda for cliente in contexto.clientes}
    C = contexto.capacidad_vehiculo
    U = {cliente.id: cliente.nivel_maximo for cliente in contexto.clientes}
    
    w, theta, z, x, I, B = {}, {}, {}, {}, {}, {}
    
    for r in solucion.rutas:
        for i in contexto.clientes:
            w[i.id, r] = solver.BoolVar(f"w_{i.id}_{r}")
    
    for t in range(contexto.horizonte_tiempo):
        for i in contexto.clientes:
            theta[i.id, t] = solver.BoolVar(f"theta_{i.id}_{t}")
            x[i.id, t] = solver.IntVar(0, i.nivel_maximo, f"x_{i.id}_{t}")
    
    for r in solucion.rutas:
        for t in range(contexto.horizonte_tiempo):
            z[r, t] = solver.BoolVar(f"z_{r}_{t}")
    
    for t in range(contexto.horizonte_tiempo + 1):
        for i in contexto.clientes:
            I[i.id, t] = solver.IntVar(0, i.nivel_maximo, f"I_{i.id}_{t}")
        B[t] = solver.IntVar(0, solver.infinity(), f"B_{t}")
    
    solver.Minimize(
        sum(contexto.proveedor.costo_almacenamiento * B[t] for t in range(contexto.horizonte_tiempo + 1))
        + sum(sum(i.costo_almacenamiento * I[i.id, t] for i in contexto.clientes) for t in range(contexto.horizonte_tiempo + 1))
        - sum(sum(matriz_ahorro[i.id, r] * w[i.id, r] for i in contexto.clientes) for r in solucion.rutas)
    )
    
    for t in range(1, contexto.horizonte_tiempo + 1):
        solver.Add(B[t] == B[t - 1] + contexto.proveedor.nivel_produccion - sum(x[i.id, t - 1] for i in contexto.clientes))
    
    for t in range(contexto.horizonte_tiempo):
        solver.Add(B[t] >= sum(x[i.id, t] for i in contexto.clientes))
    
    for i in contexto.clientes:
        solver.Add(I[i.id, t] == i.nivel_almacenamiento)
        for t in range(1, contexto.horizonte_tiempo + 1):
            solver.Add(I[i.id, t] == I[i.id, t - 1] + x[i.id, t - 1] - demanda[i.id])
            solver.Add(I[i.id, t] <= U[i.id])
    
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(x[i.id, t] <= U[i.id] * sum(sigma[i.id, r] * z[r, t] for r in solucion.rutas))
            solver.Add(x[i.id, t] >= 0)
    
    for t in range(contexto.horizonte_tiempo):
        solver.Add(sum(x[i.id, t] for i in contexto.clientes) <= C)
    
    for r in solucion.rutas:
        solver.Add(sum(z[r, t] for t in range(contexto.horizonte_tiempo)) <= 1)
    
    for t in range(contexto.horizonte_tiempo):
        solver.Add(sum(z[r, t] for r in solucion.rutas) <= 1)
    
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        nueva_solucion = reconstruir_solucion_MIP1(solucion, x, z)
        return nueva_solucion
    else:
        return solucion.clonar()


def mip2_asignacion_clientes(solucion: Solucion):
    """
    Implementación del MIP2 para la asignación de clientes utilizando OR-Tools.
    
    Args:
        solucion (Solucion): Solución actual del IRP.
    
    Returns:
        Solucion: Nueva solución optimizada.
    """
    contexto = solucion.contexto
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        return solucion

    # Indica si el cliente i es visitado en el tiempo t
    delta = {
        (i.id, t): 1 if any(i in ruta.clientes for ruta in solucion.rutas if ruta == solucion.rutas[t]) else 0
        for i in contexto.clientes for t in range(contexto.horizonte_tiempo)
    }

    # Calcular costos de ahorro
    matriz_ahorro = {
        (cliente.id, r): calcular_ahorro_eliminar_cliente(r, cliente)
        for cliente in contexto.clientes for r in solucion.rutas
    }
    
    # Calcular costos de insersción
    matriz_costo_insercion = {
        (cliente.id, r): calcular_costo_insertar_cliente(r, cliente)
        for cliente in contexto.clientes for r in solucion.rutas
    }

    # Variables de decisión
    x = {}      # Cantidad entregada a cliente i en tiempo t
    I = {}      # Inventario del cliente i en tiempo t
    B = {}      # Inventario del proveedor en tiempo t
    w = {}      # Binary: 1 si el cliente i es removido en tiempo t
    v = {}      # Binary: 1 si el cliente i es insertado en tiempo t
    theta = {}  # Binary: 1 si el cliente i es visitado en tiempo t (para OU)

    # Initialize variables
    for t in range(contexto.horizonte_tiempo):
        for i in contexto.clientes:
            w[i.id, t] = solver.BoolVar(f"w_{i.id}_{t}")
            v[i.id, t] = solver.BoolVar(f"v_{i.id}_{t}")
            x[i.id, t] = solver.IntVar(0, i.nivel_maximo, f"x_{i.id}_{t}")

    for t in range(contexto.horizonte_tiempo + 1):
        for i in contexto.clientes:
            I[i.id, t] = solver.IntVar(-solver.infinity(), i.nivel_maximo, f"I_{i.id}_{t}")
            theta[i.id, t] = solver.BoolVar(f"theta_{i.id}_{t}")
        B[t] = solver.IntVar(-solver.infinity(), solver.infinity(), f"B_{t}")

    # (2) El inventario del proveedor en cada periodo se calcula como el inventario del periodo anterior,
    # más la producción del proveedor, menos la cantidad entregada a los clientes en el tiempo anterior.
    solver.Add(B[0] == contexto.proveedor.nivel_almacenamiento) 
    for t in range(1, contexto.horizonte_tiempo + 1):
        solver.Add(B[t] == B[t - 1] + contexto.proveedor.nivel_produccion - sum(x[i.id, t - 1] for i in contexto.clientes))
    
    # (3) **Balance de inventario del proveedor**
    for t in range(contexto.horizonte_tiempo):
        solver.Add(B[t] >= sum(x[i.id, t] for i in contexto.clientes))

    # (4) **Balance de inventario del cliente**
    for i in contexto.clientes:
        solver.Add(I[i.id, 0] == i.nivel_almacenamiento)
        for t in range(1, contexto.horizonte_tiempo + 1):
            solver.Add(I[i.id, t] == I[i.id, t - 1] + x[i.id, t - 1] - i.nivel_demanda)
        
    if contexto.politica_reabastecimiento == "OU":
        for i in contexto.clientes:
            for t in range(contexto.horizonte_tiempo):
                ## (5) **Inventario debe estar entre 0 y el máximo del cliente**
                solver.Add(x[i.id, t] >= i.nivel_maximo * theta[i.id, t] - I[i.id, t + 1])
                ## (6) **Un cliente solo puede recibir entrega si su inventario lo permite**
                solver.Add(x[i.id, t] <= i.nivel_maximo - I[i.id, t + 1])
                ## (7) **Restricciones de la política OU**
                solver.Add(x[i.id, t] <= i.nivel_maximo * theta[i.id, t])

    ## (8) **Restricción de capacidad del vehículo**
    for t in range(contexto.horizonte_tiempo):
        solver.Add(sum(x[i.id, t] for i in contexto.clientes) <= contexto.capacidad_vehiculo)
        
    ## (14) Restricción de no negatividad en la cantidad entregada a un cliente en todo momento
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(x[i.id, t] >= 0)

    ## (15) Restricción de no negatividad en el inventario de los clientes
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo + 1):
            solver.Add(I[i.id, t] >= 0)

    ## (16) Restricción de no negatividad en el inventario del proveedor
    for t in range(contexto.horizonte_tiempo + 1):
        solver.Add(B[t] >= 0)
                
    # (21) El cliente no puede insertarse si ya está en la ruta
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(v[i.id, t] <= 1 - delta[i.id, t])

    # (22) El cliente no puede removerse si no está en la ruta
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(w[i.id, t] <= delta[i.id, t])

    # (23) Cindicion de servicio de cliente
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(x[i.id, t] <= i.nivel_maximo * (delta[i.id, t] - w[i.id, t] + v[i.id, t]))

    # Objective function (20)
    objective = (
        contexto.proveedor.costo_almacenamiento * sum(B[t] for t in range(contexto.horizonte_tiempo + 1)) 
        + sum(sum(i.costo_almacenamiento * I[i.id, t] for i in contexto.clientes) 
            for t in range(contexto.horizonte_tiempo + 1)) 
        - sum(sum(matriz_ahorro[i.id, r] * w[i.id, t] for i in contexto.clientes)
            for t, r in enumerate(solucion.rutas))
        + sum(sum(matriz_costo_insercion[i.id, r] * v[i.id, t] for i in contexto.clientes)
             for t, r in enumerate(solucion.rutas))
    )
    
    solver.Minimize(objective)

    # Solve the model
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        nueva_solucion =  reconstruir_solucion_MIP2(solucion, x)
        return nueva_solucion
    # else:
        # print("NO RESUELVE2")
    return solucion.clonar()

def reconstruir_solucion_MIP1(solucion, x, z):
    """
    Reconstruye la solución a partir de las variables de decisión x (cantidad entregada) 
    y z (asignación de rutas a periodos de tiempo), asegurando que los clientes sean visitados 
    solo si pertenecen a una ruta activa.
    
    Args:
        solucion (Solucion): Solución inicial antes de la optimización.
        x (dict): Cantidad entregada a cada cliente en cada tiempo t.
        z (dict): Indicador binario de si una ruta r es asignada al tiempo t.

    Returns:
        Solucion: Nueva solución optimizada y reconstruida.
    """
    nueva_solucion = Solucion(tuple(Ruta((), ()) for _ in range(solucion.contexto.horizonte_tiempo)))

    for t in range(solucion.contexto.horizonte_tiempo):
        rutas_modificadas = list(nueva_solucion.rutas)  # Copia de rutas
        rutas_activas = [r for r in solucion.rutas if z[r, t].solution_value() > 0.5]
        for r in rutas_activas:
            clientes_en_ruta = [cliente for cliente in solucion.contexto.clientes if x[cliente.id, solucion.rutas.index(r)].solution_value() > 0]
            for cliente in clientes_en_ruta:
                cantidad_entregada = x[cliente.id, solucion.rutas.index(r)].solution_value()
                if cantidad_entregada > 0:
                    rutas_modificadas[t] = rutas_modificadas[t].insertar_visita(cliente, round(cantidad_entregada))
        nueva_solucion = Solucion(rutas=tuple(rutas_modificadas))

    return nueva_solucion if nueva_solucion.es_admisible else nueva_solucion


def reconstruir_solucion_MIP2(solucion, x):
    nueva_solucion = solucion.clonar()

    # Actualizar la cantidad entregada a los clientes
    for t in range(solucion.contexto.horizonte_tiempo):
        for cliente in solucion.contexto.clientes:
            cantidad_entregada = x[cliente.id, t].solution_value()
            if cantidad_entregada > 0:
                # Agregar entrega al cliente en la nueva solución
                nueva_solucion = nueva_solucion.insertar_visita(cliente, t, int(cantidad_entregada))

    # Reconstruir rutas si hubo inserciones o remociones de clientes
    for t, ruta in enumerate(solucion.rutas):
        nueva_ruta = []
        for cliente in ruta.clientes:
            if (cliente.id, t) not in x or x[cliente.id, t].solution_value() == 0:
                continue  # Si la entrega es 0, remover el cliente de la ruta
            nueva_ruta.append(cliente)
        
        # Agregar nuevos clientes si se insertaron
        for cliente in solucion.contexto.clientes:
            if x[cliente.id, t].solution_value() > 0 and cliente not in nueva_ruta:
                nueva_ruta.append(cliente)
        
        nueva_solucion.rutas[t].clientes = nueva_ruta

    return nueva_solucion if nueva_solucion.es_admisible else solucion

def calcular_ahorro_eliminar_cliente(ruta, cliente):
    """
    Calcula el ahorro de eliminar un cliente de una ruta.
    Se obtiene un ahorro si se pueden unir su predecesor y sucesor sin incrementar la distancia total.
    """
    if cliente not in ruta.clientes:
        return 0  # No hay ahorro si el cliente no está en la ruta
    
    ruta2 = ruta.clonar()
    ruta2 = ruta2.eliminar_visita(cliente)

    return ruta.costo - ruta2.costo

def calcular_costo_insertar_cliente(ruta, cliente):
    """
    Calcula el costo de insertar un cliente en una ruta.
    """
    if cliente in ruta.clientes:
        return 0  # No hay ahorro si el cliente no está en la ruta
    
    ruta2 = ruta.clonar()
    ruta2 = ruta2.insertar_visita(cliente, 10)

    return ruta.costo - ruta2.costo

