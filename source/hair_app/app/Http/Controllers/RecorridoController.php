<?php

namespace App\Http\Controllers;

use App\Models\Recorrido;
use Filament\Notifications\Notification;
use Illuminate\Http\Request;

class RecorridoController extends Controller
{
    public function guardarSolucion(Request $request, Recorrido $recorrido)
    {
        info($recorrido);
        info($request);

        // Notification::make()
        //     ->title('Procesamiento de recorrido finalizado')
        //     ->body('Ya puedes ver la mejor ruta encontrada')
        //     ->success()
        //     ->broadcast(auth()->user());

    }
}
