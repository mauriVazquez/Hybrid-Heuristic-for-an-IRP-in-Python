<?php

namespace App\Http\Controllers;

use App\enums\EstadosEnum;
use App\Models\Plantilla;
use App\Models\Ruta;
use App\Models\Solucion;
use App\Models\User;
use App\Models\Visita;
use Filament\Notifications\Notification;
use Filament\Notifications\Actions\Action;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class PlantillaController extends Controller
{
    public function guardarSolucion(Request $request, Plantilla $plantilla)
    {
        info("Vuelta");
        $solucion = $request->input('mejor_solucion');
        $user_id  = $request->input('user_id');
        DB::transaction(function () use ($solucion, $plantilla, $user_id) {
            $nuevaSolucion = Solucion::create([
                'plantilla_id' => $plantilla->id,
                'estado' => 0,
                'politica_reabastecimiento' => 'ML',
                'vehiculo_id' => $plantilla->vehiculo_id,
                'proveedor_id' => $plantilla->proveedor_id,
                'costo' => $solucion['costo'],
            ]);

            foreach ($solucion['rutas'] as $key => $ruta) {
                $rutaModelo = Ruta::create([
                    'costo' => $ruta['costo'],
                    'orden' => $key,
                    'solucion_id' => $nuevaSolucion->id,
                ]);
                foreach ($ruta['clientes'] as $key => $cliente) {
                    Visita::create([
                        'ruta_id' => $rutaModelo->id,
                        'cliente_id' => $cliente,
                        'orden' => $key,
                        'cantidad' => $ruta['cantidades'][$key],
                        'realizada' => false
                    ]);
                }
            }

            $plantilla->update([
                'estado' => EstadosEnum::Resuelto,
            ]);

            $user = User::find($user_id);
            Notification::make()
                ->actions([
                    Action::make('view')->label('Ver solución')
                        ->button()
                        ->url('soluciones/'.$nuevaSolucion->id),
                ])
                ->title('Optimización de plantilla finalizada.')
                ->success()
                ->broadcast($user);
        });
    }
}
