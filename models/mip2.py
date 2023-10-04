from itertools import permutations
from constants import constants
from models.solution import Solution
import copy


class Mip2():
    @staticmethod
    def execute(solution: Solution) -> Solution:
        # print("ENTRA AL MIP"+str(solution))
        min_cost = float("inf")
        min_cost_solution = solution

        for i in range(constants.nb_customers):
            for time in range(constants.horizon_length):
                solution_aux = solution.clone()

                if solution.routes[time].is_visited(i):
                    mip_cost = Mip2.objetive_function(solution_aux, i, None, time)
                    solution_aux.remove_visit(i, time)
                    solution_aux.refresh()
                    if mip_cost < min_cost and solution_aux.passConstraints(i, time, "REMOVE", "MIP2"):
                        # print("PASA LAS CONSTRAINTS PARA "+str(i)+" - "+str(solution_aux))
                        min_cost = mip_cost
                        min_cost_solution = solution_aux.clone()
                else:
                    mip_cost = Mip2.objetive_function(solution_aux, None, i, time)
                    solution_aux.insert_visit(i, time)
                    solution_aux.refresh()
                    if mip_cost < min_cost and solution_aux.passConstraints(i, time, "INSERT", "MIP2"):
                        min_cost = mip_cost
                        min_cost_solution = solution_aux.clone()
                        print(f"MIP2: Nueva solucion {min_cost_solution}")

        
        return min_cost_solution

    @staticmethod
    def objetive_function(solution, removed_customer, added_customer, time):
        term_1 = sum([constants.holding_cost_supplier * solution.supplier_inventory_level[t]
                      for t in range(constants.horizon_length+1)])

        term_2 = sum([sum([constants.holding_cost[i] * solution.customers_inventory_level[i][t]
                           for t in range(constants.horizon_length)])
                      for i in range(constants.nb_customers)])

        if removed_customer != None:
            customer_index = solution.routes[time].clients.index(
                removed_customer)
            aux_route = copy.deepcopy(solution.routes[time])
            aux_route.remove_visit(removed_customer)
            term_3 = solution.routes[time].cost - aux_route.cost
        else:
            term_3 = 0

        if added_customer != None:
            solution_aux = solution.clone()
            solution_aux.insert_visit(added_customer, time)
            solution_aux.refresh()
            term_4 = sum([solution_aux.routes[it].cost -
                          solution.routes[it].cost for it in range(constants.horizon_length)])
        else:
            term_4 = 0

        return term_1 + term_2 - term_3 + term_4
