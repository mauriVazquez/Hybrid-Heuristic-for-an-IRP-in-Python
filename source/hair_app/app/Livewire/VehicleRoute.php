<?php

namespace App\Livewire;

use Livewire\Component;

class VehicleRoute extends Component
{
    public $routeData = []; // Datos del grafo (coordenadas x, y)
    public function mount($routeData)
    {   
        // Simula datos de la ruta que provienen de la base de datos o de una API
        $this->routeData = $routeData;

    }

    public function render()
    {
        return view('livewire.vehicle-route');
    }
}
