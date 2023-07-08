import sys
import math
import copy
import random

# Algorithm 1 (HAIR—A hybrid heuristic)
def main(replenishment_policy):
    iterations_without_improvement = 1
    

    alpha_feasibles = 0
    alpha_unfeasibles = 0
    beta_feasibles = 0
    beta_unfeasibles = 0

    # Apply the Initialization procedure to generate an initial solution sbest.    
    s = initialization()
    sbest = copy.deepcopy(s)

    # while the number of iterations without improvement of sbest ≤ MaxIter do
    while iterations_without_improvement <= MAX_ITER:
        #Apply the Move procedure to find the best solution s´ in the neighborhood N(s) of s.
        sprima = move(s)

        if obj_function(sprima) < obj_function(sbest):
            #Apply the Improvement procedure to possibly improve s´ and set sbest ← s´
            sbest = improvement(replenishment_policy, sprima)
            iterations_without_improvement = 1

        s = copy.deepcopy(sprima)  
        if isMultiple(iterations_without_improvement, JUMP_ITER):
            #Apply the Jump procedure to modify the current solution s.
            s = jump(s) 

        iterations_without_improvement += 1
        if is_admissible(s):
            if not exceed_capacity_situation(s):
                alpha_feasibles += 1
                alpha_unfeasibles = 0
            else:
                alpha_unfeasibles += 1
                alpha_feasibles = 0

            if alpha_feasibles > 0 and isMultiple(alpha_feasibles, 10):
                alpha = alpha/2
                print('alpha feasible: ' + alpha)
                
            if alpha_unfeasibles > 0 and isMultiple(alpha_unfeasibles, 10):
                alpha = alpha * 2
                print('alpha unfeasible: ' + alpha)
                
            if not supplier_stockout_situation(s):
                beta_feasibles += 1
                beta_unfeasibles = 0
            else:
                beta_unfeasibles += 1
                beta_feasibles = 0

            if beta_feasibles > 0 and isMultiple(beta_feasibles, 10):
                beta = beta/2
                print('beta feasible: ' + beta)
                
            if beta_unfeasibles > 0 and isMultiple(beta_unfeasibles, 10):
                beta = beta * 2
                print('beta unfeasible: ' + beta)

def initialization():
    #Each customer is considered sequentially, and the delivery times are set as late as possible before a stockout situation occurs.         
    solution = [[] for _ in range(HORIZON_LENGTH)]

    vehicle_stock = min(VEHICLE_CAPACITY, START_LEVEL_SUPPLIER)
    current_level_supplier = START_LEVEL_SUPPLIER - vehicle_stock
    current_level = list(START_LEVEL)

    for t in range(HORIZON_LENGTH):
        clients_list = []
        quantities_list = []

        for i in range(NB_CUSTOMERS):
            #Defino el current level para el cliente
            current_level[i] -= DEMAND_RATE[i] 

            #Si necesita, lo reabastezco... Eso si tengo stock en el vehículo
            if current_level[i] <= MIN_LEVEL[i] and vehicle_stock > 0:
                customer_needs = MAX_LEVEL[i] - current_level[i] # lo que el cliente necesita para llenarse
                delivered_products = min(vehicle_stock, customer_needs) # productos entregados
                vehicle_stock -= delivered_products # se lo resto al camion
                current_level[i] += delivered_products # guardo los productos en el cliente
                clients_list.append(i)
                quantities_list.append(delivered_products)

        solution[t] = [ clients_list, quantities_list]

        #Al final del día, agrego los productos necesarios (agrego lo que reste para llegar al mínimo de la capacidad del vehículo y el current_level_supplier)
        quantities_to_add_to_vehicle = min(VEHICLE_CAPACITY, current_level_supplier + PRODUCTION_RATE_SUPPLIER + vehicle_stock) - vehicle_stock
        vehicle_stock += quantities_to_add_to_vehicle
        current_level_supplier -= quantities_to_add_to_vehicle
    print('Solución inicial: ' + str(solution)+' (Costo:'+str(obj_function(solution))+')')
    return solution

