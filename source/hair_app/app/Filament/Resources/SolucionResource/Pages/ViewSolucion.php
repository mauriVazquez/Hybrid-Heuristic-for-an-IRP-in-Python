<?php

namespace App\Filament\Resources\SolucionResource\Pages;

use App\Filament\Resources\SolucionResource;
use Filament\Resources\Pages\ViewRecord;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Columns\ToggleColumn;
use Filament\Tables\Table;
use Filament\Tables\Concerns\InteractsWithTable;
use Filament\Tables\Contracts\HasTable;
use Filament\Tables\Filters\SelectFilter;
use Illuminate\Database\Eloquent\Relations\HasManyThrough;

class ViewSolucion extends ViewRecord implements HasTable
{
    use InteractsWithTable;
    protected static string $resource = SolucionResource::class;


    protected static string $view = 'filament.resources.soluciones.pages.view-solucion';

    public $currentRouteData = [];

    protected function mutateFormDataBeforeFill(array $data): array
    {   
        $this->record->refresh();
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
                'name' => $visita['cliente']['nombre'],
                'color' => $visita['realizada'] ? 'green' : 'blue',
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

    public function table(Table $table): Table
    {
        return $table
            ->relationship(fn (): HasManyThrough => $this->record->visitas())
            ->columns([
                TextColumn::make('ruta.orden')->label('Ruta')
                ->bulleted(),
                TextColumn::make('cliente.nombre')->label('Cliente'),
                TextColumn::make('cantidad')->label('Cantidad'),
                ToggleColumn::make('realizada')->label('Realizada'),
            ])
            ->filters([
                // filter by ruta
                SelectFilter::make('ruta_id')
                    ->options(fn () => $this->record->rutas->pluck('orden', 'id')->toArray())
                    ->label('Ruta'),
            ]);
    }
}
