from modelos.solucion import Solucion
from modelos.entidad import Cliente
from hair.mip1 import Mip1
from hair.mip2 import Mip2
from typing import Type
from constantes import constantes
from modelos.ruta import Ruta

def mejorar(solucion : Type["Solucion"], iterador_principal : int) -> Type["Solucion"]:
    """
    Aplica un proceso iterativo de mejora a la solución dada utilizando tres tipos diferentes de optimizaciones:
    
    1. Aplicación del modelo MIP1 seguido del algoritmo Lin-Kernighan (LK).
    2. Fusión de pares consecutivos de rutas y aplicación del modelo MIP2 con ajustes para asegurar factibilidad.
    3. Aplicación directa del modelo MIP2 seguido del algoritmo LK.
    
    Durante cada iteración, si alguna de las soluciones generadas mejora el costo de la solución actual, se actualiza
    dicha solución y se continúa el proceso.
    
    Args:
        solucion (Solucion): La solución inicial sobre la que se realizarán las mejoras.
        iterador_principal (int): El número de la iteración principal actual en el proceso de mejora.
    
    Returns:
        Solucion: La mejor solución obtenida después de aplicar todas las mejoras.
    """
    
    do_continue = True
    solucion_best = lk(Solucion.obtener_empty_solucion(), solucion)

    while do_continue:
        do_continue = False

        #################### PRIMER TIPO DE MEJORA ##################
        #Se aplica el MIP1 a solucion_best, luego se le aplica LK
        solucion_prima = Mip1.ejecutar(solucion_best)
        solucion_prima = lk(solucion_best, solucion_prima)
        #Si el costo de la solución encontrada es mejor que el de solucion_best, se actualiza solucion_best
        if (solucion_prima.costo() < solucion_best.costo()):
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
                solucion_prima = lk(s1, solucion_prima)
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
                solucion_prima = lk(s2, solucion_prima)
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
        solucion_prima = lk(solucion_best, solucion_prima)
        if(solucion_prima.costo() < solucion_best.costo()):
            solucion_best = solucion_prima.clonar()
            do_continue = True 
            
    print(f"Mejora ({iterador_principal}): {solucion_prima}")
    return solucion_best.clonar()

def lk(solucion: Type["Solucion"], solucion_prima: Type["Solucion"]) -> Type["Solucion"]:
    """
    Aplica el algoritmo Lin-Kernighan (LK) para mejorar el recorrido de una solución.

    Si la solución original y la solución candidata (solucion_prima) son iguales, se clona la original. De lo contrario, 
    se trabaja sobre la solución candidata, y se aplica un proceso iterativo para optimizar el recorrido de los clientes 
    en cada ruta usando el método 2-opt.

    En cada iteración se evalúa si intercambiar dos segmentos de una ruta (mediante 2-opt) resulta en una mejora 
    en la distancia total recorrida. Si es así, se actualiza la ruta con el mejor recorrido encontrado.

    Args:
        solucion (Solucion): La solución original que se intenta mejorar.
        solucion_prima (Solucion): La solución candidata que se compara con la original.
    
    Returns:
        Solucion: La mejor solución obtenida después de aplicar la mejora.
    """
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
                        nuevo_recorrido = _swap_2opt(mejor_recorrido, i, j)
                        if _recorrido_total(nuevo_recorrido) < _recorrido_total(mejor_recorrido):
                            mejor_recorrido = nuevo_recorrido
                            mejora = True
                            
            nueva_ruta = Ruta([],[])
            for indice, cliente in enumerate(mejor_recorrido):
                nueva_ruta.insertar_visita(cliente, aux_solucion.rutas[tiempo].obtener_cantidad_entregada(cliente), indice)
                
            aux_solucion.rutas[tiempo] = nueva_ruta.clonar()
    return aux_solucion
         
def _distancia(c1 : Type["Cliente"], c2 : Type["Cliente"]):
    """
    Calcula la distancia entre dos clientes c1 y c2 utilizando la matriz de distancias predefinida.

    Args:
        c1 (Cliente): El primer cliente.
        c2 (Cliente): El segundo cliente.

    Returns:
        float: La distancia entre los dos clientes.
    """
    return constantes.matriz_distancia[c1][c2]

def _recorrido_total(recorrido):
    return sum(_distancia(recorrido[i], recorrido[i+1]) for i in range(len(recorrido) - 1)) + _distancia(recorrido[-1], recorrido[0])

def _swap_2opt(recorrido, i, j):
    nuevo_recorrido = recorrido[:i] + recorrido[i:j+1][::-1] + recorrido[j+1:]
    return nuevo_recorrido