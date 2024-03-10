import json
class SolucionesAlmacenadas:
    _soluciones = []

    @staticmethod
    def obtener_soluciones():
        return SolucionesAlmacenadas._soluciones
    
    #SETS
    @staticmethod
    def agregar_solucion(solucion):
        SolucionesAlmacenadas._soluciones.append(solucion)
    
    @staticmethod
    def borrar_todas_soluciones():
        SolucionesAlmacenadas._soluciones = []