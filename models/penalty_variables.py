class Alpha():

    _self = None

    # singleton
    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self) -> None:
        self.value = 1
        self.feasibles_counter = 0
        self.unfeasible_counter = 0
    
    def reset(self) -> None:
        self.value = 1
        self.feasibles_counter = 0
        self.unfeasible_counter = 0
        
    def update(self, multiplicator):
        self.value = self.value * multiplicator

    def unfeasible(self) -> None:
        self.unfeasible_counter += 1
        self.feasibles_counter = 0

        if (self.unfeasible_counter == 10):
            if self.value <= 16:
                self.update(2)
            self.unfeasible_counter = 0

    def feasible(self) ->None:
        self.feasibles_counter += 1
        self.unfeasible_counter = 0

        if (self.feasibles_counter == 10):
            if self.value >= 1/16:
                self.update(1/2)
            self.feasibles_counter = 0

    def get_value(self):
        return self.value


class Beta():

    _self = None

    # singleton
    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self) -> None:
        self.value = 1
        self.feasibles_counter = 0
        self.unfeasible_counter = 0
    
    def reset(self) -> None:
        self.value = 1
        self.feasibles_counter = 0
        self.unfeasible_counter = 0

    def update(self, multiplicator):
        self.value = self.value * multiplicator

    def unfeasible(self):
        self.unfeasible_counter += 1
        self.feasibles_counter = 0
        if (self.unfeasible_counter == 10):
            if self.value <= 16:
                self.update(2)
            self.unfeasible_counter = 0

    def feasible(self):
        self.feasibles_counter += 1
        self.unfeasible_counter = 0

        if (self.feasibles_counter == 10):
            if self.value >= 1/16:
                self.update(1/2)
            self.feasibles_counter = 0

    def get_value(self):
        return self.value


alpha = Alpha()
beta = Beta()
