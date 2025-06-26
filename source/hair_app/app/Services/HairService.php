<?php

namespace App\Services;

use App\Http\Resources\ClientePythonResource;
use App\Http\Resources\ProveedorPythonResource;
use App\Models\Cliente;
use App\Models\Proveedor;
use App\Models\Vehiculo;
use Exception;
use GuzzleHttp\Client;
use GuzzleHttp\RequestOptions;
use App\enums\EstadosEnum;

class HairService
{

    protected $url;
    protected $httpClient;

    public function __construct()
    {
        $this->url = env('HAIR_SERVICE_HOST');
    }

    public function getHttpClient(): Client
    {
        if (!$this->httpClient)
            $this->httpClient = new Client();

        return $this->httpClient;
    }

    public function enviarSolicitudEjecucion($plantilla_id, Proveedor $proveedor, $clientes, Vehiculo $vehiculo, $horizonLength)
    {   
        // creo un array con los datos necesarios para enviar al servicio
        $data = [
            'plantilla_id' => $plantilla_id,
            'user_id' => auth()->id(), 
            'horizonte_tiempo' => $horizonLength,
            'capacidad_vehiculo' => $vehiculo->capacidad,
            'proveedor' => ProveedorPythonResource::make($proveedor), //Formateo el proveedor
            'clientes' => ClientePythonResource::collection(Cliente::whereIn('id', $clientes)->get()), //Formateo los clientes
        ];

        // hago la petición al servicio
        $response = $this->getHttpClient()->post($this->url . '/optimizar_recorrido', [
            RequestOptions::BODY => json_encode($data),
        ]);

        // Si la respuesta no es exitosa, lanzo una excepción
        if ($response->getStatusCode() > 201)
            throw new Exception("Ocurrio un error al consultar al servicio: {$response->getBody()}", $response->getStatusCode());

        // actualizo el estado de la plantilla a procesando
        $plantilla = \App\Models\Plantilla::find($plantilla_id);
        $plantilla->estado = EstadosEnum::Procesando;
        $plantilla->save();

        // decodifico la respuesta y la retorno
        return json_decode($response->getBody());
    }
}
