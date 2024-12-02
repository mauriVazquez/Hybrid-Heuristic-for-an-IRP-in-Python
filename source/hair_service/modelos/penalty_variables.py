from hair.constantes import constantes

class FactorPenalizacion:
    """
    Clase base para Alpha y Beta que maneja la lógica común.

    Atributos:
    - value: Valor asociado a la clase.
    - factibles_contador: Contador de soluciones factibles.
    - no_factibles_contador: Contador de soluciones no factibles.
    """

    def __init__(self) -> None:
        """
        Constructor de la clase FactorPenalizacion.
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
        
    @staticmethod
    def actualizar_metricas_factibilidad(solucion):
        """
        Actualiza las métricas de factibilidad basadas en las restricciones de capacidad de los vehículos y 
        la disponibilidad de stock en los proveedores.

        Si la solución excede la capacidad del vehículo, se marcará como no factible en el componente `alpha`.
        Si hay desabastecimiento en los proveedores, se marcará como no factible en el componente `beta`.

        Args:
            solucion (Solucion): La solución que se evalúa para determinar su factibilidad.
            
        Efectos:
            - Actualiza las métricas `alpha` y `beta` dependiendo de si la solución es factible o no con respecto
            a la capacidad del vehículo y la disponibilidad de stock en los proveedores.
        """
        if solucion.es_excedida_capacidad_vehiculo():
            alpha.no_factibles()
        else:
            alpha.factible()

        if solucion.proveedor_tiene_desabastecimiento():
            beta.no_factibles()
        else:
            beta.factible()

    def no_factibles(self):
        """
        Maneja el comportamiento cuando una solución no es factible.
        """
        self.factibles_contador += 1
        self.no_factibles_contador += 1
        if (self.factibles_contador + self.no_factibles_contador) == 10:
            if self.value <= constantes.penalty_factor_min:
                self.value = self.value * 2
            self.factibles_contador = 0
            self.no_factibles_contador = 0

    def factible(self):
        """
        Maneja el comportamiento cuando una solución es factible.
        """
        self.no_factibles_contador += 0
        self.factibles_contador += 1
        if (self.factibles_contador + self.no_factibles_contador) == 10:
            if self.value >= constantes.penalty_factor_min:
                self.value = self.value * 0.5
            self.factibles_contador = 0
            self.no_factibles_contador = 0

    def obtener_valor(self):
        """
        Obtiene el valor actual de la instancia.

        Retorna:
        - float: Valor actual.
        """
        return self.value

class Alpha(FactorPenalizacion):
    """
    Clase Alpha que hereda de FactorPenalizacion.
    """
    pass

class Beta(FactorPenalizacion):
    """
    Clase Beta que hereda de FactorPenalizacion.
    """
    pass

alpha = Alpha()
beta = Beta()