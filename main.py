import sys
import math
import copy
import random
from itertools import permutations
from models.route import Route
from models.solution import Solution
from models.penalty_variables import alpha, beta
from constants import constants
from tsp_local.test import matrix
from tsp_local.base import TSP
from tsp_local.kopt import KOpt


# Algorithm 1 (HAIR—A hybrid heuristic)
def main():
    iterations_without_improvement = 1

    # Apply the Initialization procedure to generate an initial solution sbest.
    s = initialization()
    sbest = copy.deepcopy(s)

    main_iterator = 0
    # while the number of iterations without improvement of sbest ≤ MaxIter do
    while iterations_without_improvement <= MAX_ITER:
        # Apply the Move procedure to find the best solution s´ in the neighborhood N(s) of s.
        sprima = move(s)

        # Update tabu lists
        update_tabu_lists(s, sprima, main_iterator)

        if sprima.cost <= sbest.cost:
            # Apply the Improvement procedure to possibly improve s´ and set sbest ← s´
            sbest = improvement(sprima)
            iterations_without_improvement = 1

        s = copy.deepcopy(sprima)
        if isMultiple(iterations_without_improvement, JUMP_ITER):
            # Apply the Jump procedure to modify the current solution s.
            s = jump(s)

        iterations_without_improvement += 1

        # Update alpha and beta
        alpha.unfeasible() if s.vehicle_capacity_has_exceeded() else alpha.feasible()
        beta.unfeasible() if s.supplier_stockout_situation() else beta.feasible()

        main_iterator += 1
        # print(f"costo sbest = {sbest.cost}")
    print("MEJOR SOLUCION")
    print(s)


def ttl_tabu():
    lambda_ttl = 0.5
    L = 10
    return L + random.randint(0, math.floor(lambda_ttl * math.sqrt(constants.nb_customers*constants.horizon_lenght))-1)


def update_tabu_lists(s, sprima, main_iterator):
    global list_a
    global list_r

    # Acá manejamos las listas del Tabú
    for c in range(constants.nb_customers):
        ts = T(c, s)
        tsprima = T(c, sprima)
        for t in ts:
            if (not (t in tsprima)) and (not forbidden_to_append(c, t)):
                list_a.append([[c, t], main_iterator + ttl_tabu()])

        for t in tsprima:
            if (not (t in ts)) and (not forbidden_to_remove(c, t)):
                list_r.append([[c, t], main_iterator + ttl_tabu()])

    for index, element in enumerate(list_a):
        if list_a[index][1] == main_iterator:
            list_a.pop(index)

    for index, element in enumerate(list_r):
        if list_r[index][1] == main_iterator:
            list_r.pop(index)


def initialization() -> Solution:
    # Each customer is considered sequentially, and the delivery times are set as late as possible before a stockout situation occurs.
    solution = [[[], []] for _ in range(constants.horizon_lenght)]
    routes = []
    for c in range(constants.nb_customers):
        time_stockout = math.floor(
            (constants.start_level[c] - constants.min_level[c]) / constants.demand_rate[c]) - 1
        solution[time_stockout][0].append(c)
        solution[time_stockout][1].append(
            constants.max_level[c] - (constants.start_level[c] - constants.demand_rate[c] * (time_stockout+1)))

        stockout_frequency = math.floor(
            (constants.max_level[c]-constants.min_level[c]) / constants.demand_rate[c])

        for t in range(time_stockout+stockout_frequency, constants.horizon_lenght, stockout_frequency):
            solution[t][0].append(c)
            solution[t][1].append(constants.max_level[c])

    for route in solution:
        routes.append(Route(route[0], route[1]))

    sol = Solution(routes)

    return sol


