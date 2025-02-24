import math
from modelos.solucion import Solucion
from modelos.contexto_file import contexto_ejecucion
from modelos.ruta import Ruta

def inicializacion():
    contexto = contexto_ejecucion.get()

    # Crear rutas iniciales como una lista de objetos Ruta (modificables)
    solucion = Solucion([Ruta([], []) for _ in range(contexto.horizonte_tiempo)])

    for cliente in contexto.clientes:
        for t in range(1, contexto.horizonte_tiempo + 1):
            inventario_anterior = solucion.inventario_clientes[cliente.id][t - 1] if t > 0 else 0
            cantidad_necesaria = cliente.nivel_maximo - inventario_anterior
            
            if cantidad_necesaria > 0 and solucion.inventario_clientes[cliente.id][t] <= cliente.nivel_minimo:
                
                if contexto.politica_reabastecimiento == "OU":
                    # Asegurar entrega óptima y ajuste de futuras entregas
                    cantidad_entregada = min(cantidad_necesaria, solucion.inventario_proveedor[t-1])
                    solucion = solucion.insertar_visita(cliente, t - 1, cantidad_entregada)
                
                elif contexto.politica_reabastecimiento == "ML":
                    # Verificar capacidad del vehículo y proveedor
                    capacidad_restante = max(0, contexto.capacidad_vehiculo - solucion.rutas[t - 1].obtener_total_entregado())
                    cantidad_entregada = min(cantidad_necesaria, capacidad_restante, solucion.inventario_proveedor[t-1])
                    solucion = solucion.insertar_visita(cliente, t - 1, cantidad_entregada)

    print(f"✅ Inicio {solucion}")
    return solucion
