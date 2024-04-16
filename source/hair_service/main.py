from typing import Annotated

from fastapi import FastAPI, Request, Form, Body
from pydantic import BaseModel, Field

import json

app = FastAPI()


@app.get("/")
def read_root():
    print('LLegó solicitud')
    return {"Hello": "World"}


class Proveedor(BaseModel):
    data: list
    # coord_x: float = Field(default="No encontrado")
    # coord_y: float = Field(default="No encontrado")
    # costo_almacenamiento: float = Field(default="No encontrado")
    # nivel_almacenamiento: int = Field(default="No encontrado")
    # nivel_produccion: int = Field(default="No encontrado")


@app.post("/solicitud-ejecucion")
async def procesar_solicitud(horizon_length: int = Form(), proveedor: str = Form(), vehiculo: str = Form(), clientes: str = Form()):    
    proveedorJson = json.loads(proveedor),
    vehiculoJson = json.loads(vehiculo),
    clientesJson = json.loads(clientes),
    
    
    
    return {"Hello": "hellooo"}
