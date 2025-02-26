from modelos.solucion import Solucion
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
    vecindario = _crear_vecindario(solucion)

    mejor_solucion = min(
        (vecino for vecino in vecindario if tabulists.movimiento_permitido(solucion, vecino) ), 
        default=solucion.clonar(), 
        key=lambda v: v.costo
    )

    mejor_solucion_no_permitida = min(
        (vecino for vecino in vecindario if not tabulists.movimiento_permitido(solucion, vecino)), 
        default=solucion.clonar(), 
        key=lambda v: v.costo
    )

    umbral_costo = 0.97 * mejor_solucion.costo
    if mejor_solucion_no_permitida.costo < umbral_costo:
        mejor_solucion = mejor_solucion_no_permitida.clonar()

    tabulists.actualizar(solucion, mejor_solucion, iterador_principal)
    solucion.contexto.alfa.actualizar(mejor_solucion.respeta_capacidad_vehiculo())
    solucion.contexto.beta.actualizar(mejor_solucion.proveedor_sin_desabastecimiento())
    return mejor_solucion

def _crear_vecindario(in_solucion: Solucion) -> list[Solucion]:
    solucion = in_solucion.clonar()
    contexto = solucion.contexto
    vecindario = []

    vecindario_prima = [
        vecino for variante in [
            _variante_eliminacion,
            _variante_insercion,
            _variante_mover_visita,
            _variante_intercambiar_visitas
        ] for vecino in variante(solucion)
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
                            solucion_nueva = _eliminar_visita(solucion_prima, cliente_j, t)
                            if solucion_nueva.es_admisible and solucion_nueva.costo < solucion_prima.costo:
                                solucion_prima = solucion_nueva.clonar()
                                conjunto_A.append(cliente_j)
                       
                        if contexto.politica_reabastecimiento == "ML":
                            xjt = solucion_prima.rutas[t].obtener_cantidad_entregada(cliente_j)
                            y = min(xjt, min(solucion_prima.inventario_clientes[cliente_j.id][t+1:], default=xjt))
                            if y == xjt:
                                solucion_nueva = solucion_prima.quitar_cantidad_cliente(cliente_j, t, y)
                            else:
                                solucion_nueva = solucion_prima.eliminar_visita(cliente_j, t)
                                
                            if solucion_nueva.es_admisible and solucion_nueva.costo < solucion_prima.costo:
                                solucion_prima = solucion_nueva.clonar()
                                if not solucion_prima.rutas[t].es_visitado(cliente_j):
                                    conjunto_A.append(cliente_j)

            if contexto.politica_reabastecimiento == "ML":
                for t in solucion_prima.tiempos_cliente(cliente_i):
                    for cliente_j in solucion_prima.rutas[t].clientes:
                        if cliente_j.costo_almacenamiento < contexto.proveedor.costo_almacenamiento:
                            y = max([
                                solucion_prima.inventario_clientes[cliente_j.id][t_futuro] +
                                solucion_prima.rutas[t_futuro].obtener_cantidad_entregada(cliente_j)
                                for t_futuro in range(t + 1, contexto.horizonte_tiempo)
                            ], default = 0)
                            solucion_nueva = solucion_prima.agregar_cantidad_cliente(cliente_j, t, cliente_j.nivel_maximo - y)
                            if solucion_nueva.costo < solucion_prima.costo:
                                solucion_prima = solucion_nueva.clonar()

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

def _insertar_visita(solucion, cliente, t):
    """
    Inserta una visita siguiendo estrictamente las políticas OU y ML según el paper.
    
    Teoría:
    1. Primero agregar el cliente a la ruta usando el método de inserción más barato
    2. Luego establecer la cantidad según la política:
       - OU: Ui - nivel_actual, y reducir la misma cantidad de la siguiente visita
       - ML: min(Ui - nivel_actual, capacidad_vehiculo, stock_proveedor), o rit si es 0
            (puede violar restricciones de capacidad pero mantiene solución admisible)
    """
    # 1. Primero insertamos usando el método de inserción más barato
    nueva_solucion = solucion.insertar_visita(cliente, t)  # Asumimos que implementa cheapest insertion
    
    inventario_actual = nueva_solucion.inventario_clientes[cliente.id][t]
    
    # 2. Establecer cantidad según la política
    if solucion.contexto.politica_reabastecimiento == "OU":
        # OU Policy: cantidad = Ui - nivel_actual
        cantidad_entregada = cliente.nivel_maximo - inventario_actual
        
        # Buscar siguiente visita y reducir la misma cantidad
        tiempos_cliente = nueva_solucion.tiempos_cliente(cliente)
        t_next = next((t_futuro for t_futuro in tiempos_cliente if t_futuro > t), None)
        
        if t_next is not None:
            cantidad_siguiente = nueva_solucion.rutas[t_next].obtener_cantidad_entregada(cliente)
            if cantidad_siguiente <= cantidad_entregada:
                nueva_solucion = nueva_solucion.eliminar_visita(cliente, t_next)
            else:
                nueva_solucion = nueva_solucion.quitar_cantidad_cliente(cliente, t_next, cantidad_entregada)
    
     # 🔹 **ML Policy: Mínimo entre Ui, capacidad vehicular y stock proveedor**
    elif solucion.contexto.politica_reabastecimiento == "ML":
        cantidad_entregada = min(
            cliente.nivel_maximo - inventario_actual,
            solucion.contexto.capacidad_vehiculo - solucion.rutas[t].obtener_total_entregado(),
            solucion.inventario_proveedor[t]
        )
        if cantidad_entregada == 0:
            cantidad_entregada = cliente.nivel_demanda  

    # ✅ **Si el cliente ya está en la ruta, modificar cantidad en vez de agregar duplicados**
    if cliente in solucion.rutas[t].clientes:
        rutas_modificadas = list(solucion.rutas)
        rutas_modificadas[t] = rutas_modificadas[t].modificar_cantidad_cliente(cliente, cantidad_entregada)
        return Solucion(rutas=tuple(rutas_modificadas))
    
    # 🔹 Insertar la nueva visita con la cantidad calculada
    return solucion.insertar_visita(cliente, t, cantidad_entregada)

def _eliminar_visita(solucion, cliente, t):
    """
    Elimina una visita siguiendo estrictamente las políticas OU y ML según el paper.
    
    Teoría:
    1. Primero eliminar el cliente de la ruta y enlazar predecesor con sucesor
    2. Luego según la política:
       - OU: Transferir cantidad a siguiente visita, solo si no causa stockout
       - ML: Si no hay stockout, eliminar. Si hay, intentar compensar con visita anterior
    """
    # Obtener cantidad antes de eliminar
    cantidad_eliminada = solucion.rutas[t].obtener_cantidad_entregada(cliente)
    tiempos_cliente = solucion.tiempos_cliente(cliente)
    t_next = next((t_futuro for t_futuro in tiempos_cliente if t_futuro > t), None)
    t_prev = next((t_pasado for t_pasado in reversed(tiempos_cliente) if t_pasado < t), None)
    
    # 1. Eliminar cliente y enlazar predecesor con sucesor
    nueva_solucion = solucion.eliminar_visita(cliente, t)  # Asumimos que maneja el enlace pred-succ
    
    # 2. Procesar según la política
    if solucion.contexto.politica_reabastecimiento == "OU":
        # Verificar si causa stockout
        if nueva_solucion.inventario_clientes[cliente.id][t] < cliente.nivel_minimo:
            return solucion  # No eliminar si causa stockout
        
        # Transferir cantidad a siguiente visita
        tiempos_cliente = solucion.tiempos_cliente(cliente)
        t_next = next((t_futuro for t_futuro in tiempos_cliente if t_futuro > t), None)
        
        if t_next is not None:
            nueva_solucion = nueva_solucion.agregar_cantidad_cliente(cliente, t_next, cantidad_eliminada)
        
        return nueva_solucion
    
    elif solucion.contexto.politica_reabastecimiento == "ML":
        if nueva_solucion.inventario_clientes[cliente.id][t] >= cliente.nivel_minimo:
            return nueva_solucion  # ✅ Si no hay stockout, eliminación exitosa
        
        if t_prev is not None:
            y = nueva_solucion.inventario_clientes[cliente.id][t_prev]
        
            if y >= cantidad_eliminada:
                return solucion  

            cantidad_aumentada = cantidad_eliminada - y
            if nueva_solucion.inventario_clientes[cliente.id][t_prev] + nueva_solucion.rutas[t_prev].cantidad_entregada(cliente) + cantidad_aumentada <= cliente.nivel_maximo:
                rutas_modificadas = list(nueva_solucion.rutas)
                rutas_modificadas[t_prev] = rutas_modificadas[t_prev].agregar_cantidad_cliente(cliente, cantidad_aumentada)
                return Solucion(rutas=tuple(rutas_modificadas))
        return solucion