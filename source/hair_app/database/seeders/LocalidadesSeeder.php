<?php
namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Provincia;
use App\Models\Departamento;
use App\Models\Localidad;

class LocalidadesSeeder extends Seeder
{
    public function run()
    {
        $this->provinciasSeeder();
        $this->departamentosSeeder();
        $this->localidadesSeeder();
    }

    public function provinciasSeeder()
    {
        $file = file_get_contents(base_path('database/data/provincias.json'));
        $datos = json_decode($file, true);

        foreach ($datos['provincias'] as $provincia) {
            $p = Provincia::find($provincia['id']);
            if (!$p) {
                Provincia::create([
                    'id' => $provincia['id'],
                    'nombre' => $provincia['nombre'],
                ]);
            }
        }
    }

    public function departamentosSeeder()
    {
        $file = file_get_contents(base_path('database/data/departamentos_pampeanos.json'));
        $datos = json_decode($file, true);

        foreach ($datos['departamentos'] as $departamento) {
            $d = Departamento::find($departamento['id']);
            if (!$d) {
                Departamento::create([
                    'id' => $departamento['id'],
                    'nombre' => $departamento['nombre'],
                    'provincia_id' => $departamento['provincia']['id'],
                ]);
            }
        }
    }

    public function localidadesSeeder()
    {
        $file = file_get_contents(base_path('database/data/localidades_pampeanas.json'));
        $datos = json_decode($file, true);

        foreach ($datos['localidades'] as $localidad) {
            $dep = Departamento::find($localidad['departamento']['id']);
            if ($dep) {
                $l = Localidad::find($localidad['id']);
                if (!$l) {
                    Localidad::create([
                        'id' => $localidad['id'],
                        'nombre' => $localidad['nombre'],
                        'departamento_id' => $localidad['departamento']['id'],
                    ]);
                }
            }
        }
    }
}