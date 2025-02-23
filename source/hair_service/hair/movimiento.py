from modelos.solucion import Solucion
from random import randint
import math

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
    
    mejor_solucion = min(
        (vecino for vecino in vecindario if tabulists.movimiento_permitido(solucion, vecino)), 
        default=solucion.clonar(), 
        key=lambda v: v.costo
    )

    mejor_solucion_no_permitida = min(
        (vecino for vecino in vecindario if not tabulists.movimiento_permitido(solucion, vecino)), 
        default=solucion.clonar(), 
        key=lambda v: v.costo
    )
   
    proximo_salto = iterador_principal + solucion.contexto.jump_iter - (iterador_principal % solucion.contexto.jump_iter)
    jump_iter = solucion.contexto.jump_iter
    factor = (proximo_salto - iterador_principal) / jump_iter  # Normalizar el avance hacia el salto
    multiplicador_tolerancia = 1 + (1 / (1 + math.exp(-12 * (factor - 0.6)))) * 0.3  # Ajuste más fuerte cerca del salto

    umbral_costo = multiplicador_tolerancia * min(solucion.costo, mejor_solucion.costo)
    if mejor_solucion_no_permitida.costo < umbral_costo:
        mejor_solucion = mejor_solucion_no_permitida.clonar()

    # Actualizar la lista tabú con la mejor solución seleccionada
    tabulists.actualizar(solucion, mejor_solucion, iterador_principal)
    solucion.contexto.alfa.actualizar(mejor_solucion.respeta_capacidad_vehiculo())
    solucion.contexto.beta.actualizar(mejor_solucion.proveedor_sin_desabastecimiento())
    print(f"MOVIMIENTO {mejor_solucion}")
    return mejor_solucion

def _crear_vecindario(solucion: Solucion) -> list[Solucion]:
    """
    Construcción del vecindario N(s) mejorado, asegurando adherencia estricta a la teoría.
    """
    contexto = solucion.contexto
    vecindario = []
    L_a, L_r = set(), set()  # Listas tabú de adición y eliminación de visitas

    vecindario_prima = [
        vecino for variante in [
            _variante_eliminacion,
            _variante_insercion,
            _variante_mover_visita,
            _variante_intercambiar_visitas
        ] for vecino in variante(solucion) if vecino.es_admisible
    ]
    
    for solucion_prima in vecindario_prima:
        conjunto_A = [cliente for cliente in contexto.clientes if solucion.tiempos_cliente(cliente) != solucion_prima.tiempos_cliente(cliente)]
        
        while conjunto_A:
            cliente_i = conjunto_A.pop(0)
            
            for t in solucion_prima.tiempos_cliente(cliente_i):
                for cliente_j in solucion_prima.rutas[t].clientes:
                    if t not in solucion_prima.tiempos_cliente(cliente_j):
                        continue  
                    
                    if cliente_j.costo_almacenamiento > contexto.proveedor.costo_almacenamiento or \
                       solucion_prima.rutas[t].obtener_total_entregado() > contexto.capacidad_vehiculo or \
                       solucion_prima.inventario_proveedor[t] < 0:
                        
                        if contexto.politica_reabastecimiento == "OU":
                            if (cliente_j, t) not in L_a:
                                solucion_nueva = solucion_prima.eliminar_visita(cliente_j, t)
                                if solucion_nueva.es_admisible and solucion_nueva.costo < solucion_prima.costo:
                                    solucion_prima = solucion_nueva.clonar()
                                    conjunto_A.append(cliente_j)
                                    L_a.add((cliente_j, t))
                        
                        if contexto.politica_reabastecimiento == "ML":
                            xjt = solucion_prima.rutas[t].obtener_cantidad_entregada(cliente_j)
                            y = min(xjt, min(solucion_prima.inventario_clientes[cliente_j.id][:t], default=xjt))
                            
                            if (cliente_j, t) not in L_r:
                                solucion_nueva = solucion_prima.quitar_cantidad_cliente(cliente_j, t, y)
                                if solucion_nueva.es_admisible and solucion_nueva.costo < solucion_prima.costo:
                                    solucion_prima = solucion_nueva.clonar()
                                    conjunto_A.append(cliente_j)
                                    L_r.add((cliente_j, t))
            
            if contexto.politica_reabastecimiento == "ML":
                for t in solucion_prima.tiempos_cliente(cliente_i):
                    for cliente_j in solucion_prima.rutas[t].clientes:
                        if cliente_j.costo_almacenamiento < contexto.proveedor.costo_almacenamiento and not solucion_prima.rutas[t].es_visitado(cliente_j):
                            y = max([solucion_prima.inventario_clientes[cliente_j.id][t_prima] + solucion_prima.rutas[t_prima].obtener_cantidad_entregada(cliente_j) 
                                for t_prima in range(t, contexto.horizonte_tiempo)], default=0)
                            
                            if (cliente_j, t) not in L_r:
                                solucion_nueva = solucion_prima.insertar_visita(cliente_j, t, y)
                                if solucion_nueva.es_admisible and solucion_nueva.costo < solucion_prima.costo:
                                    solucion_prima = solucion_nueva.clonar()
                                    conjunto_A.append(cliente_j)
                                    L_r.add((cliente_j, t))
        
        if solucion_prima.es_admisible:
            vecindario.append(solucion_prima)
    
    return vecindario