def move(solution):
    neighborhood_set = neighborhood(solution)
    if len(neighborhood_set) > 0:
        best_solution = copy.deepcopy(neighborhood_set[0])
        min_cost_solution = obj_function(best_solution)
        for solution_prima in neighborhood_set:
            if obj_function(solution_prima) < min_cost_solution:
                best_solution = copy.deepcopy(solution_prima)
                min_cost_solution = obj_function(solution_prima)
    else:
        best_solution = copy.deepcopy(solution)
    return best_solution

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
            do_continue = True

        # (* Second type of improvement *)
        # Set smerge ← sbest.
        solution_merge = copy.deepcopy(solution)
        # Determine the set L of all pairs (r1, r2) of consecutive routes in sbest.
        # for all pairs (r1, r2) ∈ L do                                                     #TODO
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

#TODO
def MIP1(replenishment_policy, solution):
    savings = []
    for i in range (NB_CUSTOMERS):
        if(passConstraints(solution, i , t)): 
            aux_copy = copy.deepcopy(solution)

            # busco el t donde es visitado i
            for time in range(HORIZON_LENGTH):
                t = aux_copy[time][0].index(i)

            remove_visit(i,t,aux_copy)
            saving = MIP1objFunction(aux_copy, i)
            savings.append(saving)
    minimum = min()

    return minimum

def MIP1objFunction(solution, removed_customer):
    # cual sería t prima
    term_1, term_2, term_3 = 0,0,0
    #TODO: calcular bt
    bt = 1
    for t in range(HORIZON_LENGTH):
        term_1 += HOLDING_COST_SUPPLIER * bt

    for i in range(NB_CUSTOMERS):
        for t in range(HORIZON_LENGTH):
            term_2 += HOLDING_COST[i] * customer_inventory_level(i,solution,t)

    #TODO: calcular savings (This savings is calculated by simply joining the predecessor with the successor of i)
    savings = 1
    # wir binary variable equal to 1 if customer i is removed from route r
    for i in range(NB_CUSTOMERS):
        for r in len(solution):
            wir = 1 if removed_customer == i else 0
            term_3 += savings * wir

    return term_1 + term_2 - term_3


def passConstraints(solution, i, t):
    return True

#TODO
def LK(solution, solution_prima = []):
    return solution

#TODO
def jump(solution):
    return solution

def variants_type1(solution):
    print("COMIENZA TIPO 1")
    neighborhood_prima = []
    for i in range (NB_CUSTOMERS):
        #La eliminación del cliente parece ser interesante cuando hi>h0
        if HOLDING_COST[i] > HOLDING_COST_SUPPLIER:
            for t in range (HORIZON_LENGTH):
                solution_copy = copy.deepcopy(solution)
                if i in solution_copy[t][0]:
                    solution_copy = remove_visit(i,t,solution_copy)
                    if is_admissible(solution_copy):
                        print(str(solution_copy)+ str(obj_function(solution_copy)))
                        neighborhood_prima.append(solution_copy)
                        # print("ADMISSIBLE")
    return neighborhood_prima

def variants_type2(solution):
    print("Inicio tipo 2")
    neighborhood_prima = []
    for i in range (NB_CUSTOMERS):
        for t in range (HORIZON_LENGTH):
            solution_copy = copy.deepcopy(solution)
            if not i in solution_copy[t][0]:
                solution_copy = insert_visit(i, t, solution_copy)
                if is_admissible(solution_copy):
                    print(str(solution_copy)+ str(obj_function(solution_copy)))
                    neighborhood_prima.append(solution_copy)
                    # print("ADMISSIBLE")
    return neighborhood_prima

