<?php

namespace App\Filament\Resources\FormularioEjecucionResource\Pages;

use App\Filament\Resources\FormularioEjecucionResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListFormularioEjecucions extends ListRecords
{
    protected static string $resource = FormularioEjecucionResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),
        ];
    }
}
