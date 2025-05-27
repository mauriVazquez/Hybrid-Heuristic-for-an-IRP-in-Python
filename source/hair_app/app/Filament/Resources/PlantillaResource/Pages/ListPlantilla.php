<?php

namespace App\Filament\Resources\PlantillaResource\Pages;

use App\Filament\Resources\PlantillaResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListPlantillas extends ListRecords
{
    protected static string $resource = PlantillaResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),
        ];
    }
}
