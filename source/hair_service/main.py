from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, Field
from hair_main import hair_execute

import json

app = FastAPI()


@app.get("/")
def read_root():
    print('LLegó solicitud')
    return {"Hello": "World"}


class Proveedor(BaseModel):
    id : str
    coord_x : float
    coord_y : float
    costo_almacenamiento : float
    nivel_almacenamiento : int
    nivel_produccion : int

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
    horizon_length: int = Field( default=None)
    capacidad_vehiculo: int = Field( default=None)
    proveedor: Proveedor = Field(default = None)
    clientes : List[Cliente] = Field(default = None)


@app.post("/solicitud-ejecucion")
async def procesar_solicitud(param : Param):
    response = hair_execute(param.horizon_length, param.capacidad_vehiculo, param.proveedor, param.clientes)
    return response
