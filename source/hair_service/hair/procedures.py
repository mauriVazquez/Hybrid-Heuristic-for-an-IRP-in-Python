import concurrent.futures
from constantes import constantes
from modelos.solucion import Solucion
from modelos.ruta import Ruta
from random import random, randint
from typing import Type

from hair.mip1 import Mip1
from hair.mip2 import Mip2
from tsp_local.base import TSP
from tsp_local.kopt import KOpt

from modelos.tabulists import tabulists
from modelos.penalty_variables import FactorPenalizacion

from modelos.tripletManager import triplet_manager


def inicializacion() -> Type["Solucion"]:
    """
    Inicializa una solución donde cada cliente es considerado secuencialmente.
    
    Los tiempos de entrega se establecen lo más tarde posible antes de que ocurra una situación de desabastecimiento. 
    La solución obtenida es admisible pero no necesariamente factible, ya que depende de la política de reabastecimiento.
    
    Returns:
        Solucion: Un objeto Solucion con las rutas iniciales y cantidades asignadas.
    """
    # Obtener una solución vacía inicial
    solucion = Solucion.obtener_empty_solucion()
    for index, cliente in enumerate(constantes.clientes):
        for t in range(constantes.horizonte_tiempo):
            stock = solucion.inventario_clientes.get(cliente.id)[t]
            if solucion.inventario_clientes.get(cliente.id)[t] <= cliente.nivel_minimo:
                #  Calcular la máxima cantidad posible de entregar sin sobrepasar la capacidad máxima
                max_entrega = cliente.nivel_maximo - stock
                # Insertar visita en el tiempo actual, entregando una cantidad dependiente a la política de reabastecimiento
                cantidad_entregada = max_entrega if (constantes.politica_reabastecimiento == "OU") else randint(cliente.nivel_demanda, max_entrega)
                solucion.rutas[t].insertar_visita(cliente, cantidad_entregada, None)
                solucion.refrescar()
    print(f"Inicial: {solucion}")
    return solucion

def movimiento(solucion: Type["Solucion"], iterador_principal : int) -> Type["Solucion"]:
    """
    Realiza un movimiento sobre la solución actual, explora su vecindario y devuelve una nueva solución.
    Evalúa el vecindario y actualiza la lista tabú con la mejor solución permitida o con un mínimo absoluto.
    
    Args:
        solucion (Solucion): La solución actual.
        mejor_solucion (Solucion): La mejor solución encontrada hasta ahora.
        iterador_principal (int): El número de iteraciones del algoritmo.

    Returns:
        Solucion: La mejor solución encontrada para el vecindario de la solución ingresada.
    """
    # Paso 1: Creación de neighborhood_prima de solucion s (N'(s))
    neighborhood_prima  = _crear_n_prima(solucion)
    # Paso 2: Creación de neighborhood de solucion s (N(s))
    neighborhood        = _crear_n(solucion, neighborhood_prima)

    respuesta        = solucion.clonar()
    costo_respuesta  = float("inf")
    
    for neighbor in neighborhood:
        neighbor.refrescar()
        if tabulists.movimiento_permitido(solucion, neighbor) and (neighbor.costo < costo_respuesta):
            respuesta = neighbor.clonar()
            costo_respuesta = respuesta.costo
    
    for neighbor in neighborhood:
        if ((not tabulists.movimiento_permitido(solucion, neighbor)) and ( neighbor.costo < (0.7 * costo_respuesta))):
            respuesta = neighbor.clonar()
            costo_respuesta = respuesta.costo
    
    # Actualizar la lista tabú con la solución seleccionada
    tabulists.actualizar(solucion, respuesta, iterador_principal)

    # Actualizar métricas según restricciones de capacidad y desabastecimiento
    FactorPenalizacion.actualizar_metricas_factibilidad(respuesta)

    respuesta.refrescar()
    return respuesta

