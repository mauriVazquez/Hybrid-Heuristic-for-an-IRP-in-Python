from modelos.solucion import Solucion
from modelos.contexto_file import contexto_ejecucion
from modelos.ruta import Ruta

def inicializacion():
    contexto = contexto_ejecucion.get()
    # Crear rutas iniciales como una tupla de objetos Ruta (inmutables)
    solucion = Solucion(tuple(Ruta((), ()) for _ in range(contexto.horizonte_tiempo)))
    for cliente in contexto.clientes:
        for t in range(contexto.horizonte_tiempo):
            if solucion.inventario_clientes[cliente.id][t + 1] < cliente.nivel_minimo:    
                solucion = solucion.insertar_visita(cliente, t, len(solucion.rutas[t].clientes))
    print(solucion)
    return solucion
