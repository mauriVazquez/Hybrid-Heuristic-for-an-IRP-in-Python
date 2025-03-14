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
                # solucion = solucion.insertar_visita(cliente, t - 1, len(solucion.rutas[t - 1].clientes))
                rutas_modificadas = list(solucion.rutas)
                cantidad = cliente.nivel_maximo - solucion.inventario_clientes[cliente.id][t - 1]
                if solucion.contexto.politica_reabastecimiento == "ML":
                    cantidad = min(cantidad,
                        contexto.capacidad_vehiculo - solucion.rutas[t-1].obtener_total_entregado(),
                        solucion.inventario_proveedor[t - 1]
                    )
                    if cantidad <= 0:
                        cantidad = max(cantidad, cliente.nivel_demanda)
                rutas_modificadas[t - 1] = rutas_modificadas[t -1].insertar_visita(cliente, cantidad, len(solucion.rutas[t -1].clientes))             
                solucion = Solucion(tuple(r for r in rutas_modificadas))
    print(f"Inicio {solucion}")
    return solucion
