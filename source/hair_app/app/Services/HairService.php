<?php


namespace App\Services;

use App\Http\Resources\ClientePythonCollection;
use App\Http\Resources\ClientePythonResource;
use App\Http\Resources\ProveedorPythonResource;
use App\Http\Resources\VehiculoPythonResource;
use App\Models\Cliente;
use App\Models\Proveedor;
use App\Models\Vehiculo;
use GuzzleHttp\Client;
use GuzzleHttp\Psr7\Request;
use GuzzleHttp\RequestOptions;
use Illuminate\Support\Facades\Http;

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
            'proveedor' => ProveedorPythonResource::make($proveedor)->jsonSerialize(),
            'clientes' => ClientePythonResource::collection(Cliente::whereIn('id', $clientes)->get())->jsonSerialize(),
            'vehiculo' => VehiculoPythonResource::make($vehiculo)->jsonSerialize(),
            'horizon_length' => $horizonLength,
        ];

        info($data);

        $response = $this->getHttpClient()->post($this->url . '/solicitud-ejecucion', [
            RequestOptions::FORM_PARAMS => $data,
            RequestOptions::HEADERS => [
                'Content-Type' => "application/x-www-form-urlencoded"
            ]
        ]);

        info($response->getBody());

        return $response->getBody();
    }
}
