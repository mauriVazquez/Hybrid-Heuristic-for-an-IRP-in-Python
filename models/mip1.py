from itertools import permutations
from constants import constants
from models.solution import Solution
import copy

class Mip1():
    @staticmethod
    def execute(solution : Solution):
        min_cost = float("inf")
        min_cost_solution = None
        permutation_orders = list(permutations(range(constants.horizon_lenght)))

        for perm in permutation_orders:
            new_solution = solution.clone()
            new_solution.sort_list(perm)
            print(new_solution)
            new_solution.refresh()
            
            for i in range(constants.nb_customers):
                # if(passConstraints(new_solution, i)):
                # print("PASA LAS CONSTRAINTS PARA "+str(i))

                # busco el t donde es visitado i
                for time in range(constants.horizon_lenght):
                    aux_copy = new_solution.clone()
                    if aux_copy.routes[time].is_visited(i):
                        mip_cost = Mip1.MIP1objFunction(aux_copy, i, time)
                        aux_copy.routes[time].remove_visit(i)
                        aux_copy.refresh()

                        if mip_cost < min_cost and passConstraints(aux_copy, i, time, "REMOVE", "MIP1"):
                            # print("PASA LAS CONSTRAINTS PARA "+str(i)+" - "+str(aux_copy))
                            min_cost = mip_cost
                            min_cost_solution = aux_copy.clone()

        return min_cost_solution if min_cost_solution is not None else solution
    
    def MIP1objFunction(solution: Solution, removed_customer, removed_time):
        term_1 = sum(constants.holding_cost_supplier * solution.supplier_inventory_level[t]
                    for t in range(constants.horizon_lenght+1))
        term_2 = sum(sum(constants.holding_cost[i] * solution.customers_inventory_level[t][i] for t in range(constants.horizon_lenght+1))
                    for i in range(constants.nb_customers))
        
        # 3rd term represents the saving (in this implementation)
        aux_route = copy.deepcopy(solution.routes[removed_time])
        aux_route.remove_visit(removed_customer)
        term_3 = solution.routes[removed_time].cost - aux_route.cost
        return term_1 + term_2 - term_3