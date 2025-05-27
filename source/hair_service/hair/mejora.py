from modelos.solucion import Solucion
from modelos.ruta import Ruta
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
from ortools.linear_solver import pywraplp
def mejora(solucion: Solucion, iterador_principal: int) -> Solucion:
    """
    Aplica un procedimiento iterativo de mejoras basado en MIP1, MIP2 y Lin-Kernighan (LK).
    """
    continuar = True
    mejor_solucion = LK(None, solucion)
    
    while continuar:
        continuar = False
        
        # PRIMERA MEJORA: Aplicación iterativa de MIP1 + LK
        status, mip1 = mip1_route_assignment(mejor_solucion)
        if status == pywraplp.Solver.OPTIMAL:
            solucion_prima = mip1.clonar()
            solucion_prima = LK(mejor_solucion, solucion_prima)
            if solucion_prima.costo() < mejor_solucion.costo():
                mejor_solucion = solucion_prima.clonar()
                continuar = True
        
        # SEGUNDA MEJORA: Merge de rutas consecutivas en ambas direcciones + MIP2
        solucion_merge = mejor_solucion.clonar()
        # Crear lista de pares de rutas consecutivas
        L = [(i, i + 1) for i in range(len(solucion_merge.rutas) - 1)]
        
        # Iteración sobre pares de rutas
        for ruta1_idx, ruta2_idx in L:
            # Merge hacia adelante (ruta i con ruta i+1)
            s1 = mejor_solucion.merge_rutas(ruta1_idx, ruta2_idx)
            status, mip2 = mip2_asignacion_clientes(s1)  # Aplicar MIP2
            
            if (status == pywraplp.Solver.INFEASIBLE) and (ruta2_idx < solucion.contexto.horizonte_tiempo - 1):
                rutas_modificadas = [r for r in s1.rutas]
                r_aux = rutas_modificadas[ruta2_idx].clonar()
                rutas_modificadas[ruta2_idx] = rutas_modificadas[ruta2_idx + 1].clonar()
                rutas_modificadas[ruta2_idx + 1] = r_aux.clonar()
                s1 = Solucion(rutas=tuple(r for r in rutas_modificadas))
                    
            status, mip2 = mip2_asignacion_clientes(s1)  # Aplicar MIP2
            if status == pywraplp.Solver.FEASIBLE:
                solucion_prima = LK(s1, mip2)
                if solucion_prima.costo() < solucion_merge.costo():
                    solucion_merge = solucion_prima.clonar()
       
            # Merge hacia atrás (ruta i+1 con ruta i)
            s2 = mejor_solucion.merge_rutas(ruta2_idx, ruta1_idx)
            status, mip2 = mip2_asignacion_clientes(s2)  # Aplicar MIP2   
            if (status == pywraplp.Solver.INFEASIBLE) and (ruta1_idx > 0):
                rutas_modificadas = [r for r in s2.rutas]
                r_aux = rutas_modificadas[ruta1_idx].clonar()
                rutas_modificadas[ruta1_idx] = rutas_modificadas[ruta1_idx - 1].clonar()
                rutas_modificadas[ruta1_idx - 1] = r_aux.clonar()
                s2 = Solucion(rutas=tuple(r for r in rutas_modificadas))
                    
            status, mip2 = mip2_asignacion_clientes(s2)  # Aplicar MIP2
            if status == pywraplp.Solver.FEASIBLE:
                solucion_prima = LK(s2, mip2)
                if solucion_prima.costo() < solucion_merge.costo():
                    solucion_merge = solucion_prima.clonar()
       
        # Aplicar el mejor resultado de los merges
        if solucion_merge.costo() < mejor_solucion.costo():
            mejor_solucion = solucion_merge.clonar()
            continuar = True

        # TERCERA MEJORA: Aplicación de MIP2 + LK
        status, solucion_prima = mip2_asignacion_clientes(mejor_solucion)
        if status == pywraplp.Solver.OPTIMAL:
            solucion_prima = LK(mejor_solucion, solucion_prima)
            if solucion_prima.costo() < mejor_solucion.costo():
                mejor_solucion = solucion_prima.clonar()
                continuar = True
            
    # print(f"MEJORA {mejor_solucion}")
    return mejor_solucion

