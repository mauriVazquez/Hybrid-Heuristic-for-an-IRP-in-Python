# import matplotlib.pyplot as plt
import numpy as np
from modelos.ruta import Ruta
from typing import Type
from modelos.penalty_variables import alpha, beta
from constantes import constantes


class Solucion():
  
    def __init__(self,  rutas: list[Ruta] = None) -> None:
        self.rutas = rutas if rutas else [Ruta for _ in range(constantes.horizon_length)]
        
    def __str__(self) -> str:
        return "".join("T"+str(i+1)+"= "+ruta.__str__()+"    " for i, ruta in enumerate(self.rutas)) + 'Costo:' + str(self.costo()) + (" F" if self.es_factible() else (" A"  if self.es_admisible() else " N"))

    def obtener_empty_solucion() -> Type["Solucion"]:
        return Solucion([Ruta(ruta[0], ruta[1]) for ruta in [[[], []] for _ in range(constantes.horizon_length)]])

    def imprimir_detalle(self) -> str:
        resp = "Clientes visitados:"+" ".join("T"+str(i+1)+"= "+ruta.__str__()+"\t" for i, ruta in enumerate(self.rutas)) + "\n"
        resp += 'Inventario de proveedor: ' + str(self.obtener_niveles_inventario_proveedor()) + "\n"
        resp += 'Inventario de clientes: ' + str(self.obtener_niveles_inventario_clientes()) + "\n"
        resp += '¿Admisible? : ' + ('SI' if self.es_admisible() else 'NO') + "\n"
        resp += '¿Factible? : ' + ('SI' if self.es_factible() else 'NO') + "\n"
        resp += 'Función objetivo: ' + str(self.costo()) + "\n"
        print(resp)
    
    def to_json(self, iteration, tag):   
        return {
            "proveedor_id":str(constantes.proveedor.id), 
            "iteration":iteration,
            "tag":tag,
            "rutas":{i:ruta.to_json() for i, ruta in enumerate(self.rutas)},
            "costo": self.costo()
        }

    def clonar(self) -> Type["Solucion"]:
        return Solucion([ruta.clonar() for ruta in self.rutas])

    def es_igual(self, solution2) -> bool:
        return all(self.rutas[i].es_igual(solution2.rutas[i]) for i in range(constantes.horizon_length))
        
    def es_admisible(self) -> bool:
        return not (self.cliente_tiene_desabastecimiento() or self.cliente_tiene_sobreabastecimiento())

    def es_factible(self) -> bool:
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
        return any(constantes.capacidad_vehiculo < ruta.obtener_total_entregado() for ruta in self.rutas)

    def cliente_tiene_desabastecimiento(self) -> bool:
        return any(self.obtener_niveles_inventario_cliente(cliente)[tiempo] < 0
                   for cliente in constantes.clientes
                   for tiempo in range(constantes.horizon_length))

    def cliente_tiene_sobreabastecimiento(self) -> bool:
        return any(self.obtener_niveles_inventario_cliente(cliente)[tiempo] > cliente.nivel_maximo
                   for cliente in constantes.clientes
                   for tiempo in range(constantes.horizon_length))
    
    def proveedor_tiene_desabastecimiento(self) -> bool:
        return any(nivel_inventario < 0 for nivel_inventario in self.obtener_niveles_inventario_proveedor())
    
    def obtener_niveles_inventario_proveedor(self):
        proveedor = constantes.proveedor
        nivel_almacenamiento = proveedor.nivel_almacenamiento
        niveles = [nivel_almacenamiento]
        for t in range(1, constantes.horizon_length + 1):
            nivel_almacenamiento += proveedor.nivel_produccion - self.rutas[t-1].obtener_total_entregado()
            niveles.append(nivel_almacenamiento)
        nivel_almacenamiento += proveedor.nivel_produccion
        niveles.append(nivel_almacenamiento)
        return niveles
    
    def obtener_niveles_inventario_cliente(self, cliente):
        nivel_almacenamiento = cliente.nivel_almacenamiento
        cliente_inventario = [nivel_almacenamiento]
        for t in range(1, constantes.horizon_length + 1):
            nivel_almacenamiento += self.rutas[t-1].obtener_cantidad_entregada(cliente) - cliente.nivel_demanda
            cliente_inventario.append(nivel_almacenamiento)          
        return cliente_inventario
           
    def obtener_niveles_inventario_clientes(self):
        return [self.obtener_niveles_inventario_cliente(cliente) for cliente in constantes.clientes]

    # Retorna el conjunto de tiempos donde un cliente es visitado en una solucion dada.
    def T(self, cliente):
        return [tiempo for tiempo in range(constantes.horizon_length) if self.rutas[tiempo].es_visitado(cliente)]
   
    def costo(self):      
        proveedor_nivel_inventario = self.obtener_niveles_inventario_proveedor()
        # First term (costo_almacenamiento)
        costo_almacenamiento = sum(proveedor_nivel_inventario) * constantes.proveedor.costo_almacenamiento
        costo_almacenamiento += sum(cliente.costo_almacenamiento * self.obtener_niveles_inventario_cliente(cliente)[tiempo]  
                for tiempo in range(constantes.horizon_length + 1)
                for cliente in constantes.clientes)
            
        # Second term (costo_transporte)
        costo_transporte = sum(self.rutas[tiempo].obtener_costo() for tiempo in range(constantes.horizon_length))

        # Third term (penalty 1)
        penalty1 = sum(max(0,self.rutas[tiempo].obtener_total_entregado() - constantes.capacidad_vehiculo) 
                       for tiempo in range(constantes.horizon_length)) * alpha.obtener_valor() 
        
        # Fourth term
        penalty2 = sum(max(0, -proveedor_nivel_inventario[tiempo]) 
                       for tiempo in range(constantes.horizon_length+1)) * beta.obtener_valor()
       
        return costo_almacenamiento + costo_transporte + penalty1 + penalty2
    
    def remover_visita(self, cliente, tiempo) -> None:
        # En primer lugar guardo los tiempos en que el cliente fue visitado
        tiempos_cliente = self.T(cliente)

        if (tiempo in tiempos_cliente):
            # Guardo el indice del tiempo de la eliminación, para despues acceder fácilmente al anterior y al posterior.
            index = tiempos_cliente.index(tiempo)
            
            # Primero eliminamos al cliente i de la ruta del vehículo en el tiempo t y su predecesor se enlaza con su sucesor.
            cantidad_eliminado = self.rutas[tiempo].remover_visita(cliente)
            
            # La cantidad entregada al cliente en el tiempo t se transfiere a la visita siguiente (si la hay). 
            # Tal eliminación se realiza solo si no crea un desabastecimiento en el cliente i para mantener la solución admisible.
            if (constantes.politica_reabastecimiento == "OU"):
                # Si no era el último, transfiero la cantidad entregada a la siguiente visita
                if index < len(tiempos_cliente) - 1:
                    self.rutas[index+1].agregar_cantidad_cliente(cliente, cantidad_eliminado)
                
            # Si se genera desabastecimiento en el cliente la eliminación sólo se realiza si puede evitarse aumentando la cantidad entregada
            # en la visita anterior a un valor no mayor que la capacidad máxima Ui. 
            if (constantes.politica_reabastecimiento == "ML") and self.cliente_tiene_desabastecimiento():
                # Si no era el primero, se intenta aumentar la cantidad entregada a la visita anterior a un valor que no supere Ui
                if index > 0:
                    cantidad = (cliente.nivel_maximo - self.obtener_niveles_inventario_cliente(cliente)[tiempos_cliente[index-1]])
                    self.rutas[tiempos_cliente[index-1]].agregar_cantidad_cliente(cliente, cantidad)
        
    def insertar_visita(self, cliente, tiempo) -> None:
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

    def merge_rutas(self, rutabase_indice, rutasecondary_indice) -> None:
        for cliente in self.rutas[rutasecondary_indice].clientes:
            if(not self.rutas[rutabase_indice].es_visitado(cliente)):
                self.rutas[rutabase_indice].insertar_visita(cliente, self.rutas[rutasecondary_indice].obtener_cantidad_entregada(cliente), None)
        self.rutas[rutasecondary_indice] = Ruta([],[])

    def cumple_restricciones(self, MIP, MIPcliente = None, MIPtiempo = None, operation = None):
        B   = self.obtener_niveles_inventario_proveedor()
        I   = self.obtener_niveles_inventario_clientes()
        r0  = [constantes.proveedor.nivel_produccion for t in range(constantes.horizon_length+1)]
        ri  = [c.nivel_demanda for c in constantes.clientes]
        x   = [
            [self.rutas[t].obtener_cantidad_entregada(c) for t in range(constantes.horizon_length)]
            for c in constantes.clientes
        ]
        x_np = np.array(x)
        
        theta = [
            [(1 if self.rutas[t].es_visitado(c) else 0) for t in range(constantes.horizon_length)]
            for c in constantes.clientes
        ]
        
       
        # Restricción 2: Definición del nivel de inventario del proveedor.
        if (not all([(B[t] == (B[t-1] + r0[t-1] - np.sum( x_np[:, t-1]))) for t in range(1, constantes.horizon_length+1)])):
            return 2            
        
        # Restricción 3: El nivel de inventario del proveedor debe poder satisfacer la demanda en el tiempo t.
        if (not all(B[t] >= np.sum( x_np[:, t]) for t in range(constantes.horizon_length))):
            return 3
        
        # Restricción 4: Definición del nivel de inventario de los clientes
        if (not all([(I[c][t] == (I[c][t-1] + x[c][t-1] - ri[c] ))
                for c in range(len(constantes.clientes))
                for t in range(1, constantes.horizon_length+1)]
        )):
            return 4
        
        # Restricción 5: La cantidad entregada al cliente no es menos de la necesaria para llenar el inventario.
        if (not all([(x[c][t] >= ((cliente.nivel_maximo * theta[c][t]) - I[c][t]))
            for c, cliente in enumerate(constantes.clientes)
            for t in range(constantes.horizon_length)]
        )):
            return 5
        
        # Restricción 6: La cantidad entregada al cliente no debe generar sobreabastecimiento en el cliente.
        if (not all([( x[c][t] <= (cliente.nivel_maximo - I[c][t]) )
            for c, cliente in enumerate(constantes.clientes)
            for t in range(constantes.horizon_length)]
        )):
            return 6
        
        # Restricción 7: La cantidad entregada a un cliente es menor o igual al nivel máximo de inventario si es que lo visita.
        if  (not all([( x[c][t] <= (cliente.nivel_maximo * theta[c][t]) )
            for c, cliente in enumerate(constantes.clientes)
            for t in range(constantes.horizon_length)]
        )):
            return 7
            
        # Restricción 8: La cantidad entregada a los clientes en un t dado, es menor o igual a la capacidad del camión.
        if (not all([np.sum( x_np[:, t]) <= constantes.capacidad_vehiculo for t in range(constantes.horizon_length)])):
            return 8
        
        #TO DO: 9 10 11 12 13 (Sólo MIP1)
        
        # Restricción 14: La cantidad entregada a los clientes siempre debe ser mayor o igual a cero
        if not np.all(x_np >= 0):
            return 14
        
        #Restricción 17: Theeta puede tener el valor 0 o 1
        if not all(value in [0, 1] for fila in theta for value in fila):
            return 17
        
        #TO DO: 18 19 (Sólo MIP1)
        
        
        if MIP == 2:
            v   = [
                [ (1 if ((operation == "INSERT") and (MIPtiempo == t) and (MIPcliente == c)) else 0 ) for t in range(constantes.horizon_length)]
                for c in constantes.clientes
            ]
            w   = [
                [ (1 if ((operation == "REMOVE") and (MIPtiempo == t) and (MIPcliente == c)) else 0 ) for t in range(constantes.horizon_length)]
                for c in constantes.clientes
            ]
            
            # Restricción 21: v_it no puede ser 1 y theta 1, implicaría que se insertó y está presente ¿¿??
            if not all([ ( v[c][t] <= ( 1 - theta[c][t]) )
                for c in range(len(constantes.clientes))
                for t in range(constantes.horizon_length)]
            ):
                return 21
            
            # Restricción 22:  w_it no puede ser 1 y theta 0, implicaría que se borró y no está presente ¿¿??
            if not all([ ( w[c][t] <= theta[c][t] )
                for c in range(len(constantes.clientes))
                for t in range(constantes.horizon_length)]
            ):
                return 22
    
            # Restricción 23: La cantidad entregada al cliente i no puede ser mayor a la capacidad máxima
            if not all([ ( x[c][t] <= (cliente.nivel_maximo * (theta[c][t] + v[c][t] - w[c][t])))
                for c, cliente in enumerate(constantes.clientes)
                for t in range(constantes.horizon_length)]
            ):
                return 23
            
            #Restricción 24: v_it debe ser 0 o 1
            if not all(value in [0, 1] for fila in v for value in fila):
                return 24
            
            #Restricción 25: w_it debe ser 0 o 1
            if not all(value in [0, 1] for fila in w for value in fila):
                return 25
            
        return 0
            
    # def graficar_rutas(self):
    #     clients_coords = []
    #     for tiempo in range(constantes.horizon_length):
    #         x = [cliente.coord_x for cliente in self.rutas[tiempo].clientes]
    #         y = [cliente.coord_y for cliente in self.rutas[tiempo].clientes]
    #         clients_coords.append([x,y])
 
    #     # Create a figure and subplots
    #     fig, axes = plt.subplots(2, 2, figsize=(10, 6))  # Adjust rows, columns, and figure size

    #     # Generate and display plots in each subplot
    #     for i, (ax, client_coord) in enumerate(zip(axes.flat, clients_coords)):
    #         x = [constantes.proveedor.coord_x]+client_coord[0]+[constantes.proveedor.coord_x]
    #         y = [constantes.proveedor.coord_y]+client_coord[1]+[constantes.proveedor.coord_y]
    #         ax.plot(x,y)
    #         ax.set_title(f"Ruta {i+1}")

    #     # Adjust layout and display all plots at once
    #     plt.tight_layout()
    #     plt.show()