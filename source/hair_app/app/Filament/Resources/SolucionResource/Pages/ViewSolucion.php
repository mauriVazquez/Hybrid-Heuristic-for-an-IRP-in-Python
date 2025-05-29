<?php

namespace App\Filament\Resources\SolucionResource\Pages;

use App\Filament\Resources\SolucionResource;
use App\Models\Visita;
use Filament\Resources\Pages\ViewRecord;
use Filament\Tables\Columns\TextColumn;
use Filament\Tables\Columns\ToggleColumn;
use Filament\Tables\Table;
use Filament\Tables\Concerns\InteractsWithTable;
use Filament\Tables\Contracts\HasTable;
use Illuminate\Database\Eloquent\Builder;
use Livewire\Livewire;

class ViewSolucion extends ViewRecord implements HasTable
{
    use InteractsWithTable;

    protected static string $resource = SolucionResource::class;
    protected static string $view = 'filament.resources.soluciones.pages.view-solucion';

    public int|string|null $rutaId = null;
    public $rutas = [];
    public string $canvasRefreshKey = '';

    public function getTitle(): string
    {
        return 'Ver Solución';
    }

    protected function mutateFormDataBeforeFill(array $data): array
    {
        $this->record->refresh();
        $this->rutaId ??= $this->record->rutas->first()?->id;
        $this->rutas = $this->record->rutas->toArray(); // O ->all() si querés objetos
        $this->canvasRefreshKey = now()->timestamp;
        return $data;
    }

    public function updatedRutaId(): void
    {
        $this->resetTable();
    }

    public function getCurrentRouteDataProperty(): array
    {
        $ruta = $this->record->rutas->firstWhere('id', $this->rutaId);

        if (!$ruta) {
            return [
                'orden' => '-',
                'puntos' => [],
            ];
        }

        $proveedor = [
            'name' => 'Proveedor',
            'color' => 'red',
            'x' => $this->record->proveedor['coord_x'],
            'y' => $this->record->proveedor['coord_y'],
        ];

        $visitas = collect($ruta['visitas'] ?? [])->map(fn($visita) => [
            'name'  => $visita['cliente']['nombre'],
            'color' => $visita['realizada'] ? 'green' : 'blue',
            'x'     => $visita['cliente']['coord_x'],
            'y'     => $visita['cliente']['coord_y'],
        ])->toArray();

        return [
            'orden'  => $ruta['orden'],
            'puntos' => array_merge([$proveedor], $visitas, [$proveedor]),
        ];
    }

    public function table(Table $table): Table
    {
        return $table
            ->query(fn() => \App\Models\Visita::query()
                ->where('ruta_id', $this->rutaId)
                ->whereHas('ruta', fn($q) => $q->where('solucion_id', $this->record->id)))
            ->columns([
                TextColumn::make('ruta.orden')->label('Ruta')->bulleted(),
                TextColumn::make('cliente.nombre')->label('Cliente'),
                TextColumn::make('cantidad')->label('Cantidad'),
                ToggleColumn::make('realizada')
                    ->label('Realizada')
                    ->afterStateUpdated(function () {
                        $this->record->refresh(); // Asegura tener el modelo actualizado
                        $this->canvasRefreshKey = now()->timestamp;
                    }),

            ])
            ->emptyStateIcon('heroicon-o-check')
            ->emptyStateHeading('No hay visitas en esta ruta')
            ->emptyStateDescription('Seleccioná otra ruta para ver sus visitas.')
        ;
    }
}
