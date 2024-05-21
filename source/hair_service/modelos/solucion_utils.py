from modelos.solucion import Solucion
from constantes import constantes
from modelos.mip1 import Mip1
from modelos.mip2 import Mip2
from modelos.ruta import Ruta

from random import randint
from typing import Type

from modelos.tabulists import tabulists
from tsp_local.base import TSP
from tsp_local.kopt import KOpt

def inicializar():
    solucion = _obtener_empty_solucion()
    # Simular demanda de clientes y actualizar stock
    for cliente in constantes.clientes:
        stock_cliente = cliente.nivel_almacenamiento
        for t in range(constantes.horizon_length):
            stock_cliente -= cliente.nivel_demanda
            if stock_cliente < cliente.nivel_demanda:
                # Calcular cantidad máxima a entregar
                maxima_entrega = cliente.nivel_maximo - stock_cliente
                # Calcular cantidad a entregar según la política
                cantidad_entregada = maxima_entrega if constantes.politica_reabastecimiento == "ML" else randint(1, maxima_entrega)
                # Insertar visita en la solución
                solucion.rutas[t].insertar_visita(cliente, cantidad_entregada , None)
                    # Actualizar demanda acumulada
                stock_cliente += cantidad_entregada
    print(f"Inicialización: {solucion}")
    return solucion

def mover(solucion) -> Type["Solucion"]:
    neighborhood = _variante_eliminacion(solucion)
    neighborhood += _variante_insercion(solucion)
    neighborhood += _variante_mover_visita(solucion)
    neighborhood += _variante_intercambiar_visitas(solucion)
    minimo = min(neighborhood, key=lambda neighbor: neighbor.costo(), default=solucion.clonar())
    return minimo 

def mejorar(solucion):
    do_continue = True
    solucion_best = solucion.clonar()
    solucion_best = _LK(_obtener_empty_solucion(), solucion_best)

    while do_continue:
        do_continue = False

        #PRIMER TIPO DE MEJORA
        #Se aplica el MIP1 a solucion_best, luego se le aplica LK
        solucion_prima = Mip1.ejecutar(solucion_best)
        solucion_prima = _LK(solucion_best, solucion_prima)
        
        #Si el costo de la solución encontrada es mejor que el de solucion_best, se actualiza solucion_best
        if solucion_prima.costo() < solucion_best.costo():
            #print(f"first improvement: {solucion_prima.costo()}")
            solucion_best = solucion_prima.clonar()
            do_continue = True

        #SEGUNDO TIPO DE MEJORA
        solucion_merge = solucion_best.clonar()
        # Se determina el conjunto L, con pares de rutas consecutivas de la solución.
        L = [[solucion_best.rutas[r-1], solucion_best.rutas[r]] for r in range(1, len(solucion_best.rutas))]
        for i in range(len(L)):
            # Por cada par de rutas, se crea una solución s1 que resulta de trasladar las visitas de r2 a r1
            s1 = solucion_best.clonar()
            s1.merge_rutas(i,i+1)
            #Se aplica el Mip2 a la solución s1 encontrada
            aux_solucion = Mip2.ejecutar(s1)
            # Si el resultado de aplicar el MIP2 sobre s1 no es factible y r no es la última ruta en s1, entonces
            #se anticipa la siguiente ruta despues de r en un período de tiempo
            if (not aux_solucion.es_factible()) and (i + 2 < len(s1.rutas)):
                s1.merge_rutas(i+1,i+2)
            #Si el resultado de aplicar el MIP2 a s1 es factible, entonces solucion_prima es una solución óptima
            aux_solucion = Mip2.ejecutar(s1)
            if aux_solucion.es_factible():
                solucion_prima = _LK(s1, aux_solucion)
                if solucion_prima.costo() < solucion_merge.costo():
                    solucion_merge = solucion_prima.clonar()

            #Por cada par de rutas, se crea una solución s2 que resulta de trasladar las visitas de r1 a r2
            s2 = solucion_best.clonar()
            s2.merge_rutas(i+1,i)
            aux_solucion = Mip2.ejecutar(s2)
            #Si el resultado de aplicar el MIP2 sobre s2 no es factible y r no es la primer ruta en s2, entonces
            #se posterga la siguiente ruta despues de r en un período de tiempo
            if (not aux_solucion.es_factible()) and (i > 0):
                s2.merge_rutas(i,i-1)
            #Si el resultado de aplicar el MIP2 a s2 es factible, entonces solucion_prima es una solución óptima
            aux_solucion = Mip2.ejecutar(s2)
            if aux_solucion.es_factible():
                solucion_prima = _LK(s2, solucion_prima)
                #En este punto solucion_merge es la mejor solución entre solucion_best y la primer parte de esta mejora.
                if solucion_prima.costo() < solucion_merge.costo():
                    solucion_merge = solucion_prima.clonar()
        #Si el costo de solucion_merge es mejor que el de solucion_best, se actualiza el valor de solucion_best
        if solucion_merge.costo() < solucion_best.costo():
            #print(f"second improvement: {solucion_merge.costo()}")
            solucion_best = solucion_merge.clonar()
            do_continue = True

        #TERCER TIPO DE MEJORA
        #Se aplica el MIP2 a solucion_best, luego se le aplica LK
        solucion_prima = Mip2.ejecutar(solucion_best)
        solucion_prima = _LK(solucion_best, solucion_prima)
        if solucion_prima.costo() < solucion_best.costo():
            #print(f"Third improvement: {solucion_prima.costo()}")
            solucion_best = solucion_prima.clonar()
            do_continue = True 
    #print(f"sbest despues de improvement {solucion_best}")
    return solucion_best.clonar()