def mejora(solucion_original : Type["Solucion"], iterador_principal : int) -> Type["Solucion"]:
    """
    Aplica un proceso iterativo de mejora a la solución dada utilizando tres tipos diferentes de optimizaciones:
    
    1. Aplicación del modelo MIP1 seguido del algoritmo Lin-Kernighan (LK).
    2. Fusión de pares consecutivos de rutas y aplicación del modelo MIP2 con ajustes para asegurar factibilidad.
    3. Aplicación directa del modelo MIP2 seguido del algoritmo LK.
    
    Durante cada iteración, si alguna de las soluciones generadas mejora el costo de la solución actual, se actualiza
    dicha solución y se continúa el proceso.
    
    Args:
        solucion (Solucion): La solución inicial sobre la que se realizarán las mejoras.
        iterador_principal (int): El número de la iteración principal actual en el proceso de mejora.
    
    Returns:
        Solucion: La mejor solución obtenida después de aplicar todas las mejoras.
    """  
    do_continue = True
    
    solucion = solucion_original.clonar()
    mejor_solucion = lk(Solucion.obtener_empty_solucion(), solucion)

    while do_continue:
        do_continue = False

        #################### PRIMER TIPO DE MEJORA ##################
        #Se aplica el MIP1 a mejor_solucion, luego se le aplica LK
        solucion_prima = Mip1.ejecutar(mejor_solucion)
        solucion_prima = lk(mejor_solucion, solucion_prima)
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
                solucion_prima = lk(s1, aux_solucion)
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
                solucion_prima = lk(s2, aux_solucion)
                #En este punto solucion_merge es la mejor solución entre mejor_solucion y la primer parte de esta mejora.
                if solucion_prima.costo < solucion_merge.costo:
                    solucion_merge = solucion_prima.clonar()
                    
        #Si el costo de solucion_merge es mejor que el de mejor_solucion, se actualiza el valor de mejor_solucion
        if solucion_merge.costo < mejor_solucion.costo:
            mejor_solucion = solucion_merge.clonar()
            do_continue = True
            # print(f"Mejora 2 {mejor_solucion}")

        #TERCER TIPO DE MEJORA
        #Se aplica el MIP2 a mejor_solucion, luego se le aplica LK
        solucion_prima = Mip2.ejecutar(mejor_solucion)
        solucion_prima = lk(mejor_solucion, solucion_prima)
        if solucion_prima.costo < mejor_solucion.costo:
            mejor_solucion = solucion_prima.clonar()
            do_continue = True 
            print(f"Mejora 3 {mejor_solucion}")

    print(f"Mejora ({iterador_principal}): {solucion_prima}")
    return mejor_solucion.clonar()

def salto(solucion, iterador_principal):
    mejor_solucion = solucion.clonar()
    print(len(triplet_manager.triplets))
    if len(triplet_manager.triplets) > 0:
        #Mientras haya triplets
        while triplet_manager.triplets:
            solucion_base = mejor_solucion.clonar()
            
            #Se realizan jumps en función de algún triplet random
            cliente, tiempo_visitado, tiempo_not_visitado = triplet_manager.obtener_triplet_aleatorio() 

            cantidad_eliminado = solucion_base.rutas[tiempo_visitado].remover_visita(cliente)
            solucion_base.refrescar()
            solucion_base.rutas[tiempo_not_visitado].insertar_visita(cliente, cantidad_eliminado, None)
            solucion_base.refrescar()
            
            if all(c >= 0 for c in solucion_base.inventario_clientes.get(cliente.id, None)):
                mejor_solucion = solucion_base.clonar()
                    
        #Cuando no se puedan hacer mas saltos, se retorna la respuesta de ejecutar el MIP2 sobre la solución encontrada.
        mejor_solucion = Mip2.ejecutar(mejor_solucion)
    print(f"Salto ({iterador_principal}): {mejor_solucion}")
    return mejor_solucion.clonar()

def lk(solucion: Type["Solucion"], solucion_prima: Type["Solucion"]) -> Type["Solucion"]:
    if solucion.es_igual(solucion_prima):
        aux_solucion = solucion.clonar()
    else:
        aux_solucion = solucion_prima.clonar()
        for tiempo in range(constantes.horizonte_tiempo):
            tamano_matriz = len(solucion_prima.rutas[tiempo].clientes)+1
            matriz =  [[0] * tamano_matriz for _ in range(tamano_matriz)]

            # Proveedor distancia
            for indice, cliente in enumerate(solucion_prima.rutas[tiempo].clientes):
                matriz[0][indice+1] = cliente.distancia_proveedor
                matriz[indice+1][0] = cliente.distancia_proveedor

            # Clientes distancias
            for indice, c in enumerate(solucion_prima.rutas[tiempo].clientes):
                for indice2, c2 in enumerate(solucion_prima.rutas[tiempo].clientes):
                    matriz[indice+1][indice2+1] = constantes.matriz_distancia[c.id][c2.id]

            # Make an instance with all nodes
            TSP.setEdges(matriz)
            path, costo = KOpt(range(len(matriz))).optimise()
            
            aux_solucion.rutas[tiempo] = Ruta(
                [solucion_prima.rutas[tiempo].clientes[indice - 1] for indice in path[1:]],
                [solucion_prima.rutas[tiempo].cantidades[indice - 1] for indice in path[1:]]
            )

    aux_solucion.refrescar()
    return aux_solucion

# Satélites de MOVER

