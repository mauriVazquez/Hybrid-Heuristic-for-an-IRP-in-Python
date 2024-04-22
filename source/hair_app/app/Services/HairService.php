<?php
namespace App\Services;

use App\Http\Resources\ClientePythonResource;
use App\Http\Resources\ProveedorPythonResource;
use App\Models\Cliente;
use App\Models\Proveedor;
use App\Models\Vehiculo;
use GuzzleHttp\Client;
use GuzzleHttp\RequestOptions;

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

    public function enviarSolicitudEjecucion(Proveedor $proveedor, $clientes, Vehiculo $vehiculo, $horizonLength)
    {
        $data = [
            'horizon_length' => $horizonLength,
            'capacidad_vehiculo' => $vehiculo->capacidad,
            'proveedor' => ProveedorPythonResource::make($proveedor),
            'clientes' => ClientePythonResource::collection(Cliente::whereIn('id', $clientes)->get()),
        ];

        $response = $this->getHttpClient()->post($this->url . '/solicitud-ejecucion', [
            RequestOptions::BODY => json_encode($data),
        ]);
        return $response->getBody();
    }
}
