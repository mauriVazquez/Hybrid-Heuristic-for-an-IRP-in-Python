from hair.contexto import constantes_contexto
from modelos.solucion import Solucion
from modelos.ruta import Ruta

from hair.mip1 import Mip1
from hair.mip2 import Mip2

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def mejora(solucion : Solucion, iterador_principal : int) -> Solucion:
    """
    Aplica un proceso iterativo de mejora a la solución dada utilizando tres tipos diferentes de optimizaciones:
    
    1. Aplicación del modelo MIP1 seguido del tsp_solver.
    2. Fusión de pares consecutivos de rutas y aplicación del modelo MIP2 con ajustes para asegurar factibilidad.
    3. Aplicación directa del modelo MIP2 seguido del algoritmo tsp_solver.
    
    Durante cada iteración, si alguna de las soluciones generadas mejora el costo de la solución actual, se actualiza
    dicha solución y se continúa el proceso.
    
    Args:
        solucion (Solucion): La solución inicial sobre la que se realizarán las mejoras.
        iterador_principal (int): El número de la iteración principal actual en el proceso de mejora.
    
    Returns:
        Solucion: La mejor solución obtenida después de aplicar todas las mejoras.
    """  
    constantes = constantes_contexto.get()
    do_continue = True
    
    mejor_solucion = tsp_solver(None, solucion)

    while do_continue:
        do_continue = False

        #################### PRIMER TIPO DE MEJORA ##################
        #Se aplica el MIP1 a mejor_solucion, luego se le aplica tsp_solver
        solucion_prima = Mip1.ejecutar(mejor_solucion)
        solucion_prima = tsp_solver(mejor_solucion, solucion_prima)
        #Si el costo de la solución encontrada es mejor que el de mejor_solucion, se actualiza mejor_solucion
        if (solucion_prima.costo < mejor_solucion.costo):
            mejor_solucion = solucion_prima.clonar()
            do_continue = True
            # print(f"Mejora 1 {mejor_solucion}")
        
        #################### SEGUNDO TIPO DE MEJORA ####################
        solucion_merge = mejor_solucion.clonar()

        for i in range(constantes.horizonte_tiempo - 1):
            # Por cada par de rutas, se crea una solución s1 que resulta de trasladar las visitas de r2 a r1
            s1 = mejor_solucion.clonar()
            s1.merge_rutas(i, i+1)
            #Se aplica el Mip2 a la solución s1 encontrada
            aux_solucion = Mip2.ejecutar(s1)
            
            # Si el resultado de aplicar el MIP2 sobre s1 no es factible y r no es la última ruta en s1, entonces
            #se anticipa la siguiente ruta despues de r en un período de tiempo
            if (not aux_solucion.es_factible) and ((i + 2) < len(s1.rutas)):
                s1.merge_rutas(i+1,i+2)
                aux_solucion = Mip2.ejecutar(s1)
                
            #Si el resultado de aplicar el MIP2 a s1 es factible, entonces solucion_prima es una solución óptima
            if aux_solucion.es_factible:
                solucion_prima = tsp_solver(s1, aux_solucion)
                if solucion_prima.costo < solucion_merge.costo:
                    solucion_merge = solucion_prima.clonar()

            #Por cada par de rutas, se crea una solución s2 que resulta de trasladar las visitas de r1 a r2
            s2 = mejor_solucion.clonar()
            s2.merge_rutas(i+1,i)
            aux_solucion = Mip2.ejecutar(s2)
            
            #Si el resultado de aplicar el MIP2 sobre s2 no es factible y r no es la primer ruta en s2, entonces
            #se posterga la siguiente ruta despues de r en un período de tiempo
            if (not aux_solucion.es_factible) and (i > 0):
                s2.merge_rutas(i,i-1)
                aux_solucion = Mip2.ejecutar(s2)
                
            #Si el resultado de aplicar el MIP2 a s2 es factible, entonces solucion_prima es una solución óptima
            if aux_solucion.es_factible:
                solucion_prima = tsp_solver(s2, aux_solucion)
                #En este punto solucion_merge es la mejor solución entre mejor_solucion y la primer parte de esta mejora.
                if solucion_prima.costo < solucion_merge.costo:
                    solucion_merge = solucion_prima.clonar()
                    
        #Si el costo de solucion_merge es mejor que el de mejor_solucion, se actualiza el valor de mejor_solucion
        if solucion_merge.costo < mejor_solucion.costo:
            mejor_solucion = solucion_merge.clonar()
            do_continue = True
            # print(f"Mejora 2 {mejor_solucion}")

        #TERCER TIPO DE MEJORA
        #Se aplica el MIP2 a mejor_solucion, luego se le aplica tsp_solver
        solucion_prima = Mip2.ejecutar(mejor_solucion)
        solucion_prima = tsp_solver(mejor_solucion, solucion_prima)
        if solucion_prima.costo < mejor_solucion.costo:
            mejor_solucion = solucion_prima.clonar()
            do_continue = True 
            # print(f"Mejora 3 {mejor_solucion}")

    mejor_solucion.refrescar()
    print(f"Mejora ({iterador_principal}): {mejor_solucion}")
    return mejor_solucion.clonar()


