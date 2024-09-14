from modelos.solucion import Solucion
from typing import Type
from random import random
from modelos.tabulists import tabulists
from constantes import constantes
from modelos.penalty_variables import alpha, beta
import concurrent.futures

def mover(solucion: Type["Solucion"], iterador_principal : int) -> Type["Solucion"]:
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
    # Creación de neighborhood_prima de solucion s (N'(s))
    neighborhood_prima = _crear_n_prima(solucion)
    
    # Creación de neighborhood de solucion s (N(s)) a partir de N'(s)
    neighborhood = _crear_n(solucion, neighborhood_prima)

    respuesta = solucion.clonar()
    for neighbor in neighborhood:
        permitido       = tabulists.movimiento_permitido(solucion, neighbor)   
        if neighbor.costo() < (respuesta.costo() if permitido else (0.85 * respuesta.costo())):
            respuesta = neighbor.clonar()

    tabulists.actualizar(solucion, respuesta, iterador_principal)
    alpha.no_factibles() if respuesta.es_excedida_capacidad_vehiculo() else alpha.factible()
    beta.no_factibles() if respuesta.proveedor_tiene_desabastecimiento() else beta.factible()
    return respuesta

def _crear_n_prima(solucion: Type["Solucion"]) -> list[Type["Solucion"]]:
    """
    Crea el vecindario primario (N'(s)) aplicando diferentes variaciones sobre la solución actual.
    Las variaciones se ejecutan en paralelo usando hilos.

    Args:
        solucion (Solucion): La solución actual.

    Returns:
        list[Solucion]: Lista de soluciones generadas por las variaciones.
    """
    
    # TODO Probar rendimiento sin paralelismo 
    # neighborhood_prima  = _variante_eliminacion(solucion)
    # neighborhood_prima += _variante_insercion(solucion)
    # neighborhood_prima += _variante_mover_visita(solucion)
    # neighborhood_prima += _variante_intercambiar_visitas(solucion)
    
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
                    if (cliente.costo_almacenamiento > constantes.proveedor.costo_almacenamiento) or (solucion_prima.rutas[t].obtener_total_entregado() > constantes.capacidad_vehiculo) or (solucion_prima.obtener_niveles_inventario_proveedor()[t] < 0):
                        # Política OU
                        if constantes.politica_reabastecimiento == "OU":
                            # Definir s" como la solucion obtenida al remover la visita al cliente en el tiempo t de s'
                            solucion_dosprima = solucion_prima.clonar()
                            solucion_dosprima.remover_visita(cliente, t)
                            # Si s" es admisible y f(s") < f(s') 
                            if (solucion_dosprima.es_admisible() and (solucion_dosprima.costo() < solucion_prima.costo())):
                                # Asignar s" a s' y se agrega j a A. 
                                solucion_prima = solucion_dosprima.clonar()
                                conjunto_A.append(cliente)   

                        #Política ML: 
                        if constantes.politica_reabastecimiento == "ML":
                            # y ← min{xjt, min t'>t Ijt'}.        
                            xjt = solucion_prima.rutas[t].obtener_cantidad_entregada(cliente)
                            niveles_inventario = solucion_prima.obtener_niveles_inventario_cliente(cliente)
                            ijt = niveles_inventario[(t+1):-1]
                            y = min(xjt, min((ijt if (ijt != []) else [xjt])))
                            
                            # Sea s" la solución obtenida desde s' tras remover 'y' unidades de entrega al cliente en el tiempo t 
                            # (la visita al cliente en el tiempo t se elimina si y = xjt). 
                            solucion_dosprima = solucion_prima.clonar()
                            if y == xjt:
                                solucion_dosprima.rutas[t].remover_visita(cliente)
                            else:
                                solucion_dosprima.rutas[t].quitar_cantidad_cliente(cliente, y)
                                
                            # Si f(s") < f(s'), asignar s" a s'
                            if solucion_dosprima.costo() < solucion_prima.costo():
                                # Agregar el cliente al conjunto A si el cliente no es visitado en el tiempo t en s'
                                if not solucion_prima.rutas[t].es_visitado(cliente):
                                    conjunto_A.append(cliente)
                                solucion_prima = solucion_dosprima.clonar()

                # Política ML: 
                if constantes.politica_reabastecimiento == "ML":
                    for cliente in solucion_prima.rutas[t].clientes:
                        if cliente.costo_almacenamiento < constantes.proveedor.costo_almacenamiento:
                            # Sea y ← max t'≥t(Ijt' + xjt'). 
                            niveles_inventario_cliente = solucion_prima.obtener_niveles_inventario_cliente(cliente)
                            entregas = [(solucion_prima.rutas[t2].obtener_cantidad_entregada(cliente) + niveles_inventario_cliente[t2]) 
                                for t2 in range(t, constantes.horizon_length )]
                            y = max(entregas) if entregas else 0
                            
                            # Sea s" la solución obtenida desde s' tras añadir Uj − y unidades de entrega al cliente en el tiempo t
                            solucion_dosprima = solucion_prima.clonar()
                            solucion_dosprima.rutas[t].agregar_cantidad_cliente(cliente, (cliente.nivel_maximo - y))

                            if solucion_dosprima.costo() < solucion_prima.costo():
                                solucion_prima = solucion_dosprima.clonar()                              
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
            if solucion_copy.es_admisible():
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
            if (not solucion.rutas[index].es_visitado(cliente)):
                solucion_copy = solucion.clonar()
                solucion_copy.insertar_visita(cliente, index)
                if solucion_copy.es_admisible():
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
            for t_not_visitado in (set(range(constantes.horizon_length)) - set(set_t_visitado)):
                solucion_copy = new_solucion.clonar()
                solucion_copy.insertar_visita(cliente, t_not_visitado)
                if solucion_copy.es_admisible():
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
                    
                    if solucion_copy.es_admisible():
                        neighborhood_prima.append(solucion_copy)                                           
    return neighborhood_prima
    