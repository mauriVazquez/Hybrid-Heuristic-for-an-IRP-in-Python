from modelos.solucion import Solucion
from typing import Type
from modelos.mip1 import Mip1
from modelos.mip2 import Mip2

from tsp_local.base import TSP
from tsp_local.kopt import KOpt

from constantes import constantes
from modelos.ruta import Ruta
from itertools import permutations


def mejorar(solucion, iterador_principal):
    do_continue = True
    solucion_best = _LK(Solucion.obtener_empty_solucion(), solucion)

    while do_continue:
        do_continue = False

        #################### PRIMER TIPO DE MEJORA ##################
        #Se aplica el MIP1 a solucion_best, luego se le aplica LK
        solucion_prima = Mip1.ejecutar(solucion_best)
        solucion_prima = _LK(solucion_best, solucion_prima)
        #Si el costo de la solución encontrada es mejor que el de solucion_best, se actualiza solucion_best
        if solucion_prima.costo() < solucion_best.costo():
            solucion_best = solucion_prima.clonar()
            do_continue = True

        #################### SEGUNDO TIPO DE MEJORA ####################
        solucion_merge = solucion_best.clonar()
        # Se determina el conjunto L, con pares de rutas consecutivas de la solución.
        L = [[solucion_best.rutas[r-1], solucion_best.rutas[r]] for r in range(1, len(solucion_best.rutas))]
        for i in range(len(L)):
            # Por cada par de rutas, se crea una solución s1 que resulta de trasladar las visitas de r2 a r1
            s1 = solucion_best.clonar()
            s1.merge_rutas(i, i+1)
            #Se aplica el Mip2 a la solución s1 encontrada
            aux_solucion = Mip2.ejecutar(s1)
            # Si el resultado de aplicar el MIP2 sobre s1 no es factible y r no es la última ruta en s1, entonces
            #se anticipa la siguiente ruta despues de r en un período de tiempo
            if (not aux_solucion.es_factible()) and ((i + 2) < len(s1.rutas)):
                s1.merge_rutas(i+1,i+2)
                aux_solucion = Mip2.ejecutar(s1)
            #Si el resultado de aplicar el MIP2 a s1 es factible, entonces solucion_prima es una solución óptima
            if aux_solucion.es_factible():
                solucion_prima = _LK(s1, solucion_prima)
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
                aux_solucion = Mip2.ejecutar(s2)
            #Si el resultado de aplicar el MIP2 a s2 es factible, entonces solucion_prima es una solución óptima
            if aux_solucion.es_factible():
                solucion_prima = _LK(s2, solucion_prima)
                #En este punto solucion_merge es la mejor solución entre solucion_best y la primer parte de esta mejora.
                if solucion_prima.costo() < solucion_merge.costo():
                    solucion_merge = solucion_prima.clonar()
                    
        #Si el costo de solucion_merge es mejor que el de solucion_best, se actualiza el valor de solucion_best
        if solucion_merge.costo() < solucion_best.costo():
            solucion_best = solucion_merge.clonar()
            do_continue = True

        #TERCER TIPO DE MEJORA
        #Se aplica el MIP2 a solucion_best, luego se le aplica LK
        solucion_prima = Mip2.ejecutar(solucion_best)
        solucion_prima = _LK(solucion_best, solucion_prima)
        if solucion_prima.costo() < solucion_best.costo():
            solucion_best = solucion_prima.clonar()
            do_continue = True 
    print(f"Mejora ({iterador_principal}): {solucion_prima}")
    return solucion_best.clonar()

def _LK(solucion: Type["Solucion"], solucion_prima: Type["Solucion"]) -> Type["Solucion"]:
    aux_solucion = solucion.clonar()
    
    if not solucion.es_igual(solucion_prima):
        aux_solucion = solucion_prima.clonar()
        for tiempo in range(constantes.horizon_length):
            tamano_matriz = len(solucion_prima.rutas[tiempo].clientes) + 1
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

