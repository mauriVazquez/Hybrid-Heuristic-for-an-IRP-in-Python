import matplotlib.pyplot as plt
from modelos.ruta import Ruta
from modelos.entidad import Cliente
from modelos.contexto_file import contexto_ejecucion

class Solucion:
    """
    Clase que representa una solución para el problema de ruteo de inventarios.

    Contiene las rutas, niveles de inventario de clientes y proveedor, y calcula
    la factibilidad, admisibilidad y costo total de la solución.
    """

    def __init__(self, rutas=None) -> None:
        """
        Inicializa una solución con rutas y calcula sus propiedades iniciales.

        Args:
            rutas (tuple[Ruta], opcional): Conjunto de rutas que conforman la solución.
        """
        self.contexto = contexto_ejecucion.get()
        self.rutas = tuple(rutas or [Ruta((), ()) for _ in range(self.contexto.horizonte_tiempo)])
        self.inventario_clientes = {
            cliente.id: self._obtener_niveles_inventario_cliente(cliente)
            for cliente in self.contexto.clientes
        }
        self.inventario_proveedor = self._obtener_niveles_inventario_proveedor()
        self.costo = round(self._costo(), 2)
        self.es_admisible = self.es_admisible()
        self.es_factible = self.es_factible()

    def __str__(self) -> str:
        factibilidad = "F" if (self.es_factible == True) else ("A" if (self.es_admisible == True) else "N")
        rutas_str = " ".join(f"T{str(i + 1)} = {ruta}" for i, ruta in enumerate(self.rutas))
        return f"{rutas_str} Costo: {self.costo} {factibilidad}"

    def __json__(self, iteration: int, tag: str) -> dict:
        return {
            "proveedor_id": str(self.contexto.proveedor.id),
            "iteration": iteration,
            "tag": tag,
            "rutas": {i: ruta.__json__() for i, ruta in enumerate(self.rutas)},
            "costo": self.costo,
        }

    def imprimir_detalle(self) -> str:
            """
            Representación detallada en string de la solución.

            Returns:
                str: Resumen de las rutas, costo y estado de factibilidad.
            """
            costo_almacenamiento = self.contexto.proveedor.costo_almacenamiento * sum(self.inventario_proveedor) + sum(
                c.costo_almacenamiento * sum(self.inventario_clientes[c.id]) for c in self.contexto.clientes
            )
            costo_transporte = sum(ruta.costo for ruta in self.rutas)
            penalty1 = sum(
                max(0, ruta.obtener_total_entregado() - self.contexto.capacidad_vehiculo) for ruta in self.rutas
            ) * self.contexto.alfa.obtener_valor()

            penalty2 = sum(max(0, -nivel) for nivel in self.inventario_proveedor) * self.contexto.beta.obtener_valor()
            
            resp = "Clientes visitados:"        +" ".join(f"T{str(i+1)} = {ruta}    "  for i, ruta in enumerate(self.rutas)) + "\n"
            resp += 'Inventario de proveedor: ' + str(self.inventario_proveedor) + "\n"
            resp += 'Inventario de clientes: '  + str(self.inventario_clientes) + "\n"
            resp += '¿Admisible? : '            + ('SI' if self.es_admisible else 'NO') + "\n"
            resp += '¿Factible? : '             + ('SI' if self.es_factible else 'NO') + "\n"
            resp += 'Función objetivo: '        + str(self.costo) + "\n"
            resp += "Composición de costo objetivo: \n"
            resp += f"\t costo_almacenamiento = {costo_almacenamiento} \n "
            resp += f"\t costo_transporte = {costo_transporte} \n "
            resp += f"\t penalizacion1 = {penalty1} \n "
            resp += f"\t penalizacion2 = {penalty2} \n "
            print(resp)

    def clonar(self) -> 'Solucion':
        return Solucion(rutas=self.rutas)

    def es_admisible(self) -> bool:
        """
        Verifica si la solución es admisible (sin desabastecimiento ni sobreabastecimiento en clientes).

        Returns:
            bool: True si la solución es admisible, False en caso contrario.
        """
        cliente_sin_desabastecimiento = all(
            self.inventario_clientes[cliente.id][t] >= cliente.nivel_minimo
            for cliente in self.contexto.clientes
            for t in range(self.contexto.horizonte_tiempo + 1)
        )

        cliente_sin_sobreabastecimiento = all(
            self.inventario_clientes[cliente.id][t] <= cliente.nivel_maximo
            for cliente in self.contexto.clientes
            for t in range(self.contexto.horizonte_tiempo + 1)
        )
        return cliente_sin_desabastecimiento and cliente_sin_sobreabastecimiento

    def es_factible(self) -> bool:
        """
        Verifica si una solución es factible: Para ello, la solución es admisible, no tiene desabastecimiento en el proveedor
        y no se excede la capacidad del vehículo.

        Returns:
            bool: True si la solución cumple todas las restricciones, False en caso contrario.
        """
        return self.es_admisible and self.proveedor_sin_desabastecimiento() and self.respeta_capacidad_vehiculo()

    def es_igual(self, solucion2: "Solucion") -> bool:
        """
        Verifica si esta solución es igual a otra.

        Args:
            solucion2 (Solucion): La solución a comparar.

        Returns:
            bool: True si las soluciones son iguales, False en caso contrario.
        """
        return (
            solucion2 is not None
            and all(r1.es_igual(r2) for r1, r2 in zip(self.rutas, solucion2.rutas))
            and self.costo == solucion2.costo
        )

    def proveedor_sin_desabastecimiento(self) -> bool:
        """
        Verifica si el proveedor tiene desabastecimiento.

        Returns:
            bool: True si el proveedor tiene inventario por debajo de 0.
        """
        return all(nivel >= 0 for nivel in self.inventario_proveedor)

    def respeta_capacidad_vehiculo(self) -> bool:
        """
        Verifica si la cantidad entregada en alguna ruta excede la capacidad del vehículo.

        Returns:
            bool: True si la capacidad del vehículo no se excede, False en caso contrario.
        """
        return all(self.contexto.capacidad_vehiculo >= ruta.obtener_total_entregado() for ruta in self.rutas)


    def insertar_visita(self, cliente: Cliente, tiempo: int, cantidad :int = None) -> 'Solucion':
        """
        Inserta una visita a un cliente en un tiempo dado y devuelve una nueva instancia de Solución.

        Args:
            cliente (Cliente): Cliente a insertar.
            tiempo (int): Tiempo en el que se realiza la visita.
        """
        rutas_modificadas = list(self.rutas)
        nueva_ruta = rutas_modificadas[tiempo].insertar_visita(cliente, (cantidad or cliente.nivel_maximo))
        rutas_modificadas[tiempo] = nueva_ruta
        return Solucion(rutas=tuple(rutas_modificadas))

    def eliminar_visita(self, cliente: Cliente, tiempo: int) -> 'Solucion':
        """
        Elimina la visita de un cliente en un tiempo dado y devuelve una nueva instancia de Solución.

        Args:
            cliente (Cliente): Cliente a remover.
            tiempo (int): Tiempo en el que se remueve la visita.
        """
        rutas_modificadas = list(self.rutas)
        nueva_ruta = rutas_modificadas[tiempo].eliminar_visita(cliente)
        rutas_modificadas[tiempo] = nueva_ruta
        return Solucion(rutas=tuple(rutas_modificadas))

    def quitar_cantidad_cliente(self, cliente: Cliente, tiempo: int, cantidad: int) -> 'Solucion':
        """
        Reduce la cantidad entregada a un cliente en una visita específica dentro de la ruta.
        
        Args:
            cliente (Cliente): Cliente al que se le reducirá la cantidad entregada.
            tiempo (int): Tiempo en el que ocurre la visita.
            cantidad (int): Cantidad a reducir.
        
        Returns:
            Solucion: Nueva instancia de Solución con la cantidad ajustada.
        """
        rutas_modificadas = list(self.rutas)
        nueva_ruta = rutas_modificadas[tiempo].quitar_cantidad_cliente(cliente, cantidad)
        rutas_modificadas[tiempo] = nueva_ruta
        
        return Solucion(rutas=tuple(rutas_modificadas))

    def agregar_cantidad_cliente(self, cliente: Cliente, tiempo: int, cantidad: int) -> 'Solucion':
        """
        Reduce la cantidad entregada a un cliente en una visita específica dentro de la ruta.
        
        Args:
            cliente (Cliente): Cliente al que se le reducirá la cantidad entregada.
            tiempo (int): Tiempo en el que ocurre la visita.
            cantidad (int): Cantidad a reducir.
        
        Returns:
            Solucion: Nueva instancia de Solución con la cantidad ajustada.
        """
        rutas_modificadas = list(self.rutas)
        nueva_ruta = rutas_modificadas[tiempo].agregar_cantidad_cliente(cliente, cantidad)
        rutas_modificadas[tiempo] = nueva_ruta
        
        return Solucion(rutas=tuple(rutas_modificadas))

    def establecer_cantidad_cliente(self, cliente: Cliente, tiempo: int, cantidad: int) -> 'Solucion':
        """
        Establece la cantidad exacta a entregar a un cliente en una visita específica dentro de la ruta.
        
        Args:
            cliente (Cliente): Cliente al que se le establecerá la cantidad entregada.
            tiempo (int): Tiempo en el que ocurre la visita.
            cantidad (int): Cantidad exacta a establecer.
        
        Returns:
            Solucion: Nueva instancia de Solución con la cantidad establecida.
        """
        rutas_modificadas = list(self.rutas)
        nueva_ruta = rutas_modificadas[tiempo].establecer_cantidad_cliente(cliente, cantidad)
        rutas_modificadas[tiempo] = nueva_ruta
        
        return Solucion(rutas=tuple(rutas_modificadas))

    def merge_rutas(self, indice_ruta_principal: int, indice_ruta_secundaria: int) -> 'Solucion':
        """
        Combina dos rutas en una, manteniendo las visitas únicas y sumando correctamente las cantidades entregadas.

        Args:
            indice_ruta_principal (int): Índice de la ruta base.
            indice_ruta_secundaria (int): Índice de la ruta secundaria.

        Returns:
            Solucion: Nueva instancia con las rutas fusionadas.
        """
        # Obtener las rutas a fusionar
        ruta_base = self.rutas[indice_ruta_principal]
        ruta_secundaria = self.rutas[indice_ruta_secundaria]

        # Diccionario para fusionar clientes y cantidades entregadas
        cantidad_entregada_fusionada = {c: cantidad for c, cantidad in zip(ruta_base.clientes, ruta_base.cantidades)}

        for cliente, cantidad in zip(ruta_secundaria.clientes, ruta_secundaria.cantidades):
            if cliente in cantidad_entregada_fusionada:
                cantidad_entregada_fusionada[cliente] += cantidad  # 🔹 Sumar entrega si el cliente ya estaba
            else:
                cantidad_entregada_fusionada[cliente] = cantidad  # 🔹 Agregar nuevo cliente

        # Construir la nueva ruta sin duplicados
        clientes_fusionados = tuple(cantidad_entregada_fusionada.keys())
        cantidades_fusionadas = tuple(cantidad_entregada_fusionada.values())

        # Crear una nueva lista de rutas con la ruta fusionada
        rutas_modificadas = list(self.rutas)
        rutas_modificadas[indice_ruta_principal] = Ruta(clientes_fusionados, cantidades_fusionadas)
        rutas_modificadas[indice_ruta_secundaria] = Ruta((), ())  # 🔹 Ruta vacía en el índice fusionado

        return Solucion(rutas=tuple(rutas_modificadas))

    def tiempos_cliente(self, cliente: Cliente):
        return [t for t in range(self.contexto.horizonte_tiempo) if self.rutas[t].es_visitado(cliente)]

    def _obtener_niveles_inventario_cliente(self, cliente: Cliente):
        inventario = [cliente.nivel_almacenamiento]  # Nivel inicial
        for ruta in self.rutas:
            inventario.append(inventario[-1] + ruta.obtener_cantidad_entregada(cliente) - cliente.nivel_demanda)
        return inventario
    
    def _obtener_niveles_inventario_proveedor(self):
        proveedor = self.contexto.proveedor
        inventario = [proveedor.nivel_almacenamiento]  # Nivel inicial
        for ruta in self.rutas:
            inventario.append(inventario[-1] + proveedor.nivel_produccion - ruta.obtener_total_entregado())
        return inventario


    def _costo(self) -> float:
        costo_almacenamiento = self.contexto.proveedor.costo_almacenamiento * sum(self.inventario_proveedor) + sum(
            c.costo_almacenamiento * sum(self.inventario_clientes[c.id]) for c in self.contexto.clientes
        )
        
        costo_transporte = sum(ruta.costo for ruta in self.rutas)
        
        exceso_vehiculo = sum( max(0, ruta.obtener_total_entregado() - self.contexto.capacidad_vehiculo) for ruta in self.rutas) 

        desabastecimiento_proveedor = sum(max(0, -nivel) for nivel in self.inventario_proveedor) 

        return (costo_almacenamiento 
            + costo_transporte 
            + (exceso_vehiculo * self.contexto.alfa.obtener_valor())
            + (desabastecimiento_proveedor * self.contexto.beta.obtener_valor())
        )
        
    def calcular_ahorro_remocion(self, cliente, tiempo):
        """
        Calculate the transportation savings if a customer is removed from a route.
        """
        ruta = self.rutas[tiempo]
        if cliente not in ruta.clientes:
            return 0  # No savings if the client is not in the route

        idx = ruta.clientes.index(cliente)
        prev = ruta.clientes[idx - 1] if idx > 0 else None
        next = ruta.clientes[idx + 1] if idx < len(ruta.clientes) - 1 else None
        if prev is None or next is None:
            return 0  # No savings if removing an isolated customer

        matriz_distancia = self.contexto.matriz_distancia
        original_cost = matriz_distancia[prev.id][cliente.id] + matriz_distancia[cliente.id][next.id]
        new_cost = matriz_distancia[prev.id][next.id]
        
        # Savings from removing customer
        return original_cost - new_cost

    def calcular_costo_insercion(self, cliente, tiempo):
        """
        Calculate the cheapest cost increase if a customer is inserted into a route.
        """
        ruta = self.rutas[tiempo]
        if cliente in ruta.clientes:
            return float("inf")  # Can't insert if already in the route

        best_cost = float("inf")
        best_idx = -1

        matriz_distancia = self.contexto.matriz_distancia
        
        for idx in range(len(ruta.clientes) + 1):
            prev = ruta.clientes[idx - 1] if idx > 0 else None
            next = ruta.clientes[idx] if idx < len(ruta.clientes) else None

            if prev is None or next is None:
                continue  # Skip cases where there's no valid insertion

            # Compute insertion cost
            insertion_cost = matriz_distancia[prev.id][cliente.id] + matriz_distancia[cliente.id][next.id] - matriz_distancia[prev.id][next.id]

            if insertion_cost < best_cost:
                best_cost = insertion_cost
                best_idx = idx

        return best_cost if best_idx != -1 else float("inf")

    def reasignar_ruta(self, ruta, nuevo_tiempo):
        """
        Reassigns a route to a new time period while keeping its structure unchanged.
        """
        nueva_solucion = self.clonar()

        rutas_modificadas = list(nueva_solucion.rutas)

        tiempo_actual = None
        for t, r in enumerate(rutas_modificadas):
            if r.clientes == ruta.clientes and r.cantidades == ruta.cantidades:
                tiempo_actual = t
                break
        
        if tiempo_actual is None or tiempo_actual == nuevo_tiempo:
            return nueva_solucion  # No reassignment needed

        rutas_modificadas[tiempo_actual] = Ruta((), ())  # Empty route in old position

        rutas_modificadas[nuevo_tiempo] = ruta

        nueva_solucion.rutas = tuple(rutas_modificadas)

        return nueva_solucion


    def graficar_rutas(self):
        contexto = self.contexto
        proveedor = contexto.proveedor

        # Generar coordenadas de las rutas con IDs de clientes
        rutas_coords = [
            (
                [proveedor.coord_x] + [cliente.coord_x for cliente in ruta.clientes] + [proveedor.coord_x],
                [proveedor.coord_y] + [cliente.coord_y for cliente in ruta.clientes] + [proveedor.coord_y],
                [None] + [cliente.id for cliente in ruta.clientes] + [None]  # IDs de los clientes
            )
            for ruta in self.rutas
        ]

        # Crear subplots dinámicos según cantidad de rutas
        fig, axes = plt.subplots(len(rutas_coords), figsize=(12, 8))

        # Asegurar que `axes` sea siempre iterable
        if len(rutas_coords) == 1:
            axes = [axes]

        # Dibujar cada ruta
        for i, (ax, coords) in enumerate(zip(axes, rutas_coords)):  
            x, y, ids = coords  # Extraer coordenadas y IDs

            # Dibujar líneas de la ruta
            ax.plot(x, y, linestyle='-', color='blue')

            # Dibujar IDs en lugar de los puntos
            for cx, cy, cid in zip(x[1:-1], y[1:-1], ids[1:-1]):  # Evita el proveedor
                ax.text(cx, cy, str(cid), fontsize=12, color='blue', ha='center', va='center', fontweight='bold')

            # Resaltar el proveedor con marcador rojo
            ax.text(proveedor.coord_x, proveedor.coord_y, "0", fontsize=12, color='red', ha='right', va='bottom', fontweight='bold')

            ax.set_title(f"Ruta {i+1}")

        plt.tight_layout()
        plt.show()
