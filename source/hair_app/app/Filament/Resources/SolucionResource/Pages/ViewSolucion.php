<?php

namespace App\Filament\Resources\SolucionResource\Pages;

use App\Filament\Resources\SolucionResource;
use Filament\Actions;
use Filament\Resources\Pages\ViewRecord;

class ViewSolucion extends ViewRecord
{
    protected static string $resource = SolucionResource::class;

    protected static string $view = 'filament.resources.soluciones.pages.view-solucion';

    public $currentRouteData = [];
    
    protected function mutateFormDataBeforeFill(array $data): array
    {
        $this->setCurrentRouteData($this->record['rutas'][0]);
        return $data;
    }

    public function setCurrentRouteData($ruta)
    {
        $this->currentRouteData = $this->getRouteData($ruta);
    }

    public function getRouteData($ruta): array
    {

        $routeData = [];
        
        // get Proveedor coords 
        $routeData[] = [
            'x' => $this->record['proveedor']['coord_x'],
            'y' => $this->record['proveedor']['coord_y'],
        ];

        foreach ($ruta['visitas'] ?? [] as $visita) {
            $routeData[] = [
                'name' => 'Cliente',
                'color' => 'blue',
                'x' => $visita['cliente']['coord_x'],
                'y' => $visita['cliente']['coord_y'],
            ];
        }

        $routeData[] = [
            'name' => 'Proveedor',
            'color' => 'red',
            'x' => $this->record['proveedor']['coord_x'],
            'y' => $this->record['proveedor']['coord_y'],
        ];

        return $routeData;
    }
}
