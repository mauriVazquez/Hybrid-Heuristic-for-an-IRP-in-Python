from typing import Annotated

from fastapi import FastAPI, Request, Form, Body
from pydantic import BaseModel, Field

app = FastAPI()


@app.get("/")
def read_root():
    print('LLegó solicitud')
    return {"Hello": "World"}


class Proveedor(BaseModel):
    id: str = Field(alias='proveedor.id', default="No encontrado")
    # coord_x: float = Field(default="No encontrado")
    # coord_y: float = Field(default="No encontrado")
    # costo_almacenamiento: float = Field(default="No encontrado")
    # nivel_almacenamiento: int = Field(default="No encontrado")
    # nivel_produccion: int = Field(default="No encontrado")


@app.post("/solicitud-ejecucion")
async def procesar_solicitud(horizon_length: int = Form(), proveedor: Proveedor = Form()):
    print(horizon_length)
    print(proveedor)
    return {"Hello": "hellooo"}