def variants_type3(solution):
    print("Inicio tipo 3")
    neighborhood_prima = []
    for i in range (NB_CUSTOMERS):
        is_in_list = []
        not_in_list = []
        for t in range (HORIZON_LENGTH):
            if i in solution[t][0]:
                is_in_list.append(t)
            else:
                not_in_list.append(t)

            for is_in in is_in_list:
                quantity = solution[is_in][1][solution[is_in][0].index(i)]
                saux = remove_visit(i, is_in, solution)
                for time_notpresent in not_in_list:
                    saux[time_notpresent][0].append(i)
                    saux[time_notpresent][1].append(quantity)

                    if is_admissible(saux):
                        print(str(saux)+ str(obj_function(saux)))
                        neighborhood_prima.append(saux)
    return neighborhood_prima

def neighborhood(solution):
    # Build N'(s) by using the four simple types of changes on s and set N(s) ← ∅; 
    neighborhood_prima = make_neighborhood_prima(solution)
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
                    if (HOLDING_COST[j] > HOLDING_COST_SUPPLIER) or (total_quantity_delivered(solution_prima, time) > VEHICLE_CAPACITY) or (supplier_inventory_level(solution_prima, time) < 0):
                        # OU policy: 
                        if REPLENISHMENT_POLICY == "OU":
                            # Let s00 be the solution obtained from s0 by removing the visit to j at time t. 
                            solution_dosprima = remove_visit(j, time, solution_prima)
                            # if s00 is admissible and f(s00) < f(s0) then 
                            if is_admissible(solution_dosprima) and obj_function(solution_dosprima) < obj_function(solution_prima):
                                # Set s0 ← s00 and add j to A. 
                                solution_prima = solution_dosprima
                                set_A.append(j)        
                            # end if 

                        # ML policy: 
                        if REPLENISHMENT_POLICY == "ML":
                            # Let y ← min{xjt, mint0>t Ijt0}.
                            xjt = solution_prima[time][1][solution_prima[time][0].index(j)]
                            y = min(xjt, customer_inventory_level(j, solution_prima, time))     #TODO, time or time +1??                            
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
                                if not j in solution_prima[time][0]:
                                    set_A.append(j)

                # ML policy: 
                if REPLENISHMENT_POLICY == "ML":
                    for j in solution_prima[time][0]:
                        if HOLDING_COST[j] < HOLDING_COST_SUPPLIER:
                            # Let y ← max t'≥t(Ijt' + xjt'). 
                            xjt = solution_prima[time][1][solution_prima[time][0].index(j)]
                            y = customer_inventory_level(j, solution_prima, time) + xjt                #TODO Ver que es ese t'

                            # Let s" be the solution obtained from s' by adding Uj − y units of delivery to j at time t. 
                            solution_dosprima = copy.deepcopy(solution_prima)
                            solution_dosprima[time][1][solution_dosprima[time][0].index(j)] += (MAX_LEVEL[j] - y)

                            if obj_function(solution_dosprima) < obj_function(solution_prima):
                                solution_prima = copy.deepcopy(solution_dosprima)

        neighborhood.append(copy.deepcopy(solution_prima)) 
    return neighborhood

def construct_A(solution, solution_prima):
    A = []
    for customer in range(NB_CUSTOMERS):
        if not T(customer, solution) == T(customer, solution_prima):
            A.append(customer)
    return A

def T(customer, solution):
    times = []
    for i in range(HORIZON_LENGTH):
        if customer in solution[i][0]:
            times.append(i)
    return times

def make_neighborhood_prima(solution):
    solution_prima = copy.deepcopy(solution)
    print("Nuevo vecindario")
    neighborhood_prima = variants_type1(solution_prima)
    neighborhood_prima.extend(variants_type2(solution_prima))
    # neighborhood_prima.extend(variants_type3(solution_prima))
    # neighborhood_prima.append(variants_type4(solution))
    print(neighborhood_prima)
    return neighborhood_prima

