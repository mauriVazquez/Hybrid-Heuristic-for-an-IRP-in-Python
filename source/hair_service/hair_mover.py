from modelos.solucion import Solucion
from typing import Type
from random import random
from modelos.tabulists import tabulists
from constantes import constantes

def mover(solucion, mejor_solucion, iterador_principal) -> Type["Solucion"]:
    # Creación de neighborhood_prima
    neighborhood_prima  = _variante_eliminacion(solucion)
    neighborhood_prima += _variante_insercion(solucion)
    neighborhood_prima += _variante_mover_visita(solucion)
    neighborhood_prima += _variante_intercambiar_visitas(solucion)
    
    # Creación de neighborhood a partir de neighborhood_prima
    neighborhood = []
    #Por cada solución en N'(S)
    for solucion_prima in neighborhood_prima:
        # Determinar el conjunto A de clientes tales que Ti(s) != Ti(s'). 
        conjunto_A = [cliente for cliente in constantes.clientes if (solucion.T(cliente) != solucion_prima.T(cliente))]
        
        # Mientras el conjunto_A no esté vacío
        while len(conjunto_A) > 0:
            # Elegir alteatoriamente un cliente de A y removerlo
            cliente_removido = conjunto_A.pop(int(random() * len(conjunto_A)))
            # Considerar todos los tiempos de entrega t∈T(cliente) y todos los clientes entregados en el tiempo t en s'
            for t in solucion_prima.T(cliente_removido):
                for cliente in solucion_prima.rutas[t].clientes:
                    # Verificar si hj > h0, Qt(s') > C o Bt(s') < 0 
                    if (cliente.costo_almacenamiento > constantes.proveedor.costo_almacenamiento) or (solucion_prima.rutas[t].obtener_total_entregado() > constantes.capacidad_vehiculo) or (solucion_prima.obtener_niveles_inventario_proveedor()[t] < 0):
                        # Política OU
                        if constantes.politica_reabastecimiento == "OU":
                            # Definir s" como la solucion obtenida al remover la visita al cliente en el tiempo t de s'
                            solucion_dosprima = solucion_prima.clonar()
                            solucion_dosprima.rutas[t].remover_visita(cliente)
                            # Si s" es admisible y f(s") < f(s') 
                            if solucion_dosprima.es_admisible() and (solucion_dosprima.costo() < solucion_prima.costo()):
                                # Asignar s" a s' y se agrega j a A. 
                                solucion_prima = solucion_dosprima.clonar()
                                conjunto_A.append(cliente)   

                        #Política ML: 
                        if constantes.politica_reabastecimiento == "ML":
                            # y ← min{xjt, min t'>t Ijt'}.        
                            xjt = solucion_prima.rutas[t].obtener_cantidad_entregada(cliente)
                            niveles_inventario = solucion_prima.obtener_niveles_inventario_cliente(cliente)
                            ijt = niveles_inventario[(t+1):-1]
                            y = min(xjt, min((ijt if (ijt != []) else [xjt])))
                            
                            # Sea s" la solución obtenida desde s' tras remover 'y' unidades de entrega al cliente en el tiempo t 
                            # (la visita al cliente en el tiempo t se elimina si y = xjt). 
                            solucion_dosprima = solucion_prima.clonar()
                            if y == xjt:
                                solucion_dosprima.rutas[t].remover_visita(cliente)
                            else:
                                solucion_dosprima.rutas[t].quitar_cantidad_cliente(cliente, y)
                                
                            # Si f(s") < f(s'), asignar s" a s'
                            if solucion_dosprima.costo() < solucion_prima.costo():
                                # Agregar el cliente al conjunto A si el cliente no es visitado en el tiempo t en s'
                                if not solucion_prima.rutas[t].es_visitado(cliente):
                                    conjunto_A.append(cliente)
                                solucion_prima = solucion_dosprima.clonar()

                # Política ML: 
                if constantes.politica_reabastecimiento == "ML":
                    for cliente in solucion_prima.rutas[t].clientes:
                        if cliente.costo_almacenamiento < constantes.proveedor.costo_almacenamiento:
                            # Sea y ← max t'≥t(Ijt' + xjt'). 
                            niveles_inventario_cliente = solucion_prima.obtener_niveles_inventario_cliente(cliente)
                            entregas = [(solucion_prima.rutas[t2].obtener_cantidad_entregada(cliente) + niveles_inventario_cliente[t2]) 
                                for t2 in range(t, constantes.horizon_length )]
                            y = max(entregas) if entregas else 0
                            
                            # Sea s" la solución obtenida desde s' tras añadir Uj − y unidades de entrega al cliente en el tiempo t
                            solucion_dosprima = solucion_prima.clonar()
                            solucion_dosprima.rutas[t].agregar_cantidad_cliente(cliente, (cliente.nivel_maximo - y))

                            if solucion_dosprima.costo() < solucion_prima.costo():
                                solucion_prima = solucion_dosprima.clonar()
                                
        neighborhood.append(solucion_prima.clonar()) 

    respuesta = None
    for neighbor in neighborhood:
        if (str(neighbor) != str(solucion)):
            # Si aún no se setea respuesta, la seteo si el movimiento está permitido o si la solucion es mejor que sbest.
            if ((respuesta is None) and  ((tabulists.movimiento_permitido(solucion, neighbor)) or (neighbor.costo() < mejor_solucion.costo()))):
                respuesta = neighbor.clonar()
            elif ((respuesta is not None) and (neighbor.costo() < respuesta.costo())):
                if ((tabulists.movimiento_permitido(solucion, neighbor)) or (neighbor.costo() < mejor_solucion.costo())):
                    respuesta = neighbor.clonar()             
    
    respuesta = (solucion if (respuesta is None) else respuesta)
    tabulists.actualizar(solucion, respuesta, iterador_principal)

    return respuesta

