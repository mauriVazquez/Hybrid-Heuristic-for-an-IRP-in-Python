from itertools import permutations
from constants import constants
from models.solution import Solution
import copy


class Mip1():
    @staticmethod
    def execute(solution: Solution):
        solution.refresh()
        min_cost = float("inf")
        min_cost_solution = None

        for perm in permutations(range(constants.horizon_length)):
            new_solution = solution.clone()
            new_solution.sort_list(perm)
            new_solution.refresh()

            for i in range(constants.nb_customers):
                # if(passConstraints(new_solution, i)):
                # print("PASA LAS CONSTRAINTS PARA "+str(i))

                # busco el t donde es visitado i
                for time in range(constants.horizon_length):
                    aux_copy = new_solution.clone()
                    if aux_copy.routes[time].is_visited(i):
                        mip_cost = Mip1.objetive_function(aux_copy, i, time)
                        aux_copy.routes[time].remove_visit(i)
                        aux_copy.refresh()
                        if mip_cost < min_cost and aux_copy.passConstraints(i, time, "REMOVE", "MIP1"):
                            # print("PASA LAS CONSTRAINTS PARA "+str(i)+" - "+str(aux_copy))
                            min_cost = mip_cost
                            min_cost_solution = aux_copy.clone()
                            print(f"MIP1: Nueva solucion {min_cost_solution}")
                            
        return min_cost_solution if min_cost_solution is not None else solution
    
    @staticmethod
    def objetive_function(solution: Solution, removed_customer, removed_time):
        solution.refresh()
        term_1 = constants.holding_cost_supplier * sum(solution.B(t) for t in range(constants.horizon_length+1))
        
        term_2 = sum(sum(constants.holding_cost[i] * solution.customers_inventory_level[i][t] for t in range(constants.horizon_length+1))
                     for i in range(constants.nb_customers))

        # 3rd term represents the saving (in this implementation)
        aux_route = copy.deepcopy(solution.routes[removed_time])
        aux_route.remove_visit(removed_customer)
        term_3 = solution.routes[removed_time].cost - aux_route.cost
        return term_1 + term_2 - term_3
