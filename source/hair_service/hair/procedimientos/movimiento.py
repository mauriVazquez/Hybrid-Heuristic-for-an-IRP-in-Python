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
    mejor_costo = float("inf")

    # Buscar la mejor solución permitida por la lista tabú
    for vecino in vecindario:
        if tabulists.movimiento_permitido(solucion, vecino) and vecino.costo < mejor_costo:
            mejor_solucion = vecino.clonar()
            mejor_costo = vecino.costo

    # Ajustar el costo umbral para considerar soluciones tabú
    umbral_costo = 0.9 * min(solucion.costo, mejor_costo)
    for vecino in vecindario:
        if not tabulists.movimiento_permitido(solucion, vecino) and vecino.costo < umbral_costo:
            mejor_solucion = vecino.clonar()
            mejor_costo = vecino.costo


    # Refrescar la solución antes de devolverla
    mejor_solucion.refrescar()
    
    # Actualizar la lista tabú con la mejor solución seleccionada
    tabulists.actualizar(solucion, mejor_solucion, iterador_principal)
    constantes.alfa.actualizar(mejor_solucion.es_excedida_capacidad_vehiculo() == False)
    constantes.beta.actualizar(mejor_solucion.proveedor_tiene_desabastecimiento() == False)
    
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
        conjunto_A = [cliente for cliente in constantes.clientes if solucion.T(cliente) != solucion_prima.T(cliente)]

        while conjunto_A:
            cliente_removido = conjunto_A.pop(randint(0, len(conjunto_A) - 1))

            for t in solucion_prima.T(cliente_removido):
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
        for t in solucion.T(cliente):
            solucion_copy = solucion.clonar()
            solucion_copy.remover_visita(cliente, t)
            if (solucion_copy.es_admisible and (not solucion.es_igual(solucion_copy))):
                vecindario_prima.append(solucion_copy)
    return vecindario_prima


def _variante_insercion(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones insertando nuevas visitas a clientes en la solución actual.
    """
    constantes = constantes_contexto.get()
    vecindario_prima = []
    for t in range(len(solucion.rutas)):
        for cliente in constantes.clientes:
            if (not solucion.es_visitado(cliente, t)):
                solucion_copy = solucion.clonar()
                solucion_copy.insertar_visita(cliente, t)
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
        set_t_visitado = solucion.T(cliente)
        set_t_no_visitado = (set(range(constantes.horizonte_tiempo)) - set(set_t_visitado))
        for t_visitado in set_t_visitado:
            new_solucion = solucion.clonar()
            new_solucion.rutas[t_visitado].remover_visita(cliente)
            for t_not_visitado in set_t_no_visitado:
                solucion_copy = new_solucion.clonar()
                solucion_copy.insertar_visita(cliente, t_not_visitado)
                if (solucion_copy.es_admisible and (not solucion.es_igual(solucion_copy))):
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
            for iter_t in (set(solucion.T(cliente1)) - set(solucion.T(cliente2))):
                for iter_tprima in (set(solucion.T(cliente2)) - set(solucion.T(cliente1))):
                    solucion_copy = solucion.clonar()
                    # Remover visitas
                    solucion_copy.remover_visita(cliente1, iter_t)
                    solucion_copy.remover_visita(cliente2, iter_tprima)
                    #Añadir nuevas visitas
                    solucion_copy.insertar_visita(cliente1,iter_tprima)
                    solucion_copy.insertar_visita(cliente2,iter_t)
                    if (solucion_copy.es_admisible and (not solucion.es_igual(solucion_copy))):
                        vecindario_prima.append(solucion_copy)                                           
    return vecindario_prima
