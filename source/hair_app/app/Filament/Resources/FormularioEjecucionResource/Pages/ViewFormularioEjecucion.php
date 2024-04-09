<?php

namespace App\Filament\Resources\FormularioEjecucionResource\Pages;

use App\Filament\Resources\FormularioEjecucionResource;
use App\Http\Controllers\PythonController;
use App\Models\Zona;
use Filament\Resources\Pages\Concerns\InteractsWithRecord;
use Filament\Resources\Pages\ViewRecord;
use Illuminate\Contracts\Support\Htmlable;
use PhpParser\Node\Stmt\Label;

class ViewFormularioEjecucion extends ViewRecord
{
    use InteractsWithRecord;
    protected static string $resource = FormularioEjecucionResource::class;
    protected static string $view = 'filament.pages.view-results';
    
    public function getTitle() : string
    {
      return '';
    }
    public function getColumnSpan()
    {
     return 2;   
    }
    public function getColumnStart()
    {
     return 2;   
    }

    public function mount(int | string $record): void
    {
        $this->record = $this->resolveRecord($record);
        $response = PythonController::runPythonScript(
            $this->record->proveedor->id, 
            $this->record->clientes->pluck('id'), 
            $this->record->vehiculo->id, 
            '2'
        );
        $this->attributes['soluciones'] = $response->data ?? null;
    }
}
