from modelos.solucion import Solucion
import random

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
    
    # Normalización del progreso dentro del ciclo de salto
    multiplicador_tolerancia = 1.05 - 1 * (iterador_principal / (solucion.contexto.jump_iter - (iterador_principal % solucion.contexto.jump_iter))) 

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
    Construcción del vecindario N(s), asegurando adherencia estricta a la teoría.
    Se genera primero N'(s) con las variantes básicas y luego se aplican ajustes adicionales
    según la política OU o ML.
    """
    contexto = solucion.contexto
    vecindario = []

    # 🔹 Paso 1: Crear N'(s) aplicando las variantes estándar de generación de vecinos
    vecindario_prima = [
        vecino for variante in [
            _variante_eliminacion,
            _variante_insercion,
            _variante_mover_visita,
            _variante_intercambiar_visitas
        ] for vecino in variante(solucion) if ((vecino.es_admisible) and (not vecino.es_igual(solucion)))
    ]
    
    # 🔹 Paso 2: Aplicar ajustes adicionales basados en la teoría
    for solucion_prima in vecindario_prima:
        conjunto_A = [cliente for cliente in contexto.clientes if solucion.tiempos_cliente(cliente) != solucion_prima.tiempos_cliente(cliente)]
        while conjunto_A:
            cliente_i = conjunto_A.pop(random.randint(0, len(conjunto_A) - 1))
            for t in solucion_prima.tiempos_cliente(cliente_i):
                for cliente_j in solucion_prima.rutas[t].clientes:
                    if t not in solucion_prima.tiempos_cliente(cliente_j):
                        continue  
                    
                    if cliente_j.costo_almacenamiento > contexto.proveedor.costo_almacenamiento or \
                       solucion_prima.rutas[t].obtener_total_entregado() > contexto.capacidad_vehiculo or \
                       solucion_prima.inventario_proveedor[t] < 0:

                        if contexto.politica_reabastecimiento == "OU":
                            solucion_nueva = _eliminar_visita(solucion_prima, cliente_j, t)
                            if (solucion_nueva.es_admisible) and (solucion_nueva.costo < solucion_prima.costo):
                               solucion_prima = solucion_nueva
                               conjunto_A.append(cliente_j)

                        # ✅ **ML Policy: Reducir entrega pero asegurando que no haya stockout**
                        if contexto.politica_reabastecimiento == "ML":
                            xjt = solucion_prima.rutas[t].obtener_cantidad_entregada(cliente_j)
                            y = min(xjt, min(solucion_prima.inventario_clientes[cliente_j.id][t+1:], default=xjt))
                            
                            if y > xjt:  
                                solucion_nueva = _eliminar_visita(solucion_prima, cliente_j, t)
                            else:
                                solucion_nueva = solucion_prima.quitar_cantidad_cliente(cliente_j, t, y)
                                
                            if solucion_nueva.es_admisible and solucion_nueva.costo < solucion_prima.costo:
                                solucion_prima = solucion_nueva
                                if not solucion_prima.rutas[t].es_visitado(cliente_j):
                                    conjunto_A.append(cliente_j) 

            # ✅ **ML Policy: Revisar si se puede almacenar en cliente**
            if contexto.politica_reabastecimiento == "ML":
                for cliente_j in solucion_prima.rutas[t].clientes:
                    if cliente_j.costo_almacenamiento < contexto.proveedor.costo_almacenamiento:
                        y = max([
                            solucion_prima.inventario_clientes[cliente_j.id][t_futuro] +
                            solucion_prima.rutas[t_futuro].obtener_cantidad_entregada(cliente_j) 
                            for t_futuro in range(t, contexto.horizonte_tiempo)
                        ])
                        solucion_nueva = solucion.agregar_cantidad_cliente(cliente_j, t, cliente_j.nivel_maximo - y)

                        if  solucion_nueva.costo < solucion_prima.costo:
                            solucion_prima = solucion_nueva

        if solucion_prima.es_admisible:
            vecindario.append(solucion_prima)  # 🔹 Validación final

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
            solucion_intermedia = _eliminar_visita(solucion, cliente, t_origen)
            for t_destino in posibles_destinos:
                nueva_solucion = _insertar_visita(solucion_intermedia, cliente, t_destino)
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
                solucion_intermedia = _eliminar_visita(solucion, cliente1, iter_t)
                solucion_intermedia = _insertar_visita(solucion_intermedia, cliente2, iter_t)
                for iter_tprima in posibles_tiempos2:
                    nueva_solucion = solucion_intermedia.clonar()
                    nueva_solucion = _insertar_visita(nueva_solucion, cliente1, iter_tprima)
                    nueva_solucion = _eliminar_visita(nueva_solucion, cliente2, iter_tprima)
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
    if solucion.contexto.politica_reabastecimiento == "OU":
        cantidad_entregada = cliente.nivel_maximo - solucion.inventario_clientes[cliente.id][t]
        if cantidad_entregada > 0:
            nueva_solucion = solucion.insertar_visita(cliente, t, cantidad_entregada)
                
            # Buscar siguiente visita y reducir la misma cantidad
            t_next = next((t_futuro for t_futuro in nueva_solucion.tiempos_cliente(cliente) if t_futuro > t), None)
            if t_next is not None:
                cantidad_siguiente = cliente.nivel_maximo - nueva_solucion.inventario_clientes[cliente.id][t_next]
                if cantidad_siguiente == 0:
                    nueva_solucion = nueva_solucion.eliminar_visita(cliente, t_next)
                else:
                    nueva_solucion = nueva_solucion.establecer_cantidad_cliente(cliente, t_next, cliente.nivel_maximo - cantidad_siguiente)
        else:
            nueva_solucion = solucion
            
     # 🔹 **ML Policy: Mínimo entre Ui, capacidad vehicular y stock proveedor**
    elif solucion.contexto.politica_reabastecimiento == "ML":
        cantidad_entregada = min(
            cliente.nivel_maximo - solucion.inventario_clientes[cliente.id][t],
            solucion.contexto.capacidad_vehiculo - solucion.rutas[t].obtener_total_entregado(),
            solucion.inventario_proveedor[t]
        )
        if cantidad_entregada <= 0:
            cantidad_entregada = cliente.nivel_demanda  
            
        nueva_solucion = solucion.insertar_visita(cliente, t, cantidad_entregada)
    return nueva_solucion

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
    
    
    nueva_solucion = solucion.eliminar_visita(cliente, t)  # Asumimos que maneja el enlace pred-succ
    
    if solucion.contexto.politica_reabastecimiento == "OU":    
        # Transferir cantidad a siguiente visita        
        if t_next is not None:
            nueva_solucion = nueva_solucion.agregar_cantidad_cliente(cliente, t_next, cantidad_eliminada)
        if min(nueva_solucion.inventario_clientes[cliente.id]) < cliente.nivel_minimo:
            return solucion.clonar()
        return nueva_solucion
    
    elif solucion.contexto.politica_reabastecimiento == "ML":
        if max(nueva_solucion.inventario_clientes[cliente.id]) > cliente.nivel_minimo:
            return nueva_solucion
        
        if t_prev is not None:
            y = nueva_solucion.inventario_clientes[cliente.id][t_prev]
        
            if y >= cantidad_eliminada:
                return solucion.clonar()  

            cantidad_aumentada = cantidad_eliminada - y
            if nueva_solucion.inventario_clientes[cliente.id][t_prev] + nueva_solucion.rutas[t_prev].obtener_cantidad_entregada(cliente) + cantidad_aumentada <= cliente.nivel_maximo:
                return nueva_solucion.agregar_cantidad_cliente(cliente, t_prev, cantidad_aumentada)
        return solucion.clonar()