from modelos.solucion import Solucion
from modelos.ruta import Ruta
import math
from ortools.constraint_solver import routing_enums_pb2, pywrapcp
from ortools.linear_solver import pywraplp

def mejora(solucion: Solucion, iterador_principal: int) -> Solucion:
    """
    Aplica un procedimiento iterativo de mejoras basado en MIP1, MIP2 y Lin-Kernighan (LK).
    """
    mejor_solucion = LK(None, solucion)
    do_continue = True

    while do_continue:
        do_continue = False
        # PRIMERA MEJORA: Aplicación iterativa de MIP1 + LK
        solucion_prima = mip1_route_assignment(mejor_solucion)
        solucion_prima = LK(mejor_solucion, solucion_prima)
        if solucion_prima.es_admisible and solucion_prima.costo < mejor_solucion.costo:
            mejor_solucion = solucion_prima.clonar()
            do_continue = True
        
        # # SEGUNDA MEJORA: Merge de rutas consecutivas en ambas direcciones + MIP2
        solucion_merge = mejor_solucion.clonar()
        
        # Crear lista de pares de rutas consecutivas
        L = [(i, i+1) for i in range(len(mejor_solucion.rutas)-1)]
        
        # Iteración sobre pares de rutas
        for ruta1_idx, ruta2_idx in L:
            # Merge hacia adelante (ruta i con ruta i+1)
            s1 = mejor_solucion.merge_rutas(ruta1_idx, ruta2_idx)
            s1 = mip2_asignacion_clientes(s1)  # Aplicar MIP2
            
            if s1.es_factible:
                s1_mejorada = LK(mejor_solucion, s1)
                if s1_mejorada.costo < solucion_merge.costo:
                    solucion_merge = s1_mejorada.clonar()
       
            # Merge hacia atrás (ruta i con ruta i-1)
            if ruta1_idx > 0:  # Solo si no es la primera ruta
                s2 = mejor_solucion.merge_rutas(ruta1_idx - 1, ruta1_idx)
                s2 = mip2_asignacion_clientes(s2)  # Aplicar MIP2
                
                if s2.es_factible:
                    s2_mejorada = LK(mejor_solucion, s2)
                    if s2_mejorada.costo < solucion_merge.costo:
                        solucion_merge = s2_mejorada.clonar()
       
        # Aplicar el mejor resultado de los merges
        if solucion_merge.costo < mejor_solucion.costo:
            mejor_solucion = solucion_merge.clonar()
            do_continue = True

        # TERCERA MEJORA: Aplicación de MIP2 + LK
        solucion_prima = mip2_asignacion_clientes(mejor_solucion)
        solucion_prima = LK(mejor_solucion, solucion_prima)
        if solucion_prima.es_admisible and solucion_prima.costo < mejor_solucion.costo:
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
    
    
def mip1_route_assignment(solucion: Solucion):
    """
    Implementa el MIP1 con TODAS las restricciones correctamente formuladas en OR-Tools.

    - Asigna rutas a periodos de tiempo sin cambiar la estructura de las rutas.
    - Evita la duplicación de clientes en rutas.
    - Cumple con la política de reabastecimiento OU y las restricciones del modelo.
    """
    contexto = solucion.contexto
    solver = pywraplp.Solver.CreateSolver("SCIP")
    if not solver:
        raise Exception("No se pudo inicializar el solver.")

    matriz_ahorro = {
        (cliente.id, r): calcular_ahorro_cliente_ruta(solucion, cliente, r)
        for cliente in contexto.clientes for r in range(len(solucion.rutas))
    }

    # **Definir variables de decisión**
    x = {}  # Cantidad entregada a cliente i en tiempo t
    I = {}  # Inventario del cliente i en tiempo t
    B = {}  # Inventario del proveedor en tiempo t
    w = {}  # Binary: 1 si el cliente i es removido de la ruta r
    z = {}  # Binary: 1 si la ruta r es asignada al tiempo t
    y = {}  # Variable auxiliar para evitar multiplicación de binarios

    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            x[i.id, t] = solver.NumVar(0, i.nivel_maximo, f"x_{i.id}_{t}")
            I[i.id, t] = solver.NumVar(0, i.nivel_maximo, f"I_{i.id}_{t}")
            w[i.id, t] = solver.BoolVar(f"w_{i.id}_{t}")

    for t in range(contexto.horizonte_tiempo):
        B[t] = solver.NumVar(0, solver.infinity(), f"B_{t}")

    for r in range(len(solucion.rutas)):
        for t in range(contexto.horizonte_tiempo):
            z[r, t] = solver.BoolVar(f"z_{r}_{t}")

    # 🔹 **Definir variable auxiliar para modelar `z[r,t] * (1 - w[i,r])`**
    for i in contexto.clientes:
        for r in range(len(solucion.rutas)):
            for t in range(contexto.horizonte_tiempo):
                y[i.id, r, t] = solver.BoolVar(f"y_{i.id}_{r}_{t}")

                # Modelar la multiplicación de binarios con restricciones lineales
                solver.Add(y[i.id, r, t] <= z[r, t])
                solver.Add(y[i.id, r, t] <= 1 - w[i.id, r])
                solver.Add(y[i.id, r, t] >= z[r, t] + (1 - w[i.id, r]) - 1)

    #🔹 **Restricciones del modelo**
    ## (2) Balance de inventario del proveedor
    # El inventario del proveedor en cada periodo se calcula como el inventario del periodo anterior,
    # más la producción del proveedor, menos la cantidad entregada a los clientes.
    for t in range(1, contexto.horizonte_tiempo):  # Excluye t=0 porque no tiene un t-1 válido
        solver.Add(B[t] == B[t - 1] + contexto.proveedor.nivel_produccion - sum(x[i.id, t] for i in contexto.clientes))
    
    ## (3) **Balance de inventario del proveedor**
    for t in range(1, contexto.horizonte_tiempo):
        solver.Add(B[t] == B[t - 1] + contexto.proveedor.nivel_produccion - sum(x[i.id, t] for i in contexto.clientes))

    ## (4) **Balance de inventario del cliente**
    for i in contexto.clientes:
        for t in range(1, contexto.horizonte_tiempo):
            solver.Add(I[i.id, t] == I[i.id, t - 1] + x[i.id, t - 1] - i.nivel_demanda)
            solver.Add(I[i.id, t] >= i.nivel_minimo)

    if contexto.politica_reabastecimiento == "OU":
        ## (5) **Inventario debe estar entre 0 y el máximo del cliente**
        for i in contexto.clientes:
            for t in range(contexto.horizonte_tiempo):
                solver.Add(I[i.id, t] - i.nivel_demanda >= 0)
                solver.Add(I[i.id, t] <= i.nivel_maximo)

        ## (6) **Un cliente solo puede recibir entrega si su inventario lo permite**
        for i in contexto.clientes:
            for t in range(contexto.horizonte_tiempo):
                solver.Add(x[i.id, t] <= i.nivel_maximo - I[i.id, t])
                
        ## (7) **Restricciones de la política OU**
        for i in contexto.clientes:
            for t in range(contexto.horizonte_tiempo):
                solver.Add(x[i.id, t] <= i.nivel_maximo * y[i.id, r, t])

    ## (8) **Restricción de capacidad del vehículo**
    for t in range(contexto.horizonte_tiempo):
        solver.Add(sum(x[i.id, t] for i in contexto.clientes) <= contexto.capacidad_vehiculo)
        solver.Add(sum(x[i.id, t] for i in contexto.clientes) >= sum(i.nivel_demanda for i in contexto.clientes))

    ## (9) **Cada ruta r solo puede ser asignada a un periodo t**
    for r in range(len(solucion.rutas)):
        solver.Add(sum(z[r, t] for t in range(contexto.horizonte_tiempo)) <= 1)

    ## (10) **Máximo de una ruta en cada periodo**
    for t in range(contexto.horizonte_tiempo):
        solver.Add(sum(z[r, t] for r in range(len(solucion.rutas))) <= 1)

    ## (11) **Un cliente solo puede ser servido si está en la ruta asignada al tiempo t**
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(x[i.id, t] <= i.nivel_maximo * sum(z[r, t] for r in range(len(solucion.rutas))))

    ## (12) **Si un cliente es removido, no puede ser servido en t**
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(x[i.id, t] <= i.nivel_maximo * (1 - w[i.id, t]))

    ## (13) **Un cliente solo puede ser removido si estaba en la ruta original**
    for i in contexto.clientes:
        for r in range(len(solucion.rutas)):
            solver.Add(w[i.id, r] <= sum(z[r, t] for t in range(contexto.horizonte_tiempo)) - sum(x[i.id, t] for t in range(contexto.horizonte_tiempo)))

    ## (14) Restricción de no negatividad en la cantidad entregada x_{it}
    # La cantidad de productos entregados a un cliente en un período no puede ser negativa.
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(x[i.id, t] >= 0)

    ## (15) Restricción de no negatividad en el inventario I_{it}
    # El inventario de un cliente en un período no puede ser negativo.
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(I[i.id, t] >= 0)

    ## (16) Restricción de no negatividad en el inventario del proveedor B_t
    # El inventario del proveedor en un período no puede ser negativo.
    for t in range(contexto.horizonte_tiempo):
        solver.Add(B[t] >= 0)

    ## (17) Restricción específica de OU: Relación entre inventario y entregas (solo para OU)
    # Esta restricción asegura que el inventario del cliente no supere su nivel máximo de almacenamiento.
    if contexto.politica_reabastecimiento == "OU":
        for i in contexto.clientes:
            for t in range(contexto.horizonte_tiempo):
                solver.Add(I[i.id, t] <= i.nivel_maximo * x[i.id, t])

    ## (18) Restricción de binariedad en la variable de eliminación w_{ir}
    # La variable w_{ir} debe ser binaria: 1 si el cliente es removido, 0 si no.
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(w[i.id, t] >= 0)
            solver.Add(w[i.id, t] <= 1)

    ## (19) Restricción de binariedad en la asignación de rutas z_{rt}
    # La variable z_{rt} debe ser binaria: 1 si la ruta está asignada al período t, 0 si no.
    for r in range(len(solucion.rutas)):
        for t in range(contexto.horizonte_tiempo):
            solver.Add(z[r, t] >= 0)
            solver.Add(z[r, t] <= 1)

    # 🔹 **Función Objetivo**
    solver.Minimize(
        sum(contexto.proveedor.costo_almacenamiento * B[t] for t in range(contexto.horizonte_tiempo))
        + sum(i.costo_almacenamiento * I[i.id, t] for i in contexto.clientes for t in range(contexto.horizonte_tiempo))
        - sum(matriz_ahorro[i.id, r] * w[i.id, r] for i in contexto.clientes for r in range(len(solucion.rutas)))
    )

    # 🔹 **Resolver el problema**
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        return reconstruir_solucion(solucion, x, z)
    else:
        return solucion


