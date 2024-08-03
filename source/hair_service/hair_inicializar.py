from modelos.solucion import Solucion
from constantes import constantes
from modelos.ruta import Ruta
from random import randint
from typing import Type

def inicializar():
    """
    En el proceso de inicialización cada cliente es considerado secuencialmente.
    Los tiempos de entrega se establecen lo más tarde posible antes de que ocurra una situación de desabastecimiento. 
    Tal solución es obviamente admisible, pero no necesariamente factible.
    """
    # Obtener una solución vacía inicial
    solucion = _obtener_empty_solucion()
    # Iterar sobre cada cliente
    for cliente in constantes.clientes:
        stock_cliente = cliente.nivel_almacenamiento
        # Iterar sobre cada periodo en el horizonte de planificación
        for t in range(constantes.horizon_length + 1):
            stock_cliente -= cliente.nivel_demanda
            if stock_cliente < cliente.nivel_minimo:
                # Calcular la máxima cantidad posible de entregar sin sobrepasar la capacidad máxima
                max_entrega = cliente.nivel_maximo - solucion.obtener_niveles_inventario_cliente(cliente)[t-1]
                # Insertar visita en el tiempo anterior, entregando una cantidad dependiente a la política de reabastecimiento
                cantidad_entregada = max_entrega if constantes.politica_reabastecimiento == "OU" else randint(cliente.nivel_demanda, max_entrega)
                solucion.rutas[t-1].insertar_visita(cliente, cantidad_entregada, len(solucion.rutas[t-1].clientes))
                # Actualizar el stock del cliente después de la entrega
                stock_cliente += cantidad_entregada
    # Imprimir el detalle de la solución
    return solucion

def _obtener_empty_solucion() -> Type["Solucion"]:
    return Solucion([Ruta(ruta[0], ruta[1]) for ruta in [[[], []] for _ in range(constantes.horizon_length)]])
