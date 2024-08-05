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
        nivel_almacenamiento = constantes.proveedor.nivel_almacenamiento
        niveles = [nivel_almacenamiento]
        for t in range(constantes.horizon_length):
            nivel_almacenamiento = nivel_almacenamiento + constantes.proveedor.nivel_produccion - self.rutas[t-1].obtener_total_entregado()
            niveles.append(nivel_almacenamiento)
        return niveles
    
    def obtener_niveles_inventario_cliente(self, cliente):
        cliente_inventario = [cliente.nivel_almacenamiento]
        for tiempo in range(1, constantes.horizon_length):
            cliente_inventario.append(cliente_inventario[tiempo-1] + self.rutas[tiempo-1].obtener_cantidad_entregada(cliente) - cliente.nivel_demanda)          
        cliente_inventario.append(cliente_inventario[tiempo] - cliente.nivel_demanda)
        return cliente_inventario
           
    def obtener_niveles_inventario_clientes(self):
        return {cliente.id:self.obtener_niveles_inventario_cliente(cliente) for cliente in constantes.clientes}

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

    def remover_visita(self, cliente, tiempo):
        # Cuando eliminamos una visita al cliente i en el tiempo t, primero eliminamos al cliente i de la ruta del vehículo en el tiempo t, 
        # y su predecesor se enlaza con su sucesor.
        self.rutas[tiempo].remover_visita(cliente)
        
    # Cuando insertamos una visita al cliente en el tiempo t, primero añadimos al cliente a la ruta del vehículo en el tiempo t usando el método de inserción más barato.
    def insertar_visita(self, cliente, tiempo):
        cantidad_entregada = min(
            cliente.nivel_maximo - self.obtener_niveles_inventario_cliente(cliente)[tiempo],
            constantes.capacidad_vehiculo - self.rutas[tiempo].obtener_total_entregado(),
            self.obtener_niveles_inventario_proveedor()[tiempo]
        )
        self.rutas[tiempo].insertar_visita(cliente, (cantidad_entregada if (cantidad_entregada > 0) else cliente.nivel_demanda), None)

    def merge_rutas(self, rutabase_indice, rutasecondary_indice) -> None:
        for cliente in self.rutas[rutasecondary_indice].clientes:
            if(not self.rutas[rutabase_indice].es_visitado(cliente)):
                self.rutas[rutabase_indice].insertar_visita(cliente, self.rutas[rutasecondary_indice].obtener_cantidad_entregada(cliente), None)
            # else:
            #     self.rutas[rutabase_indice].agregar_cantidad_cliente(cliente, self.rutas[rutasecondary_indice].obtener_cantidad_entregada(cliente))
        self.rutas[rutasecondary_indice] = Ruta([],[])


    def cumple_restricciones(self, MIP, MIPcliente = None, MIPtiempo = None, operation = None): 
        niveles_inventario_proveedor = self.obtener_niveles_inventario_proveedor()
        for tiempo in range(constantes.horizon_length):
            
            # Restricción 3: La cantidad entregada en t, es menor o igual al nivel de inventario del proveedor en t.
            if niveles_inventario_proveedor[tiempo] < self.rutas[tiempo].obtener_total_entregado():
                return 3
            
            for cliente in constantes.clientes:
                theeta = 1 if self.rutas[tiempo].es_visitado(cliente) else 0
                niveles_inventario_cliente = self.obtener_niveles_inventario_cliente(cliente)
                xij = self.rutas[tiempo].obtener_cantidad_entregada(cliente)
                
                # Restricción 5: La cantidad entregada a un cliente en un tiempo dado es mayor o igual a la capacidad máxima menos el nivel de inventario (si lo visita en el tiempo dado).
                if (constantes.politica_reabastecimiento == "OU") and (xij < ((cliente.nivel_maximo * theeta) - niveles_inventario_cliente[tiempo])):
                    return 5
                
                # Restricción 6: La cantidad entregada a un cliente en un tiempo dado debe ser menor o igual a la capacidad máxima menos el nivel de inventario (Junto con C5, definen OU)
                if xij > (cliente.nivel_maximo - niveles_inventario_cliente[tiempo]):
                    return 6
                
                # Restricción 7: La cantidad entregada a un cliente es menor o igual al nivel máximo de inventario si es que lo visita.
                if (constantes.politica_reabastecimiento == "OU") and (xij > (cliente.nivel_maximo * theeta)):
                    return 7
                
                # Restricción 8: La cantidad entregada a los clientes en un tiempo dado, es menor o igual a la capacidad del camión.
                if self.rutas[tiempo].obtener_total_entregado() > constantes.capacidad_vehiculo:
                    return 8
                
                # Restricción 14: La cantidad entregada a los clientes siempre debe ser mayor a cero
                if (self.rutas[tiempo].es_visitado(cliente) and (xij <= 0)):
                    return 14
                
                #Restricción 17: Theeta puede tener el valor 0 o 1
                if theeta not in [0, 1]:
                    return 17
        
        #Restriccións 9 -13: #TODO (IMPORTANTE: SON SOLO DE MIP1)
        if (MIP == 1):
            for ruta in self.rutas:
                for ruta2 in self.rutas:
                    if (ruta != ruta2) and ruta.es_igual(ruta2):
                            return 9
                    
        # Restricciones 18 y 19 son obvias     
        for tiempo in range(constantes.horizon_length + 1):
            for cliente in constantes.clientes:
                niveles_inventario_cliente = self.obtener_niveles_inventario_cliente(cliente)
                 
                # Restricción 4
                if (tiempo != 0) and (niveles_inventario_cliente[tiempo] != (niveles_inventario_cliente[tiempo-1] + self.rutas[tiempo-1].obtener_cantidad_entregada(cliente) - cliente.nivel_demanda)):
                    return 4

                # Restricción 15: No puede haber desabastecimiento
                if (tiempo < constantes.horizon_length) and (niveles_inventario_cliente[tiempo] < 0):
                    return 15
                
            #Restricción 16: No puede haber desabastecimiento en el proveedor
            if self.obtener_niveles_inventario_proveedor()[tiempo] < 0:
                return 16

        if (MIP == 2):
            v_it = 1 if (operation == "INSERT") else 0
            w_it = 1 if (operation == "REMOVE") else 0
            sigma_it = 1 if self.rutas[MIPtiempo].es_visitado(MIPcliente) else 0
            
            #Restricción 18: w_it debe ser 0 o 1
            if w_it not in [0, 1]:
                return 18
            
            # Restricción 21: v_it no puede ser 1 y sigma_it 1, implicaría que se insertó y está presente ¿¿??
            if v_it >( 1 - sigma_it):
                return 21
            
            # Restricción 22:  w_it no puede ser 1 y sigma_it 0, implicaría que se borró y no está presente ¿¿??
            if w_it > sigma_it:
                return 22
            
            # Restricción 23: La cantidad entregada al cliente i no puede ser mayor a la capacidad máxima
            if self.rutas[MIPtiempo].obtener_cantidad_entregada(MIPcliente) > (MIPcliente.nivel_maximo * (sigma_it - w_it + v_it)):
                return 23
            
            #Restricción 24: v_it debe ser 0 o 1
            if not v_it in [0,1]:
                return 24
            
            #Restricción 25: w_it debe ser 0 o 1
            if not w_it in [0,1]:
                return 25
        return 0

    def draw_rutas(self):
        clients_coords = []
        for tiempo in range(constantes.horizon_length):
            x = [cliente.coord_x for cliente in self.rutas[tiempo].clientes]
            y = [cliente.coord_y for cliente in self.rutas[tiempo].clientes]
            clients_coords.append([x,y])
        Graph.draw_rutas(clients_coords,[constantes.proveedor.coord_x, constantes.proveedor.coord_y])