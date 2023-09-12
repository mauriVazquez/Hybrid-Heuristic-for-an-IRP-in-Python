from constants import constants
from models.solution import Solution
from random import randint

class TripletManager():
    _self = None

    # singleton
    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self) -> None:
        self.triplets = [[client, time, time_prima] 
            for client in range(constants.nb_customers)
                for time in range(constants.horizon_length)
                    for time_prima in range(constants.horizon_length)
                        if time != time_prima]

    def reset(self):
        self.__init__()
        
    def remove_triplets_from_solution(self, solution: Solution):
        print("Cantidad Anterior"+str(len(self.triplets)))
        self.triplets = [triplet for triplet in self.triplets 
            if (solution.routes[triplet[1]].is_visited(triplet[0]) and (not solution.routes[triplet[2]].is_visited(triplet[0])))]
        print("Cantidad Posterior"+str(len(self.triplets)))

    def get_random_triplet(self):
        return self.triplets.pop(randint(0,len(self.triplets)-1))
    
triplet_manager = TripletManager()