def _variante_eliminacion(solucion) -> list[Type["Solucion"]]:
    neighborhood_prima = []
    for index, rutas in enumerate(solucion.rutas):
        for cliente in solucion.rutas[index].clientes:
            solucion_copy = solucion.clonar()
            solucion_copy = _remover_visita(solucion_copy, cliente, index)  
            if solucion_copy.es_admisible():
                neighborhood_prima.append(solucion_copy.clonar())
    return neighborhood_prima

def _variante_insercion(solucion) -> list[Type["Solucion"]]:
    neighborhood_prima = []
    for index, rutas in enumerate(solucion.rutas):
        for cliente in constantes.clientes:
            if (not solucion.rutas[index].es_visitado(cliente)):
                solucion_copy = solucion.clonar()
                solucion_copy = _insertar_visita(solucion_copy, cliente, index)
                if solucion_copy.es_admisible():
                    neighborhood_prima.append(solucion_copy)
    return neighborhood_prima

def _variante_mover_visita(solucion) -> list[Type["Solucion"]]:
    neighborhood_prima = []
    for cliente in constantes.clientes:
        set_t_visitado = solucion.T(cliente)
        for t_visitado in set_t_visitado:
            new_solucion = solucion.clonar()
            new_solucion = _remover_visita(new_solucion, cliente, t_visitado)
            for t_not_visitado in set(range(constantes.horizon_length)) - set(set_t_visitado):
                solucion_copy = new_solucion.clonar()
                solucion_copy = _insertar_visita(solucion_copy, cliente, t_not_visitado)
                if solucion_copy.es_admisible():
                    neighborhood_prima.append(solucion_copy)
    return neighborhood_prima

def _variante_intercambiar_visitas(solucion) -> list[Type["Solucion"]]:
    neighborhood_prima = []
    for cliente1 in constantes.clientes:
        for cliente2 in list(set(constantes.clientes) -set([cliente1])):
            for iter_t in (set(solucion.T(cliente1)) - set(solucion.T(cliente2))):
                for iter_tprima in (set(solucion.T(cliente2)) - set(solucion.T(cliente1))):
                    solucion_copy = solucion.clonar()
                    # Remover visitas
                    solucion_copy = _remover_visita(solucion_copy, cliente1, iter_t)
                    solucion_copy = _remover_visita(solucion_copy, cliente2, iter_tprima)
                    #Añadir nuevas visitas
                    solucion_copy = _insertar_visita(solucion_copy, cliente1,iter_tprima)
                    solucion_copy = _insertar_visita(solucion_copy, cliente2,iter_t)
                    
                    if solucion_copy.es_admisible():
                        neighborhood_prima.append(solucion_copy)                                           
    return neighborhood_prima

