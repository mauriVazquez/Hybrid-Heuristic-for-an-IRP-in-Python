<?php

namespace App\Filament\Resources\RecorridoResource\Pages;

use App\Filament\Resources\RecorridoResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListRecorridos extends ListRecords
{
    protected static string $resource = RecorridoResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),
        ];
    }
}