def move(solution) -> Solution:
    neighborhood_set = neighborhood(solution)

    best_solution = solution

    for sol in neighborhood_set:
        if sol.cost < best_solution.cost:
            best_solution = sol

    # if len(neighborhood_set) > 0:
    #     best_solution = copy.deepcopy(neighborhood_set[0])
    #     min_cost_solution = obj_function(best_solution)
    #     for solution_prima in neighborhood_set:
    #         if obj_function(solution_prima) < min_cost_solution:
    #             best_solution = copy.deepcopy(solution_prima)
    #             min_cost_solution = obj_function(solution_prima)
    # else:
    #     best_solution = solution

    return best_solution


def improvement(solution_best : Solution):
    # Set continue ← true.
    do_continue = True

    empty_solution = Solution([Route(route[0], route[1]) for route in [[[], []] for _ in range(constants.horizon_lenght)] ])
    
    # Set sbest ← LK(sbest)
    solution_best = LK(empty_solution,solution_best)
    # while continue do
    while do_continue:
        # Set continue ← false.
        do_continue = False

        # (* First type of improvement *)
        # Let s' be an optimal solution of MIP1(, sbest). Set s' ← LK(sbest, s').
        solution_prima = MIP1(solution_best)
        solution_prima = LK(solution_best, solution_prima)
       
        # if f(s') < f(sbest) then Set sbest ← s' and continue ← true.
        if solution_prima.cost < solution_best.cost:
            solution_best = copy.deepcopy(solution_prima)
            do_continue = True

        # (* Second type of improvement *)
        # Set smerge ← sbest.
        solution_merge = copy.deepcopy(solution_best)

        # Determine the set L of all pairs (r1, r2) of consecutive routes in sbest.
        L = [[solution_best.routes[r-1], solution_best.routes[r]] for r in range(1,len(solution_best.routes))]
        
        # for all pairs (r1, r2) ∈ L do                                                     
        for i, pair_of_routes in enumerate(L):
            # Let s1 be the solution obtained from sbest by merging r1 and r2 into a single route r
            # assigned to the same time as r1.
            s1 = copy.deepcopy(solution_best)
            s1.routes[i].clients = copy.deepcopy(pair_of_routes[0].clients) + copy.deepcopy(pair_of_routes[1].clients)
            s1.routes[i].quantities = copy.deepcopy(pair_of_routes[0].quantities) + copy.deepcopy((pair_of_routes[1].quantities)) 
            s1.routes[i].refresh()
           
            s1.routes[i+1].clients = []
            s1.routes[i+1].quantities = []
            s1.routes[i+1].refresh()  
            #Refresh s1  
            s1.refresh()

            aux_solution = MIP2(s1)
            #TODO
            # if MIP2(, s1) is infeasible and r is not the last route in s1 then
                # Modify s1 by anticipating the first route after r by one time period.
            

            # if MIP2(, s1) is feasible then
                # Let s' be an optimal solution of MIP2(, s1).
                # Set s' ← LK(s1, s').
            if aux_solution.is_feasible():
                solution_prima = copy.deepcopy(aux_solution)
                solution_prima = LK(s1,solution_prima)
                # if f(s') < f(smerge) then Set smerge ← s'
                if solution_prima.objetive_function() < solution_merge.objetive_function():
                    solution_merge = solution_prima

            # Let s2 be the solution obtained from sbest by merging r1 and r2 into a single route r assigned to the same time as r2.
            s2 = copy.deepcopy(solution_best)
            s2.routes[i+1].clients = copy.deepcopy(pair_of_routes[0].clients) + copy.deepcopy(pair_of_routes[1].clients)
            s2.routes[i+1].quantities = copy.deepcopy(pair_of_routes[0].quantities) + copy.deepcopy((pair_of_routes[1].quantities)) 
            s2.routes[i+1].refresh()
            
            s2.routes[i].clients = []
            s2.routes[i].quantities = []
            s2.routes[i].refresh()  
            #Refresh s2  
            s2.refresh()

            aux_solution = MIP2(s2)
            #TODO
            # if MIP2(, s2) is infeasible and r is not the first route in s2 then
                # Modify s2 by delaying the last route before r by one time period.
            
            # if MIP2(, s2) is feasible then
                # Let s' be an optimal solution of MIP2(, s2).
                # Set s'← LK(s2, s').
            if aux_solution.is_feasible():
                solution_prima = copy.deepcopy(aux_solution)
                solution_prima = LK(s2,solution_prima)
                # if f(s') < f(smerge) then
                    #   Set smerge ← s'
                if solution_prima.objetive_function() < solution_merge.objetive_function():
                    solution_merge = solution_prima

        # if f(smerge) < f(sbest) then Set sbest ← s' and continue ← true.
        if solution_merge.objetive_function() < solution_best.objetive_function():
            solution_best = copy.deepcopy(solution_prima)
            do_continue = True

        # (* Third type of improvement *)
        # Let s' be an optimal solution of MIP2(, sbest).
        solution_prima = MIP2(solution_best)
        # Set s'← LK(sbest, s').
        solution_prima = LK(solution_best, solution_prima)
        
        # if f(s') < f(sbest) then Set sbest ← s' and continue ← true.
        if solution_prima.objetive_function() < solution_best.objetive_function():
            solution_best = solution_prima
            do_continue = True

    return solution_best