def LK(solucion: Solucion, solucion_prima : Solucion) -> Solucion:
    """
    Aplica Lin-Kernighan heurístico para mejorar la solución.
    """
    if ((solucion is not None) and solucion.es_igual(solucion_prima)):
        return solucion_prima
        
    iter_sol = solucion_prima
    for r, ruta in enumerate(iter_sol.rutas):
        if len(ruta.clientes) > 1:
            clientes = ruta.clientes
            # Crear matriz de distancias original
            matriz_distancia = [
                [iter_sol.contexto.matriz_distancia[c1.id][c2.id] for c1 in clientes]
                for c2 in clientes
            ]
            fila_proveedor = [c.distancia_proveedor for c in clientes]
            fila_proveedor.insert(0, 0)  # Distancia del proveedor a sí mismo
            for i, c in enumerate(clientes):
                matriz_distancia[i].insert(0, c.distancia_proveedor)

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
        return solucion
    
    
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
    
    U = {cliente.id: cliente.nivel_maximo for cliente in contexto.clientes}
    
    # Definición de variables
    w, theta, z, x, I, B = {}, {}, {}, {}, {}, {}
    for r in solucion.rutas:
        for i in contexto.clientes:
            w[i.id, r] = solver.BoolVar(f"w_{i.id}_{r}")
    
    for t in range(contexto.horizonte_tiempo):
        for i in contexto.clientes:
            theta[i.id, t] = solver.BoolVar(f"theta_{i.id}_{t}")
            x[i.id, t] = solver.IntVar(-solver.infinity(), U[i.id], f"x_{i.id}_{t}")
    
    for r in solucion.rutas:
        for t in range(contexto.horizonte_tiempo):
            z[r, t] = solver.BoolVar(f"z_{r}_{t}")
    
    for t in range(contexto.horizonte_tiempo + 1):
        for i in contexto.clientes:
            I[i.id, t] = solver.IntVar(-solver.infinity(), U[i.id], f"I_{i.id}_{t}")
        B[t] = solver.IntVar(-solver.infinity(), solver.infinity(), f"B_{t}")
    
    # Fijar valores iniciales conocidos
    B_inicial = contexto.proveedor.nivel_almacenamiento 
    solver.Add(B[0] == B_inicial)
    for i in contexto.clientes:
        I_inicial = i.nivel_almacenamiento 
        solver.Add(I[i.id, 0] == I_inicial)

    # (2) El inventario del proveedor en cada periodo se calcula como el inventario del periodo anterior,
    # más la producción del proveedor, menos la cantidad entregada a los clientes en el tiempo anterior.
    for t in range(1, contexto.horizonte_tiempo + 1):
        solver.Add(B[t] == B[t - 1] + contexto.proveedor.nivel_produccion - sum(x[i.id, t - 1] for i in contexto.clientes))

    # (3) **Balance de inventario del proveedor**
    for t in range(contexto.horizonte_tiempo):
        solver.Add(B[t] >= sum(x[i.id, t] for i in contexto.clientes))

    # (4) **Balance de inventario del cliente**
    for i in contexto.clientes:
        for t in range(1, contexto.horizonte_tiempo + 1):
            solver.Add(I[i.id, t] == I[i.id, t - 1] + x[i.id, t - 1] - i.nivel_demanda)
        
    if contexto.politica_reabastecimiento == "OU":
        for i in contexto.clientes:
            for t in range(contexto.horizonte_tiempo):
                ## (5) **Inventario debe estar entre 0 y el máximo del cliente**
                solver.Add(x[i.id, t] >= U[i.id] * theta[i.id, t] - I[i.id, t])
                ## (7) **Restricciones de la política OU**
                solver.Add(x[i.id, t] <= U[i.id] * theta[i.id, t])
    
    ## (6) **Un cliente solo puede recibir entrega si su inventario lo permite**
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(x[i.id, t] <= U[i.id] - I[i.id, t])
        
    ## (8) **Restricción de capacidad del vehículo**
    for t in range(contexto.horizonte_tiempo):
        solver.Add(sum(x[i.id, t] for i in contexto.clientes) <= contexto.capacidad_vehiculo)
        
    ## (9) **Cada ruta r solo puede ser asignada a un periodo t**
    for r in solucion.rutas:
        solver.Add(sum(z[r, t] for t in range(contexto.horizonte_tiempo)) <= 1)

    ## (10) **Máximo de una ruta en cada periodo**
    for t in range(contexto.horizonte_tiempo):
        solver.Add(sum(z[r, t] for r in solucion.rutas) <= 1)

    ## (11) **Un cliente solo puede ser servido si está en la ruta asignada al tiempo t**
    for i in contexto.clientes:
        for t, r in enumerate(solucion.rutas):
            solver.Add(x[i.id, t] <= U[i.id] * sum(sigma[i.id, r] * z[r, t] for r in solucion.rutas))

    ## (12) **Si un cliente es removido, no puede ser servido en t**
    for i in contexto.clientes:
        for t, r in enumerate(solucion.rutas):
            solver.Add(x[i.id, t] <= U[i.id] * (2 - (sigma[i.id, r] * (z[r, t] + w[i.id, r]))))

    ## (13) **Un cliente solo puede ser removido si estaba en la ruta original**
    for i in contexto.clientes:
        for r in solucion.rutas:
            solver.Add(w[i.id, r] <= sigma[i.id, r] * sum(z[r, t] for t in range(contexto.horizonte_tiempo)))

    ## (14) Restricción de no negatividad en la cantidad entregada x_{it}
    # La cantidad de productos entregados a un cliente en un período no puede ser negativa.
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(x[i.id, t] >= 0)

    ## (15) Restricción de no negatividad en el inventario I_{it}
    # El inventario de un cliente en un período no puede ser negativo.
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo + 1):
            solver.Add(I[i.id, t] >= 0)

    ## (16) Restricción de no negatividad en el inventario del proveedor B_t
    # El inventario del proveedor en un período no puede ser negativo.
    for t in range(contexto.horizonte_tiempo + 1):
        solver.Add(B[t] >= 0)

    solver.Minimize(
        sum(contexto.proveedor.costo_almacenamiento * B[t] for t in range(contexto.horizonte_tiempo + 1))
        + sum(sum(i.costo_almacenamiento * I[i.id, t] for i in contexto.clientes) for t in range(contexto.horizonte_tiempo + 1))
        - sum(sum(matriz_ahorro[i.id, r] * w[i.id, r] for i in contexto.clientes) for r in solucion.rutas)
    )
    
    status = solver.Solve()
    if (status == pywraplp.Solver.OPTIMAL) or (status == pywraplp.Solver.FEASIBLE):
        nueva_solucion = reconstruir_solucion_MIP1(solucion, w, x, z)
        if nueva_solucion.es_admisible:
            return status, nueva_solucion

    return status, solucion


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
    sigma = {
        (i.id, t): (1 if (i in r.clientes) else 0)
        for i in contexto.clientes for t, r in enumerate(solucion.rutas)
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

    U = {cliente.id: cliente.nivel_maximo for cliente in contexto.clientes}
    
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
            x[i.id, t] = solver.IntVar(-solver.infinity(), U[i.id], f"x_{i.id}_{t}")

    for t in range(contexto.horizonte_tiempo + 1):
        for i in contexto.clientes:
            I[i.id, t] = solver.IntVar(-solver.infinity(), U[i.id], f"I_{i.id}_{t}")
            theta[i.id, t] = solver.BoolVar(f"theta_{i.id}_{t}")
        B[t] = solver.IntVar(-solver.infinity(), solver.infinity(), f"B_{t}")

    # Fijar valores iniciales conocidos
    B_inicial = contexto.proveedor.nivel_almacenamiento
    solver.Add(B[0] == B_inicial)
    for i in contexto.clientes:
        I_inicial = i.nivel_almacenamiento
        solver.Add(I[i.id, 0] == I_inicial)

    # (2) El inventario del proveedor en cada periodo se calcula como el inventario del periodo anterior,
    # más la producción del proveedor, menos la cantidad entregada a los clientes en el tiempo anterior.
    for t in range(1, contexto.horizonte_tiempo + 1):
        solver.Add(B[t] == B[t - 1] + contexto.proveedor.nivel_produccion - sum(x[i.id, t - 1] for i in contexto.clientes))

    # (3) **Balance de inventario del proveedor**
    for t in range(contexto.horizonte_tiempo):
        solver.Add(B[t] >= sum(x[i.id, t] for i in contexto.clientes))

    # (4) **Balance de inventario del cliente**
    for i in contexto.clientes:
        for t in range(1, contexto.horizonte_tiempo + 1):
            solver.Add(I[i.id, t] == I[i.id, t - 1] + x[i.id, t - 1] - i.nivel_demanda)
        
    if contexto.politica_reabastecimiento == "OU":
        for i in contexto.clientes:
            for t in range(contexto.horizonte_tiempo):
                ## (5) **Inventario debe estar entre 0 y el máximo del cliente**
                solver.Add(x[i.id, t] >= U[i.id] * theta[i.id, t] - I[i.id, t])
                ## (7) **Restricciones de la política OU**
                solver.Add(x[i.id, t] <= U[i.id] * theta[i.id, t])
    
    ## (6) **Un cliente solo puede recibir entrega si su inventario lo permite**
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(x[i.id, t] <= U[i.id] - I[i.id, t])
        
    ## (8) **Restricción de capacidad del vehículo**
    for t in range(contexto.horizonte_tiempo):
        solver.Add(sum(x[i.id, t] for i in contexto.clientes) <= contexto.capacidad_vehiculo)
        
    ## (14) Restricción de no negatividad en la cantidad entregada x_{it}
    # La cantidad de productos entregados a un cliente en un período no puede ser negativa.
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(x[i.id, t] >= 0)

    ## (15) Restricción de no negatividad en el inventario I_{it}
    # El inventario de un cliente en un período no puede ser negativo.
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo + 1):
            solver.Add(I[i.id, t] >= 0)

    ## (16) Restricción de no negatividad en el inventario del proveedor B_t
    # El inventario del proveedor en un período no puede ser negativo.
    for t in range(contexto.horizonte_tiempo + 1):
        solver.Add(B[t] >= 0)
            
    # (21) El cliente no puede insertarse si ya está en la ruta
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(v[i.id, t] <= 1 - sigma[i.id, t])

    # (22) El cliente no puede removerse si no está en la ruta
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(w[i.id, t] <= sigma[i.id, t])

    # (23) Cindicion de servicio de cliente
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(x[i.id, t] <=U[i.id] * (sigma[i.id, t] - w[i.id, t] + v[i.id, t]))

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
    if (status == pywraplp.Solver.OPTIMAL) or (status == pywraplp.Solver.FEASIBLE):                
        nueva_solucion =  reconstruir_solucion_MIP2(solucion, v, w, x)
        if nueva_solucion.es_admisible:
            return status, nueva_solucion
    return status, solucion

