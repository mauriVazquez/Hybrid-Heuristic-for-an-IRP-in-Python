<?php

namespace Database\Seeders;

use App\Models\Cliente;
use App\Models\Proveedor;
use App\Models\Zona;
use App\Models\Vehiculo;
use App\Models\Localidad;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\File;

class EntidadSeeder extends Seeder
{
    protected function obtener_marca_vehiculo_aleatoria(){
        $carMakesAndModels = [
            "Fiat" => ["Fiorino", "Doblo"],
            "Peugeot" => ["Partner", "Expert"],
            "Citroën" => ["Berlingo", "Jumper"],
            "Renault" => ["Kangoo", "Master"],
            "Volkswagen" => ["Caddy", "Transporter"],
            "Iveco" => ["Daily"],
            "Mercedes-Benz" => ["Sprinter"],
        ];
        $marca = array_rand($carMakesAndModels);
        $modelo = array_rand($carMakesAndModels[$marca]);
        return ["marca" => $marca, "modelo" =>$carMakesAndModels[$marca][$modelo]];
    }

    public function cargar_vehiculo($data, $file, $zona_id)
    {
        //Tomo un modelo aleatorio
        $vehiculo_aleatorio = $this->obtener_marca_vehiculo_aleatoria();
        $colores = ['Blanco','Gris','Negro'];
        $vehiculo = Vehiculo::firstOrCreate(
            ['patente' => $file],
            [
                'patente' => $file,
                'marca' => $vehiculo_aleatorio['marca'],
                'nombre_modelo' =>  $vehiculo_aleatorio['modelo'],
                'anio' => rand(date('Y')-5, date('Y')),
                'color' => $colores[array_rand($colores)],
                'capacidad' => $data[2],
                'zona_id' => $zona_id,
            ]
        );
    }

    public function cargar_proveedor($data, $localidad_id, $zona_id)
    {
        $faker = \Faker\Factory::create();

        $proveedor = Proveedor::firstOrCreate(
            ['coord_x' => $data[1], 'coord_y' => $data[2]],
            [
                'localidad_id' => $localidad_id,
                'nombre' => $faker->name,
                'direccion' => $faker->address,
                'coord_x' => $data[1],
                'coord_y' => $data[2],
                'nivel_almacenamiento' => $data[3],
                'nivel_produccion' => $data[4],
                'costo_almacenamiento' => $data[5],
                'zona_id' => $zona_id,
            ]
        );
    }

    public function cargar_cliente($data, $localidad_id, $zona_id)
    {
        $faker = \Faker\Factory::create();
        
        $cliente = Cliente::firstOrCreate(
            ['coord_x' => $data[1], 'coord_y' => $data[2]],
            [
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
                'zona_id' => $zona_id,
            ]
        );
    }

    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $base_path = base_path('database/data/instancias');

        foreach (File::files($base_path) as $file) {
            $fileName = basename($file);
            $file_path = $base_path . DIRECTORY_SEPARATOR . $fileName;
            $zona = Zona::firstOrCreate(['nombre' => $fileName]);
            
            //Tomo una localidad random
            $localidad = Localidad::inRandomOrder()->first();

            $content = File::get($file_path);
            // Dividir las líneas del archivo
            $lines = explode("\n", $content);
            for ($i = 0; $i < count($lines); $i++) {
                $data = preg_split('/\s+/', trim($lines[$i]));
                if(sizeof($data) > 1){
                    switch ($i) {
                        case 0:
                            $this->cargar_vehiculo($data, $fileName, $zona->id);
                            break;
                        case 1:
                            $this->cargar_proveedor($data, $localidad->id, $zona->id);
                            break;
                        default:
                            $this->cargar_cliente($data, $localidad->id, $zona->id);
                    }
                }
            }
        }
    }
}
