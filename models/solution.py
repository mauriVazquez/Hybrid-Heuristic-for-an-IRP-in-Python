import sys
import copy
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
        return str([str(route) for route in self.routes ]) + '. Function objetivo: ' + str(self.cost)

        # resp = "Rutas:\n"
        # for route in self.routes:
        #     resp += route.__str__() + "\n\n"

        # resp += 'Function objetivo: ' + str(self.cost) + "\n"
        # resp += 'supplier_inventory_level: ' + \
        #     str(self.supplier_inventory_level) + "\n"
        # resp += 'customers_inventory_level: ' + \
        #     str(self.customers_inventory_level) + "\n"
            
        # resp += 'Stock out ? : ' + ('si' if self.client_has_stockout else 'no') + "\n"
        # resp += 'over stock ? : ' + ('si' if self.client_has_overstock else 'no') + "\n"

        # return resp

    @staticmethod
    def get_empty_solution() -> Type["Solution"]:
        return Solution([Route(route[0], route[1]) for route in [[[], []] for _ in range(constants.horizon_length)]])
    
    def objetive_function(self):
        holding_cost, transportation_cost, penalty1, penalty2 = 0, 0, 0, 0

        for time in range(constants.horizon_length):
            # First term (holding_cost)
            bt = self.supplier_inventory_level[time]
            holding_cost_t = constants.holding_cost_supplier * bt
            for i in range(constants.nb_customers):
                holding_cost_t += constants.holding_cost[i] * \
                    self.customers_inventory_level[time][i]
            holding_cost += holding_cost_t

            # Second term (transportation_cost)
            transportation_cost += self.routes[time].cost

            # Third term (penalty 1)
            penalty1 += max(0,
                            self.routes[time].get_total_quantity() - constants.vehicle_capacity)

            # Fourth term
            penalty2 += max(0, - bt)

        # t prima
        holding_cost_t = constants.holding_cost_supplier * \
            self.supplier_inventory_level[time + 1]
        for i in range(constants.nb_customers):
            holding_cost_t += constants.holding_cost[i] * \
                (self.customers_inventory_level[time + 1][i])
        holding_cost += holding_cost_t

        # bt en t prima
        bt = self.supplier_inventory_level[time + 1]
        penalty2 += max(0, - bt)

        return holding_cost + transportation_cost + alpha.get_value() * penalty1 + beta.get_value() * penalty2

    def get_supplier_inventory_level(self):
        current_level = constants.start_level_supplier
        inventory_level = [
            current_level := current_level + (constants.production_rate_supplier - route.get_total_quantity())
            for route in self.routes
        ]
        inventory_level.append( current_level + constants.production_rate_supplier)
        return inventory_level

    def customer_inventory_level(self, customer, time):
        return constants.start_level[customer] + sum(
                self.routes[t].get_customer_quantity_delivered(customer) - constants.demand_rate[customer]
                for t in range(time)
            )

    def get_customers_inventory_level(self):
        return [[ 
            self.customer_inventory_level(customer, time + 1) if time < constants.horizon_length else (self.customer_inventory_level(customer, time) - constants.demand_rate[customer])
            for customer in range(constants.nb_customers)]
            for time in range(constants.horizon_length + 1)]
    
    def vehicle_capacity_has_exceeded(self) -> bool:
        return any(route.vehicle_capacity_has_exceeded() for route in self.routes)

    def supplier_stockout_situation(self) -> bool:
        stock_level = constants.start_level_supplier
        return any(stock_level + constants.production_rate_supplier - route.get_total_quantity() < 0 for route in self.routes)

    def client_stockout_situation(self) -> bool:    
        return any(self.customers_inventory_level[time][customer] <= constants.min_level[customer]
               for customer in range(constants.nb_customers)
               for time in range(constants.horizon_length))

    def client_overstock_situation(self) -> bool:
        return any(self.customers_inventory_level[time][customer] > constants.max_level[customer]
               for customer in range(constants.nb_customers)
               for time in range(constants.horizon_length))

    def is_admissible(self) -> bool:
        return not (self.client_has_stockout or self.client_has_overstock)

    def is_feasible(self) -> bool:
        return self.is_admissible() and not (self.supplier_stockout_situation() or self.vehicle_capacity_has_exceeded())

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
                    self.routes[t].add_customer_quantity(customer, quantity_removed)
                    break
        elif constants.replenishment_policy == "ML":
            if self.client_stockout_situation():
                for tinverso in range(time):
                    t2 = time - tinverso
                    if self.routes[t2].is_visited(customer):
                        quantity = constants.max_level[customer] - self.customers_inventory_level[t2][customer]
                        self.routes[t2].add_customer_quantity(customer, quantity)
                        break
                    
        self.refresh()
        
    def insert_visit(self, customer, time):
        
        cheapest_index = self.routes[time].cheapest_index_to_insert(customer)

        if constants.replenishment_policy == "OU":
            quantity_delivered = constants.max_level[customer] - self.customers_inventory_level[time][customer]
            self.routes[time].insert_visit(customer, cheapest_index, quantity_delivered)  
                
            for t in range(time + 1, constants.horizon_length):
                if self.routes[t].is_visited(customer):
                    self.routes[t].remove_customer_quantity(customer, quantity_delivered)
                    break
                
        elif constants.replenishment_policy == "ML":
            quantity_delivered = min(
                constants.max_level[customer] - self.customers_inventory_level[time][customer],
                constants.vehicle_capacity - self.routes[time].get_total_quantity(), 
                self.supplier_inventory_level[time]
                )
        
            quantity_delivered = quantity_delivered if quantity_delivered > 0 else constants.demand_rate[customer]
            self.routes[time].insert_visit(customer, cheapest_index, quantity_delivered)
            
        self.refresh()
    
    def previous_visit(self, current_time, customer):
        for index in range(current_time - 1, -1, -1):
            if(self.routes[index].is_visited(customer)):
                return index
        
        return None
    
    def get_all_customer_inventory_level(self, customer) -> list:
        inventories = []
        for inventories_level in self.customers_inventory_level:
            inventories.append(inventories_level[customer])
            
        return inventories
    
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

    def variants_type1(self) -> list[Type["Solution"]]:
        # print("Inicio tipo 1")
        neighborhood_prima = []
        for customer in range(constants.nb_customers):
            # La eliminación del cliente parece ser interesante cuando hi>h0
            if constants.holding_cost[customer] > constants.holding_cost_supplier:
                for time in range(constants.horizon_length):
                    solution_copy = copy.deepcopy(self)
                    if (solution_copy.routes[time].is_visited(customer)) and (not tabulists.forbidden_to_remove(customer, time)):
                        solution_copy.remove_visit(customer, time)
                        if solution_copy.is_admissible():
                            neighborhood_prima.append(solution_copy)
                            # print("Variant Type 1")
        return neighborhood_prima


    def variants_type2(self) -> list[Type["Solution"]]:
        # print("Inicio tipo 2")
        neighborhood_prima = []
        for customer in range(constants.nb_customers):
            for time in range(constants.horizon_length):
                solution_copy = self.clone()
                if (not solution_copy.routes[time].is_visited(customer)) and (not tabulists.forbidden_to_append(customer, time)):
                    solution_copy.insert_visit(customer, time)
                    if solution_copy.is_admissible():
                        neighborhood_prima.append(solution_copy)
                        # print("Variant type 2")
        return neighborhood_prima


    def variants_type3(self) -> list[Type["Solution"]]:
        neighborhood_prima = []
        for customer in range(constants.nb_customers):
            set_t_visited = self.T(customer)
            set_t_not_visited = [x for x in list(range(constants.horizon_length)) if x not in set_t_visited]

            for t_visited in set_t_visited:
                new_solution = self.clone()
                quantity_removed = new_solution.routes[t_visited].remove_visit(customer)
                for t_not_visited in set_t_not_visited:
                    if not tabulists.forbidden_to_remove(customer, t_visited) and not tabulists.forbidden_to_append(customer, t_not_visited):
                        saux = copy.deepcopy(new_solution)
                        saux_cheapest_index = saux.routes[t_not_visited].cheapest_index_to_insert(customer)
                        saux.routes[t_not_visited].insert_visit(customer, saux_cheapest_index, quantity_removed)
                        if saux.is_admissible():
                            # print("Variant Type 3")
                            neighborhood_prima.append(saux)
        return neighborhood_prima

    def variants_type4(self) -> list[Type["Solution"]]:
        neighborhood_prima = []
        for t1 in range(constants.horizon_length):
            for client1 in self.routes[t1].clients:
                for t2 in range(constants.horizon_length):
                    if t1 != t2:
                        for client2 in self.routes[t2].clients:
                            if not ((self.routes[t1].is_visited(client2)) or (self.routes[t2].is_visited(client1)) or tabulists.forbidden_to_append(client1, t2) or tabulists.forbidden_to_remove(client1, t1) or tabulists.forbidden_to_append(client2, t1) or tabulists.forbidden_to_remove(client2, t2)):
                                saux = self.clone()
                                saux.routes[t1].insert_visit(client2, 
                                                            saux.routes[t1].cheapest_index_to_insert(client2), 
                                                            saux.routes[t2].remove_visit(client2))
                                saux.routes[t2].insert_visit(client1, 
                                                            saux.routes[t2].cheapest_index_to_insert(client1), 
                                                            saux.routes[t1].remove_visit(client1))
                                saux.refresh()
                                if saux.is_admissible():
                                    # print("Solucion admisible en variante 4")
                                    neighborhood_prima.append(saux)
        return neighborhood_prima
    
    def clone(self) -> Type["Solution"]:
        return copy.deepcopy(self)
    
    def theeta(self, i, t):
        return (1 if self.routes[t].is_visited(i) else 0)

    def passConstraints(self, i, t, operation, MIP):

        # Constraint 3
        if self.supplier_inventory_level[t] < self.routes[t].get_total_quantity():
            # print("Falla la constraint  3 para" + str(self))
            return False
        # Constraint 5
        if constants.replenishment_policy == "OU" and self.routes[t].get_customer_quantity_delivered(i) < (constants.max_level[i] * self.theeta(i, t)) - self.customers_inventory_level[t][i]:
            # print("Falla la constraint  5 para" + str(self)+" para el cliente "+str(i))
            return False
        # Constraint 6
        if self.routes[t].get_customer_quantity_delivered(i) > constants.max_level[i] - self.customers_inventory_level[t][i]:
            # print("Falla la constraint  6 para" + str(self)+" para el cliente "+str(i))
            return False
        # Constraint 7
        if constants.replenishment_policy == "OU" and self.routes[t].get_customer_quantity_delivered(i) > constants.max_level[i] * self.theeta(i, t):
            # print("Falla la constraint  7 para" + str(self)+" para el cliente "+str(i))
            return False
        # Constrain 8:
        if self.routes[t].get_total_quantity() > constants.vehicle_capacity:
            # print("Falla la constraint 8: para" + str(self))
            return False

        # Constraints 9 -13:
            # TODO (IMPORTANTE: SON SOLO DE MIP1)

        # Constraint 14
        if self.routes[t].get_total_quantity() < 0:
            # print("Falla la constraint 14 para" + str(self))
            return False

        for t in range(constants.horizon_length+1):
            # Constraint 4
            if self.customers_inventory_level[t][i] != self.customers_inventory_level[t-1][i] + self.routes[t-1].get_customer_quantity_delivered(i) - (constants.demand_rate[i] if t-1 >= 0 else 0):
                # print("Falla la constraint  4 para" + str(self)+" para el cliente "+str(i))
                return False
            # Constraint 15
            if self.customers_inventory_level[t][i] < 0:
                # print("Falla la constraint 15 para" + str(self)+" para el cliente "+str(i))
                return False
            # Constraint 16
            if self.supplier_inventory_level[t] < 0:
                # print("Falla la constraint 16 para" + str(self))
                return False
        # Constraints 17 -19 son obvias

        if MIP == "MIP2":
            v_it = 1 if (operation == "INSERT") else 0
            sigma_it = 1 if (i in self[t][0]) else 0
            w_it = 1 if (operation == "REMOVE") else 0

            # Constraint 21
            if v_it > 1 - sigma_it:
                # print("Falla la constraint 21 para" + str(self)+" para el cliente "+str(i))
                return False
            # Constraint 22
            if w_it > sigma_it:
                # print("Falla la constraint 22 para" + str(self)+" para el cliente "+str(i))
                return False
            # Constraint 23
            if self.routes[t].get_total_quantity() > constants.max_level[i] * (sigma_it - w_it + v_it):
                # print("Falla la constraint 23 para" + str(self)+" para el cliente "+str(i))
                return False
            # Constraint 24
            if v_it < 0 or v_it > 1:
                # print("Falla la constraint 24 para" + str(self)+" para el cliente "+str(i))
                return False
            # Constraint 25
            if w_it < 0 or v_it > 1:
                # print("Falla la constraint 25 para" + str(self)+" para el cliente "+str(i))
                return False
        return True