def reordenar_lista(array, combinacion):
    nueva_lista = [array[i] for i in combinacion]
    return nueva_lista

def MIP1(solution):
    min_cost = float("inf")
    min_cost_solution = None
    permutation_orders = list(permutations(range(constants.horizon_lenght)))

    for perm in permutation_orders:
        new_solution = copy.deepcopy(solution)
        new_solution.sort_list(perm)

        for i in range(constants.nb_customers):
            # if(passConstraints(new_solution, i)):
            # print("PASA LAS CONSTRAINTS PARA "+str(i))

            # busco el t donde es visitado i
            for time in range(constants.horizon_lenght):
                aux_copy = copy.deepcopy(new_solution)
                if aux_copy.routes[time].is_visited(i):
                    mip_cost = MIP1objFunction(aux_copy, i, time)
                    aux_copy.routes[time].remove_visit(i)
                    aux_copy.refresh()
                    if mip_cost < min_cost and passConstraints(aux_copy, i, time, "REMOVE", "MIP1"):
                        # print("PASA LAS CONSTRAINTS PARA "+str(i)+" - "+str(aux_copy))
                        min_cost = mip_cost
                        min_cost_solution = copy.deepcopy(aux_copy)

    return min_cost_solution if min_cost_solution is not None else solution


def MIP2(solution: Solution) -> Solution:
    # print("ENTRA AL MIP"+str(solution))
    min_cost = float("inf")
    min_cost_solution = solution

    for i in range(constants.nb_customers):
        for time in range(constants.horizon_lenght):
            solution_aux = copy.deepcopy(solution)

            if solution.routes[time].is_visited(i): 
                mip_cost = MIP2objFunction(solution_aux, i, None, time)
                solution_aux.remove_visit(i, time)
                solution_aux.refresh()
                if mip_cost < min_cost and passConstraints(solution_aux, i, time, "REMOVE", "MIP2"):
                    # print("PASA LAS CONSTRAINTS PARA "+str(i)+" - "+str(solution_aux))
                    min_cost = mip_cost
                    min_cost_solution = solution_aux
            else:
                mip_cost = MIP2objFunction(solution_aux, None, i, time)
                solution_aux.insert_visit(i, time)
                solution_aux.refresh()
                if mip_cost < min_cost and passConstraints(solution_aux, i, time, "INSERT", "MIP2"):
                    min_cost = mip_cost
                    min_cost_solution = solution_aux

    # print("MIP2"+str(min_cost_solution))
    return min_cost_solution


def MIP1objFunction(solution: Solution, removed_customer, removed_time):
    term_1 =sum([constants.holding_cost_supplier * solution.supplier_inventory_level[t] 
                for t in range(constants.horizon_lenght+1)])
    term_2 =sum([sum([constants.holding_cost[i] * solution.customers_inventory_level[t][i] 
                for t in range(constants.horizon_lenght+1)])  
                for i in range(constants.nb_customers)])
    #3rd term represents the saving (in this implementation)
    aux_route = copy.deepcopy(solution.routes[removed_time])
    aux_route.remove_visit(removed_customer)
    term_3 = solution.routes[removed_time].cost - aux_route.cost
    return term_1 + term_2 - term_3


