import sys
import math
import copy
import random

from models.route import Route
from models.solution import Solution
from models.penalty_variables import alpha, beta
from models.tripletManager import triplet_manager
from models.tabulists import tabulists
from models.mip1 import Mip1
from models.mip2 import Mip2
from constants import constants

from tsp_local.base import TSP
from tsp_local.kopt import KOpt


# Algorithm 1 (HAIR—A hybrid heuristic)
def main():
    s = initialization()
    sbest = s.clone()
    
    iterations_without_improvement = 0
    main_iterator = 0
    
    while iterations_without_improvement <= MAX_ITER:
        sprima = move(s)
        
        # Update tabu lists
        update_tabu_lists(s, sprima, main_iterator)
        
        if sprima.cost < sbest.cost:
            # Apply the Improvement procedure to POSSIBLY improve s´
            sbest = improvement(sprima)
            iterations_without_improvement = 0
        else:
            iterations_without_improvement += 1
          
        s = sprima.clone()

        #TO DO: Preguntar si es jump(s) o jump(sbest), nosotros lo cambiaríamos por sbest, pero no sé si es tan obvio
        if isMultiple(iterations_without_improvement, JUMP_ITER):
            while True:
                sjump = sbest.jump(triplet_manager.get_random_triplet())
                if not sjump.client_stockout_situation():
                    s = Mip2.execute(sjump.clone())
                    break
                if len(triplet_manager.triplets) == 0:
                    break              
            triplet_manager.reset()

        #TO DO: SON SIEMPRE FEASIBLES
        # Update alpha and beta
        # alpha.unfeasible() if s.vehicle_capacity_has_exceeded() else alpha.feasible()
        # beta.unfeasible() if s.supplier_stockout_situation() else beta.feasible()

        #Considerar que es para cuando se hace una sola vez
        if iterations_without_improvement > (JUMP_ITER/2) and iterations_without_improvement <= JUMP_ITER:
            triplet_manager.remove_triplets_from_solution(s)
            print(triplet_manager.triplets)
        
        main_iterator += 1
        print(f"costo sbest = {sbest.cost}")

    print("MEJOR SOLUCION")
    print(sbest)

 # Acá manejamos las listas del Tabú
def update_tabu_lists(s: Solution, sprima: Solution, main_iterator):
    for c in range(constants.nb_customers):
        tabulists.add_forbiddens(s.T(c), sprima.T(c), c, main_iterator)
    tabulists.update_lists(main_iterator)
    

def initialization() -> Solution:
    # Each customer is considered sequentially, and the delivery times are set as late as possible before a stockout situation occurs.
    solution = [[[], []] for _ in range(constants.horizon_length)]
    
    for c in range(constants.nb_customers):
        time_stockout = math.floor(
            (constants.start_level[c] - constants.min_level[c]) / constants.demand_rate[c]) - 1
        solution[time_stockout][0].append(c)
        solution[time_stockout][1].append(
            constants.max_level[c] - (constants.start_level[c] - constants.demand_rate[c] * (time_stockout+1)))
        stockout_frequency = math.floor(
            (constants.max_level[c] - constants.min_level[c]) / constants.demand_rate[c])

        for t in range(time_stockout+stockout_frequency, constants.horizon_length, stockout_frequency):
            solution[t][0].append(c)
            solution[t][1].append(constants.max_level[c])
    
    return Solution([Route(route[0], route[1]) for route in solution])


def move(solution) -> Solution:
    neighborhood_set = neighborhood(solution)
    best_solution = solution.clone()
    for sol in neighborhood_set:
        if sol.cost < best_solution.cost:
            best_solution = sol
    return best_solution


