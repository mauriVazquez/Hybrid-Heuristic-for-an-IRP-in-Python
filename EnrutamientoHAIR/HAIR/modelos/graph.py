import matplotlib.pyplot as plt
from io import BytesIO
import base64

class Graph():
    def draw_rutas(proveedor_coords, clientes_coords):
        colors = ['red','green','blue','purple','orange','yellow','cyan','magenta','pink','brown','black','gray','darkgray']
        for tiempo in clientes_coords:
            x = [proveedor_coords[1][0]]
            y = [proveedor_coords[1][1]]
            for cliente in tiempo:
                print(cliente)
                x.append(cliente[1][0])
                y.append(cliente[1][1])
            x.append(proveedor_coords[1][0])
            y.append(proveedor_coords[1][1])
        return [x,y]

        