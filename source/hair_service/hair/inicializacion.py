from modelos.ruta import Ruta
from modelos.contexto_file import contexto_ejecucion
from modelos.solucion import Solucion

def inicializacion():
    """
    Inicializa una solución inicial para el problema de ruteo de inventarios.

    Este procedimiento genera una solución inicial donde se determina la cantidad de productos
    entregados a cada cliente en diferentes períodos de tiempo, respetando los niveles de
    inventario mínimos y máximos de cada cliente.

    Flujo del algoritmo:
    1. Se valida que los datos de entrada sean válidos.
    2. Se crea una solución inicial con rutas vacías.
    3. Se iteran los clientes y períodos de tiempo para asignar entregas necesarias.
    4. Se calcula la factibilidad y el costo de la solución final.

    Returns:
        Solucion: Un objeto que representa la solución inicial del problema.

    Raises:
        ValueError: Si no hay clientes o si el horizonte de tiempo es inválido.
    """
    # Obtener las contexto y datos del problema
    contexto = contexto_ejecucion.get()
    horizonte_tiempo = contexto.horizonte_tiempo
    clientes = contexto.clientes

    # Valido datos que podrían romper el flujo
    if not clientes:
        raise ValueError("No se ingresaron clientes")
    elif horizonte_tiempo <= 0:
        raise ValueError("El horizonte de tiempo no es válido")

    # Crear una solución inicial vacía
    solucion = Solucion([Ruta([], []) for _ in range(horizonte_tiempo)])
    
    # Iterar sobre cada cliente
    for cliente in clientes:
        inventario_actual = cliente.nivel_almacenamiento
        for t in range(horizonte_tiempo):
            # Reducir inventario por demanda
            inventario_actual -= cliente.nivel_demanda
            
            # Si el inventario cae por debajo del nivel mínimo
            if inventario_actual < cliente.nivel_minimo:
                # Calcular la cantidad a entregar
                cantidad_a_entregar = cliente.nivel_maximo - inventario_actual

                if cantidad_a_entregar > 0:
                    # Agregar entrega a la ruta correspondiente
                    solucion.rutas[t].insertar_visita(cliente, cantidad_a_entregar)
                    # Actualizar inventario
                    inventario_actual += cantidad_a_entregar
    
    # Refrescar atributos de la solución (costo, factibilidad, etc.)
    solucion.refrescar()
    if contexto.debug == True:
        print(f"Inicial: {solucion}")
    return solucion
