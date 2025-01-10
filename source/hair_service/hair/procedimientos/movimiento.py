from modelos.solucion import Solucion
from random import randint
from hair.contexto import constantes_contexto

def movimiento(solucion: Solucion, tabulists, iterador_principal: int) -> Solucion:
    """
    Realiza un movimiento sobre la solución actual, explora su vecindario y devuelve una nueva solución.
    Evalúa el vecindario y selecciona la mejor solución permitida según la lista tabú o una solución 
    no permitida con menor costo si cumple los umbrales definidos.

    Args:
        solucion (Solucion): La solución actual.
        iterador_principal (int): El número de iteraciones del algoritmo.

    Returns:
        Solucion: La mejor solución encontrada para el vecindario de la solución ingresada.
    """
    constantes = constantes_contexto.get()
    # Crear el vecindario primario (N'(s))
    vecindario_prima = _crear_n_prima(solucion)

    # Crear el vecindario completo (N(s))
    vecindario = _crear_n(solucion, vecindario_prima)

    # Inicializar la solución respuesta
    mejor_solucion = solucion.clonar()
    mejor_solucion.refrescar()
    mejor_costo = float("inf")

    # Buscar la mejor solución permitida por la lista tabú
    for vecino in vecindario:
        if (vecino is not None) and tabulists.movimiento_permitido(solucion, vecino) and (vecino.costo < mejor_costo):
            mejor_solucion = vecino.clonar()
            mejor_solucion.refrescar()
            mejor_costo = vecino.costo

    # Ajustar el costo umbral para considerar soluciones tabú
    umbral_costo = 0.9 * min(solucion.costo, mejor_costo)
    for vecino in vecindario:
        if (vecino is not None) and (not tabulists.movimiento_permitido(solucion, vecino)) and (vecino.costo < umbral_costo):
            mejor_solucion = vecino.clonar()
            mejor_solucion.refrescar()
            mejor_costo = vecino.costo
            

    # Actualizar la lista tabú con la mejor solución seleccionada
    tabulists.actualizar(solucion, mejor_solucion, iterador_principal)
    constantes.alfa.actualizar(not mejor_solucion.es_excedida_capacidad_vehiculo())
    constantes.beta.actualizar(not mejor_solucion.proveedor_tiene_desabastecimiento())
    mejor_solucion.refrescar()
    return mejor_solucion


def _crear_n_prima(solucion: Solucion) -> list[Solucion]:
    """
    Crea el vecindario primario (N'(s)) generando variaciones simples sobre la solución actual.

    Args:
        solucion (Solucion): La solución actual.

    Returns:
        list[Solucion]: Lista de soluciones generadas en el vecindario primario.
    """
    vecindario_prima = []
    vecindario_prima.extend(_variante_eliminacion(solucion))
    vecindario_prima.extend(_variante_insercion(solucion))
    vecindario_prima.extend(_variante_mover_visita(solucion))
    vecindario_prima.extend(_variante_intercambiar_visitas(solucion))
    return vecindario_prima


