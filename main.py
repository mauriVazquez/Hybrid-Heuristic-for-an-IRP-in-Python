import sys
import math


def main(instance_file, str_time_limit, sol_file, replenishment_policy):

    # Read instance data
    nb_customers, horizon_length, capacity, start_level_supplier, production_rate_supplier, \
        holding_cost_supplier, start_level, max_level, demand_rate, holding_cost, \
        dist_matrix_data, dist_supplier_data = read_input_irp(instance_file)
    
    MAX_ITER = 200*nb_customers*horizon_length
    JUMP_ITER = MAX_ITER // 2
    
    # Algorithm 1 (HAIR—A hybrid heuristic)
    # Apply the Initialization procedure to generate an initial solution s.    
    s = initialization(nb_customers, horizon_length, capacity, start_level_supplier, production_rate_supplier, \
        holding_cost_supplier, start_level, max_level, demand_rate, holding_cost, \
        dist_matrix_data, dist_supplier_data)
    # Set sbest ← s.
    sbest = s
    iterations_without_improvement = 0
    
    # while the number of iterations without improvement of sbest ≤ MaxIter do
    while iterations_without_improvement <= MAX_ITER:
        iterations_without_improvement += 1      
    #   Apply the Move procedure to find the best solution s´ in the neighborhood N(s) of s.
        sprima = move(s)
    #   if s´ is better than sbest then
        if obj_function(sprima) < obj_function(sbest):
    #       Apply the Improvement procedure to possibly improve s´ and set sbest ← s´
            sbest = improvement(replenishment_policy, sprima)
            iterations_without_improvement = 0
    
    #   Set s ← s´
        s = sprima
            
    #   if the number of iterations without improvement of sbest is a multiple of JumpIter then
        if isMultiple(iterations_without_improvement, JUMP_ITER):
    #       Apply the Jump procedure to modify the current solution s.
            s = jump(s) 

    
def initialization(nb_customers, horizon_length, capacity, start_level_supplier, production_rate_supplier, \
        holding_cost_supplier, start_level, max_level, demand_rate, holding_cost, \
        dist_matrix_data, dist_supplier_data):
    #     In the Initialization procedure, each customer from 1
    # to n is considered sequentially, and the delivery times
    # are set as late as possible before a stockout situation
    # occurs. Such a solution is obviously admissible but
    # not necessarily feasible
        
    routes = [[]] * horizon_length
    
    vehicle_stock = min(capacity, start_level_supplier)
    current_level_supplier = start_level_supplier - vehicle_stock
    current_level = start_level
    print('lo que consumen los clientes')
    print(demand_rate)
    
    print('stock clientes incial')
    print(start_level)
    for t in range(horizon_length):
        route_aux = []
        quantities_delivered_aux = []
        for i in range(nb_customers):
            current_level[i] = current_level[i] - demand_rate[i] # lo que el cliente tiene - lo que gasta por unidad de tiempo
            #client stockout situation
            if current_level[i] <= 0 and vehicle_stock > 0:
                route_aux.append(i)
                customer_needs = max_level[i] - current_level[i] # lo que el cliente necesita para llenarse
                delivered_products = min(vehicle_stock, customer_needs) # productos entregados
                quantities_delivered_aux.append(delivered_products)
                vehicle_stock -= delivered_products # se lo resto al camion
                current_level[i] += delivered_products # guardo los productos en el cliente
        routes[t] = [ route_aux, quantities_delivered_aux]
        current_level_supplier += production_rate_supplier + vehicle_stock # al final del dia añado los nuevos productos y si sobro del camion.
        vehicle_stock = min(capacity, current_level_supplier)

    print('SOLUCION:')
    print(routes)
             
    return routes   


def move(solution):
    #neighborhood of s
    return None   


def improvement(replenishment_policy, solution):
    return None


def jump(solution):
    return None


def obj_function(solution):
    return None


def read_elem(filename):
    with open(filename) as f:
        return [str(elem) for elem in f.read().split()]


# The input files follow the "Archetti" format
def read_input_irp(filename):
    file_it = iter(read_elem(filename))

    nb_customers = int(next(file_it)) - 1
    horizon_length = int(next(file_it))
    capacity = int(next(file_it))

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

    distance_matrix = compute_distance_matrix(x_coord, y_coord)
    distance_supplier = compute_distance_supplier(
        x_coord_supplier, y_coord_supplier, x_coord, y_coord)

    return nb_customers, horizon_length, capacity, start_level_supplier, \
        production_rate_supplier, holding_cost_supplier, start_level, max_level, \
        demand_rate, holding_cost, distance_matrix, distance_supplier


# Compute the distance matrix
def compute_distance_matrix(x_coord, y_coord):
    nb_customers = len(x_coord)
    distance_matrix = [[None for i in range(
        nb_customers)] for j in range(nb_customers)]
    for i in range(nb_customers):
        distance_matrix[i][i] = 0
        for j in range(nb_customers):
            dist = compute_dist(x_coord[i], x_coord[j], y_coord[i], y_coord[j])
            distance_matrix[i][j] = dist
            distance_matrix[j][i] = dist
    return distance_matrix


# Compute the distances to the supplier
def compute_distance_supplier(x_coord_supplier, y_coord_supplier, x_coord, y_coord):
    nb_customers = len(x_coord)
    distance_supplier = [None] * nb_customers
    for i in range(nb_customers):
        dist = compute_dist(
            x_coord_supplier, x_coord[i], y_coord_supplier, y_coord[i])
        distance_supplier[i] = dist
    return distance_supplier


def compute_dist(xi, xj, yi, yj):
    return round(math.sqrt(math.pow(xi - xj, 2) + math.pow(yi - yj, 2)))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python irp.py input_file output_file replenishment_policy [time_limit]")
        sys.exit(1)

    instance_file = sys.argv[1]
    sol_file = sys.argv[2]
    replenishment_policy = sys.argv[3]
    str_time_limit = sys.argv[4] if len(sys.argv) > 4 else "20"
    
    main(instance_file, str_time_limit, sol_file, replenishment_policy)


def isMultiple(num,  check_with):
	return num % check_with == 0