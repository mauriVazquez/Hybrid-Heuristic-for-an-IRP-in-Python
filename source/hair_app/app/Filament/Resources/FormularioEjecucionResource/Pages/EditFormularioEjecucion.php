<?php

namespace App\Filament\Resources\FormularioEjecucionResource\Pages;

use App\Filament\Resources\FormularioEjecucionResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditFormularioEjecucion extends EditRecord
{
    protected static string $resource = FormularioEjecucionResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\DeleteAction::make(),
        ];
    }
}
