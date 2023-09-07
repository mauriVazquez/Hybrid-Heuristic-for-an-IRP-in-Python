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
        lambda_ttl = 0.5
        L = 10
        return L + random.randint(0, math.floor(lambda_ttl * math.sqrt(constants.nb_customers*constants.horizon_lenght))-1)
    
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
        for index, element in enumerate(self.list_a):
            if self.list_a[index][1] == main_iterator:
                self.list_a.pop(index)

        for index, element in enumerate(self.list_r):
            if self.list_r[index][1] == main_iterator:
                self.list_r.pop(index)
tabulists = TabuLists()