def _variante_eliminacion(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones eliminando visitas de clientes en la solución actual, diferenciando entre ML y OU.
    """
    vecindario_prima = []
    for t, ruta in enumerate(solucion.rutas):
        for cliente in ruta.clientes:
            nueva_solucion = _eliminar_visita(solucion, cliente, t)
            if nueva_solucion.es_admisible:
                vecindario_prima.append(nueva_solucion)
    return vecindario_prima

def _variante_insercion(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones insertando nuevas visitas a clientes en la solución actual, respetando las políticas ML y OU.
    """ 
    vecindario_prima = []
    contexto = solucion.contexto
    for cliente in contexto.clientes:
        for t in set(range(solucion.contexto.horizonte_tiempo)) - set(solucion.tiempos_cliente(cliente)):   
            nueva_solucion = _insertar_visita(solucion, cliente, t)
            if nueva_solucion.es_admisible:
                vecindario_prima.append(nueva_solucion)            
    return vecindario_prima


def _variante_mover_visita(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones moviendo visitas de un cliente entre diferentes tiempos de entrega, 
    diferenciando entre ML y OU.
    """
    vecindario_prima = []
    contexto = solucion.contexto
    
    for cliente in contexto.clientes:
        tiempos_cliente_actual = solucion.tiempos_cliente(cliente)
        posibles_destinos = set(range(contexto.horizonte_tiempo)) - set(tiempos_cliente_actual)
        for t_origen in tiempos_cliente_actual:
            for t_destino in posibles_destinos:
                nueva_solucion = _eliminar_visita(solucion, cliente, t_origen)
                nueva_solucion = _insertar_visita(nueva_solucion, cliente, t_destino)
                if nueva_solucion.es_admisible:
                    vecindario_prima.append(nueva_solucion)
    return vecindario_prima


def _variante_intercambiar_visitas(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones intercambiando visitas entre dos clientes en diferentes tiempos de entrega,
    asegurando que la solución siga siendo admisible y cumpla con las políticas de OU y ML.
    """
    vecindario_prima = []
    clientes = solucion.contexto.clientes

    for cliente1 in clientes:
        for cliente2 in clientes:
            if cliente1 == cliente2:
                continue  # No intercambiar un cliente consigo mismo

            tiempos1 = set(solucion.tiempos_cliente(cliente1))
            tiempos2 = set(solucion.tiempos_cliente(cliente2))
            posibles_tiempos1 = tiempos1 - tiempos2
            posibles_tiempos2 = tiempos2 - tiempos1

            if not posibles_tiempos1 or not posibles_tiempos2:
                continue  # No hay tiempos de intercambio posibles

            for iter_t in posibles_tiempos1:
                for iter_tprima in posibles_tiempos2:
                    nueva_solucion = solucion.clonar()
                    nueva_solucion = _eliminar_visita(nueva_solucion, cliente1, iter_t)
                    if not nueva_solucion.es_admisible:
                        continue  # Si la solución se vuelve inadmisible, no continuar
                    nueva_solucion = _insertar_visita(nueva_solucion, cliente1, iter_tprima)
                    if not nueva_solucion.es_admisible:
                        continue  # Si la solución se vuelve inadmisible, no continuar
                    nueva_solucion = _eliminar_visita(nueva_solucion, cliente2, iter_tprima)
                    if not nueva_solucion.es_admisible:
                        continue  # Si la solución se vuelve inadmisible, no continuar
                    nueva_solucion = _insertar_visita(nueva_solucion, cliente2, iter_t)
                    if nueva_solucion.es_admisible:
                        vecindario_prima.append(nueva_solucion)  # Agregar solo si sigue siendo admisible

    return vecindario_prima

def _eliminar_visita(solucion, cliente, t):
    """
    Elimina una visita a un cliente en un período T asegurando adherencia total a las políticas de OU y ML.
    """
    contexto = solucion.contexto
    ruta = solucion.rutas[t]
    cantidad_transferida = ruta.obtener_cantidad_entregada(cliente)

    nueva_solucion = solucion.eliminar_visita(cliente, t)
    tiempos_cliente = solucion.tiempos_cliente(cliente)
    t_prev = next((t_s for t_s in tiempos_cliente if t_s < t), None)
    t_next = next((t_s for t_s in tiempos_cliente if t_s > t), None)
    inventario_despues = nueva_solucion.inventario_clientes[cliente.id][t]

    if contexto.politica_reabastecimiento == "OU":
        if t_next is not None:
            cantidad_en_siguiente = nueva_solucion.rutas[t_next].obtener_cantidad_entregada(cliente)
            nueva_cantidad_siguiente = min(cliente.nivel_maximo, cantidad_en_siguiente + cantidad_transferida)

            # 🔹 Si la transferencia provoca stockout, cancelar la eliminación
            if nueva_cantidad_siguiente < cliente.nivel_minimo:
                return solucion

            nueva_solucion = nueva_solucion.eliminar_visita(cliente, t_next)
            nueva_solucion = nueva_solucion.insertar_visita(cliente, t_next, nueva_cantidad_siguiente)
        else:
            # 🔹 Si no hay siguiente visita, cancelar la eliminación
            return solucion

    elif contexto.politica_reabastecimiento == "ML":
        if inventario_despues < cliente.nivel_minimo:
            if t_prev is not None:
                cantidad_en_tprev = nueva_solucion.rutas[t_prev].obtener_cantidad_entregada(cliente)
                y = min(nueva_solucion.inventario_clientes[cliente.id][t_next], cantidad_transferida) if t_next else cantidad_transferida
                cantidad_aumentada = min(cliente.nivel_maximo - nueva_solucion.inventario_clientes[cliente.id][t_prev], y)

                # 🔹 Si la cantidad aumentada supera \( U_i \), cancelar la eliminación
                if cantidad_en_tprev + cantidad_aumentada > cliente.nivel_maximo:
                    return solucion

                # 🔹 Aumentamos la entrega en t_prev
                nueva_solucion = nueva_solucion.eliminar_visita(cliente, t_prev)
                nueva_solucion = nueva_solucion.insertar_visita(cliente, t_prev, cantidad_en_tprev + cantidad_aumentada)

            elif t_next is not None:
                cantidad_reubicada = max(0, cliente.nivel_minimo - nueva_solucion.inventario_clientes[cliente.id][t_next - 1])

                # 🔹 Si la reubicación supera \( U_i \), cancelar la eliminación
                if cantidad_reubicada > cliente.nivel_maximo:
                    return solucion

                nueva_solucion = nueva_solucion.insertar_visita(cliente, t_next, cantidad_reubicada)

            else:
                # 🔹 Si no hay t_prev ni t_next, cancelar la eliminación
                return solucion

    return nueva_solucion


def _insertar_visita(solucion, cliente, t):
    """
    Inserta una visita asegurando adherencia a las políticas de OU y ML.
    """
    contexto = solucion.contexto
    cantidad_entregada = 0  

    if contexto.politica_reabastecimiento == "OU":
        cantidad_entregada = max(0, cliente.nivel_maximo - solucion.inventario_clientes[cliente.id][t - 1])
        t_next = next((t_s for t_s in solucion.tiempos_cliente(cliente) if t_s > t), None)

        if t_next is not None:
            cantidad_en_siguiente = solucion.rutas[t_next].obtener_cantidad_entregada(cliente)
            nueva_cantidad_siguiente = max(0, cantidad_en_siguiente - cantidad_entregada)

            # 🔹 Si la reducción provoca un stockout, cancelar la inserción
            if nueva_cantidad_siguiente < cliente.nivel_minimo:
                return solucion

            solucion = solucion.eliminar_visita(cliente, t_next)
            solucion = solucion.insertar_visita(cliente, t_next, nueva_cantidad_siguiente)

    elif contexto.politica_reabastecimiento == "ML":
        cantidad_entregada = min(
            max(0, cliente.nivel_maximo - solucion.inventario_clientes[cliente.id][t] + cliente.nivel_demanda),
            max(0, contexto.capacidad_vehiculo - solucion.rutas[t].obtener_total_entregado()),
            solucion.inventario_proveedor[t]
        )

        # 🔹 Si no se puede entregar nada, intentar r_it (demanda mínima)
        if cantidad_entregada == 0:
            cantidad_entregada = cliente.nivel_demanda

        # 🔹 Validación final: No exceder \( U_i \)
        if cantidad_entregada > cliente.nivel_maximo:
            return solucion

    return solucion.insertar_visita(cliente, t, cantidad_entregada)
