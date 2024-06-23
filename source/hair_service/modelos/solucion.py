from graph import Graph
from modelos.ruta import Ruta
from typing import Type
from modelos.penalty_variables import alpha, beta
from constantes import constantes

class Solucion():
  
    def __init__(self,  rutas: list[Ruta] = None) -> None:
        self.rutas = rutas if rutas else [Ruta for _ in range(constantes.horizon_length)]
        
    def __str__(self) -> str:
        return "".join("T"+str(i+1)+"= "+ruta.__str__()+"    " for i, ruta in enumerate(self.rutas)) + 'Costo:' + str(self.costo())

    def imprimir_detalle(self) -> str:
        resp = "Clientes visitados:"+" ".join("T"+str(i+1)+"= "+ruta.__str__()+"\t" for i, ruta in enumerate(self.rutas)) + "\n"
        resp += 'Inventario de proveedor: ' + str(self.obtener_niveles_inventario_proveedor()) + "\n"
        resp += 'Inventario de clientes: ' + str(self.obtener_niveles_inventario_clientes()) + "\n"
        # resp += '¿Desabastecimiento? (cliente) : ' + ('SI' if self.cliente_tiene_desabastecimiento() else 'NO') + "\n"
        # resp += '¿Sobreabastecimiento? (cliente) : ' + ('SI' if self.cliente_tiene_sobreabastecimiento() else 'NO') + "\n"
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
                   for tiempo in range(constantes.horizon_length+1))

    def cliente_tiene_sobreabastecimiento(self) -> bool:
        return any(self.obtener_niveles_inventario_cliente(cliente)[tiempo] > cliente.nivel_maximo
                   for cliente in constantes.clientes
                   for tiempo in range(constantes.horizon_length+1))
    
    def proveedor_tiene_desabastecimiento(self) -> bool:
        return any(nivel_inventario < 0 for nivel_inventario in self.obtener_niveles_inventario_proveedor())
    
    def obtener_niveles_inventario_proveedor(self):
        return [self.B(t) for t in range(constantes.horizon_length+1)]
     
    def B(self, t):
        return (
            self.B(t-1) + constantes.proveedor.nivel_produccion - self.rutas[t-1].obtener_total_entregado()
            if t > 0
            else constantes.proveedor.nivel_almacenamiento
        )
    
    def obtener_niveles_inventario_cliente(self, cliente):
        cliente_inventario = [cliente.nivel_almacenamiento]
        for tiempo in range(1, constantes.horizon_length +1):
            cliente_inventario.append(cliente_inventario[tiempo-1] + self.rutas[tiempo-1].obtener_cantidad_entregada(cliente) - cliente.nivel_demanda)          
        return cliente_inventario
           
    def obtener_niveles_inventario_clientes(self):
        return {cliente.id:self.obtener_niveles_inventario_cliente(cliente) for cliente in constantes.clientes}

    # Retorna el conjunto de tiempos donde un cliente es visitado en una solucion dada.
    def T(self, cliente):
        return [tiempo for tiempo in range(constantes.horizon_length) if self.rutas[tiempo].es_visitado(cliente)]
   
    def costo(self):
        if not any(len(ruta.clientes) > 0 for ruta in self.rutas):
            return float("inf")
        
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

    def remover_visita(self, cliente, tiempo):
        cantidad_eliminado = self.rutas[tiempo].remover_visita(cliente)
        if constantes.politica_reabastecimiento == "OU":
            for t in range(tiempo + 1, constantes.horizon_length):
                if self.rutas[t].es_visitado(cliente):
                    self.rutas[t].agregar_cantidad_cliente(cliente, cantidad_eliminado)
                    break
        elif constantes.politica_reabastecimiento == "ML":   
            if self.cliente_tiene_desabastecimiento():
                for t2 in range(tiempo, -1, -1):
                    if self.rutas[t2].es_visitado(cliente):
                        cantidad = cliente.nivel_maximo - self.obtener_niveles_inventario_cliente(cliente)[t2]
                        self.rutas[t2].agregar_cantidad_cliente(cliente, cantidad)
                        break
        
    def insertar_visita(self, cliente, tiempo):
        if constantes.politica_reabastecimiento == "OU":
            cantidad_entregada = cliente.nivel_maximo - self.obtener_niveles_inventario_cliente(cliente)[tiempo]
            self.rutas[tiempo].insertar_visita(cliente, cantidad_entregada, None)
            for t in range(tiempo + 1, constantes.horizon_length):
                if self.rutas[t].es_visitado(cliente):
                    self.rutas[t].quitar_cantidad_cliente(cliente, cantidad_entregada)
                    break
        elif constantes.politica_reabastecimiento == "ML":
            cantidad_entregada = min(
                cliente.nivel_maximo - self.obtener_niveles_inventario_cliente(cliente)[tiempo],
                constantes.capacidad_vehiculo - self.rutas[tiempo].obtener_total_entregado(),
                self.B(tiempo)
            )
            cantidad_entregada = cantidad_entregada if cantidad_entregada > 0 else cliente.nivel_demanda
            self.rutas[tiempo].insertar_visita(cliente, cantidad_entregada, None)

    def merge_rutas(self, rutabase_indice, rutasecondary_indice) -> None:
        self.rutas[rutabase_indice].clientes.extend(self.rutas[rutasecondary_indice].clientes)
        self.rutas[rutabase_indice].cantidades.extend(self.rutas[rutasecondary_indice].cantidades)
        self.rutas[rutasecondary_indice] = Ruta([],[])


    def cumple_restricciones(self, MIP, MIPcliente = None, MIPtiempo = None, operation = None): 
        for tiempo in range(constantes.horizon_length):
            # Constraint 3: La cantidad entregada en t, es menor o igual al nivel de inventario del proveedor en t.
            if self.B(tiempo) < self.rutas[tiempo].obtener_total_entregado():
                return False
            for cliente in constantes.clientes:
                theeta = 1 if self.rutas[tiempo].es_visitado(cliente) else 0
                #Constraint 17: Theeta puede tener el valor 0 o 1
                if theeta not in [0, 1]:
                    return False
                # Constraint 5: La cantidad entregada a un cliente en un tiempo dado es mayor o igual a la capacidad máxima menos el nivel de inventario (si lo visita en el tiempo dado).
                if constantes.politica_reabastecimiento == "OU" and (self.rutas[tiempo].obtener_cantidad_entregada(cliente) < (cliente.nivel_maximo * theeta) - self.obtener_niveles_inventario_cliente(cliente)[tiempo]):
                    return False
                # Constraint 6: La cantidad entregada a un cliente en un tiempo dado debe ser menor o igual a la capacidad máxima menos el nivel de inventario (Junto con C5, definen OU)
                if self.rutas[tiempo].obtener_cantidad_entregada(cliente) > cliente.nivel_maximo - self.obtener_niveles_inventario_cliente(cliente)[tiempo]:
                    return False
                # Constraint 7: La cantidad entregada a un cliente es menor o igual al nivel máximo de inventario si es que lo visita.
                if constantes.politica_reabastecimiento == "OU" and (self.rutas[tiempo].obtener_cantidad_entregada(cliente) > cliente.nivel_maximo * theeta):
                    return False
                # Constraint 8: La cantidad entregada a los clientes en un tiempo dado, es menor o igual a la capacidad del camión.
                if self.rutas[tiempo].obtener_total_entregado() > constantes.capacidad_vehiculo:
                    return False
                # Constraint 14: La cantidad entregada a los clientes siempre debe ser mayor a cero
                if self.rutas[tiempo].obtener_cantidad_entregada(cliente) < 0:
                    return False
        
        # #Constraints 9 -13: #TODO (IMPORTANTE: SON SOLO DE MIP1)
        # #Constraints 17 -19 son obvias     
        for tiempo in range(constantes.horizon_length+1):
            for cliente in constantes.clientes:
                # Constraint 4
                if tiempo == 0:
                    if self.obtener_niveles_inventario_cliente(cliente)[tiempo] != cliente.nivel_almacenamiento:
                        return False
                else:
                    if self.obtener_niveles_inventario_cliente(cliente)[tiempo] != self.obtener_niveles_inventario_cliente(cliente)[tiempo-1] + self.rutas[tiempo-1].obtener_cantidad_entregada(cliente) - cliente.nivel_demanda:
                        return False

                # Constraint 15: No puede haber desabastecimiento
                if self.obtener_niveles_inventario_cliente(cliente)[tiempo] <= 0:
                    return False
            #Constraint 16: No puede haber desabastecimiento en el proveedor
            if self.B(tiempo) < 0:
                return False

        if MIP == "MIP2":
            v_it = 1 if (operation == "INSERT") else 0
            w_it = 1 if (operation == "REMOVE") else 0
            sigma_it = 1 if self.rutas[MIPtiempo].es_visitado(MIPcliente) else 0
            #Constraint 18: w_it debe ser 0 o 1
            if w_it not in [0, 1]:
                return False
            # Constraint 21: v_it no puede ser 1 y sigma_it 1, implicaría que se insertó y está presente ¿¿??
            if v_it > 1 - sigma_it:
                return False
            # Constraint 22:  w_it no puede ser 1 y sigma_it 0, implicaría que se borró y no está presente ¿¿??
            if w_it > sigma_it:
                return False
            # Constraint 23: La cantidad entregada al cliente i no puede ser mayor a la capacidad máxima
            if self.rutas[MIPtiempo].obtener_cantidad_entregada(MIPcliente) > MIPcliente.nivel_maximo * (sigma_it - w_it + v_it):
                return False
            #Constraint 24: v_it debe ser 0 o 1
            if not v_it in [0,1]:
                return False
            #Constraint 25: w_it debe ser 0 o 1
            if not w_it in [0,1]:
                return False
        return True

    def draw_rutas(self):
        clients_coords = []
        for tiempo in range(constantes.horizon_length):
            x = [cliente.coord_x for cliente in self.rutas[tiempo].clientes]
            y = [cliente.coord_y for cliente in self.rutas[tiempo].clientes]
            clients_coords.append([x,y])
        Graph.draw_rutas(clients_coords,[constantes.proveedor.coord_x, constantes.proveedor.coord_y])