def saltar(solucion,triplet_manager):
    solucion_base = solucion.clonar()
    mejor_solucion = solucion.clonar()
    
    #Mientras haya triplets
    while triplet_manager.triplets:
        #Se realizan jumps en función de algún triplet random
        cliente, tiempo_visitado, tiempo_not_visitado = triplet_manager.obtener_triplet_aleatorio() 
        if solucion_base.rutas[tiempo_visitado].es_visitado(cliente) and (not solucion_base.rutas[tiempo_not_visitado].es_visitado(cliente)):    
            cantidad_eliminado = solucion_base.rutas[tiempo_visitado].remover_visita(cliente)
            solucion_base.rutas[tiempo_not_visitado].insertar_visita(cliente, cantidad_eliminado, None)
            if not solucion_base.cliente_tiene_stockout():
                mejor_solucion = solucion_base.clonar()
                
    #Cuando no se puedan hacer mas saltos, se retorna la respuesta de ejecutar el MIP2 sobre la solución encontrada.
    return Mip2.ejecutar(mejor_solucion)

def _obtener_empty_solucion() -> Type["Solucion"]:
    return Solucion([Ruta(ruta[0], ruta[1]) for ruta in [[[], []] for _ in range(constantes.horizon_length)]])

def _variante_eliminacion(solucion) -> list[Type["Solucion"]]:
    neighborhood_prima = []
    for cliente in constantes.clientes:
        # La eliminación de la visita es interesante si el costo de almacenamiento del cliente es mayor que el del proveedor.
        if cliente.costo_almacenamiento > constantes.proveedor.costo_almacenamiento:
            for tiempo in range(constantes.horizon_length):
                solucion_copy = solucion.clonar()
                if solucion_copy.rutas[tiempo].es_visitado(cliente) and (not tabulists.esta_prohibido_quitar(cliente.id, tiempo)):
                    solucion_copy.remover_visita(cliente, tiempo)
                    if solucion_copy.es_admisible():
                        neighborhood_prima.append(solucion_copy)
    return neighborhood_prima

def _variante_insercion(solucion) -> list[Type["Solucion"]]:
    neighborhood_prima = []
    for cliente in constantes.clientes:
        for tiempo in range(constantes.horizon_length):
            solucion_copy = solucion.clonar()
            if not (solucion_copy.rutas[tiempo].es_visitado(cliente) or tabulists.esta_prohibido_agregar(cliente.id, tiempo)):
                solucion_copy.insertar_visita(cliente, tiempo)
                if solucion_copy.es_admisible():
                    neighborhood_prima.append(solucion_copy)
    return neighborhood_prima

