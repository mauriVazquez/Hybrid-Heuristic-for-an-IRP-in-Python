import math
import random
from constants import constants

class TabuLists():
    _self = None

    # singleton
    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self) -> None:
        self.list_r = []
        self.list_a = []

    def get_ttl(self):
        lambda_ttl = constants.lambda_ttl
        L = constants.taboo_len
        return L + random.randint(0, math.floor(lambda_ttl * math.sqrt(constants.nb_customers*constants.horizon_length)))
    
    def forbidden_to_append(self, i, t):
        return any(elemento[0] == [i, t] for elemento in self.list_a)

    def forbidden_to_remove(self, i, t):
        return any(elemento[0] == [i, t] for elemento in self.list_r)
    
    def add_forbiddens(self, ts, tsprima, c, main_iterator):
        for t in ts:
            if (not (t in tsprima)) and (not self.forbidden_to_append(c, t)):
                self.list_a.append([[c, t], main_iterator + self.get_ttl()])

        for t in tsprima:
            if (not (t in ts)) and (not self.forbidden_to_remove(c, t)):
                self.list_r.append([[c, t], main_iterator + self.get_ttl()])

   
    
    def update_lists(self, main_iterator) -> None:
        def remove_condition(element):
            return element[1] > main_iterator
        self.list_a = list(filter(remove_condition, self.list_a))
        self.list_r = list(filter(remove_condition, self.list_r))
        
tabulists = TabuLists()