def mip2_asignacion_clientes(solucion):
    """
    Implementación del MIP2 para la asignación de clientes utilizando OR-Tools.
    
    Args:
        solucion (Solucion): Solución actual del IRP.
    
    Returns:
        Solucion: Nueva solución optimizada.
    """
    contexto = solucion.contexto
    clientes = contexto.clientes
    tiempo_max = contexto.horizonte_tiempo

    # Crear el solver de MIP
    solver = pywraplp.Solver.CreateSolver("SCIP")  # También puedes usar "CBC" o "GLOP" para diferentes enfoques
    if not solver:
        return solucion.clonar()  # Si OR-Tools no está disponible, retornar la misma solución

    # 🔹 Variables de decisión:
    w = {}  # w[it]: 1 si el cliente i es eliminado de la ruta en t
    v = {}  # v[it]: 1 si el cliente i es insertado en la ruta en t
    B = {}  # Inventario del proveedor en tiempo t
    x = {}  # Cantidad entregada a cliente i en tiempo t
    I = {}  # Inventario del cliente i en tiempo t
    y = {}  # Variable auxiliar para evitar multiplicación de binarios
    
    for cliente in clientes:
        for t in range(tiempo_max):
            w[cliente.id, t] = solver.BoolVar(f"w_{cliente.id}_{t}")
            v[cliente.id, t] = solver.BoolVar(f"v_{cliente.id}_{t}")
            x[cliente.id, t] = solver.NumVar(0, cliente.nivel_maximo, f"x_{cliente.id}_{t}")
            I[cliente.id, t] = solver.NumVar(0, cliente.nivel_maximo, f"I_{cliente.id}_{t}")
            w[cliente.id, t] = solver.BoolVar(f"w_{cliente.id}_{t}")

    for t in range(contexto.horizonte_tiempo):
        B[t] = solver.NumVar(0, solver.infinity(), f"B_{t}")
        
    for i in contexto.clientes:
        for r in range(len(solucion.rutas)):
            for t in range(contexto.horizonte_tiempo):
                y[i.id, r, t] = solver.BoolVar(f"y_{i.id}_{r}_{t}")
                # Modelar la multiplicación de binarios con restricciones lineales
                solver.Add(y[i.id, r, t] <= 1 - w[i.id, r])
            
    # 🔹 Función objetivo: minimizar costos de inventario y transporte
    objetivo = solver.Objective()

    for cliente in clientes:
        for t in range(tiempo_max):
            lambda_it = solucion.calcular_ahorro_remocion(cliente, t)  # Ahorro al eliminar
            mu_it = solucion.calcular_costo_insercion(cliente, t)  # Costo de inserción

            if math.isinf(lambda_it) or math.isnan(lambda_it):
                lambda_it = 0  # Evitar valores inválidos

            if math.isinf(mu_it) or math.isnan(mu_it):
                mu_it = 0  # Evitar valores inválidos

            objetivo.SetCoefficient(w[cliente.id, t], -lambda_it)  # Maximiza ahorro
            objetivo.SetCoefficient(v[cliente.id, t], mu_it)  # Minimiza costo

    objetivo.SetMinimization()
    
    ## (2) Balance de inventario del proveedor
    # El inventario del proveedor en cada periodo se calcula como el inventario del periodo anterior,
    # más la producción del proveedor, menos la cantidad entregada a los clientes.
    for t in range(1, contexto.horizonte_tiempo):  # Excluye t=0 porque no tiene un t-1 válido
        solver.Add(B[t] == B[t - 1] + contexto.proveedor.nivel_produccion - sum(x[i.id, t] for i in contexto.clientes))
    
    ## (3) **Balance de inventario del proveedor**
    for t in range(1, contexto.horizonte_tiempo):
        solver.Add(B[t] == B[t - 1] + contexto.proveedor.nivel_produccion - sum(x[i.id, t] for i in contexto.clientes))

    ## (4) **Balance de inventario del cliente**
    for i in contexto.clientes:
        for t in range(1, contexto.horizonte_tiempo):
            solver.Add(I[i.id, t] == I[i.id, t - 1] + x[i.id, t - 1] - i.nivel_demanda)
            solver.Add(I[i.id, t] >= i.nivel_minimo)

    if contexto.politica_reabastecimiento == "OU":
        ## (5) **Inventario debe estar entre 0 y el máximo del cliente**
        for i in contexto.clientes:
            for t in range(contexto.horizonte_tiempo):
                solver.Add(I[i.id, t] - i.nivel_demanda >= 0)
                solver.Add(I[i.id, t] <= i.nivel_maximo)

        ## (6) **Un cliente solo puede recibir entrega si su inventario lo permite**
        for i in contexto.clientes:
            for t in range(contexto.horizonte_tiempo):
                solver.Add(x[i.id, t] <= i.nivel_maximo - I[i.id, t])
                
        ## (7) **Restricciones de la política OU**
        for i in contexto.clientes:
            for t in range(contexto.horizonte_tiempo):
                solver.Add(x[i.id, t] <= i.nivel_maximo * y[i.id, r, t])

    ## (8) **Restricción de capacidad del vehículo**
    for t in range(contexto.horizonte_tiempo):
        solver.Add(sum(x[i.id, t] for i in contexto.clientes) <= contexto.capacidad_vehiculo)
        solver.Add(sum(x[i.id, t] for i in contexto.clientes) >= sum(i.nivel_demanda for i in contexto.clientes))

    ## (14) Restricción de no negatividad en la cantidad entregada x_{it}
    # La cantidad de productos entregados a un cliente en un período no puede ser negativa.
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(x[i.id, t] >= 0)

    ## (15) Restricción de no negatividad en el inventario I_{it}
    # El inventario de un cliente en un período no puede ser negativo.
    for i in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            solver.Add(I[i.id, t] >= 0)

    ## (16) Restricción de no negatividad en el inventario del proveedor B_t
    # El inventario del proveedor en un período no puede ser negativo.
    for t in range(contexto.horizonte_tiempo):
        solver.Add(B[t] >= 0)

    ## (17) Restricción específica de OU: Relación entre inventario y entregas (solo para OU)
    # Esta restricción asegura que el inventario del cliente no supere su nivel máximo de almacenamiento.
    if contexto.politica_reabastecimiento == "OU":
        for i in contexto.clientes:
            for t in range(contexto.horizonte_tiempo):
                solver.Add(I[i.id, t] <= i.nivel_maximo * x[i.id, t])
                
    ## Restricción (21): Un cliente no puede insertarse en una ruta que ya lo visita
    for cliente in clientes:
        for t in range(tiempo_max):
            delta_it = 1 if cliente in solucion.rutas[t].clientes else 0
            solver.Add(v[cliente.id, t] <= (1 - delta_it))

    ## Restricción (22): Un cliente no puede eliminarse de una ruta donde no está presente
    for cliente in clientes:
        for t in range(tiempo_max):
            delta_it = 1 if cliente in solucion.rutas[t].clientes else 0
            solver.Add(w[cliente.id, t] <= delta_it)

    ## Restricción (23): Un cliente puede ser atendido en t solo si ya estaba en la ruta o si fue insertado
    for cliente in clientes:
        for t in range(tiempo_max):
            solver.Add(solucion.rutas[t].obtener_cantidad_entregada(cliente) <= cliente.nivel_maximo * (delta_it - w[cliente.id, t] + v[cliente.id, t]))

    ## Restricción de variables binarias
    for cliente in clientes:
        for t in range(tiempo_max):
            solver.Add(w[cliente.id, t] >= 0)
            solver.Add(w[cliente.id, t] <= 1)
            solver.Add(v[cliente.id, t] >= 0)
            solver.Add(v[cliente.id, t] <= 1)

    # Resolver el modelo
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        nueva_solucion = solucion.clonar()

        for cliente in clientes:
            for t in range(tiempo_max):
                if w[cliente.id, t].solution_value() == 1:
                    nueva_solucion = nueva_solucion.eliminar_visita(cliente, t)
                if v[cliente.id, t].solution_value() == 1:
                    nueva_solucion = nueva_solucion.insertar_visita(cliente, t)

        return nueva_solucion

    return solucion.clonar()  # Retorna la misma solución si no encuentra óptimo


