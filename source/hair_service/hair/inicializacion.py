from modelos.solucion import Solucion
from modelos.contexto_file import contexto_ejecucion
from modelos.ruta import Ruta

def inicializacion():
    contexto = contexto_ejecucion.get()
    # Crear rutas iniciales como una tupla de objetos Ruta (inmutables)
    solucion = Solucion(tuple(Ruta((), ()) for _ in range(contexto.horizonte_tiempo)))
    for cliente in contexto.clientes:
        for t in range(1, contexto.horizonte_tiempo + 1):
            if solucion.inventario_clientes[cliente.id][t] < cliente.nivel_minimo:                   
                solucion = solucion.insertar_visita(cliente, t - 1, len(solucion.rutas[t - 1].clientes))
    print(f"Inicio {solucion}")
    # if not (solucion.cumple_politica() and solucion.es_admisible):
    #     solucion.imprimir_detalle()
    #     print("DEFASAJE EN INICIALIACION")
    #     exit(0)
    return solucion