def tsp_solver(solucion: Solucion, solucion_prima: Solucion) -> Solucion:
    """
    Función resuelve un TSP para mejorar las rutas de una solución.
    
    Args:
        solucion (Solucion): Solución inicial.
        solucion_prima (Solucion): Solución alternativa.

    Returns:
        Solucion: Solución mejorada después de aplicar el algoritmo.
    """
    constantes = constantes_contexto.get()
    # Determinar la solución base a clonar
    if ((solucion is not None) and solucion.es_igual(solucion_prima)):
        aux_solucion = solucion.clonar()  
    else:
        aux_solucion = solucion_prima.clonar()

    # Iterar sobre el horizonte de tiempo
    for t in range(constantes.horizonte_tiempo):
        
        # Obtener matriz distancia
        matriz_distancia = _obtener_matriz_distancia(aux_solucion.rutas[t])

        # Configurar los datos del problema
        data = {
            "distance_matrix": matriz_distancia,  # Matriz de distancias
            "num_vehicles": 1,                    # Un solo vehículo
            "depot": 0                            # Nodo inicial (proveedor)
        }

        # Crear el gestor de índices de ruteo
        manager = pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
        )

        # Crear el modelo de ruteo
        routing = pywrapcp.RoutingModel(manager)

        transit_callback_index = routing.RegisterTransitCallback(
            lambda from_index, to_index: data["distance_matrix"][
                manager.IndexToNode(from_index)
            ][manager.IndexToNode(to_index)]
        )

        # Establecer el costo de cada arco
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Configurar los parámetros de búsqueda
        parametros_busqueda = pywrapcp.DefaultRoutingSearchParameters()
        parametros_busqueda.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        # Resolver el problema
        solucion_modelo = routing.SolveWithParameters(parametros_busqueda)

        # Si se encuentra una solución válida, actualizar la ruta en la solución auxiliar
        if solucion_modelo:
            ruta_optima = []  # Almacena la ruta óptima
            index = routing.Start(0)  # Nodo inicial (proveedor)
            # Recorrer la solución y construir la ruta óptima
            while not routing.IsEnd(index):
                siguiente_index = solucion_modelo.Value(routing.NextVar(index))
                if manager.IndexToNode(siguiente_index) != 0:  # Excluir el nodo inicial
                    ruta_optima.append(manager.IndexToNode(siguiente_index))
                index = siguiente_index

            # Crear una nueva ruta con los clientes y cantidades de la solución auxiliar
            nueva_ruta = Ruta(
                [aux_solucion.rutas[t].clientes[indice - 1] for indice in ruta_optima],
                [aux_solucion.rutas[t].cantidades[indice - 1] for indice in ruta_optima]
            )
            aux_solucion.rutas[t] = nueva_ruta.clonar()

    # Actualizar y retornar la solucion optimizada
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
    