def _crear_n(solucion: Solucion, vecindario_prima: list[Solucion]) -> list[Solucion]:
    """
    Crea el vecindario N(s) a partir del vecindario primario N'(s), aplicando políticas de reabastecimiento.

    Args:
        solucion (Solucion): La solución actual.
        vecindario_prima (list[Solucion]): El vecindario primario generado.

    Returns:
        list[Solucion]: Vecindario final tras aplicar las políticas de reabastecimiento.
    """
    constantes = constantes_contexto.get()
    vecindario = []

    for solucion_prima in vecindario_prima:
        conjunto_A = [cliente for cliente in constantes.clientes if solucion.tiempos_cliente(cliente) != solucion_prima.tiempos_cliente(cliente)]

        while conjunto_A:
            cliente_removido = conjunto_A.pop(randint(0, len(conjunto_A) - 1))

            for t in solucion_prima.tiempos_cliente(cliente_removido):
                for cliente in solucion_prima.rutas[t].clientes:
                    if (cliente.costo_almacenamiento > constantes.proveedor.costo_almacenamiento) or \
                       (solucion_prima.rutas[t].obtener_total_entregado() > constantes.capacidad_vehiculo) or \
                       (solucion_prima.inventario_proveedor[t] < 0):

                        if constantes.politica_reabastecimiento == "OU":
                            solucion_dosprima = solucion_prima.clonar()
                            solucion_dosprima.remover_visita(cliente, t)

                            if solucion_dosprima.es_admisible and solucion_dosprima.costo < solucion_prima.costo:
                                solucion_prima = solucion_dosprima
                                conjunto_A.append(cliente)

                        elif constantes.politica_reabastecimiento == "ML":
                            xjt = solucion_prima.rutas[t].obtener_cantidad_entregada(cliente)
                            niveles_inventario = solucion_prima.inventario_clientes.get(cliente.id, [])
                            niveles_futuros = niveles_inventario[t + 1:] if niveles_inventario else []

                            y = min(xjt, min(niveles_futuros) if niveles_futuros else xjt)

                            solucion_dosprima = solucion_prima.clonar()
                            if y == xjt:
                                solucion_dosprima.rutas[t].remover_visita(cliente)
                            else:
                                solucion_dosprima.rutas[t].quitar_cantidad_cliente(cliente, y)

                            solucion_dosprima.refrescar()

                            if solucion_dosprima.costo < solucion_prima.costo:
                                if not solucion_prima.es_visitado(cliente, t):
                                    conjunto_A.append(cliente)
                                solucion_prima = solucion_dosprima

        if not solucion_prima.es_igual(solucion):
            vecindario.append(solucion_prima.clonar())

    return vecindario


