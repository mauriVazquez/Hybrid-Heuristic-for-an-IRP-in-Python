import matplotlib.pyplot as plt
from modelos.ruta import Ruta
from modelos.entidad import Cliente
from hair.contexto import constantes_contexto

class Solucion:
    """
    Clase que representa una solución para el problema de ruteo de inventarios.

    Contiene las rutas, niveles de inventario de clientes y proveedor, y calcula
    la factibilidad, admisibilidad y costo total de la solución.
    """

    def __init__(self, rutas: list = None) -> None:
        """
        Inicializa una solución con rutas y calcula sus propiedades iniciales.

        Args:
            rutas (list[Ruta], opcional): Conjunto de rutas que conforman la solución. En caso de no incluirse se generan H rutas vacías.
        """
        self.constantes = constantes_contexto.get()
        self.rutas = rutas or [Ruta([], []) for _ in range(self.constantes.horizonte_tiempo)]
        self.refrescar()
        
    def __str__(self) -> str:
        """
        Representación en string de la solución.

        Returns:
            str: Resumen de las rutas, costo y estado de factibilidad.
        """
        factibilidad = "F" if self.es_factible else ("A" if self.es_admisible else "N")
        rutas_str    = " ".join(f"T{str(i + 1)} = {ruta}" for i, ruta in enumerate(self.rutas))
        return f"{rutas_str} Costo: {self.costo} {factibilidad}"
    
    def __json__(self, iteration: int, tag: str) -> dict:
        """
        Convierte la solución a formato JSON.

        Args:
            iteration (int): Iteración actual.
            tag (str): Etiqueta asociada a la solución.

        Returns:
            dict: Representación en JSON de la solución.
        """
        return {
            "proveedor_id"  : str(self.constantes.proveedor.id),
            "iteration"     : iteration,
            "tag"           : tag,
            "rutas"         : {i: ruta.__json__() for i, ruta in enumerate(self.rutas)},
            "costo"         : self.costo,
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
        print(resp)
        
    def refrescar(self) -> None:
        """
        Actualiza las propiedades de la solución.
        """
        self.inventario_clientes = {
            cliente.id: self._niveles_inventario_cliente(cliente)
                for cliente in self.constantes.clientes
        }
        self.inventario_proveedor   = self._obtener_niveles_inventario_proveedor()
        self.es_factible            = self._es_factible()
        self.es_admisible           = self._es_admisible()
        self.costo                  = self._costo()

    def clonar(self) -> 'Solucion':
        """
        Crea una copia profunda de la solución.

        Returns:
            Solucion: Una copia de la solución actual.
        """
        return Solucion([ruta.clonar() for ruta in self.rutas])

    def _es_admisible(self) -> bool:
        """
        Verifica si la solución es admisible (sin desabastecimiento ni sobreabastecimiento en clientes).

        Returns:
            bool: True si la solución es admisible, False en caso contrario.
        """
        return not (self._cliente_tiene_desabastecimiento() or self._cliente_tiene_sobreabastecimiento())

    def _es_factible(self) -> bool:
        """
        Verifica si una solución es factible: Para ello, la solución es admisible, no tiene desabastecimiento en el proveedor y no es excedida la capacidad del vehículo.

        Returns:
            bool: True si la solución cumple todas las restricciones, False en caso contrario.
        """
        return self._es_admisible and not (self.proveedor_tiene_desabastecimiento() or self.es_excedida_capacidad_vehiculo())
        
    def es_igual(self, solucion2 : "Solucion") -> bool:
        """
        Verifica si esta solución es igual a otra.

        Args:
            solucion2 (Solucion): La solución a comparar.

        Returns:
            bool: True si las soluciones son iguales, False en caso contrario.
        """
        return (solucion2 is not None) and all(r1.es_igual(r2) for r1, r2 in zip(self.rutas, solucion2.rutas))

    def proveedor_tiene_desabastecimiento(self) -> bool:
        """
        Verifica si el proveedor tiene desabastecimiento.

        Returns:
            bool: True si el proveedor tiene inventario por debajo de 0.
        """
        return any(nivel < 0 for nivel in self.inventario_proveedor)

    def _cliente_tiene_desabastecimiento(self) -> bool:
        """
        Verifica si algún cliente tiene desabastecimiento.

        Returns:
            bool: True si algún cliente tiene inventario por debajo de su nivel mínimo en algún instante de tiempo.
        """
        return any(
            self.inventario_clientes[cliente.id][t] < cliente.nivel_minimo
            for cliente in self.constantes.clientes
            for t in range(self.constantes.horizonte_tiempo)
        )

    def _cliente_tiene_sobreabastecimiento(self) -> bool:
        """
        Verifica si algún cliente tiene sobreabastecimiento.

        Returns:
            bool: True si algún cliente tiene inventario por encima de su nivel máximo.
        """
        return any(
            self.inventario_clientes[cliente.id][t] > cliente.nivel_maximo
            for cliente in self.constantes.clientes
            for t in range(self.constantes.horizonte_tiempo)
        )

    def es_excedida_capacidad_vehiculo(self) -> bool:
        """
        Verifica si la cantidad entregada en alguna ruta excede la capacidad del vehículo.

        Returns:
            bool: True si alguna ruta excede la capacidad, False en caso contrario.
        """
        return any(self.constantes.capacidad_vehiculo < ruta.obtener_total_entregado() for ruta in self.rutas)
    
    def insertar_visita(self, cliente : Cliente, tiempo: int) -> None:
        """
        Inserta una visita a un cliente en un tiempo dado y refresca la solución.

        Args:
            cliente (Cliente): Cliente a insertar.
            tiempo (int): Tiempo en el que se realiza la visita.
        """
        cantidad_maxima = cliente.nivel_maximo - self.inventario_clientes[cliente.id][tiempo]
        if cantidad_maxima > 0:
            self.rutas[tiempo].insertar_visita(cliente, cantidad_maxima, None)
            self.refrescar()
        
    def eliminar_visita(self, cliente : Cliente, tiempo : int) -> None:
        """
        Elimina la visita de un cliente en un tiempo dado y refresca la solución.

        Args:
            cliente (Cliente): Cliente a remover.
            tiempo (int): Tiempo en el que se remueve la visita.
        """
        if self.rutas[tiempo].es_visitado(cliente):
            self.rutas[tiempo].eliminar_visita(cliente)
            self.refrescar()

    def merge_rutas(self, rutabase_indice: int, rutasecondary_indice: int) -> None:
        """
        Combina dos rutas en una, manteniendo las visitas únicas.

        Args:
            rutabase_indice (int): Índice de la ruta base.
            rutasecondary_indice (int): Índice de la ruta secundaria.
        """
        ruta_base = self.rutas[rutabase_indice]
        ruta_secundaria = self.rutas[rutasecondary_indice]

        for cliente in ruta_secundaria.clientes:
            if cliente not in ruta_base.clientes:
                ruta_base.insertar_visita(cliente, ruta_secundaria.obtener_cantidad_entregada(cliente), None)

        self.rutas[rutasecondary_indice] = Ruta([], [])
        self.refrescar()

    def tiempos_cliente(self, cliente : Cliente):
        """
        Retorna el conjunto de tiempos donde un cliente es visitado.

        Args:
            cliente (Cliente): Cliente a consultar.

        Returns:
            list[int]: Lista de índices de tiempo donde el cliente es visitado.
        """
        return [t for t in range(self.constantes.horizonte_tiempo) if self.rutas[t].es_visitado(cliente)]


    def _obtener_niveles_inventario_proveedor(self) -> list[float]:
        """
        Calcula los niveles de inventario del proveedor en cada periodo.

        Returns:
            list[float]: Lista con los niveles de inventario del proveedor en cada tiempo.

        Raises:
            AttributeError: Si las constantes, las rutas o el proveedor no están definidas.
        """
        proveedor = self.constantes.proveedor
        inventario = [proveedor.nivel_almacenamiento]
        inventario.extend( inventario[-1] + proveedor.nivel_produccion - self.rutas[t - 1].obtener_total_entregado()
            for t in range(1, self.constantes.horizonte_tiempo + 1)
        )
        return inventario

    def _niveles_inventario_cliente(self, cliente : Cliente):
        """
        Calcula los niveles de inventario del cliente en cada periodo. Consideraciones:
        - I(i,t) es el nivel de inventario del cliente, siendo una variable entra no negativa definida como:
        - I(i,0) es el nivel de inventario inicial
        - I(i,t) = I(i, t-1) + x(i,t-1) - r(i,t-1) para t perteneciente a [1, H+1]

        Args:
            cliente (Cliente): Cliente para calcular su inventario.

        Returns:
            list[float]: Lista con los niveles de inventario del cliente en cada tiempo.
        """
        inventario = [cliente.nivel_almacenamiento]
        inventario.extend( inventario[-1] + self.rutas[t - 1].obtener_cantidad_entregada(cliente) - cliente.nivel_demanda
            for t in range(1, self.constantes.horizonte_tiempo + 1)
        )
        return inventario

    def _costo(self) -> float:
        """
        Calcula el costo total de la solución.

        Returns:
            float: Costo total de la solución.
        """
        constantes = self.constantes
        
        costo_almacenamiento = sum(nivel * constantes.proveedor.costo_almacenamiento for nivel in self.inventario_proveedor)
        costo_almacenamiento += sum(c.costo_almacenamiento * sum(self.inventario_clientes[c.id]) for c in constantes.clientes)

        costo_transporte = sum([ruta.costo for ruta in self.rutas])
        
        penalty1 = sum(
            max(0, ruta.obtener_total_entregado() - constantes.capacidad_vehiculo) for ruta in self.rutas
        ) * constantes.alfa.obtener_valor()

        penalty2 = sum(max(0, -nivel) for nivel in self.inventario_proveedor) * constantes.beta.obtener_valor()

        return costo_almacenamiento + costo_transporte + penalty1 + penalty2

            
    def graficar_rutas(self):
        """
        Grafica las rutas de clientes en función del horizonte de tiempo.

        Cada ruta muestra el recorrido desde y hacia el proveedor.
        """
        constantes = self.constantes
        proveedor = constantes.proveedor
        rutas = self.rutas
        num_rutas = len(rutas)

        # Extraer coordenadas de las rutas
        rutas_coords = [
            (
                [proveedor.coord_x] + [cliente.coord_x for cliente in ruta.clientes] + [proveedor.coord_x],
                [proveedor.coord_y] + [cliente.coord_y for cliente in ruta.clientes] + [proveedor.coord_y]
            )
            for ruta in rutas
        ]

        # Determinar el número de filas y columnas para los subplots
        rows = (num_rutas + 1) // 2
        cols = 2 if num_rutas > 1 else 1

        # Crear la figura y subplots
        fig, axes = plt.subplots(rows, cols, figsize=(12, 8))
        axes = axes.flatten() if num_rutas > 1 else [axes]

        # Graficar cada ruta en su subplot correspondiente
        for i, (ax, (x, y)) in enumerate(zip(axes, rutas_coords)):
            ax.plot(x, y, marker='o', linestyle='-', color='b', label=f"Ruta {i+1}")
            ax.set_title(f"Ruta {i+1}")
            ax.set_xlabel("Coordenada X")
            ax.set_ylabel("Coordenada Y")
            ax.legend()
            ax.grid(True)

        # Ocultar subplots vacíos si hay más subplots que rutas
        for ax in axes[len(rutas_coords):]:
            ax.axis('off')

        # Ajustar diseño y mostrar gráficos
        plt.tight_layout()
        plt.show()