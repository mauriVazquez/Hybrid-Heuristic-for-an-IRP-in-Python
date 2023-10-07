import random
import datetime
from constants import constants
from models.solution import Solution

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
        self.triplets = [triplet for triplet in self.triplets 
            if (solution.routes[triplet[1]].is_visited(triplet[0]) and (not solution.routes[triplet[2]].is_visited(triplet[0])))]


    def get_random_triplet(self):
        random.seed(datetime.datetime.now().microsecond)
        return self.triplets.pop(random.randint(0,len(self.triplets)-1))
    
triplet_manager = TripletManager()
