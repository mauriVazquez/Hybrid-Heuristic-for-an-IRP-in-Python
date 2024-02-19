from graph import Graph
from modelos.ruta import Ruta
from entidades_manager import EntidadesManager
from typing import Type
from modelos.penalty_variables import alpha, beta
from modelos.tabulists import tabulists
from modelos.mip1 import Mip1
from modelos.mip2 import Mip2
from tsp_local.base import TSP
from tsp_local.kopt import KOpt

def LK(solucion: Type["Solucion"], solucion_prima: Type["Solucion"]) -> Type["Solucion"]:
    aux_solucion = solucion.clonar()
    if solucion != solucion_prima:
        aux_solucion = solucion_prima.clonar()
        for tiempo in range(EntidadesManager.obtener_parametros().horizon_length):
            tamano_matriz = len(solucion_prima.rutas[tiempo].clientes)+1
            matriz =  [[0] * tamano_matriz for _ in range(tamano_matriz)]

            # Proveedor distancia
            for indice, cliente in enumerate(solucion_prima.rutas[tiempo].clientes):
                matriz[0][indice+1] = cliente.distancia_proveedor
                matriz[indice+1][0] = cliente.distancia_proveedor

            # Clientes distancias
            for indice, c in enumerate(solucion_prima.rutas[tiempo].clientes):
                for indice2, c2 in enumerate(solucion_prima.rutas[tiempo].clientes):
                    matriz[indice+1][indice2+1] = EntidadesManager.obtener_matriz_clientes()[c.id][c2.id]

            # Make an instance with all nodes
            TSP.setEdges(matriz)
            path, costo = KOpt(range(len(matriz))).optimise()
            
            aux_solucion.rutas[tiempo] = Ruta(
                [solucion_prima.rutas[tiempo].clientes[indice - 1] for indice in path[1:]],
                [solucion_prima.rutas[tiempo].cantidades[indice - 1] for indice in path[1:]]
            )
    aux_solucion.refrescar()
    return aux_solucion if aux_solucion.costo < solucion_prima.costo else solucion_prima

