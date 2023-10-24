import matplotlib.pyplot as plt

class Graph():
    def draw_routes(coords,routes, supplier_coords):
        enum_clients = ['red','green','blue','purple','orange','yellow','cyan','magenta','pink','brown','black','gray','darkgray']
        enum_routes = enum_clients[::-1]
        for index, route in enumerate(routes):
            # # Coordenadas de los puntos
            x = [supplier_coords[0]]+route[0]+[supplier_coords[0]]
            y = [supplier_coords[1]]+route[1]+[supplier_coords[1]]
            # Graficar los puntos
            plt.plot(x, y, color=enum_routes[index], linestyle='-', linewidth=2, label='Ruta'+str(index+1), zorder=1)

        for index, coord in enumerate(coords):
            # Graficar los puntos
            plt.scatter(coord[0], coord[1], color=enum_clients[index], marker=('^' if index ==0 else 'o'), label=('Provider' if index ==0 else 'Client'+str(index-1)),zorder=2)
        

        # Personalizar el gráfico
        plt.title('Gráfico de Puntos')
        plt.xlabel('Eje X')
        plt.ylabel('Eje Y')
        plt.legend()

        # Mostrar el gráfico
        plt.show()