def MIP2objFunction(solution, removed_customer, added_customer, time):
    term_1 =sum([constants.holding_cost_supplier * solution.supplier_inventory_level[t] 
                for t in range(constants.horizon_lenght+1)])

    term_2 = sum([sum([constants.holding_cost[i] * solution.customers_inventory_level[t][i]
                for t in range(constants.horizon_lenght)])
                for i in range(constants.nb_customers)])
    
    if removed_customer != None:
        customer_index = solution.routes[time].clients.index(removed_customer)
        aux_route = copy.deepcopy(solution.routes[time])
        aux_route.remove_visit(removed_customer)
        term_3 = solution.routes[time].cost - aux_route.cost
    else:
        term_3 = 0

    if added_customer != None:
        solution_aux = copy.deepcopy(solution)
        solution_aux.insert_visit(added_customer, time)
        solution_aux.refresh()    
        term_4 = sum([solution_aux.routes[it].cost - solution.routes[it].cost for it in range(constants.horizon_lenght)])
    else:
        term_4 = 0

    return term_1 + term_2 - term_3 + term_4


def theeta(solution: Solution, i, t):
    return (1 if solution.routes[t].is_visited(i) else 0)


def passConstraints(solution: Solution, i, t, operation, MIP):
    # Constraint 3
    if solution.supplier_inventory_level[t] < solution.routes[t].get_total_quantity():
        # print("Falla la constraint  3 para" + str(solution))
        return False
    # Constraint 5
    if constants.replenishment_policy == "OU" and solution.routes[t].get_customer_quantity_delivered(i) < constants.max_level[i] * theeta(solution, i, t) - solution.customers_inventory_level[t][i]:
        # print("Falla la constraint  5 para" + str(solution)+" para el cliente "+str(i))
        return False
    # Constraint 6
    if solution.routes[t].get_customer_quantity_delivered(i) > constants.max_level[i] - solution.customers_inventory_level[t][i]:
        # print("Falla la constraint  6 para" + str(solution)+" para el cliente "+str(i))
        return False
    # Constraint 7
    if constants.replenishment_policy == "OU" and solution.routes[t].get_customer_quantity_delivered(i) > constants.max_level[i] * theeta(solution, i, t):
        # print("Falla la constraint  7 para" +
        #       str(solution)+" para el cliente "+str(i))
        return False
    # Constrain 8:
    if solution.routes[t].get_total_quantity() > constants.vehicle_capacity:
        # print("Falla la constraint 8: para" + str(solution))
        return False

    # Constraints 9 -13:
        # TODO (IMPORTANTE: SON SOLO DE MIP1)

    # Constraint 14
    if solution.routes[t].get_total_quantity() < 0:
        # print("Falla la constraint 14 para" + str(solution))
        return False

    for t in range(constants.horizon_lenght+1):
        # Constraint 4
        if solution.customers_inventory_level[t][i] != solution.customers_inventory_level[t-1][i] + solution.routes[t-1].get_customer_quantity_delivered(i) - (constants.demand_rate[i] if t-1 >= 0 else 0):
            # print("Falla la constraint  4 para" +
            #       str(solution)+" para el cliente "+str(i))
            return False
        # Constraint 15
        if solution.customers_inventory_level[t][i] < 0:
            # print("Falla la constraint 15 para" +
            #       str(solution)+" para el cliente "+str(i))
            return False
        # Constraint 16
        if solution.supplier_inventory_level[t] < 0:
            # print("Falla la constraint 16 para" + str(solution))
            return False
    # Constraints 17 -19 son obvias

    if MIP == "MIP2":
        v_it = 1 if (operation == "INSERT") else 0
        sigma_it = 1 if (i in solution[t][0]) else 0
        w_it = 1 if (operation == "REMOVE") else 0

        # Constraint 21
        if v_it > 1 - sigma_it:
            # print("Falla la constraint 21 para" +
            #       str(solution)+" para el cliente "+str(i))
            return False
        # Constraint 22
        if w_it > sigma_it:
            # print("Falla la constraint 22 para" +
            #       str(solution)+" para el cliente "+str(i))
            return False
        # Constraint 23
        if solution.routes[t].get_total_quantity() > constants.max_level[i] * (sigma_it - w_it + v_it):
            # print("Falla la constraint 23 para" +
            #       str(solution)+" para el cliente "+str(i))
            return False
        # Constraint 24
        if v_it < 0 or v_it > 1:
            # print("Falla la constraint 24 para" +
            #       str(solution)+" para el cliente "+str(i))
            return False
        # Constraint 25
        if w_it < 0 or v_it > 1:
            # print("Falla la constraint 25 para" +
            #       str(solution)+" para el cliente "+str(i))
            return False
    return True

