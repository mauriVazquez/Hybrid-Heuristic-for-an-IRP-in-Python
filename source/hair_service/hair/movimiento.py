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
    multiplicador_tolerancia = 1 + (1 / (1 + math.exp(-10 * ((proximo_salto - iterador_principal) / solucion.contexto.jump_iter - 0.7)))) * 0.2


    umbral_costo = multiplicador_tolerancia * min(solucion.costo, mejor_solucion.costo)
    if mejor_solucion_no_permitida.costo < umbral_costo:
        mejor_solucion = mejor_solucion_no_permitida.clonar()

    # Actualizar la lista tabú con la mejor solución seleccionada
    tabulists.actualizar(solucion, mejor_solucion, iterador_principal)
    solucion.contexto.alfa.actualizar(mejor_solucion.respeta_capacidad_vehiculo())
    solucion.contexto.beta.actualizar(mejor_solucion.proveedor_sin_desabastecimiento())
    # print(f"MOVIMIENTO {mejor_solucion}")
    return mejor_solucion

def _crear_vecindario(solucion: Solucion) -> list[Solucion]:
    """
    Construcción del vecindario N(s) basada en el algoritmo de la imagen.
    Se exploran los cambios en la solución mediante las políticas OU y ML.
    """
    contexto = solucion.contexto
    vecindario = []
   
    # Crear el vecindario primario (N'(s))
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
        
        while len(conjunto_A) > 0:
            cliente_i = conjunto_A.pop(0)
            
            for t in solucion_prima.tiempos_cliente(cliente_i):
                for cliente_j in solucion_prima.rutas[t].clientes:
                    if cliente_j.costo_almacenamiento > contexto.proveedor.costo_almacenamiento or solucion_prima.rutas[t].obtener_total_entregado() > contexto.capacidad_vehiculo or solucion_prima.inventario_proveedor[t] < 0:
                        
                        # OU policy: Remover la visita a j en t
                        solucion_nueva = solucion_prima.eliminar_visita(cliente_j, t)
                        if solucion_nueva.es_admisible and solucion_nueva.costo < solucion_prima.costo:
                            solucion_prima = solucion_nueva.clonar()
                            conjunto_A.append(cliente_j)
                        
                        # ML policy: Reducir entrega a j en t
                        xjt = solucion_prima.rutas[t].obtener_cantidad_entregada(cliente_j)
                        y = min(xjt, min(solucion_prima.inventario_clientes[cliente_j.id][:t], default= xjt))
                        solucion_nueva = solucion_prima.quitar_cantidad_cliente(cliente_j, t, y)
                        if solucion_nueva.es_admisible and solucion_nueva.costo < solucion_prima.costo:
                            solucion_prima = solucion_nueva.clonar()
                            conjunto_A.append(cliente_j)
            
            # ML policy: Aumentar entrega a clientes con h < h0
            for t in solucion_prima.tiempos_cliente(cliente_i):
                for cliente_j in solucion_prima.rutas[t].clientes:
                    if cliente_j.costo_almacenamiento < contexto.proveedor.costo_almacenamiento and not solucion_prima.rutas[t].es_visitado(cliente_j):
                        y = max([solucion_prima.inventario_clientes[cliente_j.id][t_prima] + solucion_prima.rutas[t_prima].obtener_cantidad_entregada(cliente_j) 
                            for t_prima in range(t, contexto.horizonte_tiempo)], default=0)
                        solucion_nueva = solucion_prima.insertar_visita(cliente_j, t, y)
                        if solucion_nueva.es_admisible and solucion_nueva.costo < solucion_prima.costo:
                            solucion_prima = solucion_nueva.clonar()
                            conjunto_A.append(cliente_j)
        
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
    diferenciando entre ML y OU.
    """
    vecindario_prima = []
    clientes = solucion.contexto.clientes
    
    for cliente1 in clientes:
        for cliente2 in clientes:
            if cliente1 == cliente2:
                continue  
            tiempos1 = set(solucion.tiempos_cliente(cliente1))
            tiempos2 = set(solucion.tiempos_cliente(cliente2))
            posibles_tiempos1 = tiempos1 - tiempos2
            posibles_tiempos2 = tiempos2 - tiempos1

            if (not posibles_tiempos1) or (not posibles_tiempos2):
                continue  # No hay tiempos de intercambio posibles

            for iter_t in posibles_tiempos1:  
                for iter_tprima in posibles_tiempos2:  
                    nueva_solucion = _eliminar_visita(solucion, cliente1, iter_t)
                    nueva_solucion = _insertar_visita(nueva_solucion, cliente1, iter_tprima)
                    if any(I < cliente1.nivel_minimo for I in nueva_solucion._obtener_niveles_inventario_cliente(cliente1)):
                        continue
                    nueva_solucion = _eliminar_visita(nueva_solucion, cliente2, iter_tprima)
                    nueva_solucion = _insertar_visita(nueva_solucion, cliente2, iter_t)

                    # Verificar si la solución sigue siendo admisible después del intercambio
                    if nueva_solucion.es_admisible:
                        vecindario_prima.append(nueva_solucion)
    return vecindario_prima

def _eliminar_visita(solucion, cliente, t):
    contexto = solucion.contexto
    ruta = solucion.rutas[t]
    # Obtener la cantidad antes de eliminar
    cantidad_transferida = ruta.obtener_cantidad_entregada(cliente)
    nueva_solucion = solucion.eliminar_visita(cliente, t)

    if contexto.politica_reabastecimiento == "OU":
        # Verificar si la eliminación en t no genera stockout antes de transferir a t'
        siguiente_t = next((t_s for t_s in solucion.tiempos_cliente(cliente) if t_s > t), None)
        if siguiente_t and nueva_solucion.rutas:
            nueva_solucion = nueva_solucion.insertar_visita(cliente, siguiente_t, cantidad_transferida)
            
    elif contexto.politica_reabastecimiento == "ML":
        if not nueva_solucion.es_admisible:
            # Evitar stockout aumentando entrega en la visita anterior
            t_anterior = max((t_p for t_p in solucion.tiempos_cliente(cliente) if t_p < t), default=None)
            if t_anterior:
                xjt = cantidad_transferida  # Usar la cantidad antes de eliminar
                niveles_futuros = [cliente.nivel_maximo - nueva_solucion.inventario_clientes[cliente.id][t_prima] for t_prima in range (t + 1, contexto.horizonte_tiempo + 1)] or [0]
                y = min(xjt, min(niveles_futuros))

                if y < xjt and ((nueva_solucion.inventario_clientes[cliente.id][t_anterior] + (xjt - y)) <= cliente.nivel_maximo) and nueva_solucion.rutas:
                    nueva_solucion = nueva_solucion.insertar_visita(cliente, t_anterior, xjt - y)
    return nueva_solucion

def _insertar_visita(solucion, cliente, t):
    contexto = solucion.contexto
    if contexto.politica_reabastecimiento == "OU":
        nivel_anterior = solucion.inventario_clientes[cliente.id][t-1] if t > 0 else cliente.nivel_almacenamiento 
        cantidad_entregada = cliente.nivel_maximo - nivel_anterior + cliente.nivel_demanda
        tiempos_cliente = solucion.tiempos_cliente(cliente)
        siguiente_t = next((t_s for t_s in tiempos_cliente if t_s > t), None)
    elif contexto.politica_reabastecimiento == "ML":
        cantidad_entregada = min(
            max(0, cliente.nivel_maximo - solucion.inventario_clientes[cliente.id][t]),
            max(0, contexto.capacidad_vehiculo - solucion.rutas[t].obtener_total_entregado()),
            solucion.inventario_proveedor[t]
        )

        # Si la cantidad es 0, forzar la entrega del nivel de demanda
        if cantidad_entregada == 0:
            cantidad_entregada = cliente.nivel_demanda 
            
    nueva_solucion = solucion.insertar_visita(cliente, t, cantidad_entregada)

    # En OU, siempre restar la cantidad en la siguiente visita (si existe)
    if contexto.politica_reabastecimiento == "OU" and (siguiente_t is not None):
        cantidad_siguiente = nueva_solucion.rutas[siguiente_t].obtener_cantidad_entregada(cliente)

        if cantidad_entregada >= cantidad_siguiente:
            # Si la cantidad en t' se vuelve 0, eliminar la visita en t'
            nueva_solucion = nueva_solucion.eliminar_visita(cliente, siguiente_t)
        else:
            # Reducir la cantidad en t' normalmente
            nueva_solucion = solucion.quitar_cantidad_cliente(cliente, siguiente_t, cantidad_entregada)
    return nueva_solucion