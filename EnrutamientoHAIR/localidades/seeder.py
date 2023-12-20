import json
from localidades.models import Provincia
from localidades.models import Departamento
from localidades.models import Localidad

def provincias_seeder():  
    with open('./localidades/data/provincias.json', 'r', encoding="utf8") as archivo_json:
        datos = json.load(archivo_json)
    for provincia in datos['provincias']:
        p = Provincia.objects.filter(id=provincia['id'])
        if not p.exists():
            Provincia.objects.create(
                id = provincia['id'],
                nombre = provincia['nombre'],
            )

def departamentos_seeder():  
    with open('./localidades/data/departamentos_pampeanos.json', 'r', encoding="utf8") as archivo_json:
        datos = json.load(archivo_json)
    for departamento in datos['departamentos']:
        d = Departamento.objects.filter(id=departamento['id'])
        if not d.exists():
            Departamento.objects.create(
                id = departamento['id'],
                nombre = departamento['nombre'],
                provincia_id = departamento['provincia']['id']
            )

def localidades_seeder(): 
    with open('./localidades/data/localidades_pampeanas.json', 'r', encoding="utf8") as archivo_json:
        datos = json.load(archivo_json)
    for localidad in datos['localidades']:
        dep = Departamento.objects.filter(id=localidad['departamento']['id'])
        if dep.exists():
            l = Localidad.objects.filter(id=localidad['id'])
            if not l.exists():
                Localidad.objects.create(
                    id = localidad['id'],
                    nombre = localidad['nombre'],
                    departamento_id = localidad['departamento']['id']
                )

def seeder():
    provincias_seeder()
    departamentos_seeder()
    localidades_seeder()

seeder()