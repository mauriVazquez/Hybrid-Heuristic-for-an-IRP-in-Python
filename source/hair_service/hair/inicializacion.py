from modelos.solucion import Solucion
from modelos.contexto_file import contexto_ejecucion
from modelos.ruta import Ruta

def inicializacion() -> Solucion:
    """
    Genera una solución inicial que cumple las siguientes condiciones:
    - Cada cliente de 1 a n es considerado secuencialmente.
    - Se realizan entregas progresivas para cubrir la demanda acumulada en cada período.
    - La solución es admisible pero no necesariamente factible.

    Returns:
        Solucion: Solución inicial generada.
    """
    # Obtener el contexto y datos del problema
    contexto = contexto_ejecucion.get()

    # Validar datos que podrían romper el flujo
    if not contexto.clientes:
        raise ValueError("No se ingresaron clientes.")
    if contexto.horizonte_tiempo <= 0:
        raise ValueError("El horizonte de tiempo no es válido.")

    # Crear una solución inicial vacía
    solucion = Solucion([Ruta([], []) for _ in range(contexto.horizonte_tiempo)])

    # Iterar sobre cada cliente
    for cliente in contexto.clientes:
        if cliente.nivel_minimo >= cliente.nivel_maximo:
            raise ValueError(f"El cliente {cliente.id} tiene un nivel mínimo mayor o igual al máximo.")

        inventario_actual = cliente.nivel_almacenamiento

        for t in range(contexto.horizonte_tiempo):
            # Reducir inventario por demanda
            inventario_actual -= cliente.nivel_demanda

            # Verificar si se requiere una entrega para evitar desabastecimiento
            if inventario_actual < 0:
                cantidad_a_entregar = cliente.nivel_maximo - inventario_actual
                solucion.rutas[t].insertar_visita(cliente, cantidad_a_entregar)
                inventario_actual += cantidad_a_entregar

    # Refrescar atributos de la solución
    solucion.refrescar()

    if contexto.debug:
        print(f"Inicial: {solucion}")

    return solucion