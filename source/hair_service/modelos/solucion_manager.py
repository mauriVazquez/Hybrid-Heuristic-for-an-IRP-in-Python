class SolucionManager():
    @staticmethod
    def inicializar():
        solucion = Solucion.obtener_empty_solucion()
        # Simular demanda de clientes y actualizar stock
        for cliente in constantes.clientes:
            stock_cliente = cliente.nivel_almacenamiento
            for t in range(constantes.horizon_length):
                stock_cliente -= cliente.nivel_demanda
                if stock_cliente < cliente.nivel_demanda:
                    # Calcular cantidad máxima a entregar
                    maxima_entrega = cliente.nivel_maximo - stock_cliente
                    # Calcular cantidad a entregar según la política
                    cantidad_entregada = maxima_entrega if constantes.politica_reabastecimiento == "ML" else randint(1, maxima_entrega)
                    # Insertar visita en la solución
                    solucion.rutas[t].insertar_visita(cliente, cantidad_entregada , None)
                     # Actualizar demanda acumulada
                    stock_cliente += cantidad_entregada
        print(f"Inicialización: {solucion}")
        return solucion