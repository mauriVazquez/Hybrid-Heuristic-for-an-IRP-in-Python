from modelos.solucion import Solucion
from random import randint
from modelos.contexto_file import contexto_ejecucion

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
    # Crear el vecindario completo (N(s))
    vecindario = _crear_vecindario(solucion)
    
    # Inicializar la solución respuesta
    mejor_solucion = solucion.clonar()
    mejor_costo = float("inf")

    # Buscar la mejor solución permitida por la lista tabú
    for vecino in vecindario:
        if tabulists.movimiento_permitido(solucion, vecino) and (vecino.costo < mejor_costo):
            mejor_solucion = vecino.clonar()
            mejor_costo = vecino.costo

    # Ajustar el costo umbral para considerar soluciones tabú
    umbral_costo = solucion.contexto.multiplicador_tolerancia * min(mejor_costo, solucion.costo)
    for vecino in vecindario:
        if ((not tabulists.movimiento_permitido(solucion, vecino)) and (vecino.costo < umbral_costo)):
            mejor_solucion = vecino.clonar()
            mejor_costo = vecino.costo

    # Actualizar la lista tabú con la mejor solución seleccionada
    tabulists.actualizar(solucion, mejor_solucion, iterador_principal)
    
    solucion.contexto.alfa.actualizar(mejor_solucion.respeta_capacidad_vehiculo())
    solucion.contexto.beta.actualizar(mejor_solucion.proveedor_sin_desabastecimiento())
    # print(f"MOVIMIENTO {mejor_solucion}")

    return mejor_solucion


def _crear_vecindario(solucion: Solucion) -> list[Solucion]:
    """
    Crea el vecindario N(s). Primero crea el vecindario primario N'(s), y luego N(s) aplicando políticas de reabastecimiento.

    Args:
        solucion (Solucion): La solución actual.

    Returns:
        list[Solucion]: Vecindario final tras aplicar las políticas de reabastecimiento.
    """
    contexto = solucion.contexto

    # Crear el vecindario primario (N'(s)) y eliminar soluciones duplicadas
    vecindario_prima = list({vecino for variante in [
        _variante_eliminacion,
        _variante_insercion,
        _variante_mover_visita,
        _variante_intercambiar_visitas
        ] for vecino in variante(solucion)})

    vecindario = []
    
    for solucion_prima in vecindario_prima:
        conjunto_A = [cliente for cliente in contexto.clientes if solucion.tiempos_cliente(cliente) != solucion_prima.tiempos_cliente(cliente)]

        # Si `conjunto_A` está vacío, evitar el bucle innecesario
        if not conjunto_A:
            continue  

        iteraciones = 0
        max_iteraciones = 20  # Evita ciclos infinitos

        while conjunto_A and iteraciones < max_iteraciones:
            iteraciones += 1
            cliente_removido = conjunto_A.pop(randint(0, len(conjunto_A) - 1))

            for t in solucion_prima.tiempos_cliente(cliente_removido):
                if not solucion_prima.rutas[t].clientes:  # Evita iterar sobre listas vacías
                    continue

                for cliente in solucion_prima.rutas[t].clientes:
                    if (cliente.costo_almacenamiento > contexto.proveedor.costo_almacenamiento) or \
                       (solucion_prima.rutas[t].obtener_total_entregado() > contexto.capacidad_vehiculo) or \
                       (solucion_prima.inventario_proveedor[t] < 0):

                        solucion_dosprima = solucion_prima.clonar()

                        if contexto.politica_reabastecimiento == "OU":
                            solucion_dosprima.eliminar_visita(cliente, t)

                        elif contexto.politica_reabastecimiento == "ML":
                            xjt = solucion_prima.rutas[t].obtener_cantidad_entregada(cliente)
                            niveles_inventario = solucion_prima.inventario_clientes[cliente.id]                            
                            niveles_futuros = niveles_inventario[t + 1:] if niveles_inventario else []

                            y = min(xjt, min(niveles_futuros) if niveles_futuros else xjt)

                            if y == xjt:
                                solucion_dosprima.rutas[t].eliminar_visita(cliente)
                            else:
                                solucion_dosprima.rutas[t].quitar_cantidad_cliente(cliente, y)

                            solucion_dosprima.refrescar()

                        # Solo actualizar si la solución mejora en al menos un 1%
                        if solucion_dosprima.es_admisible() and solucion_dosprima.costo < solucion_prima.costo * 0.99:
                            if not solucion_prima.rutas[t].es_visitado(cliente):
                                conjunto_A.append(cliente)
                            solucion_prima = solucion_dosprima

        # Permitir pequeñas diferencias en el costo para no descartar soluciones casi óptimas
        if not solucion_prima.es_igual(solucion) or abs(solucion_prima.costo - solucion.costo) > 0.01 * solucion.costo:
            vecindario.append(solucion_prima.clonar())
    return vecindario


