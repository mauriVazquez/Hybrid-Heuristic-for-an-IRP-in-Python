import random
from modelos.solucion import Solucion
from typing import Type
from constantes import constantes
from modelos.ruta import Ruta

def distancia(c1, c2):
   return constantes.matriz_distancia[c1.id][c2.id]

def recorrido_total(recorrido):
    return sum(distancia(recorrido[i], recorrido[i+1]) for i in range(len(recorrido) - 1)) + distancia(recorrido[-1], recorrido[0])

def swap_2opt(recorrido, i, j):
    nuevo_recorrido = recorrido[:i] + recorrido[i:j+1][::-1] + recorrido[j+1:]
    return nuevo_recorrido

def execute(solucion: Type["Solucion"], solucion_prima: Type["Solucion"]) -> Type["Solucion"]:
    if solucion.es_igual(solucion_prima):
        aux_solucion = solucion.clonar()
    else:
        aux_solucion = solucion_prima.clonar()

        for tiempo in range(constantes.horizon_length):
            clientes = aux_solucion.rutas[tiempo].clientes
            mejor_recorrido = clientes[:]
            mejora = True
            
            while mejora:
                mejora = False
                for i in range(1, len(clientes) - 1):
                    for j in range(i + 1, len(clientes)):
                        nuevo_recorrido = swap_2opt(mejor_recorrido, i, j)
                        if recorrido_total(nuevo_recorrido) < recorrido_total(mejor_recorrido):
                            mejor_recorrido = nuevo_recorrido
                            mejora = True
                            
            nueva_ruta = Ruta([],[])
            for indice, cliente in enumerate(mejor_recorrido):
                nueva_ruta.insertar_visita(cliente, aux_solucion.rutas[tiempo].obtener_cantidad_entregada(cliente), indice)
                
            aux_solucion.rutas[tiempo] = nueva_ruta.clonar()
    return aux_solucion
         
