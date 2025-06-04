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
        // Validación de datos de entrada
        $request->validate([
            'mejor_solucion' => 'required|array',
            'mejor_solucion.costo' => 'required|numeric',
            'mejor_solucion.rutas' => 'required|array',
            'user_id' => 'required|exists:users,id',
        ]);

        $solucion = $request->input('mejor_solucion');
        $user_id  = $request->input('user_id');

        try {
            //transacción de base de datos para asegurar la integridad de los datos
            DB::transaction(function () use ($solucion, $plantilla, $user_id) {
                //crea una nueva solución asociada a la plantilla
                $nuevaSolucion = Solucion::create([
                    'plantilla_id' => $plantilla->id,
                    'estado' => 0,
                    'politica_reabastecimiento' => 'ML',
                    'vehiculo_id' => $plantilla->vehiculo_id,
                    'proveedor_id' => $plantilla->proveedor_id,
                    'costo' => $solucion['costo'],
                ]);

                //por cada ruta en la solución, crea un modelo Ruta y le asocia las visitas
                foreach ($solucion['rutas'] as $key => $ruta) {
                    $rutaModelo = Ruta::create([
                        'costo' => $ruta['costo'],
                        'orden' => $key,
                        'solucion_id' => $nuevaSolucion->id,
                    ]);

                    foreach ($ruta['clientes'] as $key => $cliente) {
                        if (!isset($ruta['cantidades'][$key])) {
                            throw new \Exception("Error en los datos: cantidad no definida para cliente $cliente");
                        }

                        Visita::create([
                            'ruta_id' => $rutaModelo->id,
                            'cliente_id' => $cliente,
                            'orden' => $key,
                            'cantidad' => $ruta['cantidades'][$key],
                            'realizada' => false
                        ]);
                    }
                }

                // Actualizar el estado de la plantilla a Resuelto
                $plantilla->update([
                    'estado' => EstadosEnum::Resuelto,
                ]);

                // Enviar notificación al usuario
                $user = User::find($user_id);
                if ($user) {
                    Notification::make()
                        ->actions([
                            Action::make('view')->label('Ver solución')
                                ->button()
                                ->url('soluciones/' . $nuevaSolucion->id),
                        ])
                        ->title('Optimización de plantilla finalizada.')
                        ->success()
                        ->broadcast($user);
                }
            });

            return response()->json(['message' => 'Solución guardada con éxito'], 200);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Error al guardar la solución',
                'error' => $e->getMessage()
            ], 500);
        }
    }
}
