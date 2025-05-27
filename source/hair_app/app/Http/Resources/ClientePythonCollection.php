<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\ResourceCollection;

class ClientePythonCollection extends ResourceCollection
{
    /**
     * Transform the resource collection into an array.
     *
     * @return array<int|string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'data' => $this->collection->transform(function ($cliente) {
                return [
                    'id' => $cliente->id,
                    'coord_x' => $cliente->coord_x,
                    'coord_y' => $cliente->coord_y,
                    'costo_almacenamiento' => $cliente->costo_almacenamiento,
                    'nivel_almacenamiento' => $cliente->nivel_almacenamiento,
                    'nivel_maximo' => $cliente->nivel_maximo,
                    'nivel_minimo' => $cliente->nivel_minimo,
                    'nivel_demanda' => $cliente->nivel_demanda,
                ];
            })
        ];
    }
}