def _variante_eliminacion(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones eliminando visitas de clientes en la solución actual.
    """
    constantes = constantes_contexto.get()
    vecindario_prima = []
    for cliente in constantes.clientes:
        for tiempo in range(constantes.horizonte_tiempo):
            solucion_copy = _eliminar_visita(solucion, cliente, tiempo)
            solucion_copy.refrescar()
            if (solucion_copy.es_admisible and (not solucion.es_igual(solucion_copy))):
                vecindario_prima.append(solucion_copy) 
    return vecindario_prima


def _variante_insercion(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones insertando nuevas visitas a clientes en la solución actual.
    """
    constantes = constantes_contexto.get()
    vecindario_prima = []
    for cliente in constantes.clientes:
        for tiempo in range(constantes.horizonte_tiempo):
            solucion_copy = _insertar_visita(solucion, cliente, tiempo)
            solucion_copy.refrescar()
            if (solucion_copy.es_admisible and (not solucion.es_igual(solucion_copy))):
                vecindario_prima.append(solucion_copy)
    return vecindario_prima


def _variante_mover_visita(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones moviendo visitas de un cliente entre diferentes tiempos de entrega.
    """
    constantes = constantes_contexto.get()
    vecindario_prima = []
    for cliente in constantes.clientes:
        set_t_visitado = solucion.tiempos_cliente(cliente)
        set_t_no_visitado = (set(range(constantes.horizonte_tiempo)) - set(set_t_visitado))
        for t_visitado in set_t_visitado:
            new_solucion = _eliminar_visita(solucion, cliente,t_visitado)
            for t_not_visitado in set_t_no_visitado:
                solucion_copy = _insertar_visita(new_solucion, cliente, t_not_visitado)
                if all(valor >= cliente.nivel_minimo for valor in solucion_copy.inventario_clientes.get(cliente.id, None)) :
                    if(solucion_copy.es_admisible):
                        vecindario_prima.append(solucion_copy)
    return vecindario_prima


def _variante_intercambiar_visitas(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones intercambiando visitas entre dos clientes en diferentes tiempos de entrega.
    """
    constantes = constantes_contexto.get()
    vecindario_prima = []
    for cliente1 in constantes.clientes:
        for cliente2 in list(set(constantes.clientes) -set([cliente1])):
            for iter_t in (set(solucion.tiempos_cliente(cliente1)) - set(solucion.tiempos_cliente(cliente2))):
                for iter_tprima in (set(solucion.tiempos_cliente(cliente2)) - set(solucion.tiempos_cliente(cliente1))):
                    # Remover visitas
                    solucion_copy = solucion.clonar()
                    solucion_copy = _eliminar_visita(solucion_copy, cliente1, iter_t)
                    solucion_copy = _eliminar_visita(solucion_copy, cliente2, iter_tprima)
                    #Añadir nuevas visitas
                    solucion_copy = _insertar_visita(solucion_copy, cliente1, iter_tprima)
                    solucion_copy = _insertar_visita(solucion_copy, cliente2, iter_t)
                    if (solucion_copy.es_admisible and (not solucion.es_igual(solucion_copy))):
                        vecindario_prima.append(solucion_copy)                                  
    return vecindario_prima


def _eliminar_visita(solucion, cliente, tiempo):
    constantes = constantes_contexto.get()
    solucion_prima = solucion.clonar()
    solucion_prima.refrescar()
    tiempos_cliente = solucion_prima.tiempos_cliente(cliente)
    if tiempo in tiempos_cliente:
        # Guardo el indice del tiempo de la eliminación, para despues acceder fácilmente al anterior y al posterior.
        index = tiempos_cliente.index(tiempo)
        # Primero eliminamos al cliente i de la ruta del vehículo en el tiempo t y su predecesor se enlaza con su sucesor.
        cantidad_eliminado = solucion_prima.rutas[tiempo].remover_visita(cliente)
        solucion_prima.refrescar()
        
        if (constantes.politica_reabastecimiento == "OU"):
        # La cantidad entregada al cliente en el tiempo t se transfiere a la visita siguiente (si la hay). 
        # Tal eliminación se realiza solo si no crea un desabastecimiento en el cliente i para mantener la solución admisible.
            # Si no era el último, transfiero la cantidad entregada a la siguiente visita
            if index < len(tiempos_cliente) - 1:
                solucion_prima.rutas[tiempos_cliente[index+1]].agregar_cantidad_cliente(cliente, cantidad_eliminado)
                
        elif (constantes.politica_reabastecimiento == "ML"):
        # Si se genera desabastecimiento en el cliente la eliminación sólo se realiza si puede evitarse aumentando la cantidad entregada
        # en la visita anterior a un valor no mayor que la capacidad máxima Ui. 
            inventarios_cliente = solucion_prima.inventario_clientes.get(cliente.id, None)
            if any([valor < cliente.nivel_minimo for valor in inventarios_cliente]) :
                # Si no era el primero, se intenta aumentar la cantidad entregada a la visita anterior a un valor que no supere Ui
                if index > 0:
                    maximo_permitido = cliente.nivel_maximo - inventarios_cliente[tiempos_cliente[index-1]]
                    solucion_prima.rutas[tiempos_cliente[index-1]].agregar_cantidad_cliente(cliente, maximo_permitido)
        solucion_prima.refrescar()                
    return solucion_prima

def _insertar_visita(solucion, cliente, tiempo):
    constantes = constantes_contexto.get()
    solucion_prima = solucion.clonar()
    solucion_prima.refrescar()
    tiempos_cliente = solucion_prima.tiempos_cliente(cliente)
    if not (tiempo in tiempos_cliente):
        max_permitido =  cliente.nivel_maximo - solucion_prima.rutas[tiempo].obtener_cantidad_entregada(cliente)
        # Añadimos una vista al cliente en el tiempo t usando el método de inserción más barato.
        if constantes.politica_reabastecimiento == "OU":
            # La cantidad entregada se establece como Ui - Iit; La misma cantidad se elimina de la siguiente visita al cliente (si la hay).
            cantidad_entregada = max_permitido      
        elif constantes.politica_reabastecimiento == "ML":
            # La cantidad entregada al cliente en el tiempo t es la mínima entre la cantidad máxima que puede entregarse sin exceder la capacidad 
            # máxima Ui, la capacidad residual del vehículo, y la cantidad disponible en el proveedor. 
            # Si este mínimo es igual a 0, entonces se entrega una cantidad igual a la demanda del cliente, lo que podrá crear desabastecimiento 
            # en el proveedor o una violación de la restricción de capacidad del vehículo, pero la solución seguirá siendo admisible.
            capacidad_residual_vehiculo = constantes.capacidad_vehiculo - solucion_prima.rutas[tiempo].obtener_total_entregado()
            cantidad_entregada = min(max_permitido, capacidad_residual_vehiculo, solucion_prima.inventario_proveedor[tiempo])
            if cantidad_entregada == 0:
                cantidad_entregada = cliente.nivel_demanda
            
        solucion_prima.rutas[tiempo].insertar_visita(cliente, cantidad_entregada, None)
        solucion_prima.refrescar()
    return solucion_prima