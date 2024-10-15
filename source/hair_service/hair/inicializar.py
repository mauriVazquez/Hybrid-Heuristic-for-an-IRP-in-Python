from modelos.solucion import Solucion
from constantes import constantes
from random import randint
from typing import Type

def inicializar() -> Type["Solucion"]:
    """
    En el proceso de inicialización cada cliente es considerado secuencialmente.
    Los tiempos de entrega se establecen lo más tarde posible antes de que ocurra una situación de desabastecimiento. 
    Tal solución es obviamente admisible, pero no necesariamente factible.
    """
    # Obtener una solución vacía inicial
    solucion = Solucion.obtener_empty_solucion()
    for cliente in constantes.clientes:
        stock = cliente.nivel_almacenamiento
        for t in range(constantes.horizon_length):
            stock -= cliente.nivel_demanda
            if(stock < cliente.nivel_minimo):
                #  Calcular la máxima cantidad posible de entregar sin sobrepasar la capacidad máxima
                max_entrega = cliente.nivel_maximo - stock
                # Insertar visita en el tiempo actual, entregando una cantidad dependiente a la política de reabastecimiento
                cantidad_entregada = max_entrega if (constantes.politica_reabastecimiento == "OU") else randint(cliente.nivel_demanda, max_entrega)
                solucion.rutas[t].insertar_visita(cliente, cantidad_entregada, len(solucion.rutas[t].clientes))
                solucion.refrescar()
                stock += cantidad_entregada
    solucion.refrescar()
    print(f"Inicial: {solucion}")
    return solucion

