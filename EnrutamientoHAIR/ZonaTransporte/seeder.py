import os
from random import randint
from ZonaTransporte.models import Zona, Vehiculo
from datetime import datetime
from entidades.models import Cliente, Proveedor
from faker import Faker

def seeder():
    fake = Faker()
    marcamodelo = [['Toyota','Hilux'], ['Volkswagen','Amarok'],['Chevrolet','S10'],['Fiat','Strada'],['Ford','Ranger'],['Dodge','RAM']]
    ruta = 'instancias'
    # Obtener la lista de archivos y directorios en la ruta proporcionada
    lista_archivos = os.listdir(ruta)

    for archivo in lista_archivos:
        ruta_completa = os.path.join(ruta, archivo)
        with open(ruta_completa) as f:
            file_it = iter([str(elem) for elem in f.read().split()])
        nb_clientes = int(next(file_it)) - 1
        horizon_length = int(next(file_it))
        vehicle_capacity = int(next(file_it))

        zonas = Zona.objects.filter(nombre=archivo)
        if not zonas.exists():
            Zona.objects.create(
                nombre = archivo,
            )
        zona = Zona.objects.get(nombre=archivo)
       
        vehiculo = Vehiculo.objects.filter(capacidad = vehicle_capacity)
        if not vehiculo.exists():
            #Almaceno el año para su posterior uso
            random_selected = randint(0,len(marcamodelo)-1)
            Vehiculo.objects.create(
                patente = archivo,
                marca = marcamodelo[random_selected][0],
                nombre_modelo = marcamodelo[random_selected][1],
                anio = datetime.now().year,
                color = 'Blanco',
                capacidad = vehicle_capacity,
                zona = zona
            )
        # # Verificar si la ruta corresponde a un archivo
        # if os.path.isfile(ruta_completa):
        #     print("Archivo:", ruta_completa)
        # # Si es un directorio, llamar recursivamente a la función para ese directorio
        # elif os.path.isdir(ruta_completa):
        #     print("Directorio:", ruta_completa)
        #     recorrer_directorio(ruta_completa)

seeder()