def reconstruir_solucion_MIP1(solucion: Solucion, w, x, z):
    contexto = solucion.contexto
    rutas_modificadas = [Ruta((), ()) for _ in range(contexto.horizonte_tiempo)]  # Inicializa rutas vacías
    
    # Asignar las rutas utilizadas en cada tiempo t
    for r in solucion.rutas:
        for t in range(contexto.horizonte_tiempo):
            if z[r, t].solution_value():  # Si la ruta fue utilizada en t
                rutas_modificadas[t] = r

    nueva_solucion = Solucion(rutas=tuple(rutas_modificadas))

    # Asignar entregas de clientes en cada tiempo t
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            i_id = int(i.id) if isinstance(i.id, (list, tuple)) else i.id
            t_val = int(t) if isinstance(t, (list, tuple)) else t

            # Obtener cantidad entregada en la solución óptima
            cantidad_entregada_var = x.get((i_id, t_val), None)
            cantidad_entregada = int(cantidad_entregada_var.solution_value()) if cantidad_entregada_var is not None else 0

            # Si el cliente recibió algo, actualizar la ruta en t
            if cantidad_entregada > 0:
                nueva_solucion = nueva_solucion.establecer_cantidad_cliente(i, t_val, cantidad_entregada)

    # Identificar clientes removidos
    for i in contexto.clientes:
        for r in solucion.rutas:
            if (i.id, r) in w and w[i.id, r].solution_value():
                nueva_solucion = nueva_solucion.eliminar_visita(i, t)

    return nueva_solucion

