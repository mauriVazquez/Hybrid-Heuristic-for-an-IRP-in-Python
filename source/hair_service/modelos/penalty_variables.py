from constantes import constantes

class BaseAlphaBeta:
    """
    Clase base para Alpha y Beta que maneja la lógica común.

    Atributos:
    - value: Valor asociado a la clase.
    - factibles_contador: Contador de soluciones factibles.
    - no_factibles_contador: Contador de soluciones no factibles.
    """

    def __init__(self) -> None:
        """
        Constructor de la clase BaseAlphaBeta.
        Inicializa los atributos value, factibles_contador y no_factibles_contador.
        """
        self.value = 1
        self.factibles_contador = 0
        self.no_factibles_contador = 0

    def reiniciar(self) -> None:
        """
        Reinicia los atributos value, factibles_contador y no_factibles_contador a sus valores iniciales.
        """
        self.value = 1
        self.factibles_contador = 0
        self.no_factibles_contador = 0

    def actualizar(self, multiplicator):
        """
        Actualiza el valor multiplicando por el multiplicador dado.

        Parameters:
        - multiplicator: Valor multiplicador.
        """
        self.value = self.value * multiplicator

    def no_factibles(self):
        """
        Maneja el comportamiento cuando una solución no es factible.
        """
        self.no_factibles_contador += 1
        if (self.factibles_contador + self.no_factibles_contador) == 10:
            if self.value <= constantes.penalty_factor_min:
                self.actualizar(2)
            self.factibles_contador = 0
            self.no_factibles_contador = 0

    def factible(self):
        """
        Maneja el comportamiento cuando una solución es factible.
        """
        self.factibles_contador += 1
        if (self.factibles_contador + self.no_factibles_contador) == 10:
            if self.value >= constantes.penalty_factor_min:
                self.actualizar(1/2)
            self.factibles_contador = 0
            self.no_factibles_contador = 0

    def obtener_valor(self):
        """
        Obtiene el valor actual de la instancia.

        Retorna:
        - float: Valor actual.
        """
        return self.value

class Alpha(BaseAlphaBeta):
    """
    Clase Alpha que hereda de BaseAlphaBeta.
    """
    pass

class Beta(BaseAlphaBeta):
    """
    Clase Beta que hereda de BaseAlphaBeta.
    """
    pass

alpha = Alpha()
beta = Beta()