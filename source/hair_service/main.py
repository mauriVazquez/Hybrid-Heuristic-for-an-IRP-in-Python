from typing import List
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from hair.main import async_execute

app = FastAPI(
    title="HAIR Algorithm API",
    description="API para ejecutar el algoritmo HAIR basado en datos de proveedores y clientes.",
    version="1.0.0"
)

class Proveedor(BaseModel):
    id                  : str = Field(..., description="Identificador único del proveedor")
    coord_x             : float = Field(..., description="Coordenada X del proveedor")
    coord_y             : float = Field(..., description="Coordenada Y del proveedor")
    costo_almacenamiento: float = Field(..., description="Costo de almacenamiento del proveedor")
    nivel_almacenamiento: int = Field(..., description="Nivel de almacenamiento actual")
    nivel_produccion    : int = Field(..., description="Nivel de producción del proveedor")

class Cliente(BaseModel):
    id                  : str = Field(..., description="Identificador único del cliente")
    coord_x             : float = Field(..., description="Coordenada X del cliente")
    coord_y             : float = Field(..., description="Coordenada Y del cliente")
    costo_almacenamiento: float = Field(..., description="Costo de almacenamiento del cliente")
    nivel_almacenamiento: int = Field(..., description="Nivel de almacenamiento actual")
    nivel_maximo        : int = Field(..., description="Nivel máximo permitido en el inventario")
    nivel_minimo        : int = Field(..., description="Nivel mínimo permitido en el inventario")
    nivel_demanda       : int = Field(..., description="Nivel de demanda del cliente")

class Param(BaseModel):
    plantilla_id        : str = Field(default="id plantilla no encontrado", description="Identificador de la plantilla")
    user_id             : int = Field(default=0, description="ID del usuario que solicita la ejecución")
    horizonte_tiempo    : int = Field(default=None, description="Horizonte de tiempo para la ejecución")
    capacidad_vehiculo  : int = Field(default=None, description="Capacidad del vehículo en unidades")
    proveedor           : Proveedor = Field(..., description="Datos del proveedor")
    clientes            : List[Cliente] = Field(..., description="Lista de clientes asociados")

@app.post("/optimizar_recorrido", summary="Ejecutar algoritmo HAIR", description="Procesa una solicitud para ejecutar el algoritmo HAIR.")
async def procesar_solicitud(param: Param, background_tasks: BackgroundTasks):
    """
    Endpoint para procesar una solicitud de ejecución del algoritmo HAIR.
    
    - **plantilla_id**: ID de la plantilla asociada.
    - **user_id**: ID del usuario que solicita la ejecución.
    - **horizonte_tiempo**: Horizonte de tiempo (en unidades).
    - **capacidad_vehiculo**: Capacidad máxima del vehículo (en unidades).
    - **proveedor**: Información del proveedor.
    - **clientes**: Lista de clientes, con sus datos respectivos.
    """
    print(f"Se recibió la solicitud para ejecutar el algoritmo en el plantilla {param.plantilla_id}")
    try:
        background_tasks.add_task(
            async_execute, 
            param.plantilla_id, 
            param.horizonte_tiempo,
            param.capacidad_vehiculo,
            param.proveedor,
            param.clientes,
            param.user_id
        )
        return JSONResponse(
            content = {
                "message": "Solicitud de procesamiento de plantilla recibida", 
                "plantilla_id": param.plantilla_id
            }
        )
    except Exception as e:
        print(f"Error al añadir la tarea en segundo plano: {e}")
        return JSONResponse(
            content = {
                "message": "Error al procesar la solicitud", 
                "error": str(e)
            }, 
            status_code=500
        )
