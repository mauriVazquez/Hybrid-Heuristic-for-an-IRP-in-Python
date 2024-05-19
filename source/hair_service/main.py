import requests
from typing import List
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from hair_main import async_execute
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

class Proveedor(BaseModel):
    id: str
    coord_x: float
    coord_y: float
    costo_almacenamiento: float
    nivel_almacenamiento: int
    nivel_produccion: int

class Cliente(BaseModel):
    id: str
    coord_x: float
    coord_y: float
    costo_almacenamiento: float
    nivel_almacenamiento: int
    nivel_maximo: int
    nivel_minimo: int
    nivel_demanda: int

class Param(BaseModel):
    recorrido_id: str = Field(default="id recorrido no encontrado")
    horizon_length: int = Field(default=None)
    capacidad_vehiculo: int = Field(default=None)
    proveedor: Proveedor = Field(default=None)
    clientes: List[Cliente] = Field(default=None)

@app.post("/solicitud-ejecucion")
async def procesar_solicitud(param: Param, background_tasks: BackgroundTasks):
    print(f"Se recibió la solicitud para ejecutar el algoritmo en el recorrido {param.recorrido_id}")
    try:
        background_tasks.add_task(async_execute, param.recorrido_id, param.horizon_length,
                                  param.capacidad_vehiculo, param.proveedor, param.clientes)
        return JSONResponse(content={"message": "Solicitud de procesamiento de recorrido recibida", "recorrido_id": param.recorrido_id})
    except Exception as e:
        print(f"Error al añadir la tarea en segundo plano: {e}")
        return JSONResponse(content={"message": "Error al procesar la solicitud", "error": str(e)}, status_code=500)

    