def LK(solution: Solution, solution_prima:Solution) -> Solution:
    if solution == solution_prima:
        return solution
    else:
        # Load the distances
        print("soluciones distintas")
        print(solution_prima)
        for time in range(constants.horizon_lenght):
            matrix = [[0 for i in range(len(solution_prima.routes[time].clients)+1)]
                      for j in range(len(solution_prima.routes[time].clients)+1)]
            
            #Provider distance
            for  index, i in enumerate(solution_prima.routes[time].clients):
                matrix[0][index+1] = constants.distance_supplier[i]
                matrix[index+1][0] = constants.distance_supplier[i] 
           
            #Clients distances
            for index, c in enumerate(solution_prima.routes[time].clients):
                for index2, c2 in enumerate(solution_prima.routes[time].clients):
                    matrix[index+1][index2+1] = constants.distance_matrix[c][c2]
            # print(matrix)
            # Load the distances
            TSP.setEdges(matrix)
            # Make an instance with all nodes
            lk = KOpt(range(len(matrix)))
            path, cost = lk.optimise()

            # TODO: Rearmar la ruta en funcion de la respuesta de la optimización
            # print(lk)
            # print("Best path has cost: {}".format(cost))
            

    return solution

# TODO
def jump(solution):
    return solution


def variants_type1(solution: Solution) -> list[Solution]:
    # print("Inicio tipo 1")
    neighborhood_prima = []
    for customer in range(constants.nb_customers):
        # La eliminación del cliente parece ser interesante cuando hi>h0
        if constants.holding_cost[customer] > constants.holding_cost_supplier:
            for time in range(constants.horizon_lenght):
                solution_copy = copy.deepcopy(solution)
                if (solution_copy.routes[time].is_visited(customer)) and (not forbidden_to_remove(customer, time)):
                    solution_copy.remove_visit(customer, time)
                    if solution_copy.is_admissible():
                        neighborhood_prima.append(solution_copy)

    return neighborhood_prima


def variants_type2(solution: Solution) -> list[Solution]:
    # print("Inicio tipo 2")
    neighborhood_prima = []
    for customer in range(constants.nb_customers):
        for time in range(constants.horizon_lenght):
            solution_copy = copy.deepcopy(solution)
            if (not solution_copy.routes[time].is_visited(customer)) and (not forbidden_to_append(customer, time)):
                solution_copy.insert_visit(customer, time)
                if solution_copy.is_admissible():
                    neighborhood_prima.append(solution_copy)

    return neighborhood_prima


