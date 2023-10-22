from itertools import permutations
from constants import constants
from models.solution import Solution
import copy


class Mip1():
    @staticmethod
    def execute(solution: Solution):
        min_cost = float("inf")
        min_cost_solution = solution.clone()
        
        for perm in permutations(range(constants.horizon_length)):
            new_solution = solution.clone()
            new_solution.sort_list(perm)

            #Se toma la solución permutada SIN eliminación como posible alternativa
            mip_cost = Mip1.objetive_function(new_solution)
            if mip_cost < min_cost and new_solution.passConstraints("3c"):
                min_cost = mip_cost
                min_cost_solution = new_solution.clone()
            
            for i in range(constants.nb_customers):
                # busco el t donde es visitado i
                for time in range(constants.horizon_length):
                    aux_copy = new_solution.clone()
                    if aux_copy.routes[time].is_visited(i):
                        mip_cost = Mip1.objetive_function(aux_copy, i, time)
                        aux_copy.remove_visit(i,time)
                        aux_copy.refresh()
                        if mip_cost < min_cost and aux_copy.passConstraints("MIP1", i, time, "REMOVE"):
                            min_cost = mip_cost
                            min_cost_solution = aux_copy.clone()                            
        min_cost_solution.refresh()  
        print(f"SALIDA MIP1 {min_cost_solution}")    
        return min_cost_solution
    
    @staticmethod
    def objetive_function(solution: Solution, removed_customer = None, removed_time = None):
        solution.refresh()
        
        term_1 = constants.holding_cost_supplier * sum(solution.B(t) for t in range(constants.horizon_length+1))
        
        term_2 = sum(sum(constants.holding_cost[i] * solution.customers_inventory_level[i][t] 
                        for t in range(constants.horizon_length+1))
                        for i in range(constants.nb_customers))

        if removed_customer is None:
             term_3 = 0
        else:
            # 3rd term represents the saving (in this implementation)
            aux_route = copy.deepcopy(solution.routes[removed_time])
            aux_route.remove_visit(removed_customer)
            term_3 = solution.routes[removed_time].cost - aux_route.cost
           
        return term_1 + term_2 - term_3 if any(len(route.clients) > 0 for route in solution.routes) else float_info.max 