def _insertar_visita(self, cliente, tiempo):
    # Añadimos una vista al cliente en el tiempo t usando el método de inserción más barato.
    if constantes.politica_reabastecimiento == "OU":
    # La cantidad entregada se establece como Ui - Iit; La misma cantidad se elimina de la siguiente visita al cliente (si la hay).
        cantidad_entregada = (cliente.nivel_maximo - self.obtener_niveles_inventario_cliente(cliente)[tiempo])
        self.rutas[tiempo].insertar_visita(cliente, cantidad_entregada, None)
        for t in range(tiempo + 1, constantes.horizon_length):
            if self.rutas[t].es_visitado(cliente):
                self.rutas[t].quitar_cantidad_cliente(cliente, cantidad_entregada)
                if self.rutas[t].obtener_cantidad_entregada(cliente) < 0:
                    self.rutas[t].remover_visita(cliente)
                break
            
    # La cantidad entregada al cliente en el tiempo t es la mínima entre la cantidad máxima que puede entregarse sin exceder la capacidad 
    # máxima Ui, la capacidad residual del vehículo, y la cantidad disponible en el proveedor. 
    # Si este mínimo es igual a 0, entonces se entrega una cantidad igual a la demanda del cliente, lo que podrá crear desabastecimiento 
    # en el proveedor o una violación de la restricción de capacidad del vehículo, pero la solución seguirá siendo admisible.
    elif constantes.politica_reabastecimiento == "ML":
        cantidad_entregada = min(
            cliente.nivel_maximo - self.obtener_niveles_inventario_cliente(cliente)[tiempo],
            constantes.capacidad_vehiculo - self.rutas[tiempo].obtener_total_entregado(),
            self.obtener_niveles_inventario_proveedor()[tiempo]
        )
        cantidad_entregada = cantidad_entregada if cantidad_entregada > 0 else cliente.nivel_demanda
        self.rutas[tiempo].insertar_visita(cliente, cantidad_entregada, None)
    return self.clonar()
        
def _remover_visita(self, cliente, tiempo):
    # Primero eliminamos al cliente i de la ruta del vehículo en el tiempo t y su predecesor se enlaza con su sucesor.
    nueva_solucion = self.clonar()
    cantidad_eliminado = nueva_solucion.rutas[tiempo].remover_visita(cliente)
    
    # La cantidad entregada al cliente en el tiempo t se transfiere a la visita siguiente (si la hay). 
    # Tal eliminación se realiza solo si no crea un desabastecimiento en el cliente i para mantener la solución admisible.
    if constantes.politica_reabastecimiento == "OU":
        for t in range(tiempo + 1, constantes.horizon_length):
            if nueva_solucion.rutas[t].es_visitado(cliente):
                nueva_solucion.rutas[t].agregar_cantidad_cliente(cliente, cantidad_eliminado)
                break
            
    # Si se genera desabastecimiento en el cliente la eliminación sólo se realiza si puede evitarse aumentando la cantidad entregada
    # en la visita anterior a un valor no mayor que la capacidad máxima Ui. 
    if constantes.politica_reabastecimiento == "ML" and nueva_solucion.cliente_tiene_desabastecimiento():
        for t in range(tiempo, -1, -1):
            if nueva_solucion.rutas[t].es_visitado(cliente):
                cantidad = (cliente.nivel_maximo - nueva_solucion.obtener_niveles_inventario_cliente(cliente)[t])
                nueva_solucion.rutas[t].agregar_cantidad_cliente(cliente, cantidad)
                break
    return nueva_solucion.clonar()
    