def variants_type3(solution: Solution) -> list[Solution]:
    neighborhood_prima = []
    for customer in range(constants.nb_customers):
        set_t_visited = T(customer, solution)
        set_t_not_visited = [x for x in list(
            range(constants.horizon_lenght)) if x not in set_t_visited]

        for t_visited in set_t_visited:
            new_solution = copy.deepcopy(solution)
            quantity_removed = new_solution.routes[t_visited].remove_visit(
                customer)
            for t_not_visited in set_t_not_visited:
                if not forbidden_to_remove(customer, t_visited) and not forbidden_to_append(customer, t_not_visited):
                    saux = copy.deepcopy(new_solution)
                    saux_cheapest_index = saux.routes[t_not_visited].cheapest_index_to_insert(
                        customer)
                    saux.routes[t_not_visited].insert_visit(
                        customer, saux_cheapest_index, quantity_removed)
                    saux.refresh()
                    if saux.is_admissible():
                        print("Solucion admisible en variante 3")
                        neighborhood_prima.append(saux)

    return neighborhood_prima


def variants_type4(solution: Solution):

    neighborhood_prima = []
    for t1 in range(constants.horizon_lenght):
        for index, client1 in enumerate(solution.routes[t1].clients):
            for t2 in range(constants.horizon_lenght):
                if t1 != t2:
                    for index2, client2 in enumerate(solution.routes[t2].clients):
                        if not ((solution.routes[t1].is_visited(client2)) or (solution.routes[t2].is_visited(client1)) or forbidden_to_append(client1, t2) or forbidden_to_remove(client1, t1) or forbidden_to_append(client2, t1) or forbidden_to_remove(client2, t2)):
                            saux = copy.deepcopy(solution)
                            client1_quantity_removed = saux.routes[t1].remove_visit(
                                client1)
                            client2_quantity_removed = saux.routes[t2].remove_visit(
                                client2)
                            client1_cheapes_index = saux.routes[t2].cheapest_index_to_insert(
                                client1)
                            client2_cheapes_index = saux.routes[t1].cheapest_index_to_insert(
                                client2)

                            saux.routes[t1].insert_visit(
                                client2, client2_cheapes_index, client2_quantity_removed)
                            saux.routes[t2].insert_visit(
                                client1, client1_cheapes_index, client1_quantity_removed)
                            saux.refresh()

                            if saux.is_admissible():
                                print("Solucion admisible en variante 4")
                                neighborhood_prima.append(saux)

    return neighborhood_prima


def forbidden_to_append(i, t):
    return any(elemento[0] == [i, t] for elemento in list_a)


def forbidden_to_remove(i, t):
    return any(elemento[0] == [i, t] for elemento in list_r)

# Algorithm 2


