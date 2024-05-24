<?php

namespace App\Http\Controllers;

use App\enums\EstadosRecorrido;
use App\Models\Recorrido;
use App\Models\Ruta;
use App\Models\Solucion;
use App\Models\User;
use App\Models\Visita;
use Filament\Notifications\Notification;
use Filament\Notifications\Actions\Action;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class RecorridoController extends Controller
{
    public function guardarSolucion(Request $request, Recorrido $recorrido)
    {
        $solucion = $request->input('mejor_solucion');
        $user_id = $request->input('user_id');
        DB::transaction(function () use ($solucion, $recorrido, $user_id) {
            $nuevaSolucion = Solucion::create([
                'recorrido_id' => $recorrido->id,
                'estado' => 0,
                'politica_reabastecimiento' => 'ML',
                'vehiculo_id' => $recorrido->vehiculo_id,
                'proveedor_id' => $recorrido->proveedor_id,
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

            $recorrido->update([
                'estado' => EstadosRecorrido::Resuelto,
            ]);

            Notification::make()
                ->title('Procesamiento de recorrido finalizado')
                ->body('Ya puedes ver la ruta propuesta')
                ->success()
                ->actions([
                    Action::make('ver')
                        ->button(),
                ])
                ->broadcast(User::find($user_id));
        });
    }
}
