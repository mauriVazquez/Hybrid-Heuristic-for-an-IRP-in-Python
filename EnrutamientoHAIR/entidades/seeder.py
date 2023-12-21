from entidades.models import Cliente, Proveedor
from ZonaTransporte.models import Zona
from faker import Faker

def seeder():
    fake = Faker()
    zonas = Zona.objects.all()
    for zona in zonas:
        filename = './instancias/'+zona.nombre
        with open(filename) as f:
                file_it = iter([str(elem) for elem in f.read().split()])

        nb_clientes = int(next(file_it)) - 1
        horizon_length = int(next(file_it))
        vehicle_capacity = int(next(file_it))
        next(file_it)
        coord_x_proveedor = float(next(file_it))
        coord_y_proveedor = float(next(file_it))
        nivel_almacenamiento_proveedor = int(next(file_it))
        nivel_produccion_proveedor = int(next(file_it))
        costo_almacenamiento_proveedor = float(next(file_it))

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
        
seeder()