def neighborhood(solution) -> list[Solution]:
    # Build N'(s) by using the four simple types of changes on s and set N(s) ← ∅;
    neighborhood_prima = make_neighborhood_prima(solution)
    neighborhood = []

    # for all solutions s' ∈ N'(s) do
    for solution_prima in neighborhood_prima:
        # Determine the set A of customers i with Ti(s) != Ti(s').
        set_A = construct_A(solution, solution_prima)
        # while A is not empty do
        while len(set_A) > 0:
            # Choose a customer i ∈ A and remove it from A.
            removed = set_A.pop(int(random.random() * len(set_A)))
            # for all visit times t ∈ Ti(s') do
            for time in T(removed, solution_prima):
                # for all customers j served at time t in s' and such that t ∈ Tj (s') do
                for j in solution_prima.routes[time].clients:
                    # if hj > h0, Qt(s') > C or Bt(s') < 0 then
                    if (constants.holding_cost[j] > constants.holding_cost_supplier) or (solution_prima.routes[time].get_total_quantity() > constants.vehicle_capacity) or (solution_prima.supplier_inventory_level[time] < 0):
                        # OU policy:
                        if constants.replenishment_policy == "OU":
                            # Let s" be the solution obtained from s' by removing the visit to j at time t.
                            solution_dosprima = copy.deepcopy(solution_prima)
                            solution_dosprima.routes[time].remove_visit(j)
                            solution_dosprima.refresh()

                            # if s" is admissible and f(s") < f(s') then
                            if solution_dosprima.is_admissible() and solution_dosprima.cost < solution_prima.cost:
                                # Set s' ← s" and add j to A.
                                solution_prima = copy.deepcopy(
                                    solution_dosprima)
                                set_A.append(j)
                            # end if

                        # ML policy:
                        if constants.replenishment_policy == "ML":
                            # Let y ← min{xjt, min t'>t Ijt'}.
                            xjt = solution_prima.routes[time].get_customer_quantity_delivered(
                                j)

                            minijt = min(
                                solution_prima.get_all_customer_inventory_level(j)[time:-1])
                            y = min(xjt, minijt)
                            # Let s" be the solution obtained from s' by removing y units of delivery to j at time t (the visit to j at time t is removed if y = xjt).
                            solution_dosprima = copy.deepcopy(solution_prima)
                            if y == xjt:
                                solution_dosprima.routes[time].remove_visit(j)
                            else:
                                solution_dosprima.routes[time].remove_customer_quantity(
                                    j, y)

                            solution_dosprima.refresh()
                            # if f(s") < f(s') then
                            if solution_dosprima.is_admissible() and solution_dosprima.cost < solution_prima.cost:
                                # Set s' ← s"
                                # print("SOLUCION ADMISIBLE")
                                # print(solution_prima)
                                # print(f"se remueve {y} elementos de {j}, xjt: {xjt}")
                                # print(solution_dosprima)
                                solution_prima = copy.deepcopy(
                                    solution_dosprima)
                                # add j to A if j is not visited at time t in s'.
                                if not solution_prima.routes[time].is_visited(j):
                                    set_A.append(j)

                # ML policy:
                if constants.replenishment_policy == "ML":
                    for j in solution_prima.routes[time].clients:
                        if constants.holding_cost[j] < constants.holding_cost_supplier:
                            # Let y ← max t' ≥ t(Ijt' + xjt').
                            Ijt = solution_prima.get_all_customer_inventory_level(
                                j)
                            xjt = solution_prima.get_all_customer_quantity_delivered(
                                j)

                            y = max(
                                list(i+j for (i, j) in zip(xjt, Ijt[:-1]))[time:])

                            # Let s" be the solution obtained from s' by adding Uj − y units of delivery to j at time t.
                            solution_dosprima = copy.deepcopy(solution_prima)
                            solution_dosprima.routes[time].add_customer_quantity(
                                j, constants.max_level[j] - y)

                            solution_dosprima.refresh()
                            if solution_dosprima.cost < solution_prima.cost:
                                solution_prima = copy.deepcopy(
                                    solution_dosprima)

        neighborhood.append(copy.deepcopy(solution_prima))

    return neighborhood

# Returns the set of customers which are not visited at the same time in solution and solution_prima


def construct_A(solution: Solution, solution_prima: Solution) -> list:
    A = []
    for customer in range(constants.nb_customers):
        if not T(customer, solution) == T(customer, solution_prima):
            A.append(customer)
    return A

# Returns the set of times when is visited a customer in a given solution.


def T(customer, solution: Solution):
    times = []
    for time in range(constants.horizon_lenght):
        if solution.routes[time].is_visited(customer):
            times.append(time)
    return times

# Returns a solution's Neighborhood. Obtained by using the four simple types of changes on s.


def make_neighborhood_prima(solution) -> list[Solution]:
    neighborhood_prima = variants_type1(solution)
    neighborhood_prima.extend(variants_type2(solution))
    neighborhood_prima.extend(variants_type3(solution))
    neighborhood_prima.extend(variants_type4(solution))
    # print(neighborhood_prima)
    return neighborhood_prima


def isMultiple(num,  check_with):
    return num % check_with == 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(
            "Usage: python irp.py input_file output_file REPLENISHMENT_POLICY [time_limit]")
        sys.exit(1)

    instance_file = sys.argv[1]
    sol_file = sys.argv[2]

    str_time_limit = sys.argv[4] if len(sys.argv) > 4 else "20"

    MAX_ITER = 200*constants.nb_customers*constants.horizon_lenght
    JUMP_ITER = MAX_ITER // 2
   
    list_a = []
    list_r = []

    main()