def improvement(solution_best: Solution):
    do_continue = True
    solution_best = LK(Solution.get_empty_solution(), solution_best)   

    while do_continue:
        do_continue = False

        # (* First type of improvement *)
        solution_prima = Mip1.execute(solution_best)
        solution_prima = LK(solution_best, solution_prima)

        if solution_prima.cost < solution_best.cost:
            solution_best = solution_prima.clone()
            do_continue = True

        # (* Second type of improvement *)
        solution_merge = solution_best.clone()

        # Determine the set L of all pairs (r1, r2) of consecutive routes in sbest.
        L = [[solution_best.routes[r-1], solution_best.routes[r]]
             for r in range(1, len(solution_best.routes))]

        for i, pair_of_routes in enumerate(L):
            # Let s1 be the solution obtained from sbest by merging r1 and r2 into a single route r
            # assigned to the same time as r1.
            s1 = solution_best.clone()
            s1.routes[i].clients.extend(pair_of_routes[1].clients)
            s1.routes[i].quantities.extend(pair_of_routes[1].quantities)
            s1.routes[i].refresh()
            s1.routes[i+1].clients = []
            s1.routes[i+1].quantities = []
            s1.routes[i+1].refresh()
            s1.refresh()

            aux_solution = Mip2.execute(s1)
            # if MIP2(, s1) is infeasible and r is not the last route in s1 then
            # Modify s1 by anticipating the first route after r by one time period.
            if not aux_solution.is_feasible() and i + 2 < len(s1.routes):
                s1.routes[i+1].clients = copy.deepcopy(s1.routes[i+2].clients)
                s1.routes[i + 1].quantities = copy.deepcopy(s1.routes[i+2].quantities)
                s1.routes[i+1].refresh()
                s1.routes[i+2].clients = []
                s1.routes[i+2].quantities = []
                s1.routes[i+2].refresh()
                s1.refresh()
               
            # if MIP2(, s1) is feasible then
            # Let s' be an optimal solution of MIP2(, s1).
            # Set s' ← LK(s1, s').
            aux_solution = Mip2.execute(s1)
            if aux_solution.is_feasible():
                solution_prima = aux_solution.clone()
                solution_prima = LK(s1, solution_prima)
                if solution_prima.objetive_function() < solution_merge.objetive_function():
                    solution_merge = solution_prima

            # Let s2 be the solution obtained from sbest by merging r1 and r2 into a single route r assigned to the same time as r2.
            s2 = solution_best.clone()
            s2.routes[i+1].clients = pair_of_routes[0].clients + pair_of_routes[1].clients
            s2.routes[i+1].quantities = pair_of_routes[0].quantities + pair_of_routes[1].quantities
            s2.routes[i+1].refresh()
            s2.routes[i].clients = []
            s2.routes[i].quantities = []
            s2.routes[i].refresh()
            s2.refresh()

            aux_solution = Mip2.execute(s2)
            # if MIP2(, s2) is infeasible and r is not the first route in s2 then
            # Modify s2 by delaying the last route before r by one time period.
            if not aux_solution.is_feasible() and i > 0:
                s2.routes[i].clients = copy.deepcopy(s2.routes[i-1].clients)
                s2.routes[i].quantities = copy.deepcopy(s2.routes[i-1].quantities)
                s2.routes[i].refresh()
                s2.routes[i-1].clients = []
                s2.routes[i-1].quantities = []
                s2.routes[i-1].refresh()
                s2.refresh()
            
            aux_solution = Mip2.execute(s2)
            if aux_solution.is_feasible():
                solution_prima = aux_solution.clone()
                solution_prima = LK(s2, solution_prima)
                if solution_prima.objetive_function() < solution_merge.objetive_function():
                    solution_merge = solution_prima.clone()

        # if f(smerge) < f(sbest) then Set sbest ← s' and continue ← true.
        if solution_merge.objetive_function() < solution_best.objetive_function():
            solution_best = solution_prima.clone()
            do_continue = True

        # (* Third type of improvement *)
        solution_prima = Mip2.execute(solution_best)
        solution_prima = LK(solution_best, solution_prima)
        if solution_prima.objetive_function() < solution_best.objetive_function():
            solution_best = solution_prima
            do_continue = True

    return solution_best

# TODO
def jump(solution: Solution) -> Solution:

    return solution

