import json
class SolucionesAlmacenadas:
    _soluciones = []

    @staticmethod
    def obtener_soluciones():
        return SolucionesAlmacenadas._soluciones
    
    #SETS
    @staticmethod
    def agregar_solucion(solucion):
        # if id not in SolucionesAlmacenadas.solucion:
            # SolucionesAlmacenadas.solucion.append(Solucion(id, coord_x, coord_y, nivel_inicial, costo_almacenamiento, max_nivel, min_nivel, nivel_demanda, proovedor_x, proovedor_y))
        SolucionesAlmacenadas._soluciones.append(solucion)