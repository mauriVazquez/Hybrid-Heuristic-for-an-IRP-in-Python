<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class ProveedorPythonResource extends JsonResource
{
    /**
     * Transform the resource into an array.
     *
     * @return array<string, mixed>
     */
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'coord_x' => $this->coord_x,
            'coord_y' => $this->coord_y,
            'costo_almacenamiento' => $this->costo_almacenamiento,
            'nivel_almacenamiento' => $this->nivel_almacenamiento,
            'nivel_produccion' => $this->nivel_produccion,
        ];
    }
}