def obj_function(solution):
    holding_cost, transportation_cost, penalty1, penalty2 = 0, 0, 0, 0

    for t in range(HORIZON_LENGTH):

        #First term (holding_cost)
        bt = supplier_inventory_level(solution, t)
        holding_cost_T = HOLDING_COST_SUPPLIER * bt
        for i in range(NB_CUSTOMERS):
            holding_cost_T += HOLDING_COST[i] * customer_inventory_level(i, solution, t)
        holding_cost += holding_cost_T

        #Second term (transportation_cost)
        transportation_cost += transportation_costs(solution, t)

        #Third term (penalty 1)
        penalty1 += max(0, total_quantity_delivered(solution, t) - VEHICLE_CAPACITY)

        #Fourth term
        penalty2 += max(0, - bt)

    #t prima
    holding_cost_T = HOLDING_COST_SUPPLIER * (supplier_inventory_level(solution, t) + PRODUCTION_RATE_SUPPLIER)
    for i in range(NB_CUSTOMERS):
        holding_cost_T += HOLDING_COST[i] * (customer_inventory_level(i, solution, t) - DEMAND_RATE[i])
    holding_cost += holding_cost_T

    #bt en t prima
    bt += PRODUCTION_RATE_SUPPLIER
    penalty2 += max(0, - bt)

    return holding_cost + transportation_cost + alpha * penalty1 + beta * penalty2

def total_quantity_delivered(solution, t):
    total_delivered = 0
    for i in range(t):
        total_delivered += sum(solution[i][1])
    return total_delivered

def transportation_costs(solution, t):
    transportation_cost = 0
    
    nb_visited = len(solution[t][0])
    if nb_visited == 0:
        return 0
    
    #Transportation cost is sum of dis(supplier,i=0), dist(i,i-1) for 0 < supplier <nb_visited
    for i in range(nb_visited):
        transportation_cost += DIST_SUPPLIER_DATA[solution[t][0][i]] if (i == 0) else DIST_MATRIX_DATA[solution[t][0][i]][solution[t][0][i-1]]

    #Add the cost between last customer and supplier
    transportation_cost += DIST_SUPPLIER_DATA[solution[t][0][nb_visited-1]]
    return transportation_cost

def supplier_inventory_level(solution, t = 0):
    return START_LEVEL_SUPPLIER + sum((PRODUCTION_RATE_SUPPLIER - sum(solution[i][1]) )  for i in range(t))

def customer_inventory_level(customer, solution, t = 0):
    inventory_level = START_LEVEL[customer]
    for i in range(t):
        quantity_delivered = 0 
        if customer in solution[i][0]:
            quantity_delivered = solution[i][1][solution[i][0].index(customer)]
        inventory_level += (- DEMAND_RATE[customer]) + quantity_delivered
    return inventory_level

def remove_visit(customer, t, solution):
    new_solution = copy.deepcopy(solution)
    remove_index = new_solution[t][0].index(customer)
    new_solution[t][0].pop(remove_index)
    new_solution[t][1].pop(remove_index)
    return new_solution

def insert_visit(customer, t, solution):
    new_solution = copy.deepcopy(solution)
    min_cost = float("inf")

    for i in range(len(solution[t][0])+1):
        solution_aux = []
        solution_aux.append(copy.deepcopy(solution[t]))
        solution_aux[0][0].insert(i, customer)
        cost_solution = transportation_costs(solution_aux, 0)
        if cost_solution < min_cost:
            min_cost_index = i
            min_cost = cost_solution

    new_solution[t][0].insert(min_cost_index, customer)
    #TODO: Revisar que estén implementadas las dos políticas
    if REPLENISHMENT_POLICY == "ML":
        delivered = min(MAX_LEVEL[i] - customer_inventory_level(customer, new_solution, t),  VEHICLE_CAPACITY - sum(new_solution[t][1]), supplier_inventory_level(new_solution, t))
        delivered = delivered if delivered > 0 else DEMAND_RATE[i]
        new_solution[t][1].insert(min_cost_index, delivered)   
    else:
        delivered = (MAX_LEVEL[customer] - (customer_inventory_level(customer,new_solution, t)))
        new_solution[t][1].insert(min_cost_index, delivered) 
        for t2 in range(t, HORIZON_LENGTH):
            if i in new_solution[t2][0]:
                new_solution[t2][1][new_solution[t2][0].index(i)] -= delivered 
    return new_solution

