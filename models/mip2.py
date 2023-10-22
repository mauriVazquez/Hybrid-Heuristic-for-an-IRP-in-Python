from constants import constants
from models.solution import Solution
import copy


class Mip2():
    @staticmethod
    def execute(solution: Solution) -> Solution:
        solution.refresh()
        min_cost = constants.float_inf
        min_cost_solution = solution.clone()

        for i in range(constants.nb_customers):
            for time in range(constants.horizon_length):
                solution_aux = solution.clone()

                if solution.routes[time].is_visited(i):
                    mip_cost = Mip2.objetive_function(solution_aux, i, time, "REMOVE")
                    solution_aux.remove_visit(i,time)
                    if mip_cost < min_cost and solution_aux.passConstraints("MIP2", i, time, "REMOVE"):
                        min_cost = mip_cost
                        min_cost_solution = solution_aux.clone()
                else:
                    mip_cost = Mip2.objetive_function(solution_aux, i, time, "INSERT")
                    solution_aux.insert_visit(i, time)
                    if mip_cost < min_cost and solution_aux.passConstraints("MIP2", i, time, "INSERT"):
                        min_cost = mip_cost
                        min_cost_solution = solution_aux.clone()
                        print(f"MIP2: Nueva solucion {min_cost_solution}")

        return min_cost_solution

    @staticmethod
    def objetive_function(solution, customer, time, operation):
        solution.refresh()
        if not any(len(route.clients) > 0 for route in solution.routes):
            return constants.float_inf
        
        term_1 = sum([constants.holding_cost_supplier * solution.supplier_inventory_level[t]
                      for t in range(constants.horizon_length+1)])

        term_2 = sum([sum([constants.holding_cost[i] * solution.customers_inventory_level[i][t]
                    for t in range(constants.horizon_length)])
                    for i in range(constants.nb_customers)])

        if operation != "REMOVE":
            term_3 = 0
        else:
            aux_route = copy.deepcopy(solution.routes[time])
            aux_route.remove_visit(customer)
            term_3 = solution.routes[time].cost - aux_route.cost
            

        if operation != "INSERT":
            term_4 = 0
        else:
            solution_aux = solution.clone()
            solution_aux.insert_visit(customer, time)
            term_4 = solution_aux.routes[time].cost - solution.routes[time].cost

        return term_1 + term_2 - term_3 + term_4