def _crear_n_prima(solucion: Type["Solucion"]) -> list[Type["Solucion"]]:
    """
    Crea el vecindario primario (N'(s)) aplicando diferentes variaciones sobre la solución actual.
    Las variaciones se ejecutan en paralelo usando hilos.
    Args:
        solucion (Solucion): La solución actual.

    Returns:
        list[Solucion]: Lista de soluciones generadas por las variaciones.
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Ejecutar las variantes en hilos separados
        futuro_eliminacion   = executor.submit(_variante_eliminacion, solucion)
        futuro_insercion     = executor.submit(_variante_insercion, solucion)
        futuro_mover_visita  = executor.submit(_variante_mover_visita, solucion)
        futuro_intercambiar  = executor.submit(_variante_intercambiar_visitas, solucion)

        # Esperar a que todas las tareas finalicen y recolectar los resultados
        neighborhood_prima = []
        neighborhood_prima += futuro_eliminacion.result()
        neighborhood_prima += futuro_insercion.result()
        neighborhood_prima += futuro_mover_visita.result()
        neighborhood_prima += futuro_intercambiar.result()
    return neighborhood_prima

def _crear_n(solucion : Type["Solucion"], neighborhood_prima : list[Type["Solucion"]]):
    """
    Crea el vecindario (N(s)) a partir del vecindario primario N'(s), aplicando políticas de reabastecimiento.
    
    Args:
        solucion (Solucion): La solución actual.
        neighborhood_prima (list[Solucion]): El vecindario primario generado.

    Returns:
        list[Solucion]: Vecindario final tras aplicar las políticas de reabastecimiento.
    """
    # Creación de neighborhood a partir de neighborhood_prima
    neighborhood = []
    #Por cada solución en N'(S)
    for solucion_prima in neighborhood_prima:
        # Determinar el conjunto A de clientes tales que Ti(s) != Ti(s'). 
        conjunto_A = [cliente for cliente in constantes.clientes if (solucion.T(cliente) != solucion_prima.T(cliente))]
        
        # Mientras el conjunto_A no esté vacío
        while len(conjunto_A) > 0:
            # Elegir alteatoriamente un cliente de A y removerlo
            cliente_removido = conjunto_A.pop(int(random() * len(conjunto_A)))
            # Considerar todos los tiempos de entrega t∈T(cliente) y todos los clientes entregados en el tiempo t en s'
            for t in solucion_prima.T(cliente_removido):
                for cliente in solucion_prima.rutas[t].clientes:
                    # Verificar si hj > h0, Qt(s') > C o Bt(s') < 0 
                    if (cliente.costo_almacenamiento > constantes.proveedor.costo_almacenamiento) or (solucion_prima.rutas[t].obtener_total_entregado() > constantes.capacidad_vehiculo) or (solucion_prima.inventario_proveedor[t] < 0):
                        # Política OU
                        if constantes.politica_reabastecimiento == "OU":
                            # Definir s" como la solucion obtenida al remover la visita al cliente en el tiempo t de s'
                            solucion_dosprima = solucion_prima.clonar()
                            solucion_dosprima.remover_visita(cliente, t)
                            # Si s" es admisible y f(s") < f(s') 
                            if (solucion_dosprima.es_admisible and (solucion_dosprima.costo < solucion_prima.costo)):
                                # Asignar s" a s' y se agrega j a A. 
                                solucion_prima = solucion_dosprima.clonar()
                                conjunto_A.append(cliente)   

                        #Política ML: 
                        if constantes.politica_reabastecimiento == "ML":
                            # y ← min{xjt, min t'>t Ijt'}.        
                            xjt = solucion_prima.rutas[t].obtener_cantidad_entregada(cliente)
                            niveles_inventario = solucion_prima.inventario_clientes.get(cliente.id, None)
                            ijt = niveles_inventario[(t+1):-1]
                            y = min(xjt, min((ijt if (ijt != []) else [xjt])))
                            
                            # Sea s" la solución obtenida desde s' tras remover 'y' unidades de entrega al cliente en el tiempo t 
                            # (la visita al cliente en el tiempo t se elimina si y = xjt). 
                            solucion_dosprima = solucion_prima.clonar()
                            if y == xjt:
                                solucion_dosprima.rutas[t].remover_visita(cliente)
                                solucion_dosprima.refrescar()
                            else:
                                solucion_dosprima.rutas[t].quitar_cantidad_cliente(cliente, y)
                                solucion_dosprima.refrescar()
                                
                            # Si f(s") < f(s'), asignar s" a s'
                            if solucion_dosprima.costo < solucion_prima.costo:
                                # Agregar el cliente al conjunto A si el cliente no es visitado en el tiempo t en s'
                                if not solucion_prima.es_visitado(cliente, t):
                                    conjunto_A.append(cliente)
                                solucion_prima = solucion_dosprima.clonar()

                # Política ML: 
                if constantes.politica_reabastecimiento == "ML":
                    for cliente in solucion_prima.rutas[t].clientes:
                        if cliente.costo_almacenamiento < constantes.proveedor.costo_almacenamiento:
                            # Sea y ← max t'≥t(Ijt' + xjt'). 
                            niveles_inventario_cliente = solucion_prima.inventario_clientes.get(cliente.id, None)
                            entregas = [(solucion_prima.rutas[t2].obtener_cantidad_entregada(cliente) + niveles_inventario_cliente[t2]) 
                                for t2 in range(t, constantes.horizonte_tiempo )]
                            y = max(entregas) if entregas else 0
                            
                            # Sea s" la solución obtenida desde s' tras añadir Uj − y unidades de entrega al cliente en el tiempo t
                            solucion_dosprima = solucion_prima.clonar()
                            solucion_dosprima.rutas[t].agregar_cantidad_cliente(cliente, (cliente.nivel_maximo - y))
                            solucion_dosprima.refrescar()
                            
                            if solucion_dosprima.costo < solucion_prima.costo:
                                solucion_prima = solucion_dosprima.clonar() 
        if not solucion_prima.es_igual(solucion):
            neighborhood.append(solucion_prima.clonar()) 
    return neighborhood

def _variante_eliminacion(solucion : Type["Solucion"]) -> list[Type["Solucion"]]:
    """
    Genera soluciones eliminando visitas de clientes en la solución actual.

    Args:
        solucion (Solucion): La solución actual.

    Returns:
        list[Solucion]: Lista de soluciones tras aplicar la variante de eliminación.
    """
    neighborhood_prima = []
    for cliente in constantes.clientes:
        for t in solucion.T(cliente):
            solucion_copy = solucion.clonar()
            solucion_copy.remover_visita(cliente, t)
            if solucion_copy.es_admisible:
                neighborhood_prima.append(solucion_copy)
    return neighborhood_prima

def _variante_insercion(solucion : Type["Solucion"]) -> list[Type["Solucion"]]:
    """
    Genera soluciones insertando nuevas visitas a clientes en la solución actual.

    Args:
        solucion (Solucion): La solución actual.

    Returns:
        list[Solucion]: Lista de soluciones tras aplicar la variante de inserción.
    """
    neighborhood_prima = []
    for index in range(len(solucion.rutas)):
        for cliente in constantes.clientes:
            if (not solucion.es_visitado(cliente, index)):
                solucion_copy = solucion.clonar()
                solucion_copy.insertar_visita(cliente, index)
                if solucion_copy.es_admisible:
                    neighborhood_prima.append(solucion_copy)
    return neighborhood_prima

def _variante_mover_visita(solucion : Type["Solucion"]) -> list[Type["Solucion"]]:
    """
    Genera soluciones moviendo visitas de un cliente entre diferentes tiempos de entrega.

    Args:
        solucion (Solucion): La solución actual.

    Returns:
        list[Solucion]: Lista de soluciones tras aplicar la variante de mover visitas.
    """
    neighborhood_prima = []
    for cliente in constantes.clientes:
        set_t_visitado = solucion.T(cliente)
        for t_visitado in set_t_visitado:
            new_solucion = solucion.clonar()
            new_solucion.remover_visita(cliente, t_visitado)
            for t_not_visitado in (set(range(constantes.horizonte_tiempo)) - set(set_t_visitado)):
                solucion_copy = new_solucion.clonar()
                solucion_copy.insertar_visita(cliente, t_not_visitado)
                if solucion_copy.es_admisible:
                    neighborhood_prima.append(solucion_copy)
    return neighborhood_prima

def _variante_intercambiar_visitas(solucion : Type["Solucion"]) -> list[Type["Solucion"]]:
    """
    Genera soluciones intercambiando visitas entre dos clientes en diferentes tiempos de entrega.

    Args:
        solucion (Solucion): La solución actual.

    Returns:
        list[Solucion]: Lista de soluciones tras aplicar la variante de intercambiar visitas.
    """
    neighborhood_prima = []
    for cliente1 in constantes.clientes:
        for cliente2 in list(set(constantes.clientes) -set([cliente1])):
            for iter_t in (set(solucion.T(cliente1)) - set(solucion.T(cliente2))):
                for iter_tprima in (set(solucion.T(cliente2)) - set(solucion.T(cliente1))):
                    solucion_copy = solucion.clonar()
                    # Remover visitas
                    solucion_copy.remover_visita(cliente1, iter_t)
                    solucion_copy.remover_visita(cliente2, iter_tprima)
                    #Añadir nuevas visitas
                    solucion_copy.insertar_visita(cliente1,iter_tprima)
                    solucion_copy.insertar_visita(cliente2,iter_t)
                    
                    if solucion_copy.es_admisible:
                        neighborhood_prima.append(solucion_copy)                                           
    return neighborhood_prima