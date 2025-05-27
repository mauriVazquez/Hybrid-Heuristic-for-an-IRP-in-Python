<?php

namespace App\Filament\Resources\PlantillaResource\Pages;

use App\enums\EstadosEnum;
use App\Filament\Resources\PlantillaResource;
use Filament\Actions;
use Filament\Resources\Pages\CreateRecord;

class CreatePlantilla extends CreateRecord
{
    protected static string $resource = PlantillaResource::class;

    protected function mutateFormDataBeforeCreate(array $data): array
    {
        $data['estado'] = EstadosEnum::Pendiente;
        return $data;
    }
}
