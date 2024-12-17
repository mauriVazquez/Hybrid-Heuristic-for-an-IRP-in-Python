import copy
import matplotlib.pyplot as plt
import numpy as np
from modelos.ruta import Ruta
from typing import Type
from hair.contexto import constantes_contexto

class Solucion():
    def __init__(self,  rutas: list[Ruta] = None) -> None:
        constantes = constantes_contexto.get()
        self.rutas                  = rutas if rutas else [Ruta for _ in range(constantes.horizonte_tiempo)]
        self.inventario_clientes    = {
            cliente.id: self._obtener_niveles_inventario_cliente(cliente) 
            for cliente in constantes.clientes
        }
        self.inventario_proveedor   = self._obtener_niveles_inventario_proveedor()
        self.es_factible            = self._es_factible()
        self.es_admisible           = self._es_admisible()
        self.costo                  = self._costo()

    def __str__(self : Type["Solucion"]) -> str:
        factibilidad = (" F" if self._es_factible() else (" A"  if self._es_admisible() else " N"))
        return "".join(f"T{str(i+1)} = {ruta}    " for i, ruta in enumerate(self.rutas)) + 'Costo:' + str(self._costo()) + factibilidad
    
    def refrescar(self : Type["Solucion"]):
        constantes = constantes_contexto.get()
        self.rutas                  = self.rutas
        self.inventario_clientes    = {
            cliente.id: self._obtener_niveles_inventario_cliente(cliente) 
            for cliente in constantes.clientes
        }
        self.inventario_proveedor   = self._obtener_niveles_inventario_proveedor()
        self.es_factible            = self._es_factible()
        self.es_admisible           = self._es_admisible()
        self.costo                  = self._costo()

    def imprimir_detalle(self) -> str:
        resp = "Clientes visitados:"        +" ".join(f"T{str(i+1)} = {ruta}    "  for i, ruta in enumerate(self.rutas)) + "\n"
        resp += 'Inventario de proveedor: ' + str(self.inventario_proveedor) + "\n"
        resp += 'Inventario de clientes: '  + str(self.inventario_clientes) + "\n"
        resp += '¿Admisible? : '            + ('SI' if self.es_admisible else 'NO') + "\n"
        resp += '¿Factible? : '             + ('SI' if self.es_factible else 'NO') + "\n"
        resp += 'Función objetivo: '        + str(self.costo) + "\n"
        print(resp)
    
    def to_json(self, iteration, tag):   
        constantes = constantes_contexto.get()
        return {
            "proveedor_id"  :   str(constantes.proveedor.id), 
            "iteration"     :   iteration,
            "tag"           :   tag,
            "rutas"         :   {i:ruta.to_json() for i, ruta in enumerate(self.rutas)},
            "costo"         :    self.costo
        }

    def clonar(self) -> Type["Solucion"]:
        clonacion                        = Solucion([ruta.clonar() for ruta in self.rutas])
        clonacion.rutas                  = [ruta.clonar() for ruta in self.rutas]
        clonacion.inventario_clientes    = copy.deepcopy(self.inventario_clientes)
        clonacion.inventario_proveedor   = copy.deepcopy(self.inventario_proveedor)
        clonacion.es_factible            = self.es_factible
        clonacion.es_admisible           = self.es_admisible
        clonacion.costo                  = self.costo
        return clonacion

    def es_igual(self, solution2) -> bool:
        constantes = constantes_contexto.get()
        if ((self is None) and (solution2 is None)):
            return True
        elif ((self is None) or (solution2 is None)):
            return False
        else:
            return all(self.rutas[i].es_igual(solution2.rutas[i]) for i in range(constantes.horizonte_tiempo))
    
    def es_visitado(self, cliente, t) -> bool :
        return self.rutas[t].es_visitado(cliente)
    
    def _es_admisible(self) -> bool:
        return not (self.cliente_tiene_desabastecimiento() or self.cliente_tiene_sobreabastecimiento())

    def _es_factible(self) -> bool:
        #Para que una solución sea factible:
        # - No debe haber faltantes de stock ni en el proveedor ni en los clientes en T' (Bt ≥ 0 e Iit ≥ 0)
        # - El nivel de inventario de cada cliente i no debe ser superior a su nivel máximo Ui
        # - La cantidad total entregada en cualquier momento no debe superar la capacidad del vehículo C.
        return not (
            self.cliente_tiene_desabastecimiento() 
            or self.proveedor_tiene_desabastecimiento()  
            or self.cliente_tiene_sobreabastecimiento() 
            or self.es_excedida_capacidad_vehiculo()
        )

    def es_excedida_capacidad_vehiculo(self) -> bool:
        constantes = constantes_contexto.get()
        return any(constantes.capacidad_vehiculo < ruta.obtener_total_entregado() for ruta in self.rutas)

    def cliente_tiene_desabastecimiento(self) -> bool:
        constantes = constantes_contexto.get()
        return any(self.inventario_clientes.get(cliente.id, None)[tiempo] < cliente.nivel_minimo
                   for cliente in constantes.clientes
                   for tiempo in range(constantes.horizonte_tiempo))

    def cliente_tiene_sobreabastecimiento(self) -> bool:
        constantes = constantes_contexto.get()
        return any(self.inventario_clientes.get(cliente.id, None)[tiempo] > cliente.nivel_maximo
                   for cliente in constantes.clientes
                   for tiempo in range(constantes.horizonte_tiempo))
    
    def proveedor_tiene_desabastecimiento(self) -> bool:
        return any(nivel_inventario < 0 for nivel_inventario in self.inventario_proveedor)
    
    def _obtener_niveles_inventario_proveedor(self):
        constantes = constantes_contexto.get()
        proveedor = constantes.proveedor
        nivel_almacenamiento = proveedor.nivel_almacenamiento
        niveles = [nivel_almacenamiento]
        for t in range(1, constantes.horizonte_tiempo + 1):
            nivel_almacenamiento += proveedor.nivel_produccion - self.rutas[t-1].obtener_total_entregado()
            niveles.append(nivel_almacenamiento)
        nivel_almacenamiento += proveedor.nivel_produccion
        niveles.append(nivel_almacenamiento)
        return niveles
    
    def _obtener_niveles_inventario_cliente(self, cliente):
        constantes = constantes_contexto.get()
        nivel_almacenamiento = cliente.nivel_almacenamiento
        cliente_inventario = [nivel_almacenamiento]
        for t in range(1, constantes.horizonte_tiempo + 1):
            nivel_almacenamiento += self.rutas[t-1].obtener_cantidad_entregada(cliente) - cliente.nivel_demanda
            cliente_inventario.append(nivel_almacenamiento)          
        return cliente_inventario

    # Retorna el conjunto de tiempos donde un cliente es visitado en una solucion dada.
    def T(self, cliente):
        constantes = constantes_contexto.get()
        return [tiempo for tiempo in range(constantes.horizonte_tiempo) if self.es_visitado(cliente, tiempo)]
   
    def _costo(self):
        constantes = constantes_contexto.get()      
        proveedor_nivel_inventario = self.inventario_proveedor
        # First term (costo_almacenamiento)
        costo_almacenamiento = sum(proveedor_nivel_inventario) * constantes.proveedor.costo_almacenamiento
        costo_almacenamiento += sum(cliente.costo_almacenamiento * self.inventario_clientes.get(cliente.id, None)[tiempo]  
                for tiempo in range(constantes.horizonte_tiempo + 1)
                for cliente in constantes.clientes)
            
        # Second term (costo_transporte)
        costo_transporte = sum(self.rutas[tiempo].obtener_costo() for tiempo in range(constantes.horizonte_tiempo))

        # Third term (penalty 1)
        penalty1 = sum(max(0,self.rutas[tiempo].obtener_total_entregado() - constantes.capacidad_vehiculo) 
                       for tiempo in range(constantes.horizonte_tiempo)) * constantes.alfa.obtener_valor() 
        
        # Fourth term
        penalty2 = sum(max(0, -proveedor_nivel_inventario[tiempo]) 
                       for tiempo in range(constantes.horizonte_tiempo+1)) * constantes.beta.obtener_valor()
       
        return costo_almacenamiento + costo_transporte + penalty1 + penalty2
    
    def remover_visita(self, cliente, tiempo) -> None:
        constantes = constantes_contexto.get()
        # En primer lugar guardo los tiempos en que el cliente fue visitado
        tiempos_cliente = self.T(cliente)

        if (tiempo in tiempos_cliente):
            # Guardo el indice del tiempo de la eliminación, para despues acceder fácilmente al anterior y al posterior.
            index = tiempos_cliente.index(tiempo)
            
            # Primero eliminamos al cliente i de la ruta del vehículo en el tiempo t y su predecesor se enlaza con su sucesor.
            cantidad_eliminado = self.rutas[tiempo].remover_visita(cliente)
            self.refrescar()
            
            # La cantidad entregada al cliente en el tiempo t se transfiere a la visita siguiente (si la hay). 
            # Tal eliminación se realiza solo si no crea un desabastecimiento en el cliente i para mantener la solución admisible.
            if (constantes.politica_reabastecimiento == "OU"):
                # Si no era el último, transfiero la cantidad entregada a la siguiente visita
                if index < len(tiempos_cliente) - 1:
                    self.rutas[index+1].agregar_cantidad_cliente(cliente, cantidad_eliminado)
                    self.refrescar()
                    
            # Si se genera desabastecimiento en el cliente la eliminación sólo se realiza si puede evitarse aumentando la cantidad entregada
            # en la visita anterior a un valor no mayor que la capacidad máxima Ui. 
            if (constantes.politica_reabastecimiento == "ML") and self.cliente_tiene_desabastecimiento():
                # Si no era el primero, se intenta aumentar la cantidad entregada a la visita anterior a un valor que no supere Ui
                if index > 0:
                    cantidad = (cliente.nivel_maximo - self.inventario_clientes.get(cliente.id, None)[tiempos_cliente[index-1]])
                    self.rutas[tiempos_cliente[index-1]].agregar_cantidad_cliente(cliente, cantidad)
                    self.refrescar()
        
    def insertar_visita(self, cliente, tiempo) -> None:
        constantes = constantes_contexto.get()
        # Añadimos una vista al cliente en el tiempo t usando el método de inserción más barato.
        if constantes.politica_reabastecimiento == "OU":
        # La cantidad entregada se establece como Ui - Iit; La misma cantidad se elimina de la siguiente visita al cliente (si la hay).
            cantidad_entregada = (cliente.nivel_maximo - self.inventario_clientes.get(cliente.id, None)[tiempo])
            self.rutas[tiempo].insertar_visita(cliente, cantidad_entregada, None)
            self.refrescar()
            for t in range(tiempo + 1, constantes.horizonte_tiempo):
                if self.es_visitado(cliente, t):
                    self.rutas[t].quitar_cantidad_cliente(cliente, cantidad_entregada)
                    self.refrescar()
                    if self.rutas[t].obtener_cantidad_entregada(cliente) < 0:
                        self.rutas[t].remover_visita(cliente)
                        self.refrescar()
                    break
                
        # La cantidad entregada al cliente en el tiempo t es la mínima entre la cantidad máxima que puede entregarse sin exceder la capacidad 
        # máxima Ui, la capacidad residual del vehículo, y la cantidad disponible en el proveedor. 
        # Si este mínimo es igual a 0, entonces se entrega una cantidad igual a la demanda del cliente, lo que podrá crear desabastecimiento 
        # en el proveedor o una violación de la restricción de capacidad del vehículo, pero la solución seguirá siendo admisible.
        elif constantes.politica_reabastecimiento == "ML":
            cantidad_entregada = min(
                cliente.nivel_maximo - self.inventario_clientes.get(cliente.id, None)[tiempo],
                constantes.capacidad_vehiculo - self.rutas[tiempo].obtener_total_entregado(),
                self.inventario_proveedor[tiempo]
            )
            cantidad_entregada = cantidad_entregada if cantidad_entregada > 0 else cliente.nivel_demanda
            self.rutas[tiempo].insertar_visita(cliente, cantidad_entregada, None)
            self.refrescar()

    def merge_rutas(self, rutabase_indice, rutasecondary_indice) -> None:
        for cliente in self.rutas[rutasecondary_indice].clientes:
            if(not self.es_visitado(cliente, rutabase_indice)):
                self.rutas[rutabase_indice].insertar_visita(cliente, self.rutas[rutasecondary_indice].obtener_cantidad_entregada(cliente), None)
                self.refrescar()
        self.rutas[rutasecondary_indice] = Ruta([],[])
        
        self.refrescar()

    def cumple_restricciones(self, MIP, MIPcliente = None, MIPtiempo = None, operation = None):
        constantes = constantes_contexto.get()
        B   = self.inventario_proveedor
        I   = [self.inventario_clientes.get(cliente.id, None) for cliente in constantes.clientes]
        r0  = [constantes.proveedor.nivel_produccion for t in range(constantes.horizonte_tiempo+1)]
        ri  = [c.nivel_demanda for c in constantes.clientes]
        x   = [
            [self.rutas[t].obtener_cantidad_entregada(c) for t in range(constantes.horizonte_tiempo)]
            for c in constantes.clientes
        ]
        x_np = np.array(x)
        theta = [
            [(1 if self.es_visitado(c, t) else 0) for t in range(constantes.horizonte_tiempo)]
            for c in constantes.clientes
        ]
        
        # Variables MIP 2
        v   = [
            [ (1 if ((operation == "INSERT") and (MIPtiempo == t) and (MIPcliente == c)) else 0 ) for t in range(constantes.horizonte_tiempo)]
            for c in constantes.clientes
        ]
        w   = [
            [ (1 if ((operation == "REMOVE") and (MIPtiempo == t) and (MIPcliente == c)) else 0 ) for t in range(constantes.horizonte_tiempo)]
            for c in constantes.clientes
        ]
        sigma = [
            [(1 if self.es_visitado(c, t) else 0) for t in range(constantes.horizonte_tiempo)]
            for c in constantes.clientes
        ]
       
        # Restricción 2: Definición del nivel de inventario del proveedor.
        if (not all([(B[t] == (B[t-1] + r0[t-1] - np.sum( x_np[:, t-1]))) for t in range(1, constantes.horizonte_tiempo+1)])):
            return 2            
        
        # Restricción 3: El nivel de inventario del proveedor debe poder satisfacer la demanda en el tiempo t.
        if (not all(B[t] >= np.sum( x_np[:, t]) for t in range(constantes.horizonte_tiempo))):
            return 3
        
        # Restricción 4: Definición del nivel de inventario de los clientes
        if (not all([(I[c][t] == (I[c][t-1] + x[c][t-1] - ri[c] ))
                for c in range(len(constantes.clientes))
                for t in range(1, constantes.horizonte_tiempo+1)]
        )):
            return 4
        
        if constantes.politica_reabastecimiento == "OU": 
            # Restricción 5: La cantidad entregada al cliente no es menos de la necesaria para llenar el inventario.
            if (not all([(x[c][t] >= ((cliente.nivel_maximo * theta[c][t]) - I[c][t]))
                for c, cliente in enumerate(constantes.clientes)
                for t in range(constantes.horizonte_tiempo)]
            )):
                return 5
        
        # Restricción 6: La cantidad entregada al cliente no debe generar sobreabastecimiento en el cliente.
        if (not all([( x[c][t] <= (cliente.nivel_maximo - I[c][t]) )
            for c, cliente in enumerate(constantes.clientes)
            for t in range(constantes.horizonte_tiempo)]
        )):
            return 6
        
        if constantes.politica_reabastecimiento == "OU":
            # Restricción 7: La cantidad entregada a un cliente es menor o igual al nivel máximo de inventario si es que lo visita.
            if  (not all([( x[c][t] <= (cliente.nivel_maximo * theta[c][t]) )
                for c, cliente in enumerate(constantes.clientes)
                for t in range(constantes.horizonte_tiempo)]
            )):
                return 7
            
        # Restricción 8: La cantidad entregada a los clientes en un t dado, es menor o igual a la capacidad del camión.
        if (not all([np.sum( x_np[:, t]) <= constantes.capacidad_vehiculo for t in range(constantes.horizonte_tiempo)])):
            return 8
        
        if MIP == 1:
            #  Restricción 9: Una ruta solo puede asignarse a un período de tiempo
            if not all(sum(ruta) <= 1 for ruta in sigma):
                return 9

            # Restricción 10: Solo una ruta puede asignarse a un período de tiempo dado
            if not all(sum(tiempo) <= 1 for tiempo in zip(*sigma)):
                return 10

            # Restricción 11: Un cliente puede ser atendido solo si la ruta está asignada
            if not all(x[c][t] <= constantes.clientes[c].nivel_maximo * sigma[c][t] for c in range(len(constantes.clientes)) for t in range(constantes.horizonte_tiempo)):
                return 11

            # Restricción 12: No puede atenderse un cliente si fue removido de la ruta asignada
            if not all(x[c][t] == 0 if w[c][t] else True for c in range(len(constantes.clientes)) for t in range(constantes.horizonte_tiempo)):
                return 12
            
            # Restricción 13: Un cliente puede ser removido solo si su ruta está asignada
            if not all(w[c][t] <= sigma[c][t] for c in range(len(constantes.clientes)) for t in range(constantes.horizonte_tiempo)):
                return 13

            # Restricción 18: Las variables de asignación de rutas (zr_t) deben ser binarias
            if not all(value in [0, 1] for fila in sigma for value in fila):
                return 18

            # Restricción 19: La variable de asignación epsilon_it debe ser binaria
            if not all(value in [0, 1] for fila in theta for value in fila):
                return 19

            # Restricción 20: El inventario en los clientes debe ser mayor o igual a cero
            if not all(I[c][t] >= 0 for c in range(len(constantes.clientes)) for t in range(constantes.horizonte_tiempo)):
                return 20
        
        # Restricción 14: La cantidad entregada a los clientes siempre debe ser mayor o igual a cero
        if not np.all(x_np >= 0):
            return 14
        
        #Restricción 17: Theeta puede tener el valor 0 o 1
        if constantes.politica_reabastecimiento == "OU":
            if not all(value in [0, 1] for fila in theta for value in fila):
                return 17
          
        if MIP == 2:            
            # Restricción 21 (MIP2): Si se inserta una visita, no debe haber una visita existente
            if not all(v[c][t] <= 1 - sigma[c][t] for c in range(len(constantes.clientes)) for t in range(constantes.horizonte_tiempo)):
                return 21

            # Restricción 22 (MIP2): Si se elimina una visita, debe existir previamente una visita
            if not all(w[c][t] <= sigma[c][t] for c in range(len(constantes.clientes)) for t in range(constantes.horizonte_tiempo)):
                return 22
    
            # Restricción 23: La cantidad entregada al cliente i no puede ser mayor a la capacidad máxima
            if not all([ ( x[c][t] <= (cliente.nivel_maximo * (sigma[c][t] + v[c][t] - w[c][t])))
                for c, cliente in enumerate(constantes.clientes)
                for t in range(constantes.horizonte_tiempo)]
            ):
                return 23
            
            #Restricción 24: v_it debe ser 0 o 1
            if not all(value in [0, 1] for fila in v for value in fila):
                return 24
            
            #Restricción 25: w_it debe ser 0 o 1
            if not all(value in [0, 1] for fila in w for value in fila):
                return 25
            
        return 0
            
    def graficar_rutas(self):
        clients_coords = []
        constantes = constantes_contexto.get()
        for tiempo in range(constantes.horizonte_tiempo):
            x = [cliente.coord_x for cliente in self.rutas[tiempo].clientes]
            y = [cliente.coord_y for cliente in self.rutas[tiempo].clientes]
            clients_coords.append([x,y])
 
        # Create a figure and subplots
        fig, axes = plt.subplots(2, 2, figsize=(10, 6))  # Adjust rows, columns, and figure size

        # Generate and display plots in each subplot
        for i, (ax, client_coord) in enumerate(zip(axes.flat, clients_coords)):
            x = [constantes.proveedor.coord_x]+client_coord[0]+[constantes.proveedor.coord_x]
            y = [constantes.proveedor.coord_y]+client_coord[1]+[constantes.proveedor.coord_y]
            ax.plot(x,y)
            ax.set_title(f"Ruta {i+1}")

        # Adjust layout and display all plots at once
        plt.tight_layout()
        plt.show()