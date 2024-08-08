import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
class Graph():
    def draw_rutas(clients_coords, proveedor_coords):
        # Create a figure and subplots
        fig, axes = plt.subplots(2, 2, figsize=(10, 6))  # Adjust rows, columns, and figure size

        # Generate and display plots in each subplot
        for i, (ax, client_coord) in enumerate(zip(axes.flat, clients_coords)):
            x = [proveedor_coords[0]]+client_coord[0]+[proveedor_coords[0]]
            y = [proveedor_coords[1]]+client_coord[1]+[proveedor_coords[1]]
            print(x)
            print(y)
            ax.plot(x,y)
            ax.set_title(f"Ruta {i+1}")

        # Adjust layout and display all plots at once
        plt.tight_layout()
        plt.show()

        # colors = ['red','green','blue','purple','orange','yellow','cyan','magenta','pink','brown','black','gray','darkgray']
    
        # for indice, ruta in enumerate(clients_coords):
        #     # # Coordenadas de los puntos
        #     x = [proveedor_coords[0]]+ruta[0]+[proveedor_coords[0]]
        #     y = [proveedor_coords[1]]+ruta[1]+[proveedor_coords[1]]
        #     # Graficar los puntos
        #     plt.plot(x, y, color=colors[indice], linestyle='-', linewidth=1, label='Ruta'+str(indice+1), zorder=1)

        # # for client_coord in clients_coords:
        # #     # Graficar los puntos
        # #     plt.scatter(client_coord[0], client_coord[1], color=colors[indice], marker='o', label='Cliente'+str(indice-1),zorder=2)
            
       
        # # plt.scatter(proveedor_coords[0], proveedor_coords[1], color=colors[indice], marker='^', label='Proveedor' ,zorder=2)
        

        # # Personalizar el gráfico
        # plt.title('Gráfico de Puntos')
        # plt.xlabel('Eje X')
        # plt.ylabel('Eje Y')
        # plt.legend()

        # # Mostrar el gráfico
        # plt.show()