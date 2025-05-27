<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class ClientePythonResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->resource->id,
            'coord_x' => $this->resource->coord_x,
            'coord_y' => $this->resource->coord_y,
            'costo_almacenamiento' => $this->resource->costo_almacenamiento,
            'nivel_almacenamiento' => $this->resource->nivel_almacenamiento,
            'nivel_maximo' => $this->resource->nivel_maximo,
            'nivel_minimo' => $this->resource->nivel_minimo,
            'nivel_demanda' => $this->resource->nivel_demanda,
        ];
    }
}
