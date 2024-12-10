import math

#Distancia entre dos puntos
def compute_dist(xi, xj, yi, yj):
    return math.sqrt(math.pow(xi - xj, 2) + math.pow(yi - yj, 2))

class Ruta():
    @staticmethod
    def obtener_costo_recorrido(clientes) -> float:
        #Distancia del primer cliente al proveedor + distancia del último al proveedor, mas distancia entre clientes
        return 0.0 if not clientes else (
            clientes[0].distancia_proveedor
            + sum(compute_dist(c1.coord_x, c0.coord_x, c1.coord_y, c0.coord_y) for c0, c1 in zip(clientes, clientes[1:]))
            + clientes[-1].distancia_proveedor 
        )
    
    def __init__(self, clientes, cantidades) -> None:
        self.clientes = clientes if clientes else []  # Lista de clientes en la ruta
        self.cantidades = cantidades if cantidades else []  # Cantidades entregadas a cada cliente
    
    def __str__(self) -> str:
        return f"[{[cliente.id for cliente in self.clientes]},{self.cantidades}]"
    
    def to_json(self) -> None: 
        return {"clientes":list({str(c.id) for c in self.clientes}),"cantidades":list({c for c in self.cantidades}),"costo":self.obtener_costo()}
    
    def clonar(self):
        return Ruta([clientes for clientes in self.clientes],[cantidades for cantidades in self.cantidades])
    
    def obtener_costo(self):
        return self.obtener_costo_recorrido(self.clientes)
    
    def obtener_total_entregado(self) -> int:
        return sum(self.cantidades)
    
    def obtener_cantidad_entregada(self, cliente) -> int:
        return next((self.cantidades[i] for i, it_cliente in enumerate(self.clientes) if (it_cliente == cliente)), 0)
    
    def es_visitado(self, cliente) -> bool:
        return cliente in self.clientes
    
    def insertar_visita(self, cliente, cantidad, indice):
        if indice is None:
            indice = min( 
                range(len(self.clientes) + 1), 
                key=lambda pos: self.obtener_costo_recorrido(self.clientes[:pos] + [cliente] + self.clientes[pos:])
            )
        self.clientes.insert(indice, cliente)
        self.cantidades.insert(indice, cantidad)

    def remover_visita(self, cliente) -> int:
        indice = next((i for i, c in enumerate(self.clientes) if c.id == cliente.id), None)
        if indice is not None:
            cantidad_removida = self.cantidades.pop(indice)
            self.clientes.pop(indice)
            return cantidad_removida
        return 0
    
    def agregar_cantidad_cliente(self, cliente, cantidad):
        for i, c in enumerate(self.clientes):
            if c == cliente:
                self.cantidades[i] += cantidad
                break
    
    def quitar_cantidad_cliente(self, cliente, cantidad): 
        self.cantidades[self.clientes.index(cliente)] -= cantidad
    
    def es_igual(self, ruta2):
        return  (self.clientes == ruta2.clientes) and (self.cantidades == ruta2.cantidades)