def _variante_mover_visita(solucion) -> list[Type["Solucion"]]:
    neighborhood_prima = []
    for cliente in constantes.clientes:
        set_t_visitado = solucion.T(cliente)
        set_t_not_visitado = set(range(constantes.horizon_length)) - set(set_t_visitado)
        for t_visitado in set_t_visitado:
            new_solucion = solucion.clonar()
            cantidad_eliminado = new_solucion.rutas[t_visitado].remover_visita(cliente)
            for t_not_visitado in set_t_not_visitado:
                if not (tabulists.esta_prohibido_quitar(cliente.id, t_visitado) or tabulists.esta_prohibido_agregar(cliente.id, t_not_visitado)):
                    solucion_copy = new_solucion.clonar()
                    solucion_copy.rutas[t_not_visitado].insertar_visita(cliente, cantidad_eliminado, None)
                    if solucion_copy.es_admisible():
                        neighborhood_prima.append(solucion_copy)
    return neighborhood_prima

def _variante_intercambiar_visitas(solucion) -> list[Type["Solucion"]]:
    neighborhood_prima = []
    for t1 in range(constantes.horizon_length):
        for t2 in range(constantes.horizon_length):
            if t1 != t2:
                for cliente1 in solucion.rutas[t1].clientes:
                    for cliente2 in solucion.rutas[t2].clientes:
                        if not(solucion.rutas[t1].es_visitado(cliente2) or solucion.rutas[t2].es_visitado(cliente1)
                                or tabulists.esta_prohibido_agregar(cliente1.id, t2) or tabulists.esta_prohibido_quitar(cliente1.id, t1) 
                                or tabulists.esta_prohibido_agregar(cliente2.id, t1) or tabulists.esta_prohibido_quitar(cliente2.id, t2)):
                            solucion_copy = solucion.clonar()
                            # Mover cliente1 de t1 a t2
                            cantidad_to_insert = solucion_copy.rutas[t1].remover_visita(cliente1)
                            solucion_copy.rutas[t2].insertar_visita(cliente1,cantidad_to_insert,None)
                            # Mover cliente1 de t2 a t1
                            cantidad_to_insert = solucion_copy.rutas[t2].remover_visita(cliente2)
                            solucion_copy.rutas[t1].insertar_visita(cliente2,cantidad_to_insert,None)
                            if solucion_copy.es_admisible():
                                neighborhood_prima.append(solucion_copy)
    return neighborhood_prima


def _LK(solucion: Type["Solucion"], solucion_prima: Type["Solucion"]) -> Type["Solucion"]:
    aux_solucion = solucion.clonar()
    if solucion != solucion_prima:
        aux_solucion = solucion_prima.clonar()
        for tiempo in range(constantes.horizon_length):
            tamano_matriz = len(solucion_prima.rutas[tiempo].clientes)+1
            matriz =  [[0] * tamano_matriz for _ in range(tamano_matriz)]

            # Proveedor distancia
            for indice, cliente in enumerate(solucion_prima.rutas[tiempo].clientes):
                matriz[0][indice+1] = cliente.distancia_proveedor
                matriz[indice+1][0] = cliente.distancia_proveedor

            # Clientes distancias
            for indice, c in enumerate(solucion_prima.rutas[tiempo].clientes):
                for indice2, c2 in enumerate(solucion_prima.rutas[tiempo].clientes):
                    matriz[indice+1][indice2+1] = constantes.matriz_distancia[c.id][c2.id]

            # Make an instance with all nodes
            TSP.setEdges(matriz)
            path, costo = KOpt(range(len(matriz))).optimise()
            
            aux_solucion.rutas[tiempo] = Ruta(
                [solucion_prima.rutas[tiempo].clientes[indice - 1] for indice in path[1:]],
                [solucion_prima.rutas[tiempo].cantidades[indice - 1] for indice in path[1:]]
            )

    return aux_solucion if aux_solucion.costo() < solucion_prima.costo() else solucion_prima