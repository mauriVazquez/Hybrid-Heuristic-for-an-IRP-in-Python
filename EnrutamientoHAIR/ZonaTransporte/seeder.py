import os
from random import randint
from ZonaTransporte.models import Zona, Vehiculo
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
        print(nb_clientes)
        next(file_it)
        coord_x_proveedor = float(next(file_it))
        coord_y_proveedor = float(next(file_it))
        nivel_almacenamiento_proveedor = int(next(file_it))
        nivel_produccion_proveedor = int(next(file_it))
        costo_almacenamiento_proveedor = float(next(file_it))

        zonas = Zona.objects.filter(nombre=archivo)
        if not zonas.exists():
            Zona.objects.create(
                nombre = archivo,
            )
        zona = Zona.objects.get(nombre=archivo)
       
        vehiculo = Vehiculo.objects.filter(zona = zona.id)
        if not vehiculo.exists():
            random_selected = randint(0,len(marcamodelo)-1)
            Vehiculo.objects.create(
                patente = 'AG'+str(randint(100,999))+'PY',
                marca = marcamodelo[random_selected][0],
                modelo = marcamodelo[random_selected][1],
                color = 'Blanco',
                capacidad = vehicle_capacity,
                zona_id = zona.id
            )

        proveedor = Proveedor.objects.filter(coord_x=coord_x_proveedor, coord_y = coord_y_proveedor)
        if not proveedor.exists():
            Proveedor.objects.create(
                nombre = fake.company(),
                localidad_id = 42105030,
                direccion = fake.address(),
                coord_x = coord_x_proveedor,
                coord_y = coord_y_proveedor,
                costo_almacenamiento = costo_almacenamiento_proveedor,
                nivel_almacenamiento = nivel_almacenamiento_proveedor,
                nivel_maximo = 100000,
                nivel_minimo = 0,
                nivel_produccion = nivel_produccion_proveedor,
                zona_id = zona.id
            )

        for i in range(nb_clientes):
            next(file_it)
            coord_x = float(next(file_it))
            coord_y = float(next(file_it))
            nivel_almacenamiento = int(next(file_it))
            nivel_maximo = int(next(file_it))
            nivel_minimo = int(next(file_it))
            nivel_demanda = int(next(file_it))
            costo_almacenamiento = float(next(file_it))
            
            clientes = Cliente.objects.filter(coord_x=coord_x, coord_y=coord_y)
            if not clientes.exists():
                Cliente.objects.create(
                    nombre = fake.name(),
                    localidad_id = 42105030,
                    direccion = fake.address(),
                    coord_x = coord_x,
                    coord_y = coord_y,
                    costo_almacenamiento = costo_almacenamiento,
                    nivel_almacenamiento = nivel_almacenamiento,
                    nivel_maximo = nivel_maximo,
                    nivel_minimo = nivel_minimo,
                    nivel_demanda = nivel_demanda,
                    zona_id = zona.id
                )
        # # Verificar si la ruta corresponde a un archivo
        # if os.path.isfile(ruta_completa):
        #     print("Archivo:", ruta_completa)
        # # Si es un directorio, llamar recursivamente a la función para ese directorio
        # elif os.path.isdir(ruta_completa):
        #     print("Directorio:", ruta_completa)
        #     recorrer_directorio(ruta_completa)

seeder()