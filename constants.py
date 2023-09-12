import math
import sys

class Constants():

    _self = None

    # singleton
    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self) -> None:
        self.read_input_irp(sys.argv[1])
        self.replenishment_policy = sys.argv[3]

    def read_input_irp(self, filename):
        file_it = iter(self.read_elem(filename))

        nb_customers = int(next(file_it)) - 1
        horizon_length = int(next(file_it))
        vehicle_capacity = int(next(file_it))

        x_coord = [None] * nb_customers
        y_coord = [None] * nb_customers
        start_level = [None] * nb_customers
        max_level = [None] * nb_customers
        min_level = [None] * nb_customers
        demand_rate = [None] * nb_customers
        holding_cost = [None] * nb_customers

        next(file_it)
        x_coord_supplier = float(next(file_it))
        y_coord_supplier = float(next(file_it))
        start_level_supplier = int(next(file_it))
        production_rate_supplier = int(next(file_it))
        holding_cost_supplier = float(next(file_it))
        for i in range(nb_customers):
            next(file_it)
            x_coord[i] = float(next(file_it))
            y_coord[i] = float(next(file_it))
            start_level[i] = int(next(file_it))
            max_level[i] = int(next(file_it))
            min_level[i] = int(next(file_it))
            demand_rate[i] = int(next(file_it))
            holding_cost[i] = float(next(file_it))

        distance_matrix = self.compute_distance_matrix(x_coord, y_coord)
        distance_supplier = self.compute_distance_supplier(
            x_coord_supplier, y_coord_supplier, x_coord, y_coord)

        self.nb_customers = nb_customers
        self.horizon_length = horizon_length
        self.vehicle_capacity = vehicle_capacity
        self.start_level_supplier = start_level_supplier
        self.production_rate_supplier = production_rate_supplier
        self.holding_cost_supplier = holding_cost_supplier
        self.start_level = start_level
        self.max_level = max_level
        self.min_level = min_level
        self.demand_rate = demand_rate
        self.holding_cost = holding_cost
        self.distance_matrix = distance_matrix
        self.distance_supplier = distance_supplier

    # Compute the distance matrix

    def compute_distance_matrix(self, x_coord, y_coord):
        nb_customers = len(x_coord)
        distance_matrix = [[None for i in range(
            nb_customers)] for j in range(nb_customers)]
        for i in range(nb_customers):
            distance_matrix[i][i] = 0
            for j in range(nb_customers):
                dist = self.compute_dist(
                    x_coord[i], x_coord[j], y_coord[i], y_coord[j])
                distance_matrix[i][j] = dist
                distance_matrix[j][i] = dist
        return distance_matrix

    # Compute the distances to the supplier

    def compute_distance_supplier(self, x_coord_supplier, y_coord_supplier, x_coord, y_coord):
        nb_customers = len(x_coord)
        distance_supplier = [None] * nb_customers
        for i in range(nb_customers):
            dist = self.compute_dist(
                x_coord_supplier, x_coord[i], y_coord_supplier, y_coord[i])
            distance_supplier[i] = dist
        return distance_supplier

    def compute_dist(self, xi, xj, yi, yj):
        return round(math.sqrt(math.pow(xi - xj, 2) + math.pow(yi - yj, 2)))

    def read_elem(self, filename):
        with open(filename) as f:
            return [str(elem) for elem in f.read().split()]


constants = Constants()
