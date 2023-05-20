import sys
import math
import copy
import random


def main(instance_file, str_time_limit, sol_file, replenishment_policy):
    
    # Read instance data
    MAX_ITER = 200*nb_customers*horizon_length
    JUMP_ITER = MAX_ITER // 2
    
    # Algorithm 1 (HAIR—A hybrid heuristic)
    # Apply the Initialization procedure to generate an initial solution s.    
    s = initialization()
    print(s)
    print(dist_matrix_data)
    print(dist_supplier_data)
    print(transportation_costs(s,0))
    # Set sbest ← s.
    sbest = copy.deepcopy(s)
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

    
def initialization() -> list:
    #     In the Initialization procedure, each customer from 1
    # to n is considered sequentially, and the delivery times
    # are set as late as possible before a stockout situation
    # occurs. Such a solution is obviously admissible but
    # not necessarily feasible
        
    routes = [[]] * horizon_length
    
    vehicle_stock = min(capacity, start_level_supplier)
    current_level_supplier = start_level_supplier - vehicle_stock
    current_level = list(start_level)

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
          
    return routes   


def move(solution):
    #neighborhood of s
    neighborhood = neighborhood(solution)
    best_solution = neighborhood[0]
    min_cost_solution = obj_function(best_solution)
    for solution_prima in neighborhood:
        if obj_function(solution_prima) < min_cost_solution:
            best_solution = solution_prima
            min_cost_solution = obj_function(solution_prima)
    return copy.deepcopy(best_solution)


def improvement(replenishment_policy, solution):
    # Set continue ← true.
    do_continue = True
    # Set sbest ← LK(sbest)
    solution = LK(solution)
    # while continue do
    while do_continue:
        # Set continue ← false.
        do_continue = False
 
        # (* First type of improvement *)
        # Let s' be an optimal solution of MIP1(, sbest). Set s0 ← LK(sbest, s0).
        solution_prima = MIP1(replenishment_policy, solution)
        solution_prima = LK(solution, solution_prima)
        # if f(s') < f(sbest) then Set sbest ← s' and continue ← true.
        if obj_function(solution_prima) < obj_function(solution):
            solution = copy.deepcopy(solution_prima)
            do_continue = true

        # (* Second type of improvement *)
        # Set smerge ← sbest.
        solution_merge = copy.deepcopy(solution)
        # Determine the set L of all pairs (r1, r2) of consecutive routes in sbest.
        # for all pairs (r1, r2) ∈ L do                                                     #TO DO
            # Let s1 be the solution obtained from sbest by merging r1 and r2 into a single route r
            # assigned to the same time as r1.
    
            # if MIP2(, s1) is infeasible and r is not the last route in s1 then 
                # Modify s1 by anticipating the first route after r by one time period.
            # if MIP2(, s1) is feasible then
                # Let s' be an optimal solution of MIP2(, s1). 
                # Set s' ← LK(s1, s0).

            # if f(s') < f(smerge) then 
                # Set smerge ← s'

            # Let s2 be the solution obtained from sbest by merging r1 and r2 into a single route r assigned to the same time as r2.
            # if MIP2(, s2) is infeasible and r is not the first route in s2 then 
                # Modify s2 by delaying the last route before r by one time period.
            # if MIP2(, s2) is feasible then
                # Let s' be an optimal solution of MIP2(, s2). 
                # Set s'← LK(s2, s0).
                # if f(s') < f(smerge) then 
                #   Set smerge ← s'

        # if f(smerge) < f(sbest) then 
            #Set sbest ← s'
            #continue ← true. 
        
        #(* Third type of improvement *)
        #Let s' be an optimal solution of MIP2(, sbest). 
        # Set s'← LK(sbest, s0).

        # if f(s') < f(sbest) then 
            #Set sbest ← s'
            # continue ← true.

    return solution

def LK(solution):
    return None

def jump(solution):
    return None