# Algorithm 2
def neighborhood(solution) -> list[Solution]:
    # Build N'(s) by using the four simple types of changes on s and set N(s) ← ∅;
    neighborhood_prima = make_neighborhood_prima(solution)
    neighborhood = []

    # for all solutions s' ∈ N'(s) do
    for solution_prima in neighborhood_prima:
        # Determine the set A of customers i with Ti(s) != Ti(s').
        set_A = solution.construct_A(solution_prima)
        # while A is not empty do
        while len(set_A) > 0:
            # Choose a customer i ∈ A and remove it from A.
            removed = set_A.pop(int(random.random() * len(set_A)))
            # for all visit times t ∈ Ti(s') do
            for time in solution_prima.T(removed):
                # for all customers j served at time t in s' and such that t ∈ Tj (s') do
                for j in solution_prima.routes[time].clients:
                    # if hj > h0, Qt(s') > C or Bt(s') < 0 then
                    if (constants.holding_cost[j] > constants.holding_cost_supplier) or (solution_prima.routes[time].get_total_quantity() > constants.vehicle_capacity) or (solution_prima.supplier_inventory_level[time] < 0):
                        # OU policy:
                        if constants.replenishment_policy == "OU":
                            # Let s" be the solution obtained from s' by removing the visit to j at time t.
                            solution_dosprima = solution_prima.clone()
                            solution_dosprima.routes[time].remove_visit(j)
                            solution_dosprima.refresh()

                            # if s" is admissible and f(s") < f(s') then
                            if solution_dosprima.is_admissible() and solution_dosprima.cost < solution_prima.cost:
                                # Set s' ← s" and add j to A.
                                solution_prima = solution_dosprima.clone()
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
                            solution_dosprima = solution_prima.clone()
                            if y == xjt:
                                solution_dosprima.routes[time].remove_visit(j)
                            else:
                                solution_dosprima.routes[time].remove_customer_quantity(
                                    j, y)

                            solution_dosprima.refresh()
                            # if f(s") < f(s') then
                            if solution_dosprima.is_admissible() and solution_dosprima.cost < solution_prima.cost:
                                # Set s' ← s"
                                solution_prima = solution_dosprima.clone()
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
                            solution_dosprima = solution_prima.clone()
                            solution_dosprima.routes[time].add_customer_quantity(
                                j, constants.max_level[j] - y)

                            solution_dosprima.refresh()
                            if solution_dosprima.cost < solution_prima.cost:
                                solution_prima = solution_dosprima.clone()

        neighborhood.append(solution_prima.clone())

    return neighborhood

# Returns a solution's Neighborhood. Obtained by using the four simple types of changes on s.
def make_neighborhood_prima(solution: Solution) -> list[Solution]:
    neighborhood_prima = solution.variants_type1()
    neighborhood_prima.extend(solution.variants_type2())
    neighborhood_prima.extend(solution.variants_type3())
    neighborhood_prima.extend(solution.variants_type4())
    return neighborhood_prima

def isMultiple(num,  check_with):
    return num != 0 and num % check_with == 0

def LK(solution: Solution, solution_prima: Solution) -> Solution:
    if solution == solution_prima:
        return solution
    else:

        for time in range(constants.horizon_length):
            matrix = [[0 for i in range(len(solution_prima.routes[time].clients)+1)]
                      for j in range(len(solution_prima.routes[time].clients)+1)]

            # Provider distance
            for index, i in enumerate(solution_prima.routes[time].clients):
                matrix[0][index+1] = constants.distance_supplier[i]
                matrix[index+1][0] = constants.distance_supplier[i]

            # Clients distances
            for index, c in enumerate(solution_prima.routes[time].clients):
                for index2, c2 in enumerate(solution_prima.routes[time].clients):
                    matrix[index+1][index2+1] = constants.distance_matrix[c][c2]
            # print(matrix)
            # Make an instance with all nodes
            TSP.setEdges(matrix)

            lk = KOpt(range(len(matrix)))
            # print(matrix)

            #
            # Load the distances
            path, cost = lk.optimise()

            aux = [[], []]
            for index in path[1:]:
                aux[0].append(solution_prima.routes[time].clients[index-1])
                aux[1].append(solution_prima.routes[time].quantities[index-1])
            solution_prima.routes[time] = Route(aux[0], aux[1])
    solution_prima.refresh()
    return solution_prima

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(
            "Usage: python irp.py input_file output_file REPLENISHMENT_POLICY [time_limit]")
        sys.exit(1)

    instance_file = sys.argv[1]
    sol_file = sys.argv[2]

    str_time_limit = sys.argv[4] if len(sys.argv) > 4 else "20"

    MAX_ITER = 200*constants.nb_customers*constants.horizon_length
    JUMP_ITER = MAX_ITER // 2
    main()