#TODO
def is_admissible(solution):
    client_has_stockout = client_stockout_situation(solution)
    client_has_overstock = client_overstock_situation(solution)
    return not (client_has_stockout or client_has_overstock)

def is_feasible(solution):

    supplier_has_stockout = supplier_stockout_situation(solution)
    capacity_exceeded = exceed_capacity_situation(solution)
    return is_admissible(solution) and not (supplier_has_stockout or capacity_exceeded)

def client_overstock_situation(solution):
    for i in range(NB_CUSTOMERS):
        for t in range(HORIZON_LENGTH):
           if customer_inventory_level(i, solution, t+1) > MAX_LEVEL[i]:
                return True
    return False

def client_stockout_situation(solution):
    for i in range(NB_CUSTOMERS):
        for t in range(HORIZON_LENGTH):
           if customer_inventory_level(i, solution, t+1) < MIN_LEVEL[i]:
                return True
    return False

def supplier_stockout_situation(solution):
    initial = START_LEVEL_SUPPLIER

    for t in range(HORIZON_LENGTH):
        initial = initial + PRODUCTION_RATE_SUPPLIER - sum(solution[t][1])
        if initial < 0:
            return True

    return False

def exceed_capacity_situation(solution):
    for t in range(HORIZON_LENGTH):
        if sum(solution[t][1]) > VEHICLE_CAPACITY:
            return True

    return False

def read_elem(filename):
    with open(filename) as f:
        return [str(elem) for elem in f.read().split()]

# The input files follow the "Archetti" format
def read_input_irp(filename):
    file_it = iter(read_elem(filename))

    nb_customers = int(next(file_it)) - 1
    horizon_lenght = int(next(file_it))
    vehicle_capacity = int(next(file_it))

    x_coord = [None] * nb_customers
    y_coord = [None] * nb_customers
    start_level = [None] * nb_customers
    max_level = [None] * nb_customers
    min_level = [None] * nb_customers
    demand_rate = [None] * nb_customers
    holding_host = [None] * nb_customers

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
        holding_host[i] = float(next(file_it))

    distance_matrix = compute_distance_matrix(x_coord, y_coord)
    distance_supplier = compute_distance_supplier(
        x_coord_supplier, y_coord_supplier, x_coord, y_coord)

    return nb_customers, horizon_lenght, vehicle_capacity, start_level_supplier, \
        production_rate_supplier, holding_cost_supplier, start_level, max_level, \
        min_level, demand_rate, holding_host, distance_matrix, distance_supplier


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

def isMultiple(num,  check_with):
	return num % check_with == 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python irp.py input_file output_file REPLENISHMENT_POLICY [time_limit]")
        sys.exit(1)

    instance_file = sys.argv[1]
    sol_file = sys.argv[2]
    REPLENISHMENT_POLICY = sys.argv[3]
    str_time_limit = sys.argv[4] if len(sys.argv) > 4 else "20"
    
    NB_CUSTOMERS, HORIZON_LENGTH, VEHICLE_CAPACITY, START_LEVEL_SUPPLIER, PRODUCTION_RATE_SUPPLIER, \
    HOLDING_COST_SUPPLIER, START_LEVEL, MAX_LEVEL, MIN_LEVEL, DEMAND_RATE, HOLDING_COST, \
    DIST_MATRIX_DATA, DIST_SUPPLIER_DATA = read_input_irp(instance_file)
    
    MAX_ITER = 200*NB_CUSTOMERS*HORIZON_LENGTH
    JUMP_ITER = MAX_ITER // 2

    #penalty variables
    alpha = 1
    beta = 1
    
    main(REPLENISHMENT_POLICY)