def neighborhood(solution):
    # Build N'(s) by using the four simple types of changes on s and set N(s) ← ∅; 
    neighborhood_prima = make_neighborhood_prima()
    neighborhood = []

    # for all solutions s0 ∈ N0(s) do
    for solution_prima in neighborhood_prima:
    # Determine the set A of customers i with Ti(s) != Ti(s'). 
        set_A = construct_A(solution,solution_prima)
        # while A is not empty do 
        while len(set_A) > 0:
        # Choose a customer i ∈ A and remove it from A. 
            removed = set_A.pop(int(random.random() * len(set_A)))
            
            # for all visit times t ∈ Ti(s') do 
            for time in T(removed, solution_prima):
                # for all customers j served at time t in s' and such that t ∈ Tj (s') do
                for j in solution_prima[time][0]:
                    # if hj > h0, Qt(s0) > C or Bt(s0) < 0 then 
                    if (holding_cost[j] > holding_cost_supplier) or (total_quantity_delivered(solution_prima, time) > capacity) or (supplier_inventory_level(solution_prima, time) < 0):
                        # OU policy: 
                        if replenishment_policy == "OU":
                            # Let s00 be the solution obtained from s0 by removing the visit to j at time t. 
                            solution_dosprima = remove_visit(j, time, solution_prima)
                            # if s00 is admissible and f(s00) < f(s0) then 
                            if is_admissible(solution_dosprima) and obj_function(solution_dosprima) < obj_function(solution_prima):
                                # Set s0 ← s00 and add j to A. 
                                solution_prima = solution_dosprima
                                set_A.append(j)        
                            # end if 

                        # ML policy: 
                        if replenishment_policy == "ML":
                            # Let y ← min{xjt, mint0>t Ijt0}.
                            xjt = solution_prima[time][1][solution_prima[time][0].index(j)]
                            y = min(xjt, customer_inventory_level(j, solution_prima, time))     #TO DO, time or time +1??                            
                            # Let s'' be the solution obtained from s' by removing y units of delivery to j at time t (the visit to j at time t is removed if y = xjt). 
                            if y == xjt:
                                solution_dosprima = remove_visit(j, time, solution_prima)
                            else:
                                solution_dosprima = copy.deepcopy(solution_prima)
                                solution_dosprima[time][1][solution_dosprima[time][0].index(j)] -= y
                        
                            # if f(s00) < f(s0) then 
                            if obj_function(solution_dosprima) < obj_function(solution_prima):
                                # Set s0 ← s00
                                solution_prima = copy.deepcopy(solution_dosprima)
                                #add j to A if j is not visited at time t in s'. 
                                if not (j in solution_prima[time][0]):
                                    set_A.append(j)
                           
                # ML policy: 
                if replenishment_policy == "ML":
                    # for all customers j served at time t in s0 do 
                    for j in solution_prima[time][0]:
                        # if hj < h0 then 
                        if holding_cost[j] < holding_cost_supplier:
                            # Let y ← maxt0≥t(Ijt0 + xjt0). 
                            xjt = solution_prima[time][1][solution_prima[time][0].index(j)]
                            y = customer_inventory_level(j, solution_prima, time) + xjt                #TO DO Ver que es ese t'
                            # Let s00 be the solution obtained from s0 by adding Uj − y units of delivery to j at time t. 
                            solution_dosprima = copy.deepcopy(solution_prima)
                            solution_dosprima[time][1][solution_dosprima[time][0].index(j)] += (max_level[j] - y)
                            # if f(s00) < f(s0) then 
                            if obj_function(solution_dosprima) < obj_function(solution_prima)
                                # Set s0 ← s00. 
                                solution_prima = copy.deepcopy(solution_dosprima)
                            # end if 
                        # end if 
                    # end for 
         
        # Add s0to N(s).
        neighborhood.append(copy.deepcopy(solution_prima)) 
    return neighborhood

def construct_A(solution, solution_prima):
    A = []
    for customer in range(nb_customers):
        if not (T(customer, solution) == T(customer, solution_prima)):
            A.append(customer)
    return A

def T(customer, solution):
    times = []
    for i in range(horizon_length):
        if customer in solution[i][0]:
            times.append(i)
    return times

def make_neighborhood_prima(solution):
    return None

def obj_function(solution):
    # funcion
    return None

def total_quantity_delivered(solution, t):
    total_delivered = 0
    for i in range(t):
        total_delivered += sum(solution[i][1])
    
    return total_delivered

def transportation_costs(solution, t):

    transportation_cost = 0
    nb_visted = len(solution[t][0])
    for i in range(nb_visted):
        if i == 0:
            transportation_cost += dist_supplier_data[solution[t][0][i]]
        else:
            transportation_cost += dist_matrix_data[solution[t][0][i]][solution[t][0][i-1]]
            
    transportation_cost += dist_supplier_data[solution[t][0][nb_visted-1]]
    
    return transportation_cost

def supplier_inventory_level(solution, t = 0):
    
    inventory_level = start_level_supplier
    for i in range(t):
        inventory_level += production_rate_supplier - ( sum(solution[i][1]) )
    
    return inventory_level

def customer_inventory_level(customer, solution, t = 0):
    inventory_level = start_level[customer]
    for i in range(t):
        quantity_delivered = 0 
        if customer in solution[i][0]:
            quantity_delivered = solution[i][1][solution[i][0].index(customer)]
        
        inventory_level += (- demand_rate[customer]) + quantity_delivered
    return inventory_level

def remove_visit(customer, t, solution):
    new_solution = copy.deepcopy(solution)
    remove_index = new_solution[t][0].index(customer)
    new_solution[t][0].pop(remove_index)
    new_solution[t][1].pop(remove_index)
    return new_solution

def insert_visit(customer, t, solution):
    new_solution = copy.deepcopy(solution)
    if not (customer in new_solution[t][0]):
        new_solution[t][0].append(customer)
        #No es 0, VER!!!
        new_solution[t][0].append(0)    #TO DO
        

def archetti_obj(x, c, d):
    """
    Función objetivo de Archetti.

    Parámetros:
    x -- Lista de variables de decisión.
    c -- Lista de costos unitarios de producción.
    d -- Lista de demandas de los productos.

    Retorna:
    El valor de la función objetivo.
    """
    n = len(x)
    return sum(c[i]*x[i] for i in range(n)) + max(c[i]*x[i] for i in range(n)) + max(0, sum(x) - d)

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
    
    nb_customers, horizon_length, capacity, start_level_supplier, production_rate_supplier, \
    holding_cost_supplier, start_level, max_level, demand_rate, holding_cost, \
    dist_matrix_data, dist_supplier_data = read_input_irp(instance_file)
    
    main(instance_file, str_time_limit, sol_file, replenishment_policy)


def isMultiple(num,  check_with):
	return num % check_with == 0