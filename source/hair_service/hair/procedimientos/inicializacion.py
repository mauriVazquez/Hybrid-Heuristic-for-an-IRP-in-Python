from hair.contexto import constantes_contexto
from modelos.solucion import Solucion
from random import randint
# ALTERNATIVA 1
# def inicializacion() -> Solucion:
#     """
#     Inicializa una solución donde cada cliente es considerado secuencialmente.
    
#     Los tiempos de entrega se establecen lo más tarde posible antes de que ocurra una situación de desabastecimiento. 
#     La solución obtenida es admisible pero no necesariamente factible, ya que depende de la política de reabastecimiento.
    
#     Returns:
#         Solucion: Un objeto Solucion con las rutas iniciales y cantidades asignadas.
#     """
#     # Obtener una solución vacía inicial
#     solucion = Solucion.obtener_empty_solucion()
#     for cliente in constantes.clientes:
#         for t in range(constantes.horizonte_tiempo):
#             nivel_inventario = solucion.inventario_clientes.get(cliente.id)[t]
#             if nivel_inventario <= cliente.nivel_minimo:
#                 #  Calcular la máxima cantidad posible de entregar sin sobrepasar la capacidad máxima
#                 max_entrega = cliente.nivel_maximo - nivel_inventario
#                 # Insertar visita en el tiempo actual, entregando una cantidad dependiente a la política de reabastecimiento
#                 cantidad_entregada = max_entrega if (constantes.politica_reabastecimiento == "OU") else randint(cliente.nivel_demanda, max_entrega)
#                 solucion.rutas[t].insertar_visita(cliente, cantidad_entregada, None)
#                 solucion.refrescar()
#     print(f"Inicial: {solucion}")
#     return solucion


# ALTERNATIVA 2
def inicializacion() -> Solucion:
    """
    Inicializa una solución donde cada cliente es considerado secuencialmente.
    
    Los tiempos de entrega se establecen lo más tarde posible antes de que ocurra una situación de desabastecimiento. 
    La solución obtenida es admisible pero no necesariamente factible, ya que depende de la política de reabastecimiento.
    
    Returns:
        Solucion: Un objeto Solucion con las rutas iniciales y cantidades asignadas.
    """
    # Obtener una solución vacía inicial
    solucion = Solucion.obtener_empty_solucion()
    constantes = constantes_contexto.get()
    for cliente in constantes.clientes:
        for t in range(constantes.horizonte_tiempo - 1, -1, -1):
            nivel_inventario = solucion.inventario_clientes.get(cliente.id, [0] * constantes.horizonte_tiempo)[t]

            if nivel_inventario <= cliente.nivel_minimo:
                # Calcular la cantidad máxima que se puede entregar sin exceder la capacidad máxima del cliente
                max_entrega = cliente.nivel_maximo - nivel_inventario

                # Asegurarse de que max_entrega es positivo
                if max_entrega > 0:
                    # Determinar la cantidad a entregar según la política de reabastecimiento
                    if constantes.politica_reabastecimiento == "OU":
                        cantidad_entregada = max_entrega
                    else:  # Política ML
                        cantidad_entregada = randint(cliente.nivel_demanda, max_entrega)

                    # Insertar visita en la ruta actual permitiendo sobrecarga del vehículo
                    solucion.rutas[t].insertar_visita(cliente, cantidad_entregada, None)

    # Refrescar la solución una vez después de todas las entregas
    solucion.refrescar()

    print(f"Inicial: {solucion}")
    return solucion
