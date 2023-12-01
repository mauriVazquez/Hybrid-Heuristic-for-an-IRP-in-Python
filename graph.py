import matplotlib.pyplot as plt

class Graph():
    def draw_rutas(coords,rutas, proveedor_coords):
        colors = ['red','green','blue','purple','orange','yellow','cyan','magenta','pink','brown','black','gray','darkgray']
    
        for indice, ruta in enumerate(rutas):
            # # Coordenadas de los puntos
            x = [proveedor_coords[0]]+ruta[0]+[proveedor_coords[0]]
            y = [proveedor_coords[1]]+ruta[1]+[proveedor_coords[1]]
            # Graficar los puntos
            plt.plot(x, y, color=colors[indice], linestyle='-', linewidth=1, label='Ruta'+str(indice+1), zorder=1)

        for indice, coord in enumerate(coords):
            # Graficar los puntos
            plt.scatter(coord[0], coord[1], color=colors[indice], marker=('^' if indice ==0 else 'o'), label=('Proveedor' if indice ==0 else 'Cliente'+str(indice-1)),zorder=2)
        

        # Personalizar el gráfico
        plt.title('Gráfico de Puntos')
        plt.xlabel('Eje X')
        plt.ylabel('Eje Y')
        plt.legend()

        # Mostrar el gráfico
        plt.show()