def reconstruir_solucion_MIP2(solucion_original: Solucion, v, w, x) -> Solucion:
    """
    Reconstruye una nueva solución basada en los resultados del MIP2.
    """
    contexto = solucion_original.contexto
    horizonte = contexto.horizonte_tiempo
    
    nuevas_rutas = []

    for t in range(horizonte):
        clientes = []
        cantidades = []

        # Copiar clientes que no fueron removidos
        for cliente in solucion_original.rutas[t].clientes:
            if not w[cliente.id, t].solution_value():
                clientes.append(cliente)
                cantidades.append(int(x[cliente.id, t].solution_value()))

        # Agregar clientes insertados (respetando capacidad)
        capacidad_disponible = contexto.capacidad_vehiculo - sum(cantidades)
        for cliente in contexto.clientes:
            cantidad_entregada = int(x[cliente.id, t].solution_value())
            if (cliente not in clientes and v[cliente.id, t].solution_value()) and (0 < cantidad_entregada <= capacidad_disponible):
                clientes.append(cliente)
                cantidades.append(cantidad_entregada)
                capacidad_disponible -= cantidad_entregada  # Reducir capacidad disponible

        # Agregar la ruta solo si hay clientes
        nuevas_rutas.append(Ruta(tuple(clientes), tuple(cantidades)))

    # Asegurar que hay una ruta para cada período (rellenar vacíos)
    while len(nuevas_rutas) < horizonte:
        nuevas_rutas.append(Ruta((), ()))
        
    nueva_solucion = Solucion(rutas=tuple(nuevas_rutas))    
    return nueva_solucion

def calcular_ahorro_eliminar_cliente(ruta, cliente):
    """
    Calcula el ahorro de eliminar un cliente de una ruta.
    Se obtiene un ahorro si se pueden unir su predecesor y sucesor sin incrementar la distancia total.
    """
    if cliente not in ruta.clientes:
        return 0
    ruta2 = ruta
    ruta2 = ruta2.eliminar_visita(cliente)
    return ruta.costo - ruta2.costo

def calcular_costo_insertar_cliente(ruta, cliente):
    """
    Calcula el costo de insertar un cliente en una ruta.
    """
    if cliente in ruta.clientes:
        return 0
    ruta2 = ruta
    ruta2 = ruta2.insertar_visita(cliente, 10)

    return ruta.costo - ruta2.costo

