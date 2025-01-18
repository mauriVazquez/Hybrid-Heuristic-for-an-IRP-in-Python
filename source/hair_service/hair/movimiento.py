from modelos.solucion import Solucion
from random import randint
from hair.contexto_file import contexto_contexto

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
    contexto = contexto_contexto.get()
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
    umbral_costo = 0.8 * mejor_costo
    for vecino in vecindario:
        if ((vecino is not None) and (not tabulists.movimiento_permitido(solucion, vecino)) and (vecino.costo < umbral_costo)) or mejor_costo == float("inf"):
            mejor_solucion = vecino.clonar()
            mejor_solucion.refrescar()
            mejor_costo = vecino.costo
            

    # Actualizar la lista tabú con la mejor solución seleccionada
    mejor_solucion.refrescar()
    tabulists.actualizar(solucion, mejor_solucion, iterador_principal)
    contexto.alfa.actualizar(not mejor_solucion.es_excedida_capacidad_vehiculo())
    contexto.beta.actualizar(not mejor_solucion.proveedor_tiene_desabastecimiento())
    # print(f"MOVIMIENTO {mejor_solucion}")
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
    contexto = contexto_contexto.get()
    vecindario = []

    for solucion_prima in vecindario_prima:
        conjunto_A = [cliente for cliente in contexto.clientes if solucion.tiempos_cliente(cliente) != solucion_prima.tiempos_cliente(cliente)]

        while conjunto_A:
            cliente_removido = conjunto_A.pop(randint(0, len(conjunto_A) - 1))

            for t in solucion_prima.tiempos_cliente(cliente_removido):
                for cliente in solucion_prima.rutas[t].clientes:
                    if (cliente.costo_almacenamiento > contexto.proveedor.costo_almacenamiento) or \
                       (solucion_prima.rutas[t].obtener_total_entregado() > contexto.capacidad_vehiculo) or \
                       (solucion_prima.inventario_proveedor[t] < 0):

                        if contexto.politica_reabastecimiento == "OU":
                            solucion_dosprima = solucion_prima.clonar()
                            solucion_dosprima.eliminar_visita(cliente, t)

                            if solucion_dosprima.es_admisible and solucion_dosprima.costo < solucion_prima.costo:
                                solucion_prima = solucion_dosprima
                                conjunto_A.append(cliente)

                        elif contexto.politica_reabastecimiento == "ML":
                            xjt = solucion_prima.rutas[t].obtener_cantidad_entregada(cliente)
                            niveles_inventario = solucion_prima.inventario_clientes.get(cliente.id, [])
                            niveles_futuros = niveles_inventario[t + 1:] if niveles_inventario else []

                            y = min(xjt, min(niveles_futuros) if niveles_futuros else xjt)

                            solucion_dosprima = solucion_prima.clonar()
                            if y == xjt:
                                solucion_dosprima.rutas[t].eliminar_visita(cliente)
                            else:
                                solucion_dosprima.rutas[t].quitar_cantidad_cliente(cliente, y)

                            solucion_dosprima.refrescar()

                            if solucion_dosprima.costo < solucion_prima.costo:
                                if not solucion_prima.rutas[t].es_visitado(cliente):
                                    conjunto_A.append(cliente)
                                solucion_prima = solucion_dosprima

        if not solucion_prima.es_igual(solucion):
            vecindario.append(solucion_prima.clonar())

    return vecindario


