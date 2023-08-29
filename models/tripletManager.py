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
        self.triplets = self.initialize_triplets()
        pass

    def initialize_triplets(self):

        triplets = []

        for client in range(constants.nb_customers):
            for time in range(constants.horizon_lenght):
                for time_prima in range(constants.horizon_lenght):
                    if time != time_prima:
                        triplets.append([client, time, time_prima])

        return triplets

    def remove_triplets_from_solution(self, solution: Solution):

        # for index, triplet in enumerate(self.triplets):
        #     if not solution.routes[triplet[2]].is_visited(triplet[0]) or not solution.routes[triplet[1]].is_visited(triplet[0]) :
        #         self.triplets.pop(self.triplets.index(triplet))
        for triplet in self.triplets:
            if (not solution.routes[triplet[1]].is_visited(triplet[0])) or solution.routes[triplet[2]].is_visited(triplet[0]):
                self.triplets.pop(self.triplets.index(triplet))

            # if ( ( not solution.routes[triplet[2]].is_visited(triplet[0])) and (not solution.routes[triplet[1]].is_visited(triplet[0]))):
            #     self.triplets.pop(self.triplets.index(triplet))

triplet_manager = TripletManager()
