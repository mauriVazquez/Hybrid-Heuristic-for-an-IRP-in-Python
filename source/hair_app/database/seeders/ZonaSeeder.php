<?php

namespace Database\Seeders;

use App\Models\Zona;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\File;


class ZonaSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        $directorio = resource_path('data/instancias'); // Ajusta la ruta según tu estructura de directorios

        if (File::isDirectory($directorio)) {
            $archivos = File::files($directorio);

            // $archivos es ahora una colección de objetos 'SplFileInfo' que representan los archivos en el directorio
            foreach ($archivos as $archivo) {
                $zona = Zona::create([
                    'nombre' => $archivo->getFilename()
                ]);
            }
        } else {
            echo 'El directorio no existe.';
        }
    }
}
