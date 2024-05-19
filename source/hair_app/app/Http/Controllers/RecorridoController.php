<?php

namespace App\Http\Controllers;

use App\Models\Recorrido;
use Filament\Notifications\Notification;
use Illuminate\Http\Request;

class RecorridoController extends Controller
{
    public function guardarSolucion(Request $request, Recorrido $recorrido)
    {
        $solucion = $request->input('mejor_solucion');
        info(json_encode($solucion));
        // Notification::make()
        //     ->title('Procesamiento de recorrido finalizado')
        //     ->body('Ya puedes ver la mejor ruta encontrada')
        //     ->success()
        //     ->broadcast(auth()->user());
    }
}
