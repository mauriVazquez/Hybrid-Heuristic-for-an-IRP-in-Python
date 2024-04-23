<?php

namespace App\Filament\Resources\RecorridoResource\Pages;

use App\Filament\Resources\RecorridoResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditRecorrido extends EditRecord
{
    protected static string $resource = RecorridoResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\DeleteAction::make(),
        ];
    }
}
