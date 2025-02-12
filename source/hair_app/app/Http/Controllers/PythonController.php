<?php

namespace App\Http\Controllers;

use App\Http\Resources\ClientePythonCollection;
use App\Http\Resources\ProveedorPythonResource;
use App\Http\Resources\VehiculoPythonResource;
use App\Models\Cliente;
use App\Models\Proveedor;
use App\Models\Vehiculo;
use Illuminate\Support\Facades\Http;

class PythonController extends Controller
{
    public static function runPythonScript($proveedor_id, $clientes_id, $vehiculo_id,$horizonte_tiempo)
    {
        $data = [
            'proveedor'=> ProveedorPythonResource::make(Proveedor::find($proveedor_id)),
            'clientes' => ClientePythonCollection::make(Cliente::whereIn('id', $clientes_id)->get()),
            'vehiculo' => VehiculoPythonResource::make(Vehiculo::find($vehiculo_id)),
            'horizonte_tiempo' => $horizonte_tiempo,
        ];
        
        try {
            // Realiza la solicitud POST al servicio externo
            $response = Http::post('hair-service/optimizar_recorrido', $data);
            // Verifica si la solicitud fue exitosa (código de estado 200)
            if ($response->successful()) {
                return json_decode($response);
            } else {
                // Maneja el caso en que la solicitud no sea exitosa
                return json_encode(['error' => 'La solicitud al servicio externo no fue exitosa']);
            }
        } catch (\Exception $e) {
            // Maneja cualquier excepción que pueda ocurrir durante la solicitud
            return json_encode(['error' => $e->getMessage()]);
        }
    }
}