def _variante_eliminacion(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones eliminando visitas de clientes en la solución actual.
    """
    vecindario_prima = []
    for t, ruta in enumerate(solucion.rutas):
        for cliente in ruta.clientes:
            solucion_copy = _eliminar_visita(solucion, cliente, t)
            if solucion_copy is not None:
                solucion_copy.refrescar()
                vecindario_prima.append(solucion_copy) 
    return vecindario_prima


def _variante_insercion(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones insertando nuevas visitas a clientes en la solución actual.
    """
    contexto = contexto_contexto.get()
    vecindario_prima = []
    for cliente in contexto.clientes:
        tiempos_no_visitados = (set(range(contexto.horizonte_tiempo)) - set(solucion.tiempos_cliente(cliente)))
        for tiempo in tiempos_no_visitados:
            solucion_copy = _insertar_visita(solucion, cliente, tiempo)
            if solucion_copy is not None:
                solucion_copy.refrescar()
                vecindario_prima.append(solucion_copy)
    return vecindario_prima


def _variante_mover_visita(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones moviendo visitas de un cliente entre diferentes tiempos de entrega.
    """
    contexto = contexto_contexto.get()
    vecindario_prima = []
    for cliente in contexto.clientes:
        set_t_visitado = solucion.tiempos_cliente(cliente)
        set_t_no_visitado = (set(range(contexto.horizonte_tiempo)) - set(set_t_visitado))
        for t_visitado in set_t_visitado:
            new_solucion = _eliminar_visita(solucion, cliente,t_visitado)
            if new_solucion is not None:
                new_solucion.refrescar()
                for t_not_visitado in set_t_no_visitado:
                    solucion_copy = _insertar_visita(new_solucion, cliente, t_not_visitado)
                    if solucion_copy is not None:
                        solucion_copy.refrescar()
                        vecindario_prima.append(solucion_copy)
    return vecindario_prima


def _variante_intercambiar_visitas(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones intercambiando visitas entre dos clientes en diferentes tiempos de entrega.
    """
    contexto = contexto_contexto.get()
    vecindario_prima = []
    for cliente1 in contexto.clientes:
        for cliente2 in list(set(contexto.clientes) -set([cliente1])):
            for iter_t in (set(solucion.tiempos_cliente(cliente1)) - set(solucion.tiempos_cliente(cliente2))):
                for iter_tprima in (set(solucion.tiempos_cliente(cliente2)) - set(solucion.tiempos_cliente(cliente1))):
                    # Remover visitas
                    solucion_copy = solucion.clonar()
                    solucion_copy = _insertar_visita(solucion_copy, cliente1, iter_tprima)
                    solucion_copy = _insertar_visita(solucion_copy, cliente2, iter_t)
                    solucion_copy = _eliminar_visita(solucion_copy, cliente1, iter_t)
                    if (solucion_copy is not None):
                        solucion_copy.refrescar()
                        solucion_copy = _eliminar_visita(solucion_copy, cliente2, iter_tprima)
                        if (solucion_copy is not None):
                            solucion_copy.refrescar()
                            if (solucion_copy.es_admisible):
                                vecindario_prima.append(solucion_copy)   
    return vecindario_prima


def _eliminar_visita(solucion, cliente, tiempo):
    contexto = contexto_contexto.get()
    solucion_prima = solucion.clonar()
    solucion_prima.refrescar()
    tiempos_cliente = solucion_prima.tiempos_cliente(cliente)
    
    if tiempo in tiempos_cliente:
        # Guardo el índice del tiempo de la eliminación, para después acceder fácilmente al anterior y al posterior.
        index = tiempos_cliente.index(tiempo)
        
        # Primero eliminamos al cliente i de la ruta del vehículo en el tiempo t
        cantidad_eliminada = solucion_prima.rutas[tiempo].eliminar_visita(cliente)
        solucion_prima.refrescar()
        nuevo_inventario_cliente = solucion_prima.inventario_clientes.get(cliente.id, None)
        
        if contexto.politica_reabastecimiento == "OU":
            # Verifico si hay una próxima visita para transferir la cantidad eliminada
            if index < len(tiempos_cliente) - 1:
                tiempo_siguiente = tiempos_cliente[index + 1]
                
                # Calculo la cantidad que puedo entregar sin exceder la capacidad máxima, priorizando entregar la cantidad eliminada en t
                cantidad_a_entregar = min(cantidad_eliminada, cliente.nivel_maximo - nuevo_inventario_cliente[tiempo_siguiente])

                # Realizo la transferencia
                solucion_prima.rutas[tiempo_siguiente].agregar_cantidad_cliente(cliente, cantidad_a_entregar)
                solucion_prima.refrescar()

            # Verifico si la solución es admisible tras la transferencia
            if not solucion_prima.es_admisible:
                return None  # No es admisible, descarto la eliminación
        
        elif contexto.politica_reabastecimiento == "ML":
            # En la política ML, si hay desabastecimiento:
            if any([valor < cliente.nivel_minimo for valor in nuevo_inventario_cliente]):
                # Si no era la primera visita, intento incrementar la cantidad en la visita previa
                if index > 0:
                    x = cantidad_eliminada
                    y = min(nuevo_inventario_cliente[tiempo + 1:])
                    tiempo_anterior = tiempos_cliente[index - 1]

                    if (y < x):
                        incremento = x - y
                        if nuevo_inventario_cliente[tiempo_anterior] + incremento <= cliente.nivel_maximo:
                            solucion_prima.rutas[tiempo_anterior].agregar_cantidad_cliente(cliente, incremento)
                            solucion_prima.refrescar()
                        else:
                            return None  # No es posible evitar el desabastecimiento, descarto la eliminación
                else: 
                    # No puede evitar desabastecimiento
                    return None
    return solucion_prima



def _insertar_visita(solucion, cliente, tiempo):
    """
    Inserta una visita al cliente en el tiempo especificado siguiendo las políticas OU y ML.

    Args:
        solucion (Solucion): La solución actual.
        cliente (Cliente): El cliente al que se quiere insertar la visita.
        tiempo (int): El tiempo en el que se inserta la visita.

    Returns:
        Solucion: Una nueva solución con la visita insertada, o None si no es admisible.
    """
    contexto = contexto_contexto.get()
    solucion_prima = solucion.clonar()
    solucion_prima.refrescar()
    tiempos_cliente = solucion_prima.tiempos_cliente(cliente)
    
    if tiempo not in tiempos_cliente:
        # Calculamos la cantidad máxima permitida
        if contexto.politica_reabastecimiento == "OU":
            entrega = cliente.nivel_maximo - solucion_prima.inventario_clientes.get(cliente.id, None)[tiempo]
        elif contexto.politica_reabastecimiento == "ML":
            entrega = min(
                cliente.nivel_maximo - solucion_prima.inventario_clientes.get(cliente.id, None)[tiempo], 
                contexto.capacidad_vehiculo - solucion_prima.rutas[tiempo].obtener_total_entregado(), 
                solucion_prima.inventario_proveedor[tiempo]
            )
            if entrega <= 0:
                entrega = cliente.nivel_demanda
                
        # Inserción de la visita en la ruta
        solucion_prima.rutas[tiempo].insertar_visita(cliente, entrega, None)
        solucion_prima.refrescar()
        
        if contexto.politica_reabastecimiento == "OU":
            nuevos_tiempos_cliente = solucion_prima.tiempos_cliente(cliente)
            index = nuevos_tiempos_cliente.index(tiempo)
            if index < len(nuevos_tiempos_cliente) - 1:
                solucion_prima.rutas[nuevos_tiempos_cliente[index + 1]].quitar_cantidad_cliente(cliente, entrega)
                solucion_prima.refrescar()        
    return solucion_prima
