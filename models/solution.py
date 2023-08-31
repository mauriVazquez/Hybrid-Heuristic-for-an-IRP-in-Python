import sys
from models.route import Route
from models.penalty_variables import alpha, beta
from constants import constants


class Solution():

    def __init__(self,  routes: list[Route] = None) -> None:
        self.routes = routes if routes else [
            Route for _ in range(constants.horizon_lenght)]
        self.supplier_inventory_level = self.get_supplier_inventory_level()
        self.customers_inventory_level = self.__get_customers_inventory_level()
        self.cost = self.objetive_function()
        self.client_has_stockout = self.client_stockout_situation()
        self.client_has_overstock = self.client_overstock_situation()

    def __str__(self) -> str:
        ruta = "Rutas de la solución (clientes - cantidades)\n"
        for route in self.routes:
            ruta += "["+route.__str__()+"]\n"
        ruta += 'Function objetivo: ' + str(self.cost) + "\n"
        return ruta

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

    def objetive_function(self):
        holding_cost, transportation_cost, penalty1, penalty2 = 0, 0, 0, 0

        for time in range(constants.horizon_lenght):
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

        inventory_level = [0 for _ in range(constants.horizon_lenght+1)]
        current_level = constants.start_level_supplier

        for time in range(constants.horizon_lenght):
            current_level += (constants.production_rate_supplier -
                              self.routes[time].get_total_quantity())
            inventory_level[time] = current_level

        #   para t'

        inventory_level[constants.horizon_lenght] = current_level + \
            constants.production_rate_supplier

        return inventory_level

    def __customer_inventory_level(self, customer, time):

        inventory_level = constants.start_level[customer]
        for t in range(time):
            inventory_level += (- constants.demand_rate[customer]) + \
                self.routes[t].get_customer_quantity_delivered(customer)

        return inventory_level

    def __get_customers_inventory_level(self):

        customers_inventory = [
            [[] for _ in range(constants.nb_customers)] for _ in range(constants.horizon_lenght + 1)]

        for time in range(constants.horizon_lenght):
            for customer in range(constants.nb_customers):
                customers_inventory[time][customer] = self.__customer_inventory_level(customer, time + 1)

        # para t'
        for customer in range(constants.nb_customers):
            customers_inventory[time + 1][customer] = customers_inventory[time][customer] - constants.demand_rate[customer]

        return customers_inventory

    def vehicle_capacity_has_exceeded(self):
        for route in self.routes:
            if route.vehicle_capacity_has_exceeded():
                return True

        return False

    def supplier_stockout_situation(self):
        initial = constants.start_level_supplier

        for route in self.routes:
            initial = initial + constants.production_rate_supplier - route.get_total_quantity()
            if initial < 0:
                return True

        return False

    def client_stockout_situation(self) -> bool:
        for customer in range(constants.nb_customers):
            for time in range(constants.horizon_lenght):
                if self.customers_inventory_level[time][customer] <= constants.min_level[customer]:
                    return True

        return False

    def client_overstock_situation(self) -> bool:
        for customer in range(constants.nb_customers):
            for time in range(constants.horizon_lenght):
                if self.customers_inventory_level[time][customer] > constants.max_level[customer]:
                    return True
        return False

    def is_admissible(self) -> bool:
        return not (self.client_has_stockout or self.client_has_overstock)

    def is_feasible(self) -> bool:
        return self.is_admissible() and not (self.supplier_stockout_situation() or self.vehicle_capacity_has_exceeded())

    def refresh(self):
        self.supplier_inventory_level = self.get_supplier_inventory_level()
        self.customers_inventory_level = self.__get_customers_inventory_level()
        self.cost = self.objetive_function()
        self.client_has_stockout = self.client_stockout_situation()
        self.client_has_overstock = self.client_overstock_situation()
        
    def remove_visit(self, customer, time):
        quantity_removed = self.routes[time].remove_visit(customer)
        
        if constants.replenishment_policy == "OU":
            for t in range(time + 1, constants.horizon_lenght):
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
                
            for t in range(time + 1, constants.horizon_lenght):
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