import matplotlib.pyplot as plt
from modelos.ruta import Ruta
from modelos.entidad import Cliente
from modelos.contexto_file import contexto_ejecucion
from random import randint

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
        self.costo = self._costo()
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
            resp = "Clientes visitados:"        +" ".join(f"T{str(i+1)} = {ruta}    "  for i, ruta in enumerate(self.rutas)) + "\n"
            resp += 'Inventario de proveedor: ' + str(self.inventario_proveedor) + "\n"
            resp += 'Inventario de clientes: '  + str(self.inventario_clientes) + "\n"
            resp += '¿Admisible? : '            + ('SI' if self.es_admisible else 'NO') + "\n"
            resp += '¿Factible? : '             + ('SI' if self.es_factible else 'NO') + "\n"
            resp += 'Función objetivo: '        + str(self.costo) + "\n"
            resp += 'Cumple política: '         +str(self.cumple_politica())
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

    def _insertar_visita(self, cliente: Cliente, tiempo: int, index = None) -> 'Solucion':            
        if self.contexto.politica_reabastecimiento == "OU":
            cantidad = cliente.nivel_maximo - self.inventario_clientes[cliente.id][tiempo]
        
        if self.contexto.politica_reabastecimiento == "ML":
            cantidad = min(
                cliente.nivel_maximo - self.inventario_clientes[cliente.id][tiempo],
                self.inventario_proveedor[tiempo],
                self.contexto.capacidad_vehiculo - self.rutas[tiempo].obtener_total_entregado()
            )     
            if cantidad <= 0:
                cantidad = cliente.nivel_demanda
            
        rutas_modificadas = list(ruta for ruta in self.rutas)
        rutas_modificadas[tiempo] = rutas_modificadas[tiempo].insertar_visita(cliente, cantidad, index)
        return Solucion(rutas=tuple(rutas_modificadas))

    def _eliminar_visita(self, cliente: Cliente, tiempo: int) -> 'Solucion':
        rutas_modificadas = list(ruta for ruta in self.rutas)
        rutas_modificadas[tiempo] = rutas_modificadas[tiempo].eliminar_visita(cliente)
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
        rutas_modificadas = list(ruta for ruta in self.rutas)
        rutas_modificadas[tiempo] = rutas_modificadas[tiempo].quitar_cantidad_cliente(cliente, cantidad)
        
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
        rutas_modificadas = list(ruta for ruta in self.rutas)
        rutas_modificadas[tiempo]= rutas_modificadas[tiempo].agregar_cantidad_cliente(cliente, cantidad)
        
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
        rutas_modificadas = list(ruta for ruta in self.rutas)
        rutas_modificadas[tiempo] = rutas_modificadas[tiempo].establecer_cantidad_cliente(cliente, cantidad)
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
        clientes = list(self.rutas[indice_ruta_principal].clientes)
        for c in self.rutas[indice_ruta_secundaria].clientes:
            if c not in clientes:
                clientes.append(c)
        
        nueva_solucion = []
        for index, r in enumerate(self.rutas):
            if (index not in [indice_ruta_principal, indice_ruta_secundaria]):
                nueva_solucion.append(r.clonar())
            else:
                nueva_solucion.append(Ruta(tuple(), tuple()))        
        nueva_solucion = Solucion(rutas=tuple(r for r in nueva_solucion))
        
        for c in clientes:
            nueva_solucion = nueva_solucion.insertar_visita(c, indice_ruta_principal)

        return nueva_solucion

    def tiempos_cliente(self, cliente: Cliente):
        return [t for t in range(self.contexto.horizonte_tiempo) if self.rutas[t].es_visitado(cliente)]

    def insertar_visita(self, cliente, t, indice = None):
        """
        Inserta una visita siguiendo estrictamente las políticas OU y ML según el paper.
        
        Teoría:
        1. Primero agregar el cliente a la ruta usando el método de inserción más barato
        2. Luego establecer la cantidad según la política:
        - OU: Ui - nivel_actual, y reducir la misma cantidad de la siguiente visita
        - ML: min(Ui - nivel_actual, capacidad_vehiculo, stock_proveedor), o rit si es 0
                (puede violar restricciones de capacidad pero mantiene solución admisible)
        """    
        nueva_solucion = self._insertar_visita(cliente, t, indice)
        if nueva_solucion.contexto.politica_reabastecimiento == "OU":     
            # Buscar siguiente visita y reducir la misma cantidad
            t_next = next((t_futuro for t_futuro in nueva_solucion.tiempos_cliente(cliente) if t_futuro > t), None)
            if t_next is not None:
                nueva_solucion = nueva_solucion.quitar_cantidad_cliente(cliente, t_next, nueva_solucion.rutas[t].obtener_cantidad_entregada(cliente.id))
                if nueva_solucion.rutas[t_next].obtener_cantidad_entregada(cliente) <= 0:
                    nueva_solucion = nueva_solucion._eliminar_visita(cliente, t_next)
        return nueva_solucion


    def eliminar_visita(self, cliente, t):
        """
        Elimina una visita siguiendo estrictamente las políticas OU y ML según el paper.
        
        Teoría:
        1. Primero eliminar el cliente de la ruta y enlazar predecesor con sucesor
        2. Luego según la política:
        - OU: Transferir cantidad a siguiente visita, solo si no causa stockout
        - ML: Si no hay stockout, eliminar. Si hay, intentar compensar con visita anterior
        """    
        # Obtener cantidad antes de eliminar
        tiempos_cliente = self.tiempos_cliente(cliente)
        cantidad_eliminada = self.rutas[t].obtener_cantidad_entregada(cliente)
        nueva_solucion = self._eliminar_visita(cliente, t)
        
        if nueva_solucion.contexto.politica_reabastecimiento == "OU":    
            # Transferir cantidad a siguiente visita        
            t_next = next((t_futuro for t_futuro in tiempos_cliente if t_futuro > t), None)
            if t_next is not None:
                nueva_solucion = nueva_solucion.agregar_cantidad_cliente(cliente, t_next, cantidad_eliminada)
            return nueva_solucion if nueva_solucion.es_admisible else self.clonar()
        
        elif nueva_solucion.contexto.politica_reabastecimiento == "ML":
            if min(nueva_solucion.inventario_clientes[cliente.id]) >= cliente.nivel_minimo:
                return nueva_solucion.clonar()
            
            t_prev = next((t_pasado for t_pasado in reversed(tiempos_cliente) if t_pasado < t), None)
            
            if t_prev is not None:
                y = min(nueva_solucion.inventario_clientes[cliente.id][t+1:])
            
                if y < cantidad_eliminada:
                    nueva_solucion = nueva_solucion.agregar_cantidad_cliente(cliente, t_prev, cantidad_eliminada - y)
                    if max(nueva_solucion.inventario_clientes[cliente.id]) <= cliente.nivel_maximo:
                        return nueva_solucion.clonar()
            return self.clonar()
    
    def _obtener_niveles_inventario_cliente(self, cliente: Cliente):
        inventario = [cliente.nivel_almacenamiento]   
        for t in range(1, self.contexto.horizonte_tiempo + 1):
            inventario.append(inventario[-1] + self.rutas[t - 1].obtener_cantidad_entregada(cliente) - cliente.nivel_demanda)
        return inventario
    
    def _obtener_niveles_inventario_proveedor(self):
        proveedor = self.contexto.proveedor
        inventario = [proveedor.nivel_almacenamiento]
        for t in range(1, self.contexto.horizonte_tiempo + 1):
            inventario.append(inventario[-1] + proveedor.nivel_produccion - self.rutas[t - 1].obtener_total_entregado())
        return inventario


    def cumple_politica(self) -> bool:
        for r in self.rutas:
            for r2 in self.rutas:
                if r != r2:
                    if r.clientes == r2.clientes and r.cantidades == r2.cantidades:
                        return False
                    
        # if self.contexto.politica_reabastecimiento == "OU":
        #     for cliente in self.contexto.clientes:
        #         for t in self.tiempos_cliente(cliente):
        #             if self.inventario_clientes[cliente.id][t] != cliente.nivel_maximo:
        #                 return False
                    
        # if self.contexto.politica_reabastecimiento == "ML":
        #     for cliente in self.contexto.clientes:
        #         for t in self.tiempos_cliente(cliente):
        #             if self.inventario_clientes[cliente.id][t] > cliente.nivel_maximo or self.rutas[t].obtener_cantidad_entregada(cliente) <= 0:
        #                 return False
        return True
        
        
    def _costo(self) -> float:
        costo_almacenamiento = self.contexto.proveedor.costo_almacenamiento * sum(self.inventario_proveedor) + sum(
            c.costo_almacenamiento * sum(self.inventario_clientes[c.id]) for c in self.contexto.clientes
        )
        costo_transporte = sum(ruta.costo for ruta in self.rutas)
        
        exceso_vehiculo = sum(
            max(0, ruta.obtener_total_entregado() - self.contexto.capacidad_vehiculo) 
            for ruta in self.rutas
        )
        
        desabastecimiento_proveedor = sum(max(0, -nivel) for nivel in self.inventario_proveedor)

        return round(
            costo_almacenamiento + costo_transporte + 
            (exceso_vehiculo * self.contexto.alfa.obtener_valor()) +
            (desabastecimiento_proveedor * self.contexto.beta.obtener_valor())
        , 2)

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
