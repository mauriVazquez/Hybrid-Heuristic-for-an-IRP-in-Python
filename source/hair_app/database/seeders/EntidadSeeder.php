<?php

namespace Database\Seeders;

use App\Models\Cliente;
use App\Models\Proveedor;
use App\Models\Zona;
use App\Models\Vehiculo;
use App\Models\Localidad;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\File;

class EntidadSeeder extends Seeder
{
    public function cargar_vehiculo($data){
        if (Vehiculo::where('patente', 'abs1n5.dat')->count() == 0){
            $vehiculo = Vehiculo::create([
                'patente' => 'abs1n5.dat',
                'marca' => 'Ford',
                'nombre_modelo' => 'Transit',
                'anio' => 2023,
                'color' => 'Blanco',
                'capacidad' => $data[2],
                'zona_id' => Zona::where('nombre','=','abs1n5.dat')->first()->id,
            ]);
        }
    }

    public function cargar_proveedor($data, $localidad_id){
        $faker = \Faker\Factory::create();
        if (Proveedor::where('coord_x', $data[1])->where('coord_y', $data[2])->count() == 0){
            $proveedor = Proveedor::create([
                'localidad_id' => $localidad_id,
                'nombre' => $faker->name,
                'direccion' => $faker->address,
                'coord_x' => $data[1],
                'coord_y' => $data[2],
                'nivel_almacenamiento' => $data[3],
                'nivel_produccion' => $data[4],
                'costo_almacenamiento' => $data[5],
                'zona_id' => Zona::where('nombre','=','abs1n5.dat')->first()->id,
            ]);
        }
    }

    public function cargar_cliente($data, $localidad_id){
        $faker = \Faker\Factory::create();

        if (Cliente::where('coord_x', $data[1])->where('coord_y', $data[2])->count() == 0){
            $cliente = Cliente::create([
                'localidad_id' => $localidad_id,
                'nombre' => $faker->name,
                'direccion' => $faker->address,
                'coord_x' => $data[1],
                'coord_y' => $data[2],
                'nivel_almacenamiento' => $data[3],
                'nivel_maximo' => $data[4],
                'nivel_minimo' => $data[5],
                'nivel_demanda' => $data[6],
                'costo_almacenamiento' => $data[7],
                'zona_id' => Zona::where('nombre','=','abs1n5.dat')->first()->id,
            ]);
        }
    }

    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Ruta del archivo de texto
        $filePath = resource_path('data/instancias/abs1n5.dat');
        //Tomo una localidad random
        $localidad = Localidad::inRandomOrder()->first();
        // Verificar si el archivo existe
        if (File::exists($filePath)) {
            // Leer el contenido del archivo
            $content = File::get($filePath);

            // Dividir las líneas del archivo
            $lines = explode("\n", $content);
            for ($i=0; $i < count($lines); $i++) {
                $data = preg_split('/\s+/', trim($lines[$i]));
                switch($i){
                    case 0:
                        $this->cargar_vehiculo($data, $localidad->id);
                        break;
                    case 1:
                        $this->cargar_proveedor($data, $localidad->id);
                        break;
                    default:
                        $this->cargar_cliente($data, $localidad->id);
                }
            }
         }
    }
}
