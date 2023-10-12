from constants import constants

class Route():
    def __init__(self, clients, quantities) -> None:
        self.clients = clients if clients else []
        self.quantities = quantities if quantities else []
        self.cost = self.get_route_cost()

    def __str__(self) -> str:
        return "["+str(self.clients)+","+str(self.quantities)+"]"
        # resp = "Clientes visitados: " + str(self.clients) + "\n"
        # resp += "Cantidades: " + str(self.quantities) + "\n"
        # resp += "Costo de ruta: " + str(self.cost)
        # return resp
    
    def refresh(self):
        self.cost = self.get_route_cost()
    
    def is_vehicle_capacity_exceeded(self) -> bool:
        return constants.vehicle_capacity < self.get_total_quantity_delivered()
    
    def is_visited(self, customer) -> bool:
        return customer in self.clients
    
    def get_total_quantity_delivered(self):
        return sum(self.quantities)
    
    def get_customer_quantity_delivered(self, customer):
        index = self.clients.index(customer) if customer in self.clients else -1
        return self.quantities[index] if index >= 0 else 0

    def get_route_cost(self):
        if len(self.clients) == 0:
            transportation_cost = 0
        else:
            transportation_cost = (constants.distance_supplier[self.clients[0]] 
                + constants.distance_supplier[self.clients[len(self.clients)-1]]
                + sum((constants.distance_matrix[client][self.clients[i-1]] if  i > 0  else 0) for i, client in enumerate(self.clients))
            )
        return transportation_cost

    #Refactorizable, insertando sobre una lista quizá sea más rápido
    def get_cheapest_index_to_insert(self, customer):
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

    def remove_visit(self, customer):
        quantity_removed = self.quantities.pop(self.clients.index(customer))
        self.clients.remove(customer)
        self.refresh()
        return quantity_removed
    
    def add_customer_quantity(self, customer, quantity):
        self.quantities[self.clients.index(customer)] += quantity
    
    def remove_customer_quantity(self, customer, quantity):
        customer_index = self.clients.index(customer)
        self.quantities[customer_index] -= quantity