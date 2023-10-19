from sys import float_info
from copy import deepcopy
from models.route import Route
from models.penalty_variables import alpha, beta
from models.tabulists import tabulists
from constants import constants
from typing import Type


class Solution():
    def __init__(self,  routes: list[Route] = None) -> None:
        self.routes = routes if routes else [
            Route for _ in range(constants.horizon_length)]
        self.supplier_inventory_level = self.get_supplier_inventory_level()
        self.customers_inventory_level = self.get_customers_inventory_level()
        self.cost = self.objetive_function()
        self.client_has_stockout = self.client_stockout_situation()
        self.client_has_overstock = self.client_overstock_situation()

    def __str__(self) -> str:
        return "".join("T"+str(i+1)+"= "+route.__str__()+"    " for i, route in enumerate(self.routes)) + 'Costo:' + str(self.cost)

    def  detail(self) -> str:
        resp = "Routes:"+" ".join("T"+str(i+1)+"= "+route.__str__()+"\t" for i, route in enumerate(self.routes))
        resp += '\nObjective function: ' + str(self.cost) + "\n"
        resp += 'Supplier inventory: ' + str(self.supplier_inventory_level) + "\n"
        resp += 'Customers inventory: ' + str(self.customers_inventory_level) + "\n"
        resp += 'Has stock out ? : ' + ('yes' if self.client_has_stockout else 'no') + "\n"
        resp += 'Has over stock ? : ' + ('yes' if self.client_has_overstock else 'no') + "\n"
        return resp
    
    @staticmethod
    def get_empty_solution() -> Type["Solution"]:
        solution = Solution([Route(route[0], route[1]) for route in [[[], []] for _ in range(constants.horizon_length)]])
        solution.refresh()
        return solution

    def objetive_function(self):
        holding_cost, transportation_cost, penalty1, penalty2 = 0, 0, 0, 0
        if not any(len(route.clients) > 0 for route in self.routes):
            return float_info.max
        
        for time in range(constants.horizon_length):
            # First term (holding_cost)
            bt = self.supplier_inventory_level[time]
            holding_cost_t = constants.holding_cost_supplier * bt
            for i in range(constants.nb_customers):
                holding_cost_t += constants.holding_cost[i] * \
                    self.customers_inventory_level[i][time]
            holding_cost += holding_cost_t

            # Second term (transportation_cost)
            transportation_cost += self.routes[time].cost

            # Third term (penalty 1)
            penalty1 += max(0,
                            self.routes[time].get_total_quantity_delivered() - constants.vehicle_capacity)

            # Fourth term
            penalty2 += max(0, - bt)

        # t prima
        holding_cost_t = constants.holding_cost_supplier * \
            self.supplier_inventory_level[time + 1]
        for i in range(constants.nb_customers):
            holding_cost_t += constants.holding_cost[i] * \
                (self.customers_inventory_level[i][time + 1])
        holding_cost += holding_cost_t

        # bt en t prima
        bt = self.supplier_inventory_level[time + 1]
        penalty2 += max(0, - bt)

        return holding_cost + transportation_cost + alpha.get_value() * penalty1 + beta.get_value() * penalty2

    def get_supplier_inventory_level(self):
        current_level = constants.start_level_supplier
        inventory_level = [
            current_level := current_level + (constants.production_rate_supplier - route.get_total_quantity_delivered())
            for route in self.routes
        ]
        inventory_level.append(
            current_level + constants.production_rate_supplier)
        return inventory_level

    def customer_inventory_level(self, customer):
        
        customer_inventory = []
        customer_inventory.append(constants.start_level[customer])
        for time in range(1, constants.horizon_length +1):
            customer_inventory.append(customer_inventory[time-1] + self.routes[time-1].get_customer_quantity_delivered(customer) - constants.demand_rate[customer])
                
        return customer_inventory
           
    def get_customers_inventory_level(self):
        
        # [[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4]]
        #   [[1][1][1][1]]
        customers_inventory = []
        for customer in range(constants.nb_customers):
            customers_inventory.append(self.customer_inventory_level(customer))
        return customers_inventory

    def is_vehicle_capacity_exceeded(self) -> bool:
        return any(route.is_vehicle_capacity_exceeded() for route in self.routes)

    def supplier_stockout_situation(self) -> bool:
        stock_level = constants.start_level_supplier
        return any(stock_level + constants.production_rate_supplier - route.get_total_quantity_delivered() < 0 for route in self.routes)

    def client_stockout_situation(self) -> bool:
        return any(self.customers_inventory_level[customer][time] < constants.min_level[customer]
                   for customer in range(constants.nb_customers)
                   for time in range(constants.horizon_length))

    def client_overstock_situation(self) -> bool:
        return any(self.customers_inventory_level[customer][time] > constants.max_level[customer]
                   for customer in range(constants.nb_customers)
                   for time in range(constants.horizon_length))

    def is_admissible(self) -> bool:
        return not (self.client_has_stockout or self.client_has_overstock)

    def is_feasible(self) -> bool:
        return self.is_admissible() and not (self.supplier_stockout_situation() or self.is_vehicle_capacity_exceeded())

    def refresh(self):
        self.supplier_inventory_level = self.get_supplier_inventory_level()
        self.customers_inventory_level = self.get_customers_inventory_level()
        self.cost = self.objetive_function()
        self.client_has_stockout = self.client_stockout_situation()
        self.client_has_overstock = self.client_overstock_situation()

    def remove_visit(self, customer, time):
        quantity_removed = self.routes[time].remove_visit(customer)

        if constants.replenishment_policy == "OU":
            for t in range(time + 1, constants.horizon_length):
                if self.routes[t].is_visited(customer):
                    self.routes[t].add_customer_quantity(
                        customer, quantity_removed)
                    break
        elif constants.replenishment_policy == "ML":
            if self.client_stockout_situation():
                for tinverso in range(time):
                    t2 = time - tinverso
                    if self.routes[t2].is_visited(customer):
                        quantity = constants.max_level[customer] - \
                            self.customers_inventory_level[customer][t2]
                        self.routes[t2].add_customer_quantity(
                            customer, quantity)
                        break

        self.refresh()

    def insert_visit(self, customer, time):

        cheapest_index = self.routes[time].get_cheapest_index_to_insert(customer)

        if constants.replenishment_policy == "OU":
            quantity_delivered = constants.max_level[customer] - \
                self.customers_inventory_level[customer][time]
            self.routes[time].insert_visit(
                customer, cheapest_index, quantity_delivered)

            for t in range(time + 1, constants.horizon_length):
                if self.routes[t].is_visited(customer):
                    self.routes[t].remove_customer_quantity(
                        customer, quantity_delivered)
                    break

        elif constants.replenishment_policy == "ML":
            quantity_delivered = min(
                constants.max_level[customer] -
                self.customers_inventory_level[customer][time],
                constants.vehicle_capacity -
                self.routes[time].get_total_quantity_delivered(),
                self.supplier_inventory_level[time]
            )

            quantity_delivered = quantity_delivered if quantity_delivered > 0 else constants.demand_rate[customer]
            self.routes[time].insert_visit(customer, cheapest_index, quantity_delivered)

        self.refresh()

    def previous_visit(self, current_time, customer):
        for index in range(current_time - 1, -1, -1):
            if (self.routes[index].is_visited(customer)):
                return index

        return None

    def jump(self, triplet) -> Type["Solution"]:
        new_solution = self.clone()
        customer, time_visited, time_not_visited = triplet        
            
        if self.routes[time_visited].is_visited(customer) and (not self.routes[time_not_visited].is_visited(customer)):    
            quantity_removed = new_solution.routes[time_visited].remove_visit(customer)
            cheapest_index = new_solution.routes[time_not_visited].get_cheapest_index_to_insert(customer)
            new_solution.routes[time_not_visited].insert_visit(customer, cheapest_index, quantity_removed)
            new_solution.refresh()
        new_solution.refresh()
        return new_solution

    def get_all_customer_inventory_level(self, customer) -> list:
        return self.customers_inventory_level[customer]

    def get_all_customer_quantity_delivered(self, customer) -> list:
        quantities = []
        for route in self.routes:
            quantities.append(route.get_customer_quantity_delivered(customer))

        return quantities

    def sort_list(self, combination) -> None:
        self.routes = [self.routes[i] for i in combination]
        self.refresh()

    # Returns the set of customers which are not visited at the same time in solution and solution_prima
    def construct_A(self, solution_prima: Type["Solution"]) -> list:
        A = []
        for customer in range(constants.nb_customers):
            if not self.T(customer) == solution_prima.T(customer):
                A.append(customer)
        return A

    # Returns the set of times when is visited a customer in a given solution.
    def T(self, customer):
        times = []
        for time in range(constants.horizon_length):
            if self.routes[time].is_visited(customer):
                times.append(time)
        return times

    def variante_eliminacion(self) -> list[Type["Solution"]]:
        # print("Inicio tipo 1")
        neighborhood_prima = []
        for customer in range(constants.nb_customers):
            # La eliminación del cliente parece ser interesante cuando hi>h0
            if constants.holding_cost[customer] > constants.holding_cost_supplier:
                for time in range(constants.horizon_length):
                    solution_copy = self.clone()
                    if (solution_copy.routes[time].is_visited(customer)) and (not tabulists.forbidden_to_remove(customer, time)):
                        solution_copy.remove_visit(customer, time)
                        solution_copy.refresh()
                        if solution_copy.is_admissible():
                            neighborhood_prima.append(solution_copy)
                            # print("Variant Type 1")
        return neighborhood_prima

    def variante_insercion(self) -> list[Type["Solution"]]:
        # print("Inicio tipo 2")
        neighborhood_prima = []
        for customer in range(constants.nb_customers):
            for time in range(constants.horizon_length):
                solution_copy = self.clone()
                if (not solution_copy.routes[time].is_visited(customer)) and (not tabulists.forbidden_to_append(customer, time)):
                    solution_copy.insert_visit(customer, time)
                    solution_copy.refresh()
                    if solution_copy.is_admissible():
                        neighborhood_prima.append(solution_copy)
                        # print("Variant type 2")
        return neighborhood_prima

    def variante_mover_visita(self) -> list[Type["Solution"]]:
        neighborhood_prima = []
        for customer in range(constants.nb_customers):
            set_t_visited = self.T(customer)
            set_t_not_visited = [x for x in list(
                range(constants.horizon_length)) if x not in set_t_visited]

            for t_visited in set_t_visited:
                new_solution = self.clone()
                quantity_removed = new_solution.routes[t_visited].remove_visit(customer)
                for t_not_visited in set_t_not_visited:
                    if not tabulists.forbidden_to_remove(customer, t_visited) and not tabulists.forbidden_to_append(customer, t_not_visited):
                        saux = new_solution.clone()
                        saux_cheapest_index = saux.routes[t_not_visited].get_cheapest_index_to_insert(customer)
                        saux.routes[t_not_visited].insert_visit(customer, saux_cheapest_index, quantity_removed)
                        saux.refresh()
                        if saux.is_admissible():
                            # print("Variant Type 3")
                            neighborhood_prima.append(saux)
        return neighborhood_prima

    def variante_intercambiar_visitas(self) -> list[Type["Solution"]]:
        neighborhood_prima = []
        for t1 in range(constants.horizon_length):
            for client1 in self.routes[t1].clients:
                for t2 in range(constants.horizon_length):
                    if t1 != t2:
                        for client2 in self.routes[t2].clients:
                            if not ((self.routes[t1].is_visited(client2)) or (self.routes[t2].is_visited(client1)) or tabulists.forbidden_to_append(client1, t2) or tabulists.forbidden_to_remove(client1, t1) or tabulists.forbidden_to_append(client2, t1) or tabulists.forbidden_to_remove(client2, t2)):
                                saux = self.clone()
                                saux.routes[t1].insert_visit(client2,
                                                             saux.routes[t1].get_cheapest_index_to_insert(
                                                                 client2),
                                                             saux.routes[t2].remove_visit(client2))
                                saux.routes[t2].insert_visit(client1,
                                                             saux.routes[t2].get_cheapest_index_to_insert(
                                                                 client1),
                                                             saux.routes[t1].remove_visit(client1))
                                saux.refresh()
                                if saux.is_admissible():
                                    # print("Solucion admisible en variante 4")
                                    neighborhood_prima.append(saux)
        return neighborhood_prima

    def merge_routes(self, routebase_index, routesecondary_index) -> None:
        # print(f"Entrada al merge route con parametros {str(routebase_index)}, {str(routesecondary_index)}: {self} ")
        self.routes[routebase_index].clients.extend(self.routes[routesecondary_index].clients)
        self.routes[routebase_index].quantities.extend(self.routes[routesecondary_index].quantities)
        self.routes[routebase_index].refresh()
        self.routes[routesecondary_index].clients = []
        self.routes[routesecondary_index].quantities = []
        self.routes[routesecondary_index].refresh()
        # print(f"Salida del merge route {self}")

    def clone(self) -> Type["Solution"]:
        solution = deepcopy(self)
        solution.refresh()
        return solution

    def theeta(self, i, t):
        return (1 if self.routes[t].is_visited(i) else 0)

    def passConstraints(self, MIPcustomer = None, MIPtime = None, operation = None, MIP = None):
        # for time in range(constants.horizon_length):
        #     # Constraint 3: La cantidad entregada en t, es menor o igual al nivel de inventario del proveedor en t.
        #     if self.get_supplier_inventory_level()[time] < self.routes[time].get_total_quantity_delivered():
        #         # print("Falla la constraint  3 para" + str(self))
        #         return False
        #     # Constraint 8: La cantidad entregada a los clientes en un tiempo dado, es menor o igual a la capacidad del camión.
        #     if self.routes[time].get_total_quantity_delivered() > constants.vehicle_capacity:
        #         # print("Falla la constraint 8: para" + str(self))
        #         return False
        #      # Constraint 16
        #     if self.get_supplier_inventory_level()[time] < 0:
        #         # print("Falla la constraint 16 para" + str(self))
        #         return False
        
        #     for i in range(constants.nb_customers):
        #         #Retorna 1 si 'customer' es visitado en el tiempo 'time', caso contrario devuelve 0
        #         theeta = 1 if self.routes[time].is_visited(i) else 0
                
        #         # Constraint 4
        #         # if self.get_customers_inventory_level()[i][time] != self.get_customers_inventory_level()[i][time-1] + self.routes[time-1].get_customer_quantity_delivered(i) - constants.demand_rate[i]:
        #         #     print("Falla la constraint  4 para" + str(self))
        #         #     return False
        #         # Constraint 5 (Para OU): La cantidad entregada a un cliente en un tiempo dado es mayor o igual a la capacidad máxima menos el nivel de inventario (si lo visita en el tiempo dado).
        #         if constants.replenishment_policy == "OU" and (self.routes[time].get_customer_quantity_delivered(i) < (constants.max_level[i] * theeta) - self.get_customers_inventory_level()[i][time]):
        #             # print("Falla la constraint  5 para" + str(self))
        #             return False
        #         # Constraint 6: La cantidad entregada a un cliente en un tiempo dado debe ser menor o igual a la capacidad máxima menos el nivel de inventario (Junto con C5, definen OU)
        #         if self.routes[time].get_customer_quantity_delivered(i) > constants.max_level[i] - self.get_customers_inventory_level()[i][time]:
        #             # print("Falla la constraint  6 para" + str(self))
        #             return False
        #         # Constraint 7: La cantidad entregada a un cliente es menor o igual al nivel máximo de inventario si es que lo visita.
        #         if constants.replenishment_policy == "OU" and (self.routes[time].get_customer_quantity_delivered(i) > constants.max_level[i] * theeta):
        #             # print("Falla la constraint  7 para" + str(self))
        #             return False
        #         # Constraint 14: La cantidad entregada a los clientes siempre debe ser mayor a cero
        #         if self.routes[time].get_customer_quantity_delivered(i) < 0:
        #             # print("Falla la constraint 14 para" + str(self))
        #             return False
        #         # Constraint 15: No puede haber stockout
        #         if self.client_has_stockout:
        #             # print("Falla la constraint 15 para" + str(self)+" para el cliente "+str(i))
        #             return False
        # if MIP == "MIP2":
        #     v_it = 1 if (operation == "INSERT") else 0
        #     w_it = 1 if (operation == "REMOVE") else 0
        #     sigma_it = 1 if (MIPcustomer in self.routes[MIPtime].customers) else 0
        #     # # Constraint 21: v_it no puede ser 1 y sigma_it 1, implicaría que se insertó y está presente ¿¿??
        #     # if v_it > 1 - sigma_it:
        #     #     print("Falla la constraint 21 para" + str(self))
        #     #     return False
        #     # # Constraint 22:  w_it no puede ser 1 y sigma_it 0, implicaría que se borró y no está presente ¿¿??
        #     # if w_it > sigma_it:
        #     #     print("Falla la constraint 22 para" + str(self))
        #     #     return False
        #     # Constraint 23: La cantidad entregada al cliente i no puede ser mayor a la capacidad máxima
        #     if self.routes[MIPtime].get_customer_quantity_delivered(MIPcustomer) > constants.max_level[MIPcustomer] * (sigma_it - w_it + v_it):
        #         # print("Falla la constraint 23 para" + str(self))
        #         return False
        #     #Constraint 24: v_it debe ser 0 o 1
        #     if not v_it in [0,1]:
        #         # print("Falla la constraint 24 para" + str(self))
        #         return False
        #     #Constraint 25: w_it debe ser 0 o 1
        #     if not w_it in [0,1]:
        #         # print("Falla la constraint 25 para" + str(self))
        #         return False
            
        # # Constraint 4: Para el termino diferencial de T'
        # for i in range(constants.nb_customers):
        #     expected_level = self.get_customers_inventory_level()[i][constants.horizon_length-1] + self.routes[constants.horizon_length-1].get_customer_quantity_delivered(i) - constants.demand_rate[i]
        #     if self.get_customers_inventory_level()[i][constants.horizon_length] != expected_level:
        #         # print("Falla la constraint  4 para" + str(self))
        #         return False
        
        # #Constraints 9 -13: #TODO (IMPORTANTE: SON SOLO DE MIP1)
        # #Constraints 17 -19 son obvias

        return True

    def B(self, t):
        if (t > 0):
            b = self.B(t-1)
            return b + constants.production_rate_supplier - self.routes[t-1].get_total_quantity_delivered()
        if (t == 0):
            return constants.start_level_supplier