class Solucion():
    @staticmethod
    def obtener_empty_solucion() -> Type["Solucion"]:
        return Solucion([Ruta(ruta[0], ruta[1]) for ruta in [[[], []] for _ in range(EntidadesManager.obtener_parametros().horizon_length)]])

    @staticmethod
    def inicializar():
        solucion = Solucion.obtener_empty_solucion()
        for cliente in EntidadesManager.obtener_clientes():
            nivel_inicial, nivel_demanda = cliente.nivel_inicial, cliente.nivel_demanda
            min_nivel, max_nivel = cliente.min_nivel, cliente.max_nivel
            #Se calcula el tiempo en que sucederá el primer stockout, y la frecuencia del mismo.
            tiempo_stockout = (nivel_inicial - min_nivel) // nivel_demanda -1
            stockout_frequency = (max_nivel - min_nivel) // nivel_demanda
            #Se visita al cliente en el primer stock
            solucion.rutas[tiempo_stockout].insertar_visita(cliente, 
                    max_nivel - (nivel_inicial - nivel_demanda * (tiempo_stockout+1)),
                    len(solucion.rutas[tiempo_stockout].clientes))
            #Se calculan todos los tiempos dentro del horizonte donde ocurrirá el stockout y se agrega la visita.
            for t in range(tiempo_stockout+stockout_frequency, EntidadesManager.obtener_parametros().horizon_length, stockout_frequency):
                solucion.rutas[t].insertar_visita(cliente, max_nivel, len(solucion.rutas[t].clientes))
        solucion.refrescar()
        print(f"Inicio {solucion}")
        return solucion
    
    def __init__(self,  rutas: list[Ruta] = None) -> None:
        self.rutas = rutas if rutas else [Ruta for _ in range(EntidadesManager.obtener_parametros().horizon_length)]
        self.costo = self.funcion_objetivo()
        
    def __str__(self) -> str:
        return "".join("T"+str(i+1)+"= "+ruta.__str__()+"    " for i, ruta in enumerate(self.rutas)) + 'Costo:' + str(self.costo)

    def  detail(self) -> str:
        resp = "Clientes visitados:"+" ".join("T"+str(i+1)+"= "+ruta.__str__()+"\t" for i, ruta in enumerate(self.rutas))
        resp += '\nObjective function: ' + str(self.costo) + "\n"
        resp += 'Proveedor inventario: ' + str(self.obtener_niveles_inventario_proveedor()) + "\n"
        resp += 'Clientes inventario: ' + str(self.obtener_niveles_inventario_clientes()) + "\n"
        resp += 'Situación de Stockout? : ' + ('yes' if self.cliente_tiene_stockout() else 'no') + "\n"
        resp += 'Situacion de Overstock? : ' + ('yes' if self.cliente_tiene_overstock() else 'no') + "\n"
        return resp
    
    def refrescar(self):
        self.costo = self.funcion_objetivo()

    def clonar(self) -> Type["Solucion"]:
        return Solucion([ruta.clonar() for ruta in self.rutas])

    def es_admisible(self) -> bool:
        return not (self.cliente_tiene_stockout() or self.cliente_tiene_overstock())

    def es_factible(self) -> bool:
        return self.es_admisible() and (not self.proveedor_tiene_stockout()) and (not self.es_excedida_capacidad_vehiculo())

    def es_excedida_capacidad_vehiculo(self) -> bool:
        return any(ruta.es_excedida_capacidad_vehiculo() for ruta in self.rutas)

    def cliente_tiene_stockout(self) -> bool:
        return any(self.obtener_niveles_inventario_cliente(cliente)[tiempo] < 0
                   for cliente in EntidadesManager.obtener_clientes()
                   for tiempo in range(EntidadesManager.obtener_parametros().horizon_length+1))

    def cliente_tiene_overstock(self) -> bool:
        return any(self.obtener_niveles_inventario_cliente(cliente)[tiempo] > cliente.max_nivel
                   for cliente in EntidadesManager.obtener_clientes()
                   for tiempo in range(EntidadesManager.obtener_parametros().horizon_length))
    
    def proveedor_tiene_stockout(self) -> bool:
        return any(nivel_inventario < 0 for nivel_inventario in self.obtener_niveles_inventario_proveedor())
    
    def obtener_niveles_inventario_proveedor(self):
        return [self.B(t) for t in range(EntidadesManager.obtener_parametros().horizon_length+1)]
     
    def B(self, t):
        return (
            self.B(t-1) + EntidadesManager.obtener_proveedor().nivel_produccion - self.rutas[t-1].obtener_total_entregado()
            if t > 0
            else EntidadesManager.obtener_proveedor().nivel_inicial
        )
    
    def obtener_niveles_inventario_cliente(self, cliente):
        cliente_inventario = [cliente.nivel_inicial]
        for tiempo in range(1, EntidadesManager.obtener_parametros().horizon_length +1):
            cliente_inventario.append(cliente_inventario[tiempo-1] + self.rutas[tiempo-1].obtener_cantidad_entregada(cliente) - cliente.nivel_demanda)          
        return cliente_inventario
           
    def obtener_niveles_inventario_clientes(self):
        return {cliente.id:self.obtener_niveles_inventario_cliente(cliente) for cliente in EntidadesManager.obtener_clientes()}

    # Retorna the set of tiempos when is visitado a cliente in a given solucion.
    def T(self, cliente):
        return [tiempo for tiempo in range(EntidadesManager.obtener_parametros().horizon_length) if self.rutas[tiempo].es_visitado(cliente)]
    
    def mover(self) -> Type["Solucion"]:
        return min(self.neighborhood(), key=lambda neighbor: neighbor.costo, default=self.clonar())
    
    def mejorar(self):
        do_continue = True
        solucion_best = self.clonar()
        solucion_best = LK(Solucion.obtener_empty_solucion(), solucion_best)
        while do_continue:
            solucion_best.refrescar()
            do_continue = False

            #PRIMER TIPO DE MEJORA
            #Se aplica el MIP1 a solucion_best, luego se le aplica LK
            solucion_prima = Mip1.ejecutar(solucion_best)
            solucion_prima = LK(solucion_best, solucion_prima)
            
            #Si el costo de la solución encontrada es mejor que el de solucion_best, se actualiza solucion_best
            if solucion_prima.costo < solucion_best.costo:
                #print(f"first improvement: {solucion_prima.costo}")
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
                    solucion_prima = LK(s1, aux_solucion)
                    if solucion_prima.costo < solucion_merge.costo:
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
                    solucion_prima = LK(s2, solucion_prima)
                    #En este punto solucion_merge es la mejor solución entre solucion_best y la primer parte de esta mejora.
                    if solucion_prima.costo < solucion_merge.costo:
                        solucion_merge = solucion_prima.clonar()
            #Si el costo de solucion_merge es mejor que el de solucion_best, se actualiza el valor de solucion_best
            if solucion_merge.costo < solucion_best.costo:
                #print(f"second improvement: {solucion_merge.costo}")
                solucion_best = solucion_merge.clonar()
                do_continue = True

            #TERCER TIPO DE MEJORA
            #Se aplica el MIP2 a solucion_best, luego se le aplica LK
            solucion_prima = Mip2.ejecutar(solucion_best)
            solucion_prima = LK(solucion_best, solucion_prima)
            if solucion_prima.costo < solucion_best.costo:
                #print(f"Third improvement: {solucion_prima.costo}")
                solucion_best = solucion_prima.clonar()
                do_continue = True 
        #print(f"sbest despues de improvement {solucion_best}")
        return solucion_best.clonar()

    def saltar(self, triplet) -> Type["Solucion"]:
        new_solucion = self.clonar()
        cliente, tiempo_visitado, tiempo_not_visitado = triplet  
        if self.rutas[tiempo_visitado].es_visitado(cliente) and (not self.rutas[tiempo_not_visitado].es_visitado(cliente)):    
            cantidad_eliminado = new_solucion.rutas[tiempo_visitado].remover_visita(cliente)
            new_solucion.rutas[tiempo_not_visitado].insertar_visita(cliente, cantidad_eliminado, None)
       
        new_solucion.refrescar()
        return new_solucion
    
    def neighborhood(self) -> list[Type["Solucion"]]:
        return (
            self.variante_eliminacion()
            + self.variante_insercion()
            + self.variante_mover_visita()
            + self.variante_intercambiar_visitas()
        )
   
    def funcion_objetivo(self):
        if not any(len(ruta.clientes) > 0 for ruta in self.rutas):
            return float("inf")
        
        proveedor_nivel_inventario = self.obtener_niveles_inventario_proveedor()
    
        # First term (costo_almacenamiento)
        costo_almacenamiento = sum(proveedor_nivel_inventario) * EntidadesManager.obtener_proveedor().costo_almacenamiento
        costo_almacenamiento += sum(cliente.costo_almacenamiento * self.obtener_niveles_inventario_cliente(cliente)[tiempo]  
                for tiempo in range(EntidadesManager.obtener_parametros().horizon_length + 1)
                for cliente in EntidadesManager.obtener_clientes())
            
        # Second term (costo_transporte)
        costo_transporte = sum(self.rutas[tiempo].obtener_costo() for tiempo in range(EntidadesManager.obtener_parametros().horizon_length))

        # Third term (penalty 1)
        penalty1 = sum(max(0,self.rutas[tiempo].obtener_total_entregado() - EntidadesManager.obtener_vehiculo().capacidad) 
                       for tiempo in range(EntidadesManager.obtener_parametros().horizon_length)) * alpha.obtener_valor() 
        
        # Fourth term
        penalty2 = sum(max(0, -proveedor_nivel_inventario[tiempo]) 
                       for tiempo in range(EntidadesManager.obtener_parametros().horizon_length+1)) * beta.obtener_valor()
       
        return costo_almacenamiento + costo_transporte + penalty1 + penalty2

    def remover_visita(self, cliente, tiempo):
        cantidad_eliminado = self.rutas[tiempo].remover_visita(cliente)
        if EntidadesManager.obtener_parametros().politica_reabastecimiento == "OU":
            for t in range(tiempo + 1, EntidadesManager.obtener_parametros().horizon_length):
                if self.rutas[t].es_visitado(cliente):
                    self.rutas[t].agregar_cantidad_cliente(cliente, cantidad_eliminado)
                    break
        elif EntidadesManager.obtener_parametros().politica_reabastecimiento == "ML":
            if self.cliente_tiene_stockout():
                for tinverso in range(tiempo):
                    t2 = tiempo - tinverso
                    if self.rutas[t2].es_visitado(cliente):
                        cantidad = cliente.max_nivel - self.obtener_niveles_inventario_cliente(cliente)[t2]
                        self.rutas[t2].agregar_cantidad_cliente(cliente, cantidad)
                        break
        self.refrescar()

    def insertar_visita(self, cliente, tiempo):
        if EntidadesManager.obtener_parametros().politica_reabastecimiento == "OU":
            cantidad_delivered = cliente.max_nivel - self.obtener_niveles_inventario_cliente(cliente)[tiempo]
            self.rutas[tiempo].insertar_visita(cliente, cantidad_delivered, None)
            for t in range(tiempo + 1, EntidadesManager.obtener_parametros().horizon_length):
                if self.rutas[t].es_visitado(cliente):
                    self.rutas[t].quitar_cantidad_cliente(cliente, cantidad_delivered)
                    break
        elif EntidadesManager.obtener_parametros().politica_reabastecimiento == "ML":
            cantidad_delivered = min(
                cliente.max_nivel - self.obtener_niveles_inventario_cliente(cliente)[tiempo],
                EntidadesManager.obtener_vehiculo().capacidad - self.rutas[tiempo].obtener_total_entregado(),
                self.B(tiempo)
            )
            cantidad_delivered = cantidad_delivered if cantidad_delivered > 0 else cliente.nivel_demanda
            self.rutas[tiempo].insertar_visita(cliente, cantidad_delivered, None)
        self.refrescar()

    def variante_eliminacion(self) -> list[Type["Solucion"]]:
        neighborhood_prima = []
        for cliente in EntidadesManager.obtener_clientes():
            # La eliminación del cliente parece ser interesante cuando hi>h0
            if cliente.costo_almacenamiento > EntidadesManager.obtener_proveedor().costo_almacenamiento:
                for tiempo in range(EntidadesManager.obtener_parametros().horizon_length):
                    solucion_copy = self.clonar()
                    if (solucion_copy.rutas[tiempo].es_visitado(cliente)):
                        solucion_copy.remover_visita(cliente, tiempo)
                        if solucion_copy.es_admisible() and (not tabulists.esta_prohibido_quitar(cliente.id, tiempo)):# or solucion_copy.costo < EntidadesManager.obtener_parametros().multiplicador_tolerancia * self.costo):
                            solution_append = solucion_copy.clonar()
                            solution_append.refrescar()
                            neighborhood_prima.append(solution_append)
        return neighborhood_prima

    def variante_insercion(self) -> list[Type["Solucion"]]:
        neighborhood_prima = []
        for cliente in EntidadesManager.obtener_clientes():
            for tiempo in range(EntidadesManager.obtener_parametros().horizon_length):
                solucion_copy = self.clonar()
                if (not solucion_copy.rutas[tiempo].es_visitado(cliente)):
                    solucion_copy.insertar_visita(cliente, tiempo)
                    if solucion_copy.es_admisible() and (not tabulists.esta_prohibido_agregar(cliente, tiempo) ):#or solucion_copy.costo < EntidadesManager.obtener_parametros().multiplicador_tolerancia * self.costo):
                        solution_append = solucion_copy.clonar()
                        solution_append.refrescar()
                        neighborhood_prima.append(solution_append)
        return neighborhood_prima

    def variante_mover_visita(self) -> list[Type["Solucion"]]:
        neighborhood_prima = []
        for cliente in EntidadesManager.obtener_clientes():
            set_t_visitado = self.T(cliente)
            set_t_not_visitado = set(range(EntidadesManager.obtener_parametros().horizon_length)) - set(set_t_visitado)
            for t_visitado in set_t_visitado:
                new_solucion = self.clonar()
                cantidad_eliminado = new_solucion.rutas[t_visitado].remover_visita(cliente)
                for t_not_visitado in set_t_not_visitado:
                    solucion_copy = new_solucion.clonar()
                    solucion_copy.rutas[t_not_visitado].insertar_visita(cliente, cantidad_eliminado, None)
                    solucion_copy.refrescar()
                    if solucion_copy.es_admisible() and ((not tabulists.esta_prohibido_quitar(cliente, t_visitado) and not tabulists.esta_prohibido_agregar(cliente, t_not_visitado))):# or saux.costo < EntidadesManager.obtener_parametros().multiplicador_tolerancia * self.costo):
                        solution_append = solucion_copy.clonar()
                        solution_append.refrescar()
                        neighborhood_prima.append(solution_append)
        return neighborhood_prima

    def variante_intercambiar_visitas(self) -> list[Type["Solucion"]]:
        neighborhood_prima = []
        for t1 in range(EntidadesManager.obtener_parametros().horizon_length):
            for t2 in range(EntidadesManager.obtener_parametros().horizon_length):
                if t1 != t2:
                    for cliente1 in self.rutas[t1].clientes:
                        for cliente2 in self.rutas[t2].clientes:
                            if not(self.rutas[t1].es_visitado(cliente2) or self.rutas[t2].es_visitado(cliente1)):
                                solucion_copy = self.clonar()
                                # Mover cliente1 de t1 a t2
                                cantidad_to_insert = solucion_copy.rutas[t1].remover_visita(cliente1)
                                solucion_copy.rutas[t2].insertar_visita(cliente1,cantidad_to_insert,None)
                               # Mover cliente1 de t2 a t1
                                cantidad_to_insert = solucion_copy.rutas[t2].remover_visita(cliente2)
                                solucion_copy.rutas[t1].insertar_visita(cliente2,cantidad_to_insert,None)
                                solucion_copy.refrescar()
                                if solucion_copy.es_admisible() and (not(tabulists.esta_prohibido_agregar(cliente1, t2) or tabulists.esta_prohibido_quitar(cliente1, t1) or tabulists.esta_prohibido_agregar(cliente2, t1) or tabulists.esta_prohibido_quitar(cliente2, t2))):# or solucion_copy.costo < EntidadesManager.obtener_parametros().multiplicador_tolerancia * self.costo):
                                    solution_append = solucion_copy.clonar()
                                    solution_append.refrescar()
                                    neighborhood_prima.append(solution_append)
                                    neighborhood_prima.append(solucion_copy)
        return neighborhood_prima

    def merge_rutas(self, rutabase_indice, rutasecondary_indice) -> None:
        self.rutas[rutabase_indice].clientes.extend(self.rutas[rutasecondary_indice].clientes)
        self.rutas[rutabase_indice].cantidades.extend(self.rutas[rutasecondary_indice].cantidades)
        self.rutas[rutasecondary_indice] = Ruta([],[])
        self.refrescar()

    def pass_constraints(self, MIP, MIPcliente = None, MIPtiempo = None, operation = None): 
        for tiempo in range(EntidadesManager.obtener_parametros().horizon_length):
            # Constraint 3: La cantidad entregada en t, es menor o igual al nivel de inventario del proveedor en t.
            if self.B(tiempo) < self.rutas[tiempo].obtener_total_entregado():
                return False
            for cliente in EntidadesManager.obtener_clientes():
                theeta = 1 if self.rutas[tiempo].es_visitado(cliente) else 0
                #Constraint 17: Theeta puede tener el valor 0 o 1
                if theeta not in [0, 1]:
                    return False
                # Constraint 5: La cantidad entregada a un cliente en un tiempo dado es mayor o igual a la capacidad máxima menos el nivel de inventario (si lo visita en el tiempo dado).
                if EntidadesManager.obtener_parametros().politica_reabastecimiento == "OU" and (self.rutas[tiempo].obtener_cantidad_entregada(cliente) < (cliente.max_nivel * theeta) - self.obtener_niveles_inventario_cliente(cliente)[tiempo]):
                    return False
                # Constraint 6: La cantidad entregada a un cliente en un tiempo dado debe ser menor o igual a la capacidad máxima menos el nivel de inventario (Junto con C5, definen OU)
                if self.rutas[tiempo].obtener_cantidad_entregada(cliente) > cliente.max_nivel - self.obtener_niveles_inventario_cliente(cliente)[tiempo]:
                    return False
                # Constraint 7: La cantidad entregada a un cliente es menor o igual al nivel máximo de inventario si es que lo visita.
                if EntidadesManager.obtener_parametros().politica_reabastecimiento == "OU" and (self.rutas[tiempo].obtener_cantidad_entregada(cliente) > cliente.max_nivel * theeta):
                    return False
                # Constraint 8: La cantidad entregada a los clientes en un tiempo dado, es menor o igual a la capacidad del camión.
                if self.rutas[tiempo].obtener_total_entregado() > EntidadesManager.obtener_vehiculo().capacidad:
                    return False
                # Constraint 14: La cantidad entregada a los clientes siempre debe ser mayor a cero
                if self.rutas[tiempo].obtener_cantidad_entregada(cliente) < 0:
                    return False
        
        # #Constraints 9 -13: #TODO (IMPORTANTE: SON SOLO DE MIP1)
        # #Constraints 17 -19 son obvias     
        for tiempo in range(EntidadesManager.obtener_parametros().horizon_length+1):
            for cliente in EntidadesManager.obtener_clientes():
                # Constraint 4
                if tiempo == 0:
                    if self.obtener_niveles_inventario_cliente(cliente)[tiempo] != cliente.nivel_inicial:
                        return False
                else:
                    if self.obtener_niveles_inventario_cliente(cliente)[tiempo] != self.obtener_niveles_inventario_cliente(cliente)[tiempo-1] + self.rutas[tiempo-1].obtener_cantidad_entregada(cliente) - cliente.nivel_demanda:
                        return False

                # Constraint 15: No puede haber stockout
                if self.obtener_niveles_inventario_cliente(cliente)[tiempo] <= 0:
                    return False
            #Constraint 16: No puede haber stockout en el proveedor
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
            if self.rutas[MIPtiempo].obtener_cantidad_entregada(MIPcliente) > MIPcliente.max_nivel * (sigma_it - w_it + v_it):
                return False
            #Constraint 24: v_it debe ser 0 o 1
            if not v_it in [0,1]:
                return False
            #Constraint 25: w_it debe ser 0 o 1
            if not w_it in [0,1]:
                return False
        return True

    # def draw_rutas(self):
    #     points = []
    #     for tiempo in range(EntidadesManager.obtener_parametros().horizon_length):
    #         x = [EntidadesManager.obtener_parametros().coords[cliente+1][0] for cliente in self.rutas[tiempo].clientes]
    #         y = [EntidadesManager.obtener_parametros().coords[cliente+1][1] for cliente in self.rutas[tiempo].clientes]
    #         points.append([x,y])
    #     Graph.draw_rutas(EntidadesManager.obtener_parametros().coords,points,EntidadesManager.obtener_parametros().coords[0])