from constants import constants

class Route():

    def __init__(self, clients, quantities) -> None:
        self.clients = clients if clients else []
        self.quantities = quantities if quantities else []
        self.cost = self.get_route_cost()

    def __str__(self) -> str:
        resp = "Clientes visitados: " + str(self.clients) + "\n"
        resp += "Cantidades: " + str(self.quantities) + "\n"
        resp += "Costo de ruta: " + str(self.cost)

        return resp

    def get_total_quantity(self):
        return sum(self.quantities)

    def get_customer_quantity_delivered(self, customer):

        try:
            index = self.clients.index(customer)
            return self.quantities[index]
        except ValueError:
            return 0

    def get_route_cost(self):
        transportation_cost = 0
        for i, client in enumerate(self.clients):
            # primer cliente visitado
            if (i == 0):
                transportation_cost += constants.distance_supplier[client]
            else:
                # ultimo cliente visitado
                if (i == (len(self.clients) - 1)):
                    transportation_cost += constants.distance_supplier[client]

                transportation_cost += constants.distance_matrix[client][self.clients[i-1]]

        return transportation_cost

    def vehicle_capacity_has_exceeded(self):
        return constants.vehicle_capacity < self.get_total_quantity()
    
    def refresh(self):
        self.cost = self.get_route_cost()
        
    def remove_visit(self, customer):
        
        customer_index = self.clients.index(customer)
        self.clients.pop(customer_index)
        quantity_removed = self.quantities.pop(customer_index)
        
        self.refresh()
        return quantity_removed
    
    def is_visited(self, customer):
        return customer in self.clients
    
    def add_customer_quantity(self, customer, quantity):
        customer_index = self.clients.index(customer)
        self.quantities[customer_index] += quantity
        
    def cheapest_index_to_insert(self, customer):
        min_cost = float("inf")
        
        for pos in range(len(self.clients)+1):
            self.clients.insert(pos, customer)
            route_cost = self.get_route_cost()
            if route_cost < min_cost:
                min_cost_index = pos
                min_cost = route_cost
                
            self.clients.pop(pos)
                
        return min_cost_index
    
    def insert_visit(self,customer, index, quantity):
        self.clients.insert(index, customer)
        self.quantities.insert(index, quantity)
        
        self.refresh()
        
    def remove_customer_quantity(self, customer, quantity):
        customer_index = self.clients.index(customer)
        self.quantities[customer_index] -= quantity