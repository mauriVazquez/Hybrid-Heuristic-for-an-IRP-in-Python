from modelos.solucion import Solucion
from modelos.ruta import Ruta
import random
from copy import copy

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
    
    if len(vecindario) > 0:
        mejor_solucion = min(
            (vecino for vecino in vecindario if (tabulists.movimiento_permitido(solucion, vecino))),
            default=None,
            key=lambda v: v.costo
        )

        mejor_solucion_no_permitida = min(
            (vecino for vecino in vecindario if (not tabulists.movimiento_permitido(solucion, vecino))),
            default=None,
            key=lambda v: v.costo
        )
        
        if mejor_solucion is not None:
            if mejor_solucion_no_permitida is not None: 
                # Normalización del progreso dentro del ciclo de salto
                multiplicador_tolerancia = 1.05 - 0.1 * (iterador_principal / (solucion.contexto.jump_iter - (iterador_principal % solucion.contexto.jump_iter))) 
                umbral_costo = multiplicador_tolerancia * mejor_solucion.costo
                if (mejor_solucion_no_permitida.costo < umbral_costo):
                    mejor_solucion = mejor_solucion_no_permitida.clonar()
        else:
            mejor_solucion = mejor_solucion_no_permitida.clonar()
    else:
        print("NO MUEVE")
        mejor_solucion = solucion.clonar()

    # Actualizar la lista tabú con la mejor solución seleccionada
    tabulists.actualizar(solucion, mejor_solucion, iterador_principal)
    solucion.contexto.alfa.actualizar(mejor_solucion.respeta_capacidad_vehiculo())
    solucion.contexto.beta.actualizar(mejor_solucion.proveedor_sin_desabastecimiento())
    if not mejor_solucion.cumple_politica():
        print("DEFASAJE EN MOVIMIENTO")
        exit(0)
    return mejor_solucion

def _crear_vecindario(solucion: Solucion) -> list[Solucion]:
    """
    Construcción del vecindario N(s), asegurando adherencia estricta a la teoría.
    Se genera primero N'(s) con las variantes básicas y luego se aplican ajustes adicionales
    según la política OU o ML.
    """
    contexto = solucion.contexto
    vecindario = []

    # Paso 1: Crear N'(s) aplicando las variantes estándar de generación de vecinos
    vecindario_prima = [
        vecino for variante in [
            _variante_eliminacion,
            _variante_insercion,
            _variante_mover_visita,
            _variante_intercambiar_visitas
        ] for vecino in variante(solucion) if not vecino.es_igual(solucion)
    ]
   
    # Paso 2: Aplicar ajustes adicionales basados en la teoría
    for solucion_prima in vecindario_prima:
        conjunto_A = [cliente for cliente in contexto.clientes if (solucion.tiempos_cliente(cliente) != solucion_prima.tiempos_cliente(cliente))]
        while conjunto_A:
            cliente_i = conjunto_A.pop(0)
            tiempos_cliente = solucion_prima.tiempos_cliente(cliente_i)
            for t in tiempos_cliente:
                # Por cada cliente j atendidos en el tiempo t en s' y si t pertenece a Tj(s') 
                clientes_j =  [cliente for cliente in solucion_prima.rutas[t].clientes]
                
                for cliente_j in clientes_j: 
                    if cliente_j.costo_almacenamiento > contexto.proveedor.costo_almacenamiento or \
                       solucion_prima.rutas[t].obtener_total_entregado() > contexto.capacidad_vehiculo or \
                       solucion_prima.inventario_proveedor[t] < 0:

                        if contexto.politica_reabastecimiento == "OU":
                            solucion_nueva = solucion_prima.eliminar_visita(cliente_j, t)                            
                            if (solucion_nueva.es_admisible) and (solucion_nueva.costo < solucion_prima.costo):
                               solucion_prima = solucion_nueva
                               conjunto_A.append(cliente_j)

                        # **ML Policy: Reducir entrega pero asegurando que no haya stockout**
                        if contexto.politica_reabastecimiento == "ML":
                            xjt = solucion_prima.rutas[t].obtener_cantidad_entregada(cliente_j)
                            y = min(xjt, min(solucion_prima.inventario_clientes[cliente_j.id][t+1:], default=xjt))
                            
                            if y >= xjt:  
                                solucion_nueva = solucion_prima.eliminar_visita(cliente_j, t)
                            else:
                                solucion_nueva = solucion_prima.quitar_cantidad_cliente(cliente_j, t, y)
                                
                            if solucion_nueva.es_admisible and solucion_nueva.costo < solucion_prima.costo:
                                solucion_prima = solucion_nueva
                                if not solucion_prima.rutas[t].es_visitado(cliente_j):
                                    conjunto_A.append(cliente_j) 

                # **ML Policy: Revisar si se puede almacenar en cliente**
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
                                solucion_prima = solucion_nueva.clonar()
        if (not solucion_prima.es_igual(solucion)) and solucion_prima.cumple_politica():
            vecindario.append(solucion_prima)
    return vecindario


def _variante_eliminacion(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones eliminando visitas de clientes en la solución actual, diferenciando entre ML y OU.
    """
    vecindario_prima = []
    for t, ruta in enumerate(solucion.rutas):
        for cliente in ruta.clientes:
            nueva_solucion = solucion.eliminar_visita(cliente, t)
            if nueva_solucion.es_admisible and nueva_solucion.cumple_politica():
                vecindario_prima.append(nueva_solucion)
    return set(vecindario_prima)

def _variante_insercion(solucion: Solucion) -> list[Solucion]:
    """
    Genera soluciones insertando nuevas visitas a clientes en la solución actual, respetando las políticas ML y OU.
    """ 
    vecindario_prima = []
    contexto = solucion.contexto
    for cliente in contexto.clientes:
        for t in set(range(solucion.contexto.horizonte_tiempo)) - set(solucion.tiempos_cliente(cliente)):   
            nueva_solucion = solucion.insertar_visita(cliente, t)
            if nueva_solucion.es_admisible and nueva_solucion.cumple_politica():
                vecindario_prima.append(nueva_solucion)            
    return set(vecindario_prima)


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
        for t_destino in posibles_destinos:
            solucion_intermedia = solucion.insertar_visita(cliente, t_destino)
            for t_origen in tiempos_cliente_actual:
                nueva_solucion = solucion_intermedia.eliminar_visita(cliente, t_origen)
                if nueva_solucion.es_admisible and (t_destino in nueva_solucion.tiempos_cliente(cliente)) and not (t_origen in nueva_solucion.tiempos_cliente(cliente)):
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
                solucion_intermedia = solucion.eliminar_visita(cliente1, iter_t)
                solucion_intermedia = solucion_intermedia.insertar_visita(cliente2, iter_t)
                for iter_tprima in posibles_tiempos2:
                    nueva_solucion = solucion_intermedia
                    nueva_solucion = nueva_solucion.insertar_visita(cliente1, iter_tprima)
                    nueva_solucion = solucion.eliminar_visita(cliente2, iter_tprima)
                    if (nueva_solucion.es_admisible 
                        and (iter_tprima in nueva_solucion.tiempos_cliente(cliente1)) and not (iter_t in nueva_solucion.tiempos_cliente(cliente1))
                        and (iter_t in nueva_solucion.tiempos_cliente(cliente2)) and not (iter_tprima in nueva_solucion.tiempos_cliente(cliente2))
                    ):
                        vecindario_prima.append(nueva_solucion)  # Agregar solo si sigue siendo admisible

    return vecindario_prima