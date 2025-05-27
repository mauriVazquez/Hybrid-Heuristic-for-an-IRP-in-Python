<?php

namespace App\Filament\Resources\SolucionResource\Pages;

use App\Filament\Resources\SolucionResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditSolucion extends EditRecord
{
    protected static string $resource = SolucionResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\DeleteAction::make(),
        ];
    }
}
