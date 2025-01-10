import matplotlib.pyplot as plt
import numpy as np
from modelos.ruta import Ruta
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
            rutas (list[Ruta], opcional): Lista de rutas iniciales. Si no se proporciona,
                se crea una lista vacía para cada periodo del horizonte de tiempo.
        """
        self.constantes = constantes_contexto.get()
        self.rutas = rutas or [Ruta([], []) for _ in range(self.constantes.horizonte_tiempo)]
        self.refrescar()
    
    def refrescar(self):
        """
        Actualiza los niveles de inventario, factibilidad, admisibilidad y costo de la solución.
        """
        self.inventario_clientes = {
            cliente.id: self._obtener_niveles_inventario_cliente(cliente)
            for cliente in self.constantes.clientes
        }
        self.inventario_proveedor = self._obtener_niveles_inventario_proveedor()
        self.es_factible = self._es_factible()
        self.es_admisible = self._es_admisible()
        self.costo = self._costo()
        
    def __str__(self) -> str:
        """
        Representación en cadena de la solución.

        Returns:
            str: Resumen de las rutas, costo y estado de factibilidad.
        """
        factibilidad = "F" if self.es_factible else ("A" if self.es_admisible else "N")
        rutas_str = " ".join(f"T{str(i + 1)} = {ruta}" for i, ruta in enumerate(self.rutas))
        return f"{rutas_str}    Costo: {self.costo} {factibilidad}"

    def imprimir_detalle(self) -> str:
        resp = "Clientes visitados:"        +" ".join(f"T{str(i+1)} = {ruta}    "  for i, ruta in enumerate(self.rutas)) + "\n"
        resp += 'Inventario de proveedor: ' + str(self.inventario_proveedor) + "\n"
        resp += 'Inventario de clientes: '  + str(self.inventario_clientes) + "\n"
        resp += '¿Admisible? : '            + ('SI' if self.es_admisible else 'NO') + "\n"
        resp += '¿Factible? : '             + ('SI' if self.es_factible else 'NO') + "\n"
        resp += 'Función objetivo: '        + str(self.costo) + "\n"
        print(resp)

    def to_json(self, iteration: int, tag: str) -> dict:
        """
        Convierte la solución a formato JSON.

        Args:
            iteration (int): Iteración actual.
            tag (str): Etiqueta asociada a la solución.

        Returns:
            dict: Representación en JSON de la solución.
        """
        return {
            "proveedor_id": str(self.constantes.proveedor.id),
            "iteration": iteration,
            "tag": tag,
            "rutas": {i: ruta.to_json() for i, ruta in enumerate(self.rutas)},
            "costo": self.costo,
        }

    def clonar(self) -> 'Solucion':
        """
        Crea una copia profunda de la solución.

        Returns:
            Solucion: Una copia de la solución actual.
        """
        return Solucion([ruta.clonar() for ruta in self.rutas])

    def es_igual(self, solution2) -> bool:
        """
        Verifica si esta solución es igual a otra.

        Args:
            solution2 (Solucion): La solución a comparar.

        Returns:
            bool: True si las soluciones son iguales, False en caso contrario.
        """
        return solution2 is not None and all(r1.es_igual(r2) for r1, r2 in zip(self.rutas, solution2.rutas))

    def es_visitado(self, cliente, t) -> bool:
        """
        Verifica si un cliente específico es visitado en un tiempo dado.

        Args:
            cliente (Cliente): Cliente a verificar.
            t (int): Índice del tiempo.

        Returns:
            bool: True si el cliente es visitado, False en caso contrario.
        """
        if not (0 <= t < len(self.rutas)):
            raise IndexError(f"Índice t={t} fuera de rango.")
        return cliente in self.rutas[t].clientes

    def insertar_visita(self, cliente, tiempo) -> None:
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
        
    def remover_visita(self, cliente, tiempo) -> None:
        """
        Elimina la visita de un cliente en un tiempo dado y refresca la solución.

        Args:
            cliente (Cliente): Cliente a remover.
            tiempo (int): Tiempo en el que se remueve la visita.
        """
        if self.es_visitado(cliente, tiempo):
            self.rutas[tiempo].remover_visita(cliente)
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

    def tiempos_cliente(self, cliente):
        """
        Retorna el conjunto de tiempos donde un cliente es visitado.

        Args:
            cliente (Cliente): Cliente a consultar.

        Returns:
            list[int]: Lista de índices de tiempo donde el cliente es visitado.
        """
        return [t for t in range(self.constantes.horizonte_tiempo) if self.es_visitado(cliente, t)]

    def proveedor_tiene_desabastecimiento(self) -> bool:
        """
        Verifica si el proveedor tiene desabastecimiento.

        Returns:
            bool: True si el proveedor tiene inventario por debajo de 0.
        """
        return any(nivel < 0 for nivel in self.inventario_proveedor)

    def es_excedida_capacidad_vehiculo(self) -> bool:
        """
        Verifica si alguna ruta excede la capacidad del vehículo.

        Returns:
            bool: True si alguna ruta excede la capacidad, False en caso contrario.
        """
        return any(self.constantes.capacidad_vehiculo < ruta.obtener_total_entregado() for ruta in self.rutas)

    def _obtener_niveles_inventario_proveedor(self) -> list[float]:
        """
        Calcula los niveles de inventario del proveedor en cada periodo.

        Returns:
            list[float]: Lista con los niveles de inventario del proveedor en cada tiempo.

        Raises:
            AttributeError: Si las constantes, las rutas o el proveedor no están definidas.
        """
        proveedor = self.constantes.proveedor
        nivel_almacenamiento = proveedor.nivel_almacenamiento
        niveles = [nivel_almacenamiento]

        for t in range(self.constantes.horizonte_tiempo):
            nivel_almacenamiento += proveedor.nivel_produccion - self.rutas[t].obtener_total_entregado()
            niveles.append(nivel_almacenamiento)

        return niveles

    def _obtener_niveles_inventario_cliente(self, cliente):
        """
        Calcula los niveles de inventario del cliente en cada periodo.

        Args:
            cliente (Cliente): Cliente para calcular su inventario.

        Returns:
            list[float]: Lista con los niveles de inventario del cliente en cada tiempo.
        """
        nivel_almacenamiento = cliente.nivel_almacenamiento
        inventario = [nivel_almacenamiento]

        for t in range(1, self.constantes.horizonte_tiempo + 1):
            nivel_almacenamiento += self.rutas[t - 1].obtener_cantidad_entregada(cliente) - cliente.nivel_demanda
            inventario.append(nivel_almacenamiento)

        return inventario


    def _es_admisible(self) -> bool:
        """
        Verifica si la solución es admisible (sin desabastecimiento ni sobreabastecimiento en clientes).

        Returns:
            bool: True si la solución es admisible, False en caso contrario.
        """
        return not (self._cliente_tiene_desabastecimiento() or self._cliente_tiene_sobreabastecimiento())

    def _es_factible(self) -> bool:
        """
        Verifica si una solución es factible.

        Returns:
            bool: True si la solución cumple todas las restricciones, False en caso contrario.
        """
        return not (
            self._cliente_tiene_desabastecimiento()
            or self.proveedor_tiene_desabastecimiento()
            or self._cliente_tiene_sobreabastecimiento()
            or self.es_excedida_capacidad_vehiculo()
        )

    def _cliente_tiene_desabastecimiento(self) -> bool:
        """
        Verifica si algún cliente tiene desabastecimiento.

        Returns:
            bool: True si algún cliente tiene inventario por debajo de su nivel mínimo.
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

    def _costo(self) -> float:
        """
        Calcula el costo total de la solución.

        Returns:
            float: Costo total de la solución.
        """
        costo_almacenamiento = sum(
            nivel * self.constantes.proveedor.costo_almacenamiento
            for nivel in self.inventario_proveedor
        )
        costo_almacenamiento += sum(
            cliente.costo_almacenamiento * self.inventario_clientes[cliente.id][t]
            for cliente in self.constantes.clientes
            for t in range(self.constantes.horizonte_tiempo + 1)
        )

        costo_transporte = sum(ruta.obtener_costo() for ruta in self.rutas)

        penalty1 = sum(
            max(0, ruta.obtener_total_entregado() - self.constantes.capacidad_vehiculo)
            for ruta in self.rutas
        ) * self.constantes.alfa.obtener_valor()

        penalty2 = sum(
            max(0, -nivel) for nivel in self.inventario_proveedor
        ) * self.constantes.beta.obtener_valor()

        return costo_almacenamiento + costo_transporte + penalty1 + penalty2


    def cumple_restricciones(self, MIP, MIPcliente = None, MIPtiempo = None, operation = None):
        constantes = self.constantes
        B   = self.inventario_proveedor
        I   = [self.inventario_clientes.get(cliente.id, None) for cliente in constantes.clientes]
        r0  = [constantes.proveedor.nivel_produccion for t in range(constantes.horizonte_tiempo+1)]
        ri  = [c.nivel_demanda for c in constantes.clientes]
        x   = [
            [self.rutas[t].obtener_cantidad_entregada(c) for t in range(constantes.horizonte_tiempo)]
            for c in constantes.clientes
        ]
        x_np = np.array(x)
        theta = [
            [(1 if self.es_visitado(c, t) else 0) for t in range(constantes.horizonte_tiempo)]
            for c in constantes.clientes
        ]
        
        # Variables MIP 2
        v   = [
            [ (1 if ((operation == "INSERT") and (MIPtiempo == t) and (MIPcliente == c)) else 0 ) for t in range(constantes.horizonte_tiempo)]
            for c in constantes.clientes
        ]
        w   = [
            [ (1 if ((operation == "REMOVE") and (MIPtiempo == t) and (MIPcliente == c)) else 0 ) for t in range(constantes.horizonte_tiempo)]
            for c in constantes.clientes
        ]
        sigma = [
            [(1 if self.es_visitado(c, t) else 0) for t in range(constantes.horizonte_tiempo)]
            for c in constantes.clientes
        ]
       
        # Restricción 2: Definición del nivel de inventario del proveedor.
        if (not all([(B[t] == (B[t-1] + r0[t-1] - np.sum( x_np[:, t-1]))) for t in range(1, constantes.horizonte_tiempo+1)])):
            return 2            
        
        # Restricción 3: El nivel de inventario del proveedor debe poder satisfacer la demanda en el tiempo t.
        if (not all(B[t] >= np.sum( x_np[:, t]) for t in range(constantes.horizonte_tiempo))):
            return 3
        
        # Restricción 4: Definición del nivel de inventario de los clientes
        if (not all([(I[c][t] == (I[c][t-1] + x[c][t-1] - ri[c] ))
                for c in range(len(constantes.clientes))
                for t in range(1, constantes.horizonte_tiempo+1)]
        )):
            return 4
        
        if constantes.politica_reabastecimiento == "OU": 
            # Restricción 5: La cantidad entregada al cliente no es menos de la necesaria para llenar el inventario.
            if (not all([(x[c][t] >= ((cliente.nivel_maximo * theta[c][t]) - I[c][t]))
                for c, cliente in enumerate(constantes.clientes)
                for t in range(constantes.horizonte_tiempo)]
            )):
                return 5
        
        # Restricción 6: La cantidad entregada al cliente no debe generar sobreabastecimiento en el cliente.
        if (not all([( x[c][t] <= (cliente.nivel_maximo - I[c][t]) )
            for c, cliente in enumerate(constantes.clientes)
            for t in range(constantes.horizonte_tiempo)]
        )):
            return 6
        
        if constantes.politica_reabastecimiento == "OU":
            # Restricción 7: La cantidad entregada a un cliente es menor o igual al nivel máximo de inventario si es que lo visita.
            if  (not all([( x[c][t] <= (cliente.nivel_maximo * theta[c][t]) )
                for c, cliente in enumerate(constantes.clientes)
                for t in range(constantes.horizonte_tiempo)]
            )):
                return 7
            
        # Restricción 8: La cantidad entregada a los clientes en un t dado, es menor o igual a la capacidad del camión.
        if (not all([np.sum( x_np[:, t]) <= constantes.capacidad_vehiculo for t in range(constantes.horizonte_tiempo)])):
            return 8
        
        if MIP == 1:
            #  Restricción 9: Una ruta solo puede asignarse a un período de tiempo
            if not all(sum(ruta) <= 1 for ruta in sigma):
                return 9

            # Restricción 10: Solo una ruta puede asignarse a un período de tiempo dado
            if not all(sum(tiempo) <= 1 for tiempo in zip(*sigma)):
                return 10

            # Restricción 11: Un cliente puede ser atendido solo si la ruta está asignada
            if not all(x[c][t] <= constantes.clientes[c].nivel_maximo * sigma[c][t] for c in range(len(constantes.clientes)) for t in range(constantes.horizonte_tiempo)):
                return 11

            # Restricción 12: No puede atenderse un cliente si fue removido de la ruta asignada
            if not all(x[c][t] == 0 if w[c][t] else True for c in range(len(constantes.clientes)) for t in range(constantes.horizonte_tiempo)):
                return 12
            
            # Restricción 13: Un cliente puede ser removido solo si su ruta está asignada
            if not all(w[c][t] <= sigma[c][t] for c in range(len(constantes.clientes)) for t in range(constantes.horizonte_tiempo)):
                return 13

            # Restricción 18: Las variables de asignación de rutas (zr_t) deben ser binarias
            if not all(value in [0, 1] for fila in sigma for value in fila):
                return 18

            # Restricción 19: La variable de asignación epsilon_it debe ser binaria
            if not all(value in [0, 1] for fila in theta for value in fila):
                return 19

            # Restricción 20: El inventario en los clientes debe ser mayor o igual a cero
            if not all(I[c][t] >= 0 for c in range(len(constantes.clientes)) for t in range(constantes.horizonte_tiempo)):
                return 20
        
        # Restricción 14: La cantidad entregada a los clientes siempre debe ser mayor o igual a cero
        if not np.all(x_np >= 0):
            return 14
        
        #Restricción 17: Theeta puede tener el valor 0 o 1
        if constantes.politica_reabastecimiento == "OU":
            if not all(value in [0, 1] for fila in theta for value in fila):
                return 17
          
        if MIP == 2:            
            # Restricción 21 (MIP2): Si se inserta una visita, no debe haber una visita existente
            if not all(v[c][t] <= 1 - sigma[c][t] for c in range(len(constantes.clientes)) for t in range(constantes.horizonte_tiempo)):
                return 21

            # Restricción 22 (MIP2): Si se elimina una visita, debe existir previamente una visita
            if not all(w[c][t] <= sigma[c][t] for c in range(len(constantes.clientes)) for t in range(constantes.horizonte_tiempo)):
                return 22
    
            # Restricción 23: La cantidad entregada al cliente i no puede ser mayor a la capacidad máxima
            if not all([ ( x[c][t] <= (cliente.nivel_maximo * (sigma[c][t] + v[c][t] - w[c][t])))
                for c, cliente in enumerate(constantes.clientes)
                for t in range(constantes.horizonte_tiempo)]
            ):
                return 23
            
            #Restricción 24: v_it debe ser 0 o 1
            if not all(value in [0, 1] for fila in v for value in fila):
                return 24
            
            #Restricción 25: w_it debe ser 0 o 1
            if not all(value in [0, 1] for fila in w for value in fila):
                return 25
            
        return 0
            
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