def verificar_ruta_unica(solucion: Solucion) -> Solucion:
    """
    Verifica que no haya clientes duplicados en una misma ruta.
    Si los encuentra, los elimina manteniendo la cantidad de entrega.
    """
    rutas_modificadas = []
    
    for ruta in solucion.rutas:
        clientes_vistos = set()
        clientes_unicos = []
        cantidades_finales = []

        for cliente, cantidad in zip(ruta.clientes, ruta.cantidades):
            if cliente not in clientes_vistos:
                clientes_vistos.add(cliente)
                clientes_unicos.append(cliente)
                cantidades_finales.append(cantidad)
            else:
                print(f"⚠️ Cliente {cliente.id} duplicado en ruta. Eliminado.")

        rutas_modificadas.append(Ruta(tuple(clientes_unicos), tuple(cantidades_finales)))

    return Solucion(rutas=tuple(rutas_modificadas))


def calcular_ahorro_cliente_ruta(solucion: Solucion, cliente, ruta_idx):
    """
    Calcula el ahorro de eliminar un cliente de una ruta.
    Se obtiene un ahorro si se pueden unir su predecesor y sucesor sin incrementar la distancia total.
    """
    ruta = solucion.rutas[ruta_idx]
    if cliente not in ruta.clientes:
        return 0  # 🔹 No hay ahorro si el cliente no está en la ruta

    idx = ruta.clientes.index(cliente)
    prev = ruta.clientes[idx - 1] if idx > 0 else None
    next = ruta.clientes[idx + 1] if idx < len(ruta.clientes) - 1 else None

    if prev is None or next is None:
        return 0  # 🔹 No hay ahorro si es el primero o último cliente

    matriz_distancia = solucion.contexto.matriz_distancia
    ahorro = matriz_distancia[prev.id][cliente.id] + matriz_distancia[cliente.id][next.id] - matriz_distancia[prev.id][next.id]

    return ahorro

def reconstruir_solucion(solucion, x, z):
    """
    Reconstruye la solución a partir de las variables optimizadas.
    """
    nuevas_rutas = [Ruta((), ()) for _ in range(solucion.contexto.horizonte_tiempo)]
    for t in range(solucion.contexto.horizonte_tiempo):
        for r in range(len(solucion.rutas)):
            if z[r, t].solution_value() > 0.5:
                nuevas_rutas[t] = solucion.rutas[r]

    return Solucion(rutas=tuple(nuevas_rutas))