def _variante_eliminacion(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones eliminando visitas de clientes en la solución actual.
    """
    vecindario_prima = []
    for t, ruta in enumerate(solucion.rutas):
        for cliente in ruta.clientes:
            if len(ruta.clientes) > 1:  # Evitar rutas vacías
                solucion_copy = solucion.clonar()
                solucion_copy.eliminar_visita(cliente, t)
                if solucion_copy.es_admisible():
                    vecindario_prima.append(solucion_copy)
    return vecindario_prima

def _variante_insercion(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones insertando nuevas visitas a clientes en la solución actual.
    """
    vecindario_prima = []
    for t in range(solucion.contexto.horizonte_tiempo):
        for cliente in solucion.contexto.clientes:
            if cliente not in solucion.rutas[t].clientes:
                solucion_copy = solucion.clonar()
                solucion_copy.insertar_visita(cliente, t)
                if solucion_copy.es_admisible():
                    vecindario_prima.append(solucion_copy)
    return vecindario_prima


def _variante_mover_visita(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones moviendo visitas de un cliente entre diferentes tiempos de entrega.
    """
    vecindario_prima = []
    for cliente in solucion.contexto.clientes:
        tiempos_cliente = solucion.tiempos_cliente(cliente)
        tiempos_disponibles = set(range(solucion.contexto.horizonte_tiempo)) - set(tiempos_cliente)

        for t_origen in tiempos_cliente:
            for t_destino in tiempos_disponibles:
                solucion_copy = solucion.clonar()
                solucion_copy.eliminar_visita(cliente, t_origen)
                solucion_copy.insertar_visita(cliente, t_destino)
                if solucion_copy.es_admisible():
                    vecindario_prima.append(solucion_copy)
    return vecindario_prima


def _variante_intercambiar_visitas(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones intercambiando visitas entre dos clientes en diferentes tiempos de entrega.
    """
    vecindario_prima = []
    clientes = solucion.contexto.clientes
    tiempos_cliente = {cliente.id: set(solucion.tiempos_cliente(cliente)) for cliente in clientes}

    for cliente1 in clientes:
        for cliente2 in list(set(clientes) - {cliente1}):  # Se asegura que no haya problemas de conversión de tipos
            if not tiempos_cliente[cliente1.id] or not tiempos_cliente[cliente2.id]:  
                continue  # Si alguno de los clientes no tiene tiempos asignados, no se puede intercambiar

            for iter_t in tiempos_cliente[cliente1.id] - tiempos_cliente[cliente2.id]:  
                solucion_copy = solucion.clonar()
                solucion_copy.eliminar_visita(cliente1, iter_t)
                solucion_copy.insertar_visita(cliente2, iter_t)

                for iter_tprima in tiempos_cliente[cliente2.id] - tiempos_cliente[cliente1.id]:  
                    solucion_copy.eliminar_visita(cliente2, iter_tprima)
                    solucion_copy.insertar_visita(cliente1, iter_tprima)

                    if solucion_copy.es_admisible():  # Solo agregamos soluciones válidas
                        vecindario_prima.append(solucion_copy.clonar())  # Guardamos una copia para evitar modificaciones no deseadas

    return vecindario_prima

